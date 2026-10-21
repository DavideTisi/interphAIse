"""Run budgeted coating search. See DISCOVERY_REPORT.md for scope and objective."""
import argparse
import json
import sys
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
from interphaise.discovery import (LLM_STRATEGIES, STRATEGIES, CoatingEvaluator, SyntheticEvaluator,
                                   run_discovery, synthetic_pool)
from interphaise.llm import make_llm
from interphaise.orchestrator import OrchestratorSettings
from interphaise.policies import RuleSettings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strategy", choices=sorted(STRATEGIES), default="iterative")
    parser.add_argument("--synthetic", action="store_true",
                        help="Fake 50-candidate pool and evaluator for developing arms (no MP, not chemistry)")
    parser.add_argument("--budget", type=int, default=3)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--full", action="store_true", help="Use fixed-policy MLIP interfaces and require adhesion")
    parser.add_argument("--model", choices=[config.LLM_MODEL], default=config.LLM_MODEL,
                        help="Locked to the project-approved Haiku 5.5 model")
    parser.add_argument("--mlip", default=config.MLIP_CATHODE)
    parser.add_argument("--out", type=Path, default=Path("runs"))
    args = parser.parse_args()
    if args.synthetic and args.full:
        parser.error("--synthetic and --full are exclusive")
    cfg = config.COATING_SCREEN
    if args.synthetic:
        cfg = replace(cfg, coatings=synthetic_pool(), include_uncoated=False)
    if not 1 <= args.budget <= len(cfg.coatings):
        parser.error("budget must be between 1 and the number of configured coatings")
    root = args.out / (datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S") + "_discovery_" + uuid4().hex[:8])
    root.mkdir(parents=True)
    calc = None
    if args.full:
        from interphaise.tools.mlip import load_mlip
        calc = load_mlip(args.mlip)
    settings = OrchestratorSettings()
    if args.synthetic:
        evaluator = SyntheticEvaluator(cfg.coatings, seed=args.seed)
    else:
        evaluator = CoatingEvaluator(cfg, calc=calc, settings=settings, run_root=str(root / "evaluations"))
    llm = make_llm(args.model) if args.strategy in LLM_STRATEGIES else None
    state = run_discovery(cfg, evaluator, strategy=args.strategy, budget=args.budget,
                          seed=args.seed, llm=llm, require_adhesion=args.full, output=root / "discovery.json",
                          metadata={"mode": "synthetic" if args.synthetic else "full" if args.full else "thermodynamic",
                                    "model": args.model if llm else None, "mlip": args.mlip if args.full else None,
                                    "rules": asdict(RuleSettings()), "settings": asdict(settings)})
    print(json.dumps(state["trace"][-1], indent=2))
    print(f"Saved {root / 'discovery.json'}")


if __name__ == "__main__":
    main()
