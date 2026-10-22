"""Decision-orchestrated state machine.

    REACTIVITY ─▶ INTERFACE_TYPE ─▶ STACK_CHECK ─┐
        [det]        [LLM]             [det]     │ reactive neighbours → feedback → INTERFACE_TYPE
                                                 ▼
    for each adjacent pair in the stack:
        FACETS ─▶ MATCH+VALIDATE ─▶ ENERGETICS ─▶ JUDGE ─▶ next pair / DONE
        [LLM]        [det]             [det]       [LLM]
          ▲            │ no valid match              │ reject + action
          └────────────┴─────── feedback ◀───────────┘
              thicker_slabs / next_termination / different_facets / larger_cell

The decision policy chooses the transitions at the branch points (interface
type, facet re-planning, the judge's action); every number is computed
deterministically and every gate is hard. The policy is the LLM (default), a
person through the same prompts, or deterministic rules (policies.py) — the
three arms of the evaluation. Every decision and transition goes into the
run's decision_log.json, tagged with the policy that made it.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

from .context import Candidate, InterfaceContext, InterfaceTypeDecision, JudgeVerdict
from .log import RunLog
from .policies import Policy, as_policy
from .tools import energetics
from .tools.descriptors import interface_descriptors
from .tools.materials import get_bulk, get_entries
from .tools.matcher import MatchSettings, enumerate_interfaces
from .tools.reactivity import check_stack, elements_of, interfacial_reactivity
from .tools.validation import oxidation_map, validate


@dataclass
class OrchestratorSettings:
    n_runs: int = 3                  # consensus samples per LLM decision
    max_retries: int = 2             # per branch point
    max_facet_pairs: int = 3
    top_k_candidates: int = 2        # relaxed per facet pair
    registry_n_xy: int = 3
    registry_gaps: tuple[float, ...] = (1.8, 2.2, 2.6)
    relax: bool = True
    build_structures: bool = True    # False → stop after the interface-type decision (fast LLM-only screen)
    fmax: float = 0.05
    steps: int = 300
    match: MatchSettings = field(default_factory=MatchSettings)


class Orchestrator:
    def __init__(
        self,
        ctx: InterfaceContext,
        policy,
        calc=None,
        settings: OrchestratorSettings | None = None,
        bulk_fn=get_bulk,
        entries_fn=get_entries,
        run_root: str | None = None,
    ):
        self.ctx = ctx
        self.s = settings or OrchestratorSettings()
        # a Policy, or a bare llm(system, user) callable (wrapped in LLMPolicy)
        self.policy: Policy = as_policy(policy, n_runs=self.s.n_runs)
        self.calc = calc                     # None → dry run: stop after MATCH+VALIDATE
        self.bulk_fn = bulk_fn
        self.entries_fn = entries_fn
        self.log = RunLog(ctx.name, run_root)
        self._bulk_cache: dict = {}

    # ------------------------------------------------------------------ utils
    def _bulk(self, formula: str):
        if formula not in self._bulk_cache:
            from pymatgen.core import Composition

            red = Composition(formula).reduced_formula
            mp_id = None
            if red == Composition(self.ctx.electrode).reduced_formula:
                mp_id = self.ctx.electrode_mp_id
            elif red == Composition(self.ctx.electrolyte).reduced_formula:
                mp_id = self.ctx.electrolyte_mp_id
            self._bulk_cache[formula] = self.bulk_fn(formula, mp_id) if mp_id else self.bulk_fn(formula)
        return self._bulk_cache[formula]

    def _transition(self, frm: str, to: str, why: str):
        self.log.record("orchestrator", "transition", {"from": frm, "to": to, "why": why})

    # ------------------------------------------------------------------ stages
    def stage_reactivity(self):
        self.entries = self.entries_fn(elements_of(self.ctx.electrode, self.ctx.electrolyte))
        rep = interfacial_reactivity(self.ctx.electrode, self.ctx.electrolyte, self.entries, voltage=self.ctx.voltage)
        self.log.record("reactivity", "gate", rep, context=self.ctx.to_dict())
        return rep

    def stage_interface_type(self, rep) -> InterfaceTypeDecision:
        feedback = ""
        decision = None
        for attempt in range(self.s.max_retries + 1):
            decision, agree, samples = self.policy.decide_interface_type(self.ctx, rep, self.entries, feedback)
            self.agreement = agree
            self.log.record("interface_type", "decision", decision, policy=self.policy.name, agreement=agree,
                            samples=samples, feedback=feedback, attempt=attempt)
            if decision.interface_type == "sharp":
                return decision
            ok, results = check_stack(decision.stack, self.entries, self.ctx.voltage)
            self.log.record("stack_check", "gate", {"ok": ok, "pairs": results}, stack=decision.stack)
            if ok:
                return decision
            bad = [f"{a}|{b} reacts ({r.min_reaction_energy:+.3f} eV/atom → {', '.join(r.most_favourable.products)})"
                   for (a, b), r in results if r.reactive]
            feedback = "adjacent layers are not mutually stable: " + "; ".join(bad)
            self._transition("STACK_CHECK", "INTERFACE_TYPE", feedback)
        self._transition("STACK_CHECK", "SHARP_FALLBACK", "retries exhausted; modelling the sharp interface")
        self.agreement = 0.0
        return InterfaceTypeDecision("sharp", [self.ctx.electrode, self.ctx.electrolyte], character="none",
                                     rationale="fallback after failed stack checks")

    def stage_pair(self, substrate: str, film: str) -> dict:
        """FACETS → MATCH+VALIDATE → ENERGETICS → JUDGE for one adjacent pair."""
        s_struct, f_struct = self._bulk(substrate), self._bulk(film)
        s_oxi, f_oxi = oxidation_map(s_struct), oxidation_map(f_struct)
        match = dataclasses.replace(self.s.match)
        feedback, tried, skip = "", [], 0
        tried_pairs: set = set()
        context = (f"{self.ctx.role} side of a {self.ctx.electrode} | {self.ctx.electrolyte} cell at "
                   f"{self.ctx.voltage} V vs Li/Li+; this pair is {substrate} | {film}")

        facets = None
        for attempt in range(self.s.max_retries + 1):
            if facets is None:
                facets = self.policy.propose_facets(substrate, film, s_struct, f_struct, context,
                                                    self.s.max_facet_pairs, feedback, tried_pairs)
                self.log.record("facets", "decision", [{"choice": c, "votes": v} for c, v in facets],
                                policy=self.policy.name, pair=(substrate, film), feedback=feedback, attempt=attempt)
                if not facets:
                    break
                tried_pairs |= {(c.substrate_miller, c.film_miller) for c, _ in facets}

            # ---- MATCH + VALIDATE (deterministic)
            pool: list[tuple[Candidate, object, list[str]]] = []
            for choice, _votes in facets:
                found = enumerate_interfaces(s_struct, f_struct, choice.substrate_miller, choice.film_miller,
                                             (substrate, film), match)
                n_valid = 0
                for cand, iface in found:
                    ok, rej, warn = validate(cand, iface, max_atoms=self.ctx.max_atoms, max_strain=self.ctx.max_strain,
                                             film_oxi=f_oxi, substrate_oxi=s_oxi,
                                             film_formula=film, substrate_formula=substrate)
                    if ok:
                        pool.append((cand, iface, warn))
                        n_valid += 1
                tried.append(f"{choice.substrate_miller}/{choice.film_miller}: {len(found)} matches, {n_valid} valid")
            pool.sort(key=lambda t: t[0].von_mises_strain / self.ctx.max_strain + t[0].n_atoms / self.ctx.max_atoms)
            self.log.record("match_validate", "gate", {"n_valid": len(pool), "tried": tried[-len(facets):],
                                                       "top": [p[0] for p in pool[:10]]}, pair=(substrate, film))
            if not pool:
                feedback = "no valid lattice match within the strain/size limits for: " + "; ".join(tried)
                self._transition("MATCH", "FACETS", feedback)
                facets = None
                continue

            if self.calc is None:
                return {"pair": (substrate, film), "status": "dry_run", "candidates": [p[0] for p in pool[:10]]}

            # ---- ENERGETICS + JUDGE
            accepted, verdicts = [], []
            for cand, iface, warn in pool[skip: skip + self.s.top_k_candidates]:
                res, relaxed, start = energetics.work_of_adhesion(
                    cand, iface, self.calc, n_xy=self.s.registry_n_xy, gaps=self.s.registry_gaps,
                    fmax=self.s.fmax, steps=self.s.steps, do_relax=self.s.relax)
                desc = interface_descriptors(start, relaxed, iface.film_indices, iface.substrate_indices)
                self.log.record("energetics", "compute", {"result": res, "descriptors": desc}, warnings=warn)
                if res.w_adh is None:
                    # No validated adhesion (exhausted relaxation, unrelaxed or non-finite): never judged or ranked.
                    verdict = JudgeVerdict("reject", "next_termination",
                                           f"energetics not validated ({res.status}: {', '.join(res.unconverged) or 'n/a'})")
                    self.log.record("judge", "gate", verdict, candidate=cand)
                    verdicts.append(verdict)
                    continue
                verdict, agree = self.policy.judge(res, desc, warn)
                self.log.record("judge", "decision", verdict, policy=self.policy.name, agreement=agree,
                                candidate=cand)
                verdicts.append(verdict)
                if verdict.verdict != "reject":
                    accepted.append((res, relaxed, verdict))

            if accepted:
                res, relaxed, verdict = max(accepted, key=lambda t: t[0].w_adh)
                path = self.log.dir / f"{substrate}__{film}_best.extxyz"
                from ase import Atoms

                Atoms(relaxed.numbers, positions=relaxed.positions, cell=relaxed.cell, pbc=True).write(path)
                return {"pair": (substrate, film), "status": "ok", "best": res, "verdict": verdict,
                        "structure": str(path)}

            action = verdicts[0].action
            self._transition("JUDGE", action, verdicts[0].rationale)
            if action == "thicker_slabs":
                match.film_thickness += 1
                match.substrate_thickness += 1
            elif action == "larger_cell":
                match.max_area *= 1.5
            elif action == "next_termination":
                skip += self.s.top_k_candidates
            elif action == "different_facets":
                feedback = "judge rejected the relaxed model: " + verdicts[0].rationale
                facets = None

        return {"pair": (substrate, film), "status": "failed", "tried": tried}

    # ------------------------------------------------------------------ run
    def run(self) -> dict:
        rep = self.stage_reactivity()
        decision = self.stage_interface_type(rep)
        pairs = []
        if self.s.build_structures:
            pairs = [self.stage_pair(a, b) for a, b in zip(decision.stack[:-1], decision.stack[1:])]
        summary = {
            "case": self.ctx.name,
            "policy": self.policy.name,
            "reactivity": {"reactive": rep.reactive, "min_reaction_energy": rep.min_reaction_energy,
                           "products": rep.most_favourable.products if rep.most_favourable else []},
            "decision": decision,
            "decision_agreement": getattr(self, "agreement", None),
            "pairs": pairs,
            "counters": {"single_points": energetics.Counter.single_points,
                         "relaxations": energetics.Counter.relaxations},
            "run_dir": str(self.log.dir),
        }
        self.log.record("summary", "compute", summary)
        return summary
