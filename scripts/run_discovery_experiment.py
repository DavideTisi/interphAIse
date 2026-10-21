"""Repeat discovery runs per arm with paired pool orders. See DISCOVERY_IMPLEMENTATION_PLAN.md §6–7.

    python scripts/run_discovery_experiment.py --synthetic --repeats 3 --budget 10
    python scripts/analyse_discovery_experiment.py runs/<stamp>_experiment --accept -0.05

Repeat r shows every arm the same pool order, so list-order bias is paired across arms.
Failed runs are kept (their discovery.json has status "failed").
"""
import argparse
import json
import random
import sys
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
from interphaise.discovery import (LLM_STRATEGIES, STRATEGIES, CoatingEvaluator, SyntheticEvaluator,
                                   run_discovery, synthetic_pool)
from interphaise.llm import make_llm


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--arms", nargs="+", choices=sorted(STRATEGIES),
                        default=["random", "upfront", "sequential", "iterative"])
    parser.add_argument("--repeats", type=int, default=10)
    parser.add_argument("--budget", type=int, default=10)
    parser.add_argument("--synthetic", action="store_true", help="Fake pool and evaluator (no MP, not chemistry)")
    parser.add_argument("--pool-seed", type=int, default=0, help="Synthetic benchmark seed (fixed across repeats)")
    parser.add_argument("--temperature", type=float, default=None)
    parser.add_argument("--model", choices=[config.LLM_MODEL], default=config.LLM_MODEL)
    parser.add_argument("--out", type=Path, default=Path("runs"))
    args = parser.parse_args()

    cfg = config.COATING_SCREEN
    if args.synthetic:
        cfg = replace(cfg, coatings=synthetic_pool(), include_uncoated=False)
        base = SyntheticEvaluator(cfg.coatings, seed=args.pool_seed)
    else:
        base = CoatingEvaluator(cfg)
    if not 1 <= args.budget <= len(cfg.coatings):
        parser.error("budget must be between 1 and the pool size")

    # Outcomes are cached across runs, but every query still costs budget inside run_discovery.
    cache = {}
    def evaluator(coating):
        if coating not in cache:
            cache[coating] = base(coating)
        return cache[coating]

    llm = make_llm(args.model, temperature=args.temperature) if set(args.arms) & LLM_STRATEGIES else None
    root = args.out / (datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S") + "_experiment")
    root.mkdir(parents=True)
    experiment = dict(arms=args.arms, repeats=args.repeats, budget=args.budget, pool=cfg.coatings,
                      mode="synthetic" if args.synthetic else "thermodynamic", pool_seed=args.pool_seed,
                      model=args.model if llm else None, temperature=args.temperature,
                      table={c: asdict(e) for c, e in base.table.items()} if args.synthetic else None)
    (root / "experiment.json").write_text(json.dumps(experiment, indent=2))

    for r in range(args.repeats):
        order = cfg.coatings.copy()
        random.Random(1000 + r).shuffle(order)
        for arm in args.arms:
            out = root / f"{arm}_r{r:02d}.json"
            try:
                state = run_discovery(replace(cfg, coatings=order), evaluator, strategy=arm, budget=args.budget,
                                      seed=r, llm=llm if arm in LLM_STRATEGIES else None, output=out,
                                      metadata={"repeat": r, "model": experiment["model"],
                                                "temperature": args.temperature})
                best = state["trace"][-1]["best"]
                print(f"r{r:02d} {arm:<10} best={best['coating'] if best else None}", flush=True)
            except Exception as exc:
                print(f"r{r:02d} {arm:<10} FAILED {type(exc).__name__}: {exc}", flush=True)
    print(f"Saved {root}")


if __name__ == "__main__":
    main()
