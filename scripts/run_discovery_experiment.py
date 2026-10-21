"""Repeat discovery runs per arm against the frozen v3 benchmark. See EVALUATOR_HANDOFF.md.

    python scripts/run_discovery_experiment.py --arms random --repeats 100        # no LLM
    python scripts/run_discovery_experiment.py --repeats 10 --temperature 1.0     # main run
    python scripts/run_discovery_experiment.py --synthetic --repeats 3            # fake pool, dev only
    python scripts/analyse_discovery_experiment.py runs/<stamp>_experiment --plot curve.png

Repeat r shows every arm the same candidate order (seed r). Each run gets a fresh
BenchmarkQueries, so failed, repeated and invalid queries cost budget as defined there.
Failed runs are kept (their JSON has status "failed").
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import config
from interphaise.benchmark import BenchmarkQueries
from interphaise.discovery import LLM_STRATEGIES, PROMPT_VERSION, STRATEGIES, run_discovery, write_synthetic_benchmark
from interphaise.llm import make_llm


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--arms", nargs="+", choices=sorted(STRATEGIES),
                        default=["random", "upfront", "sequential", "iterative"])
    parser.add_argument("--repeats", type=int, default=10)
    parser.add_argument("--budget", type=int, default=10)
    parser.add_argument("--pool", type=Path, default=ROOT / "data/pools/mp_candidates_v2.json")
    parser.add_argument("--benchmark", type=Path, default=ROOT / "data/benchmarks/coating_v3.json")
    parser.add_argument("--synthetic", action="store_true", help="Fake pool and benchmark (development only)")
    parser.add_argument("--temperature", type=float, default=None)
    parser.add_argument("--model", choices=[config.LLM_MODEL], default=config.LLM_MODEL)
    parser.add_argument("--out", type=Path, default=ROOT / "runs")
    args = parser.parse_args()

    root = args.out / (datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S") + "_experiment")
    root.mkdir(parents=True)
    if args.synthetic:
        args.pool, args.benchmark = write_synthetic_benchmark(root)
    new_queries = lambda: BenchmarkQueries(args.pool, args.benchmark, budget=args.budget, allow_draft=args.synthetic)
    task = new_queries().task()  # validates hashes and budget before any paid call
    llm = make_llm(args.model, temperature=args.temperature) if set(args.arms) & LLM_STRATEGIES else None
    experiment = dict(arms=args.arms, repeats=args.repeats, budget=args.budget, synthetic=args.synthetic,
                      pool=str(args.pool), benchmark=str(args.benchmark),
                      hashes={k: task[k] for k in ("objective_sha256", "pool_sha256", "benchmark_sha256")},
                      prompt_version=PROMPT_VERSION, model=args.model if llm else None, temperature=args.temperature)
    (root / "experiment.json").write_text(json.dumps(experiment, indent=2))

    for r in range(args.repeats):
        for arm in args.arms:
            try:
                state = run_discovery(new_queries(), strategy=arm, seed=r,
                                      llm=llm if arm in LLM_STRATEGIES else None, output=root / f"{arm}_r{r:02d}.json",
                                      metadata={"repeat": r, "model": experiment["model"], "temperature": args.temperature})
                last = state["trace"][-1]
                print(f"r{r:02d} {arm:<10} best={last['best_candidate_id']} acceptable={last['any_acceptable']}", flush=True)
            except Exception as exc:
                print(f"r{r:02d} {arm:<10} FAILED {type(exc).__name__}: {exc}", flush=True)
    print(f"Saved {root}")


if __name__ == "__main__":
    main()
