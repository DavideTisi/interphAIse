"""Decision 1: which facets of two adjacent phases to put in contact."""

from __future__ import annotations

from pymatgen.core import Structure

from ..context import FacetChoice
from ..llm import LLM
from .consensus import rank_by_votes, sample
from .prompts import FACET_SYSTEM, FACET_USER


def _miller(v) -> tuple[int, int, int]:
    m = tuple(int(x) for x in v)
    if len(m) == 4:  # tolerate hkil
        m = (m[0], m[1], m[3])
    if len(m) != 3 or m == (0, 0, 0):
        raise ValueError(f"bad Miller index {v}")
    return m  # type: ignore[return-value]


def _desc(s: Structure) -> tuple[str, str]:
    sg = s.get_space_group_info()
    return f"space group {sg[0]} (#{sg[1]})", ", ".join(f"{x:.2f}" for x in s.lattice.abc) + " Å"


def propose_facets(
    substrate: str,
    film: str,
    substrate_struct: Structure,
    film_struct: Structure,
    llm: LLM,
    context: str = "",
    max_pairs: int = 3,
    n_runs: int = 3,
    feedback: str = "",
) -> list[tuple[FacetChoice, float]]:
    """Consensus-ranked facet pairs with their vote fractions."""
    s_sg, s_abc = _desc(substrate_struct)
    f_sg, f_abc = _desc(film_struct)
    system = FACET_SYSTEM.replace("{max_pairs}", str(max_pairs))
    user = FACET_USER.format(
        substrate=substrate,
        substrate_sg=s_sg,
        substrate_abc=s_abc,
        film=film,
        film_sg=f_sg,
        film_abc=f_abc,
        context=context or "battery interface model",
        feedback=f"\nPreviously tried, with outcome: {feedback}\n" if feedback else "",
    )

    def one() -> list[FacetChoice]:
        raw = llm(system, user)
        pairs = raw.get("pairs", []) if isinstance(raw, dict) else raw
        out = [
            FacetChoice(
                film=film,
                substrate=substrate,
                film_miller=_miller(p["film_miller"]),
                substrate_miller=_miller(p["substrate_miller"]),
                rationale=str(p.get("rationale", "")),
            )
            for p in pairs[:max_pairs]
        ]
        if not out:
            raise ValueError("no facet pairs returned")
        return out

    lists = sample(one, n_runs)
    return rank_by_votes(lists, key=lambda c: (c.substrate_miller, c.film_miller), top=max_pairs)
