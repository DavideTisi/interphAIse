"""Coating screen + ranker (flagship: LiCoO2 | coating | Li6PS5Cl at 4 V).

    python scripts/run_screen.py --decision-only   # reactivity + LLM calls only: minutes, no MLIP
    python scripts/run_screen.py --dry-run         # + facets and lattice matching, no MLIP
    python scripts/run_screen.py                   # full: + registry scan, relaxation, W_adh, judge
    python scripts/run_screen.py --policy rules    # same pipeline, deterministic rules instead of the LLM
    python scripts/run_screen.py --policy human    # a person answers the prompts (blind baseline)
    python scripts/compare_arms.py runs/           # rankings and decisions of the arms side by side

Writes runs/<stamp>_screen_.../ranking.md and ranking.json (LLM ranking and the
thermodynamics-only ablation side by side) plus one decision log per contact.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402
from interphaise.policies import make_policy  # noqa: E402
from interphaise.orchestrator import OrchestratorSettings  # noqa: E402
from interphaise.screen import run_screen  # noqa: E402
from interphaise.tools.mlip import load_mlip  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--decision-only", action="store_true", help="stop after the interface-type decision")
    mode.add_argument("--dry-run", action="store_true", help="match structures but no MLIP")
    ap.add_argument("--no-relax", action="store_true")
    ap.add_argument("--policy", choices=["llm", "rules", "human"], default="llm",
                    help="who makes the expert decisions: the LLM, deterministic rules, or a person")
    args = ap.parse_args()

    cfg = config.COATING_SCREEN
    calc = None
    if not (args.decision_only or args.dry_run):
        calc = load_mlip(config.MLIP_CATHODE if cfg.role == "cathode" else config.MLIP_ANODE)
    settings = OrchestratorSettings(n_runs=config.N_RUNS, max_retries=config.MAX_RETRIES,
                                    relax=not args.no_relax, build_structures=not args.decision_only)
    policy = make_policy(args.policy, config.LLM_MODEL, n_runs=config.N_RUNS)
    out = run_screen(cfg, policy, calc=calc, settings=settings)
    print(out["markdown"])
    print(f"written to {out['run_dir']}")


if __name__ == "__main__":
    main()
