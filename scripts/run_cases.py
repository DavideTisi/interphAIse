"""Run the orchestrator on the cases in config.py.

    python scripts/run_cases.py                 # all cases, LLM + MLIP
    python scripts/run_cases.py --dry-run       # stop after MATCH+VALIDATE (no MLIP)
    python scripts/run_cases.py --case 1        # one case by index
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402
from interphaise.policies import make_policy  # noqa: E402
from interphaise.log import _default  # noqa: E402
from interphaise.orchestrator import Orchestrator, OrchestratorSettings  # noqa: E402
from interphaise.tools.mlip import load_mlip  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true", help="no MLIP: reactivity, LLM decisions, matching only")
    ap.add_argument("--no-relax", action="store_true", help="single points only (fast debugging)")
    ap.add_argument("--policy", choices=["llm", "rules", "human"], default="llm",
                    help="who makes the expert decisions: the LLM, deterministic rules, or a person")
    args = ap.parse_args()

    policy = make_policy(args.policy, config.LLM_MODEL, n_runs=config.N_RUNS)
    cases = config.CASES if args.case is None else [config.CASES[args.case]]
    for ctx in cases:
        calc = None
        if not args.dry_run:
            calc = load_mlip(config.MLIP_CATHODE if ctx.role == "cathode" else config.MLIP_ANODE)
        settings = OrchestratorSettings(n_runs=config.N_RUNS, max_retries=config.MAX_RETRIES,
                                        relax=not args.no_relax)
        summary = Orchestrator(ctx, policy, calc=calc, settings=settings).run()
        print(json.dumps(summary, indent=1, default=_default))


if __name__ == "__main__":
    main()
