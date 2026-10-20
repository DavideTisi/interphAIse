"""Decision policies: who makes the three expert decisions.

The orchestrator never talks to an LLM directly; it asks a *policy*:

    decide_interface_type   sharp or interphase, layer stack, passivating or growing
    propose_facets          which facet pairs to put in contact
    judge                   is the relaxed structure physical, and what to do if not

Arms (same pipeline, same gates, same numbers; only the decisions differ):

    LLMPolicy(llm)            the LLM reasoners (reasoners/), consensus over n_runs samples
    LLMPolicy(HumanLLM())     a person answers the same prompts (human baseline)
    RulesPolicy()             deterministic expert rules, no LLM (this file)

The rules are the baseline the LLM has to beat. Every threshold lives in
RuleSettings so it can be reported and swept.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import asdict, dataclass
from typing import Callable, Protocol

import numpy as np
from pymatgen.core import Composition, Element, Structure

from .context import (
    EnergeticsResult,
    FacetChoice,
    InterfaceContext,
    InterfaceTypeDecision,
    JudgeVerdict,
    ReactivityReport,
)
from .llm import LLM


class Policy(Protocol):
    name: str

    def decide_interface_type(
        self, ctx: InterfaceContext, rep: ReactivityReport, entries, feedback: str = ""
    ) -> tuple[InterfaceTypeDecision, float, list[InterfaceTypeDecision]]: ...

    def propose_facets(
        self, substrate: str, film: str, s_struct: Structure, f_struct: Structure, context: str,
        max_pairs: int, feedback: str = "", tried: set | None = None,
    ) -> list[tuple[FacetChoice, float]]: ...

    def judge(
        self, res: EnergeticsResult, descriptors: dict, warnings: list[str]
    ) -> tuple[JudgeVerdict, float]: ...


# ---------------------------------------------------------------------------
# LLM arm (and human arm through HumanLLM)
# ---------------------------------------------------------------------------


class LLMPolicy:
    """Wraps the LLM reasoners. ``llm`` is any ``(system, user) -> dict`` callable."""

    def __init__(self, llm: LLM, n_runs: int = 3, name: str | None = None):
        self.llm = llm
        self.n_runs = n_runs
        self.name = name or ("human" if type(llm).__name__ == "HumanLLM" else "llm")

    def decide_interface_type(self, ctx, rep, entries, feedback=""):
        from .reasoners.interphase_reasoner import decide_interface_type

        return decide_interface_type(ctx, rep, self.llm, self.n_runs, feedback)

    def propose_facets(self, substrate, film, s_struct, f_struct, context, max_pairs, feedback="", tried=None):
        from .reasoners.facet_reasoner import propose_facets

        return propose_facets(substrate, film, s_struct, f_struct, self.llm, context, max_pairs, self.n_runs,
                              feedback)

    def judge(self, res, descriptors, warnings):
        from .reasoners.judge import judge

        return judge(res, descriptors, warnings, self.llm, self.n_runs)


def as_policy(llm_or_policy, n_runs: int = 3) -> Policy:
    """Accept either a Policy or a bare LLM callable (backwards compatible)."""
    if hasattr(llm_or_policy, "decide_interface_type"):
        return llm_or_policy
    return LLMPolicy(llm_or_policy, n_runs=n_runs)


# ---------------------------------------------------------------------------
# Rules arm
# ---------------------------------------------------------------------------


@dataclass
class RuleSettings:
    # Decision 1 — sharp or interphase
    sharp_threshold: float = -0.05       # eV/atom: min reaction energy above this → sharp
    max_intermediate: int = 3            # keep the dominant products (by atoms in the balanced reaction)
    # Decision 1 — passivating or growing
    metallic_gap: float = 0.1            # eV: PBE gap below this → electron-conducting phase → growing
    # Decision 2 — facets (BFDH)
    facet_max_index: int = 2
    facets_per_phase: int = 3
    # Decision 3 — physicality thresholds
    min_distance: float = 1.0            # Å, below → atoms overlap → reject, next termination
    max_gap_opening: float = 1.5         # Å, gap grew by more → slabs separated → reject, next termination
    max_penetration_fraction: float = 0.05   # atoms crossed the interface / all atoms → reject, different facets
    max_interface_displacement: float = 1.0  # Å mean in the interface region → reconstruction
    max_cn_change: float = 0.3           # relative change of interface coordination → reconstruction


def _is_metal_only(formula: str) -> bool:
    return all(Element(str(e)).is_metal for e in Composition(formula).elements)


def li_fraction(formula: str) -> float:
    c = Composition(formula)
    return c.get_atomic_fraction(Element("Li"))


def bfdh_ranking(structure: Structure, max_index: int = 2) -> list[tuple[tuple[int, int, int], float]]:
    """Bravais–Friedel–Donnay–Harker morphology ranking.

    Facets ordered by effective interplanar spacing: d_hkl / n, with n the
    smallest multiple for which the (atomic-number weighted) structure factor
    of n·(hkl) is non-zero, so systematic absences (e.g. bcc (100)) are
    handled. Larger effective d → slower growth → more prominent facet.
    Computed on the conventional standard cell.
    """
    from pymatgen.core.surface import get_symmetrically_distinct_miller_indices
    from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

    conv = SpacegroupAnalyzer(structure).get_conventional_standard_structure()
    frac = np.array(conv.frac_coords)
    z = np.array([site.specie.Z for site in conv], dtype=float)
    out = []
    for hkl in get_symmetrically_distinct_miller_indices(conv, max_index):
        h = np.array(hkl, dtype=float)
        d = conv.lattice.d_hkl(hkl)
        n_eff = None
        for n in range(1, 7):
            f = np.abs(np.sum(z * np.exp(2j * math.pi * frac @ (n * h))))
            if f > 1e-3 * z.sum():
                n_eff = n
                break
        if n_eff is None:
            continue
        out.append((tuple(int(x) for x in hkl), float(d / n_eff)))
    return sorted(out, key=lambda t: (-t[1], sum(abs(i) for i in t[0]), t[0]))


class RulesPolicy:
    """Deterministic expert rules for the three decisions. Agreement is always 1."""

    name = "rules"

    def __init__(self, settings: RuleSettings | None = None,
                 band_gap_fn: Callable[[str], float | None] | None = None):
        self.s = settings or RuleSettings()
        if band_gap_fn is None:
            from .tools.materials import get_band_gap

            band_gap_fn = get_band_gap
        self.band_gap_fn = band_gap_fn

    def describe(self) -> dict:
        return {"policy": self.name, **asdict(self.s)}

    # ---------------------------------------------------------------- decision 1
    def _order_stack(self, ctx: InterfaceContext, phases: list[str], entries) -> tuple[list[str], bool]:
        """First ordering of ``phases`` whose neighbours are all mutually stable.

        Ties are broken by Li fraction: the side with more Li gets the more
        Li-rich phases (Li-rich next to a Li-metal anode). Returns (stack, ok).
        """
        from .tools.reactivity import check_stack

        e, el = Composition(ctx.electrode).reduced_formula, Composition(ctx.electrolyte).reduced_formula
        descending = li_fraction(e) >= li_fraction(el)
        base = sorted(phases, key=lambda p: (li_fraction(p), p), reverse=descending)
        perms = [list(base)] + [list(p) for p in itertools.permutations(base) if list(p) != base]
        for perm in perms:
            stack = [e, *perm, el]
            ok, _ = check_stack(stack, entries, ctx.voltage)
            if ok:
                return stack, True
        return [e, *base, el], False

    def decide_interface_type(self, ctx, rep, entries, feedback=""):
        e, el = Composition(ctx.electrode).reduced_formula, Composition(ctx.electrolyte).reduced_formula
        if rep.min_reaction_energy > self.s.sharp_threshold or rep.most_favourable is None:
            d = InterfaceTypeDecision(
                "sharp", [e, el], character="none",
                rationale=(f"rule: min reaction energy {rep.min_reaction_energy:+.3f} eV/atom "
                           f"> {self.s.sharp_threshold:+.3f} eV/atom → sharp"))
            return d, 1.0, [d]

        amounts = rep.most_favourable.product_atoms or {p: 1.0 for p in rep.most_favourable.products}
        phases = [p for p in sorted(amounts, key=lambda p: -amounts[p]) if p not in (e, el)]
        phases = phases[: self.s.max_intermediate]
        if not phases:
            d = InterfaceTypeDecision("sharp", [e, el], character="none",
                                      rationale="rule: reactive but no product other than the end members → sharp")
            return d, 1.0, [d]

        stack, ok = self._order_stack(ctx, phases, entries)
        gaps = {p: self.band_gap_fn(p) for p in phases}
        conducting = []
        for p, g in gaps.items():
            if g is None:
                if _is_metal_only(p):
                    conducting.append(f"{p} (no gap data, metal-only composition)")
            elif g < self.s.metallic_gap:
                conducting.append(f"{p} (gap {g:.2f} eV)")
        character = "growing" if conducting else "passivating"
        gap_txt = ", ".join(f"{p}: {'?' if g is None else f'{g:.2f}'} eV" for p, g in gaps.items())
        d = InterfaceTypeDecision(
            "interphase", stack, character=character,
            rationale=(f"rule: min reaction energy {rep.min_reaction_energy:+.3f} eV/atom ≤ "
                       f"{self.s.sharp_threshold:+.3f} → interphase of the dominant hull products; order = first "
                       f"permutation with mutually stable neighbours{'' if ok else ' (none found, Li-fraction order)'}; "
                       f"band gaps {gap_txt}; "
                       + (f"electron-conducting: {', '.join(conducting)} → growing" if conducting
                          else f"all gaps ≥ {self.s.metallic_gap} eV → passivating")))
        return d, 1.0, [d]

    # ---------------------------------------------------------------- decision 2
    def propose_facets(self, substrate, film, s_struct, f_struct, context, max_pairs, feedback="", tried=None):
        tried = tried or set()
        s_rank = bfdh_ranking(s_struct, self.s.facet_max_index)
        f_rank = bfdh_ranking(f_struct, self.s.facet_max_index)
        k = self.s.facets_per_phase
        pairs = []
        # widen the window until enough untried pairs exist
        while True:
            cand = [(i + j, i, j) for i in range(min(k, len(s_rank))) for j in range(min(k, len(f_rank)))]
            cand.sort()
            pairs = [(s_rank[i], f_rank[j]) for _, i, j in cand
                     if (s_rank[i][0], f_rank[j][0]) not in tried][:max_pairs]
            if len(pairs) >= max_pairs or (k >= len(s_rank) and k >= len(f_rank)):
                break
            k += 1
        out = []
        for (sm, sd), (fm, fd) in pairs:
            out.append((FacetChoice(film=film, substrate=substrate, film_miller=fm, substrate_miller=sm,
                                    rationale=f"rule: BFDH effective d — substrate {sd:.2f} Å, film {fd:.2f} Å"),
                        1.0))
        return out

    # ---------------------------------------------------------------- decision 3
    def judge(self, res, descriptors, warnings):
        s, d = self.s, descriptors
        n = max(int(d.get("n_atoms", 1)), 1)
        crossed = d.get("film_atoms_penetrating_substrate", 0) + d.get("substrate_atoms_penetrating_film", 0)
        gap_open = d.get("gap_after_A", 0.0) - d.get("gap_before_A", 0.0)
        cn0, cn1 = d.get("mean_CN_interface_region_before"), d.get("mean_CN_interface_region_after")
        cn_change = abs(cn1 - cn0) / cn0 if cn0 else 0.0
        disp = d.get("mean_displacement_interface_region_A", 0.0)

        if d.get("min_distance_after_A", 9.9) < s.min_distance:
            v = JudgeVerdict("reject", "next_termination",
                             f"rule: overlapping atoms ({d['min_distance_after_A']:.2f} Å < {s.min_distance} Å)")
        elif gap_open > s.max_gap_opening or res.w_adh <= 0:
            v = JudgeVerdict("reject", "next_termination",
                             f"rule: slabs separated (gap +{gap_open:.2f} Å, W_adh {res.w_adh:.2f} J/m²)")
        elif crossed / n > s.max_penetration_fraction:
            v = JudgeVerdict("reject", "different_facets",
                             f"rule: {crossed} atoms crossed the interface ({crossed / n:.1%} > "
                             f"{s.max_penetration_fraction:.0%})")
        elif disp > s.max_interface_displacement or cn_change > s.max_cn_change:
            v = JudgeVerdict("reject", "thicker_slabs",
                             f"rule: strong reconstruction (mean interface displacement {disp:.2f} Å, "
                             f"coordination change {cn_change:.0%})")
        elif warnings:
            v = JudgeVerdict("accept_with_caveat", "none", "rule: passes all thresholds; caveats: " + "; ".join(warnings))
        else:
            v = JudgeVerdict("accept", "none", "rule: passes all thresholds")
        return v, 1.0


def make_policy(name: str, model: str | None = None, n_runs: int = 3, rule_settings: RuleSettings | None = None):
    """'llm' | 'rules' | 'human' → a Policy (used by the run scripts)."""
    if name == "rules":
        return RulesPolicy(rule_settings)
    if name == "human":
        from .llm import HumanLLM

        return LLMPolicy(HumanLLM(), n_runs=1, name="human")
    if name == "llm":
        from .llm import make_llm

        if not model:
            raise ValueError("the llm policy needs a model")
        return LLMPolicy(make_llm(model), n_runs=n_runs, name="llm")
    raise ValueError(f"unknown policy {name!r} (llm | rules | human)")
