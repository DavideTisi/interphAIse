"""Run budgeted coating search. See DISCOVERY_REPORT.md for scope and objective."""
import argparse
import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
from interphaise.discovery import CoatingEvaluator, run_discovery
from interphaise.llm import make_llm
from interphaise.orchestrator import OrchestratorSettings
from interphaise.policies import RuleSettings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strategy", choices=["iterative", "upfront", "random", "fixed"], default="iterative")
    parser.add_argument("--budget", type=int, default=3)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--full", action="store_true", help="Use fixed-policy MLIP interfaces and require adhesion")
    parser.add_argument("--model", choices=[config.LLM_MODEL], default=config.LLM_MODEL,
                        help="Locked to the project-approved Haiku 5.5 model")
    parser.add_argument("--mlip", default=config.MLIP_CATHODE)
    parser.add_argument("--out", type=Path, default=Path("runs"))
    args = parser.parse_args()
    if not 1 <= args.budget <= len(config.COATING_SCREEN.coatings):
        parser.error("budget must be between 1 and the number of configured coatings")
    root = args.out / (datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S") + "_discovery_" + uuid4().hex[:8])
    root.mkdir(parents=True)
    calc = None
    if args.full:
        from interphaise.tools.mlip import load_mlip
        calc = load_mlip(args.mlip)
    settings = OrchestratorSettings()
    evaluator = CoatingEvaluator(config.COATING_SCREEN, calc=calc, settings=settings, run_root=str(root / "evaluations"))
    llm = make_llm(args.model) if args.strategy in {"iterative", "upfront"} else None
    state = run_discovery(config.COATING_SCREEN, evaluator, strategy=args.strategy, budget=args.budget,
                          seed=args.seed, llm=llm, require_adhesion=args.full, output=root / "discovery.json",
                          metadata={"mode": "full" if args.full else "thermodynamic",
                                    "model": args.model if llm else None, "mlip": args.mlip if args.full else None,
                                    "rules": asdict(RuleSettings()), "settings": asdict(settings)})
    print(json.dumps(state["trace"][-1], indent=2))
    print(f"Saved {root / 'discovery.json'}")


if __name__ == "__main__":
    main()
