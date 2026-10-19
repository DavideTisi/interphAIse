"""Coating screen: which buffer layer stabilises an electrode | electrolyte contact?

For every candidate coating C the orchestrator is run on two contacts,
electrode | C and C | electrolyte, plus the uncoated baseline
electrode | electrolyte. Each contact goes through the full pipeline
(reactivity gate → LLM interface-type decision → stack check → facets →
matching → energetics → judge), then ranker.py orders the coatings.

Potential convention: both contacts of a cathode coating are evaluated at the
cathode potential (Li open at mu_Li(V)). The electrolyte side of a thin,
electronically insulating coating sees close to the cathode potential, so
this is the conservative choice used in the computational screening
literature for cathode coatings. Record it when reporting.
"""

from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass, field
from pathlib import Path

from .context import InterfaceContext
from .llm import LLM
from .log import RunLog, _default
from .orchestrator import Orchestrator, OrchestratorSettings
from .ranker import CoatingRow, ContactResult, rank, to_dict, to_markdown
from .tools.materials import get_bulk, get_entries


@dataclass
class ScreenConfig:
    electrode: str
    electrolyte: str
    coatings: list[str]
    voltage: float = 4.0
    role: str = "cathode"
    include_uncoated: bool = True
    max_atoms: int = 600
    max_strain: float = 0.04
    electrode_mp_id: str | None = None
    electrolyte_mp_id: str | None = None
    coating_mp_ids: dict[str, str] = field(default_factory=dict)


def contacts_for(cfg: ScreenConfig, coating: str | None) -> list[InterfaceContext]:
    common = dict(role=cfg.role, voltage=cfg.voltage, max_atoms=cfg.max_atoms, max_strain=cfg.max_strain)
    if coating is None:
        return [InterfaceContext(
            electrode=cfg.electrode, electrolyte=cfg.electrolyte,
            electrode_mp_id=cfg.electrode_mp_id, electrolyte_mp_id=cfg.electrolyte_mp_id,
            setting=f"uncoated {cfg.electrode} {cfg.role} in direct contact with the {cfg.electrolyte} solid electrolyte",
            **common)]
    cid = cfg.coating_mp_ids.get(coating)
    return [
        InterfaceContext(
            electrode=cfg.electrode, electrolyte=coating,
            electrode_mp_id=cfg.electrode_mp_id, electrolyte_mp_id=cid,
            setting=(f"{coating} buffer coating on a {cfg.electrode} {cfg.role}; this is the "
                     f"{cfg.electrode} | {coating} contact (the coating plays the electrolyte role here)"),
            **common),
        InterfaceContext(
            electrode=coating, electrolyte=cfg.electrolyte,
            electrode_mp_id=cid, electrolyte_mp_id=cfg.electrolyte_mp_id,
            setting=(f"{coating} buffer coating on a {cfg.electrode} {cfg.role} at {cfg.voltage} V; this is the "
                     f"{coating} | {cfg.electrolyte} contact on the electrolyte side (the coating plays the "
                     f"electrode role here)"),
            **common),
    ]


def _contact_result(summary: dict) -> ContactResult:
    d = summary["decision"]
    pairs = summary.get("pairs", [])
    ws = [p["best"].w_adh for p in pairs if p.get("status") == "ok"]
    statuses = {p.get("status") for p in pairs}
    if not pairs:
        status = "decision_only"
    elif statuses == {"ok"}:
        status = "ok"
    elif "failed" in statuses:
        status = "failed"
    else:
        status = "dry_run"
    return ContactResult(
        pair=(d.stack[0], d.stack[-1]),
        reactive=summary["reactivity"]["reactive"],
        min_reaction_energy=summary["reactivity"]["min_reaction_energy"],
        products=summary["reactivity"].get("products", []),
        interface_type=d.interface_type,
        stack=d.stack,
        character=d.character,
        agreement=summary.get("decision_agreement"),
        w_adh=min(ws) if ws and len(ws) == len(pairs) else None,
        status=status,
        run_dir=summary.get("run_dir", ""),
    )


def run_screen(
    cfg: ScreenConfig,
    llm: LLM,
    calc=None,
    settings: OrchestratorSettings | None = None,
    bulk_fn=get_bulk,
    entries_fn=get_entries,
    run_root: str | None = None,
) -> dict:
    """Run every contact, rank, and write ranking.{md,json} to the screen's run dir."""
    settings = settings or OrchestratorSettings()
    screen_log = RunLog(f"screen_{cfg.electrode}|{cfg.electrolyte}@{cfg.voltage:g}V", run_root)
    contact_root = str(screen_log.dir / "contacts")

    candidates: list[str | None] = ([None] if cfg.include_uncoated else []) + list(cfg.coatings)
    rows: list[CoatingRow] = []
    for coating in candidates:
        row = CoatingRow(coating=coating or "none")
        for ctx in contacts_for(cfg, coating):
            try:
                summary = Orchestrator(ctx, llm, calc=calc, settings=dataclasses.replace(settings),
                                       bulk_fn=bulk_fn, entries_fn=entries_fn, run_root=contact_root).run()
                row.contacts.append(_contact_result(summary))
            except Exception as e:  # one failed contact must not kill the screen
                screen_log.record("screen", "error", f"{type(e).__name__}: {e}", contact=ctx.name)
                row.contacts = []
                break
        if row.contacts:
            rows.append(row)
            screen_log.record("screen", "compute", row, coating=row.coating)

    ranked_llm = rank([dataclasses.replace(r) for r in rows], mode="llm")
    ranked_thermo = rank([dataclasses.replace(r) for r in rows], mode="thermo")
    title = f"{cfg.electrode} | coating | {cfg.electrolyte} at {cfg.voltage:g} V"
    md = (to_markdown(ranked_llm, f"Ranking with expert (LLM) interphase calls — {title}") + "\n"
          + to_markdown(ranked_thermo, f"Ablation: thermodynamics only — {title}"))
    (screen_log.dir / "ranking.md").write_text(md)
    out = {"config": dataclasses.asdict(cfg), "ranking": to_dict(ranked_llm),
           "ranking_thermo_only": to_dict(ranked_thermo), "run_dir": str(screen_log.dir)}
    (screen_log.dir / "ranking.json").write_text(json.dumps(out, indent=1, default=_default))
    screen_log.record("summary", "compute", {"ranking": [(r.rank, r.coating, r.tier) for r in ranked_llm]})
    return {**out, "markdown": md}
