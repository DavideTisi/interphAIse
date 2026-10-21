"""Success probability vs evaluations per arm, with exact random baselines.

    python scripts/analyse_discovery_experiment.py runs/<stamp>_experiment --plot curve.png

Two targets (EVALUATOR_HANDOFF.md / SYNC_ADEM.md section 6):
  acceptable : some queried candidate has acceptable == True
  best bin   : some queried candidate reaches the best ranking_key in the pool (ties count)
Successes M are counted over the whole pool, failures included in N. Failed or short
runs are kept and count as no success at steps they did not reach. Error bars: binomial SE.
"""
import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from interphaise.discovery import random_success_curve
from interphaise.discovery_evaluator import ranking_key

TARGETS = {"acceptable": lambda r, best: bool(r.get("acceptable")),
           "best bin": lambda r, best: ranking_key(r) == best}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("experiment", type=Path)
    parser.add_argument("--plot", type=Path, help="Write the success-curve figure here")
    args = parser.parse_args()

    exp = json.loads((args.experiment / "experiment.json").read_text())
    table = json.loads(Path(exp["benchmark"]).read_text())["results"]
    best = max(ranking_key(r) for r in table)
    budget = exp["budget"]
    steps = range(1, budget + 1)
    runs = {arm: [json.loads(p.read_text()) for p in sorted(args.experiment.glob(f"{arm}_r*.json"))]
            for arm in exp["arms"]}

    curves = {}
    for target, hit in TARGETS.items():
        rows = {}
        for arm, arm_runs in runs.items():
            if not arm_runs:
                continue
            first = [next((i + 1 for i, h in enumerate(r["history"]) if hit(h["result"], best)), None) for r in arm_runs]
            p = [sum(f is not None and f <= k for f in first) / len(arm_runs) for k in steps]
            rows[arm] = (p, [math.sqrt(x * (1 - x) / len(arm_runs)) for x in p], len(arm_runs),
                         sum(r["status"] != "complete" for r in arm_runs))
        m = sum(hit(r, best) for r in table)
        rows["random (exact)"] = (random_success_curve(len(table), m, budget), None, f"M={m}/N={len(table)}", 0)
        curves[target] = rows

        print(f"\n{target}: P(success) at k = 1..{budget}")
        print(f"{'arm':<16}{'runs':>12}{'failed':>8}  curve")
        for arm, (p, _, n, failed) in rows.items():
            print(f"{arm:<16}{str(n):>12}{failed:>8}  " + " ".join(f"{x:.2f}" for x in p))

    if args.plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
        for ax, (target, rows) in zip(axes, curves.items()):
            for arm, (p, se, n, _) in rows.items():
                if se is None:
                    ax.plot(steps, p, "k--", label=f"{arm} {n}")
                else:
                    ax.errorbar(steps, p, yerr=se, marker="o", capsize=3, label=f"{arm} (n={n})")
            ax.set(xlabel="evaluations", title=f"P({target} found)", ylim=(0, 1.05))
            ax.legend(fontsize=8)
        axes[0].set_ylabel("probability")
        fig.suptitle(f"{'synthetic' if exp['synthetic'] else 'frozen v3'} benchmark, budget {budget}")
        fig.tight_layout()
        fig.savefig(args.plot, dpi=150)
        print(f"Saved {args.plot}")


if __name__ == "__main__":
    main()
