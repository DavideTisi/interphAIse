"""Budgeted candidate search with a fixed evaluator, independent of the proposer."""
from __future__ import annotations

import json
import math
import random
import time
from dataclasses import asdict, dataclass, replace
from pathlib import Path

OBJECTIVE = "valid first; maximise worst-contact reaction energy; then weakest adhesion"
PROMPT = """You are a battery coating discovery scientist. Select only from available coatings.
Use chemical hypotheses and observed calculation feedback to choose promising candidates.
Do not invent computed outcomes. The fixed objective is supplied in the task.
Return {"proposals": [{"coating": "exact available formula", "hypothesis": "chemical rationale and how feedback informed the choice"}]}.
Return exactly the requested number of distinct candidates. No other candidates."""


@dataclass
class Evaluation:
    coating: str
    status: str
    worst_reaction_energy: float | None = None
    weakest_adhesion: float | None = None
    details: dict | None = None
    error: str | None = None


def quality(result: Evaluation, require_adhesion: bool = False) -> tuple:
    energy, adhesion = result.worst_reaction_energy, result.weakest_adhesion
    valid = (result.status == "ok" and energy is not None and math.isfinite(energy)
             and (not require_adhesion or (adhesion is not None and math.isfinite(adhesion))))
    if not valid:
        return (0, 0.0, 0.0)
    return (1, energy, adhesion if adhesion is not None and math.isfinite(adhesion) else 0.0)


def run_discovery(cfg, evaluator, *, strategy="iterative", budget=3, llm=None,
                  seed=0, require_adhesion=False, output: Path | None = None,
                  max_proposal_attempts=3, metadata=None):
    pool = list(cfg.coatings)
    if not pool or len(set(pool)) != len(pool):
        raise ValueError("Candidate pool must be nonempty and contain unique formulas")
    if not 1 <= budget <= len(pool) or max_proposal_attempts < 1:
        raise ValueError("Budget must be between 1 and pool size; proposal attempts must be positive")
    if strategy not in {"iterative", "upfront", "random", "fixed"}:
        raise ValueError("Unknown strategy")
    if strategy in {"iterative", "upfront"} and llm is None:
        raise ValueError("This strategy requires an LLM")
    state = dict(config=asdict(cfg), strategy=strategy, seed=seed, budget=budget,
                 objective=OBJECTIVE, require_adhesion=require_adhesion,
                 metadata=metadata or {}, proposal_attempts=[], history=[], trace=[], status="running")

    def save():
        if output is not None:
            output.parent.mkdir(parents=True, exist_ok=True)
            temp = output.with_suffix(".tmp")
            temp.write_text(json.dumps(state, indent=2, allow_nan=False))
            temp.replace(output)

    def propose(available, count):
        feedback = ""
        for _ in range(max_proposal_attempts):
            user = json.dumps(dict(task={"electrode": cfg.electrode, "electrolyte": cfg.electrolyte,
                                        "voltage": cfg.voltage}, objective=OBJECTIVE,
                                   require_adhesion=require_adhesion, available=available, count=count,
                                   evaluated=state["history"], validation_feedback=feedback))
            attempt = {"prompt": user}
            try:
                response = llm(PROMPT, user)
                attempt["response"] = response
                proposals = response["proposals"]
                if not isinstance(proposals, list) or len(proposals) != count:
                    raise ValueError("Return exactly the requested number of proposals")
                names = [p["coating"] for p in proposals]
                if any(n not in available for n in names) or len(set(names)) != len(names):
                    raise ValueError("Use distinct available candidates only")
                if any(not isinstance(p.get("hypothesis"), str) or not p["hypothesis"].strip() for p in proposals):
                    raise ValueError("Each proposal needs a nonempty hypothesis")
            except Exception as exc:
                feedback = f"{type(exc).__name__}: {exc}"
                attempt["error"] = feedback
                state["proposal_attempts"].append(attempt)
                save()
                continue
            state["proposal_attempts"].append(attempt)
            save()
            return proposals
        raise ValueError("Proposal attempts exhausted: " + feedback)

    save()
    try:
        available = pool.copy()
        planned = []
        if strategy == "upfront":
            planned = propose(available, budget)
        elif strategy in {"random", "fixed"}:
            if strategy == "random":
                random.Random(seed).shuffle(available)
            planned = [{"coating": c, "hypothesis": strategy + " baseline"} for c in available[:budget]]
        best = None
        for step in range(budget):
            proposal = propose(available, 1)[0] if strategy == "iterative" else planned[step]
            coating = proposal["coating"]
            started = time.monotonic()
            try:
                result = evaluator(coating)
                if result.coating != coating:
                    raise ValueError("Evaluator returned a different coating")
                if not quality(result, require_adhesion)[0]:
                    result = Evaluation(coating, "failed", details=result.details,
                                        error=result.error or "Invalid or incomplete evaluation")
            except Exception as exc:
                result = Evaluation(coating, "failed", error=f"{type(exc).__name__}: {exc}")
            available.remove(coating)
            state["history"].append(dict(proposal=proposal, result=asdict(result),
                                         elapsed_seconds=time.monotonic() - started))
            if quality(result, require_adhesion)[0] and (best is None or quality(result, require_adhesion) > quality(best, require_adhesion)):
                best = result
            state["trace"].append(dict(evaluations=step + 1, best=asdict(best) if best else None))
            save()
        state["status"] = "complete"
    except Exception as exc:
        state["status"] = "failed"
        state["error"] = f"{type(exc).__name__}: {exc}"
        save()
        raise
    save()
    return state


class CoatingEvaluator:
    """Same deterministic modelling policy for all search arms; never calls an LLM."""

    def __init__(self, cfg, *, calc=None, settings=None, run_root=None):
        self.cfg, self.calc, self.settings, self.run_root = cfg, calc, settings, run_root

    def __call__(self, coating):
        if coating not in self.cfg.coatings:
            raise ValueError("Candidate outside configured pool")
        from .screen import contacts_for, run_screen
        if self.calc is None:
            from .tools.materials import get_bulk, get_entries
            from .tools.reactivity import elements_of, interfacial_reactivity
            contacts = []
            for ctx in contacts_for(self.cfg, coating):
                get_bulk(ctx.electrode, ctx.electrode_mp_id)
                get_bulk(ctx.electrolyte, ctx.electrolyte_mp_id)
                entries = get_entries(elements_of(ctx.electrode, ctx.electrolyte, "Li"))
                rep = interfacial_reactivity(ctx.electrode, ctx.electrolyte, entries, ctx.voltage)
                contacts.append(dict(pair=list(rep.pair), reaction_energy=rep.min_reaction_energy,
                                     products=rep.most_favourable.products if rep.most_favourable else []))
            return Evaluation(coating, "ok", min(c["reaction_energy"] for c in contacts),
                              details={"contacts": contacts, "mode": "thermodynamic"})
        from .policies import RulesPolicy
        out = run_screen(replace(self.cfg, coatings=[coating], include_uncoated=False),
                         RulesPolicy(), calc=self.calc, settings=self.settings, run_root=self.run_root)
        if not out["ranking"]:
            return Evaluation(coating, "failed", error="No completed contacts", details={"run_dir": out["run_dir"]})
        row = out["ranking"][0]
        valid = all(c["status"] == "ok" for c in row["contacts"]) and len(row["contacts"]) == 2
        return Evaluation(coating, "ok" if valid else "failed", row["worst_reaction_energy"],
                          row["weakest_w_adh"], {"run_dir": out["run_dir"], "contacts": row["contacts"]})
