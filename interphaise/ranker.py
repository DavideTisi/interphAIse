"""Rank coatings (the battery analogue of HELLMM's overpotential leaderboard).

Each coating has one or two contacts (cathode | coating, coating | electrolyte;
the uncoated baseline has one: cathode | electrolyte). Ranking is
lexicographic, worst contact decides:

  1. tier by the worst interphase character
       tier 1  every contact sharp (nothing forms)
       tier 2  worst contact grows a passivating layer
       tier 3  any contact grows a non-passivating (electronically conducting) layer
  2. worst thermodynamic driving force (min reaction energy, closer to 0 is better)
  3. weakest work of adhesion (higher is better; missing = ranked last)
  4. consensus agreement of the decisions (higher is better)

mode="decisions" tiers come from the policy's passivating/growing calls —
                the LLM, a person, or the deterministic rules (policies.py),
                whichever arm produced the decisions. ("llm" is an alias.)
mode="thermo"    tiers from thermodynamics alone: reactive → treated as a
                 growing layer. Crude ablation; the rules arm is the fair
                 deterministic baseline.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

CHARACTER_RANK = {"none": 0, "passivating": 1, "growing": 2}
TIER_LABEL = {1: "stable on both sides", 2: "passivating interphase", 3: "growing interphase"}


@dataclass
class ContactResult:
    pair: tuple[str, str]
    reactive: bool
    min_reaction_energy: float          # eV/atom
    products: list[str]
    interface_type: str                 # sharp | interphase
    stack: list[str]
    character: str                      # none | passivating | growing
    agreement: float | None = None
    w_adh: float | None = None          # J/m^2, weakest pairwise interface in the stack
    status: str = ""                    # ok | dry_run | decision_only | failed
    run_dir: str = ""


@dataclass
class CoatingRow:
    coating: str                        # "none" for the uncoated baseline
    contacts: list[ContactResult] = field(default_factory=list)
    tier: int = 0
    rank: int = 0
    worst_reaction_energy: float = 0.0
    weakest_w_adh: float | None = None
    mean_agreement: float | None = None
    reason: str = ""


def _character(c: ContactResult, mode: str) -> str:
    if mode not in ("decisions", "llm", "thermo"):
        raise ValueError(f"unknown ranking mode {mode!r}")
    if mode == "thermo":
        return "growing" if c.reactive else "none"
    return c.character


def score(row: CoatingRow, mode: str = "decisions") -> CoatingRow:
    worst = max(row.contacts, key=lambda c: CHARACTER_RANK[_character(c, mode)])
    row.tier = 1 + CHARACTER_RANK[_character(worst, mode)]
    weakest_rxn = min(row.contacts, key=lambda c: c.min_reaction_energy)
    row.worst_reaction_energy = weakest_rxn.min_reaction_energy
    ws = [c.w_adh for c in row.contacts if c.w_adh is not None]
    row.weakest_w_adh = min(ws) if len(ws) == len(row.contacts) else None
    ags = [c.agreement for c in row.contacts if c.agreement is not None]
    row.mean_agreement = sum(ags) / len(ags) if ags else None
    if row.tier == 1:
        row.reason = "all contacts stay sharp"
    else:
        row.reason = (f"{' | '.join(worst.pair)}: {_character(worst, mode)} layer "
                      f"({' | '.join(worst.stack[1:-1]) or 'reaction products'})")
    return row


def rank(rows: list[CoatingRow], mode: str = "decisions") -> list[CoatingRow]:
    for r in rows:
        score(r, mode)
    rows = sorted(
        rows,
        key=lambda r: (
            r.tier,
            -r.worst_reaction_energy,                       # closer to zero first
            -(r.weakest_w_adh if r.weakest_w_adh is not None else float("-inf")),
            -(r.mean_agreement or 0.0),
        ),
    )
    for i, r in enumerate(rows, 1):
        r.rank = i
    return rows


def _fmt(x, f="{:.3f}"):
    return "–" if x is None else f.format(x)


def to_markdown(rows: list[CoatingRow], title: str = "") -> str:
    lines = [f"## {title}", ""] if title else []
    lines += [
        "| Rank | Coating | Tier | Contacts (type, character) | Worst ΔE_rxn (eV/atom) | Weakest W_adh (J/m²) | Agreement | Why |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        contacts = "; ".join(f"{' | '.join(c.pair)}: {c.interface_type}, {c.character}" for c in r.contacts)
        lines.append(
            f"| {r.rank} | {r.coating} | {r.tier} ({TIER_LABEL[r.tier]}) | {contacts} | "
            f"{r.worst_reaction_energy:+.3f} | {_fmt(r.weakest_w_adh, '{:.2f}')} | "
            f"{_fmt(r.mean_agreement, '{:.2f}')} | {r.reason} |"
        )
    return "\n".join(lines) + "\n"


def to_dict(rows: list[CoatingRow]) -> list[dict]:
    return [asdict(r) for r in rows]
