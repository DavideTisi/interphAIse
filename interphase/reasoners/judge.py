"""Decision 4: is the relaxed interface a physically acceptable model?"""

from __future__ import annotations

import json

from ..context import EnergeticsResult, JudgeVerdict
from ..llm import LLM
from .consensus import majority, sample
from .prompts import JUDGE_SYSTEM, JUDGE_USER

_VERDICTS = {"accept", "accept_with_caveat", "reject"}
_ACTIONS = {"none", "thicker_slabs", "next_termination", "different_facets", "larger_cell"}


def parse(raw: dict) -> JudgeVerdict:
    v = str(raw.get("verdict", "")).strip().lower()
    a = str(raw.get("action", "none")).strip().lower() or "none"
    if v not in _VERDICTS:
        raise ValueError(f"bad verdict {v!r}")
    if a not in _ACTIONS:
        raise ValueError(f"bad action {a!r}")
    if v != "reject":
        a = "none"
    elif a == "none":
        raise ValueError("reject needs an action")
    return JudgeVerdict(verdict=v, action=a, rationale=str(raw.get("rationale", "")))  # type: ignore[arg-type]


def judge(
    res: EnergeticsResult,
    descriptors: dict,
    warnings: list[str],
    llm: LLM,
    n_runs: int = 3,
) -> tuple[JudgeVerdict, float]:
    c = res.candidate
    user = JUDGE_USER.format(
        pair=" | ".join(c.pair),
        substrate_miller=c.substrate_miller,
        film_miller=c.film_miller,
        termination=c.termination,
        n_atoms=c.n_atoms,
        area=c.area,
        strain=c.von_mises_strain,
        w_adh=res.w_adh,
        warnings="; ".join(warnings) or "none",
        descriptors=json.dumps(descriptors, indent=1),
    )
    samples = sample(lambda: parse(llm(JUDGE_SYSTEM, user)), n_runs)
    return majority(samples, key=lambda v: (v.verdict, v.action))
