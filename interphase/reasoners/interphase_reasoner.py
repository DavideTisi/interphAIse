"""Decisions 2+3: does an interphase form, and in what order are its layers?

This replaces the step where a modeller reads the reactivity analysis and the
experimental literature and decides what structure to build. The hard check
afterwards (tools.reactivity.check_stack) is deterministic: a proposed stack
whose neighbours react with each other is sent back with the reason.
"""

from __future__ import annotations

from pymatgen.core import Composition

from ..context import InterfaceContext, InterfaceTypeDecision, ReactivityReport
from ..llm import LLM
from .consensus import majority, sample
from .prompts import INTERPHASE_SYSTEM, INTERPHASE_USER


def _norm(f: str) -> str:
    return Composition(f).reduced_formula


def _render(ctx: InterfaceContext, rep: ReactivityReport, feedback: str) -> str:
    chans = "\n".join(
        f"  x={c.mixing_ratio:.2f}  {c.reaction_energy:+.3f}  {', '.join(c.products)}" for c in rep.channels
    )
    best = rep.most_favourable
    return INTERPHASE_USER.format(
        electrode=ctx.electrode,
        role=ctx.role,
        voltage=ctx.voltage,
        electrolyte=ctx.electrolyte,
        temperature=ctx.temperature,
        note=rep.note,
        emin=rep.min_reaction_energy,
        xmin=best.mixing_ratio if best else 0.0,
        equation=best.equation if best else "none",
        channels=chans or "  (none)",
        feedback=f"\nFeedback on your previous proposal: {feedback}\n" if feedback else "",
    )


def allowed_phases(ctx: InterfaceContext, rep: ReactivityReport) -> set[str]:
    out = {_norm(ctx.electrode), _norm(ctx.electrolyte)}
    for c in rep.channels:
        out |= {_norm(p) for p in c.products}
    return out


def parse(raw: dict, ctx: InterfaceContext, rep: ReactivityReport) -> InterfaceTypeDecision:
    itype = str(raw.get("interface_type", "")).strip().lower()
    if itype not in {"sharp", "interphase"}:
        raise ValueError(f"bad interface_type {itype!r}")
    stack = [_norm(s) for s in raw.get("stack", [])]
    if itype == "sharp":
        stack = [_norm(ctx.electrode), _norm(ctx.electrolyte)]
    if len(stack) < 2 or stack[0] != _norm(ctx.electrode) or stack[-1] != _norm(ctx.electrolyte):
        raise ValueError(f"stack must start with the electrode and end with the electrolyte: {stack}")
    illegal = set(stack) - allowed_phases(ctx, rep)
    if illegal:
        raise ValueError(f"phases not in the reactivity products: {sorted(illegal)}")
    if len(stack) > 5:
        raise ValueError("at most 3 intermediate phases")
    conf = raw.get("confidence")
    return InterfaceTypeDecision(
        interface_type=itype,  # type: ignore[arg-type]
        stack=stack,
        rationale=f"{raw.get('rationale', '')} | kinetics: {raw.get('kinetic_argument', '')}",
        confidence=float(conf) if conf is not None else None,
    )


def decide_interface_type(
    ctx: InterfaceContext,
    rep: ReactivityReport,
    llm: LLM,
    n_runs: int = 3,
    feedback: str = "",
) -> tuple[InterfaceTypeDecision, float, list[InterfaceTypeDecision]]:
    """Consensus decision. Returns (decision, agreement fraction, all samples)."""
    user = _render(ctx, rep, feedback)
    samples = sample(lambda: parse(llm(INTERPHASE_SYSTEM, user), ctx, rep), n_runs)
    best, agree = majority(samples, key=lambda d: (d.interface_type, tuple(d.stack)))
    return best, agree, samples
