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
import subprocess
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    parser.add_argument("--start-seed", type=int, default=0)
    parser.add_argument("--workers", type=int, default=1, help="Independent runs in flight; each has its own client")
    parser.add_argument("--budget", type=int, default=10)
    parser.add_argument("--pool", type=Path, default=ROOT / "data/pools/mp_candidates_v2.json")
    parser.add_argument("--benchmark", type=Path, default=ROOT / "data/benchmarks/coating_v3.json")
    parser.add_argument("--synthetic", action="store_true", help="Fake pool and benchmark (development only)")
    parser.add_argument("--allow-draft", action="store_true",
                        help="Accept an unfrozen benchmark (offline checks/smoke only; recorded in experiment.json)")
    parser.add_argument("--temperature", type=float, default=None)
    parser.add_argument("--max-tokens", type=int, default=4096,
                        help="Output cap per call; a 10-candidate upfront shortlist needs ~2000 tokens")
    parser.add_argument("--model", choices=[config.LLM_MODEL], default=config.LLM_MODEL)
    parser.add_argument("--out", type=Path, default=ROOT / "runs")
    args = parser.parse_args()
    if args.repeats < 1 or not 1 <= args.workers <= 4 or len(set(args.arms)) != len(args.arms):
        parser.error('Require positive repeats, 1–4 workers and distinct arms')

    root = args.out / (datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f") + "_experiment")
    root.mkdir(parents=True)
    if args.synthetic:
        args.pool, args.benchmark = write_synthetic_benchmark(root)
    new_queries = lambda: BenchmarkQueries(args.pool, args.benchmark, budget=args.budget, allow_draft=args.synthetic or args.allow_draft)
    task = new_queries().task()  # validates hashes and budget before any paid call
    uses_llm = bool(set(args.arms) & LLM_STRATEGIES)
    if uses_llm:
        make_llm(args.model, temperature=args.temperature, max_tokens=args.max_tokens)  # validate configuration
    def portable(path):
        path = path.resolve()
        return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
    benchmark_status = json.loads(Path(args.benchmark).read_text())["status"]
    experiment = dict(arms=args.arms, repeats=args.repeats, budget=args.budget, synthetic=args.synthetic,
                      allow_draft=args.allow_draft, benchmark_status=benchmark_status,
                      start_seed=args.start_seed, workers=args.workers,
                      pool=portable(args.pool), benchmark=portable(args.benchmark),
                      hashes={k: task[k] for k in ("objective_sha256", "pool_sha256", "benchmark_sha256")},
                      prompt_version=PROMPT_VERSION, model=args.model if uses_llm else None, temperature=args.temperature,
                      max_tokens=args.max_tokens,
                      source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                      workflow_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                       for p in [Path(__file__).resolve(), ROOT/'interphaise/discovery.py',
                                                 ROOT/'interphaise/llm.py', ROOT/'interphaise/benchmark.py']})
    (root / "experiment.json").write_text(json.dumps(experiment, indent=2))

    print(f"Experiment {root}", flush=True)
    def run_one(r, arm):
        llm = make_llm(args.model, temperature=args.temperature, max_tokens=args.max_tokens) if arm in LLM_STRATEGIES else None
        try:
            state = run_discovery(new_queries(), strategy=arm, seed=r, llm=llm,
                                  output=root / f"{arm}_r{r:02d}.json",
                                  metadata={"repeat": r, "model": experiment["model"], "temperature": args.temperature})
            last = state['trace'][-1]
            return f"r{r:02d} {arm:<10} best={last['best_candidate_id']} acceptable={last['any_acceptable']}"
        except Exception as exc:
            return f"r{r:02d} {arm:<10} FAILED {type(exc).__name__}: {exc}"
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(run_one, r, arm)
                   for r in range(args.start_seed, args.start_seed + args.repeats) for arm in args.arms]
        for future in as_completed(futures):
            print(future.result(), flush=True)
    print(f"Saved {root}", flush=True)


if __name__ == "__main__":
    main()
