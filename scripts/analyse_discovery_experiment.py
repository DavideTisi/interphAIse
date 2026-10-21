"""Success probability vs evaluations per arm, with exact random baselines.

    python scripts/analyse_discovery_experiment.py runs/<stamp>_experiment --plot curve.png
    python scripts/analyse_discovery_experiment.py runs/<main> runs/<rerun> --plot curve.png

With several experiment directories, each arm is taken from the last directory that ran it
(e.g. a rerun of one arm). Hashes and budget must match.

Two targets (EVALUATOR_HANDOFF.md / SYNC_ADEM.md section 6):
  acceptable : some queried candidate has acceptable == True
  best bin   : some queried candidate reaches the best ranking_key in the pool (ties count)
Successes M are counted over the whole pool, failures included in N. Failed or short
runs are kept and count as no success at steps they did not reach. Error bars: 95% Wilson.

Third panel: median best penalty bin found so far (lower is better), band = quartiles over runs.
A run with no valid candidate yet counts as worse than every bin, never as an invented value.
The exact random median uses P(best bin <= b within k) = 1 - C(N - M_b, k)/C(N, k).
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


def wilson(p, n, z=1.96):
    """95% Wilson interval as (lower, upper) distances from p; nonzero width at p = 0 or 1."""
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return p - (centre - half), centre + half - p


def best_bin(results):
    keys = [ranking_key(r) for r in results]
    return min((-k[1] for k in keys if k[0]), default=math.inf)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("experiments", type=Path, nargs="+")
    parser.add_argument("--plot", type=Path, help="Write the success-curve figure here")
    args = parser.parse_args()

    exps = [(d, json.loads((d / "experiment.json").read_text())) for d in args.experiments]
    exp = exps[0][1]
    for d, other in exps[1:]:
        if other["hashes"] != exp["hashes"] or other["budget"] != exp["budget"]:
            raise SystemExit(f"{d}: hashes or budget differ from {args.experiments[0]}")
    table = json.loads(Path(exp["benchmark"]).read_text())["results"]
    best = max(ranking_key(r) for r in table)
    budget = exp["budget"]
    steps = range(1, budget + 1)
    source = {arm: d for d, e in exps for arm in e["arms"]}
    runs = {arm: [json.loads(p.read_text()) for p in sorted(d.glob(f"{arm}_r*.json"))] for arm, d in source.items()}
    for arm, d in source.items():
        print(f"{arm}: {d}")

    curves = {}
    for target, hit in TARGETS.items():
        rows = {}
        for arm, arm_runs in runs.items():
            if not arm_runs:
                continue
            first = [next((i + 1 for i, h in enumerate(r["history"]) if hit(h["result"], best)), None) for r in arm_runs]
            p = [sum(f is not None and f <= k for f in first) / len(arm_runs) for k in steps]
            rows[arm] = (p, list(zip(*[wilson(x, len(arm_runs)) for x in p])), len(arm_runs),
                         sum(r["status"] != "complete" for r in arm_runs))
        m = sum(hit(r, best) for r in table)
        rows["random (exact)"] = (random_success_curve(len(table), m, budget), None, f"M={m}/N={len(table)}", 0)
        curves[target] = rows

        print(f"\n{target}: P(success) at k = 1..{budget}")
        print(f"{'arm':<16}{'runs':>12}{'failed':>8}  curve")
        for arm, (p, _, n, failed) in rows.items():
            print(f"{arm:<16}{str(n):>12}{failed:>8}  " + " ".join(f"{x:.2f}" for x in p))

    bins = {}
    for arm, arm_runs in runs.items():
        per_k = [sorted(best_bin([h["result"] for h in r["history"][:k]]) for r in arm_runs) for k in steps]
        n = len(arm_runs)
        bins[arm] = [(v[(n - 1) // 4], v[(n - 1) // 2], v[math.ceil(3 * (n - 1) / 4)]) for v in per_k]
    valid = sorted(-ranking_key(r)[1] for r in table if ranking_key(r)[0])
    exact_median = [next(b for b in valid if random_success_curve(len(table), sum(v <= b for v in valid), k)[-1] >= 0.5)
                    for k in steps]
    print(f"\nmedian best bin so far at k = 1..{budget} (inf = no valid candidate yet)")
    for arm, rows in bins.items():
        print(f"{arm:<16}" + " ".join(f"{m:>4}" for _, m, _ in rows))
    print(f"{'random (exact)':<16}" + " ".join(f"{m:>4}" for m in exact_median))

    if args.plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(1, 3, figsize=(16, 4))
        for ax, (target, rows) in zip(axes, curves.items()):
            for arm, (p, se, n, _) in rows.items():
                if se is None:
                    ax.plot(steps, p, "k--", label=f"{arm} {n}")
                else:
                    ax.errorbar(steps, p, yerr=se, marker="o", capsize=3, label=f"{arm} (n={n})")
            ax.set(xlabel="evaluations", title=f"P({target} found)", ylim=(0, 1.05))
            ax.legend(fontsize=8)
        axes[0].set_ylabel("probability")
        ax = axes[2]
        top = max([x for rows in bins.values() for row in rows for x in row if x != math.inf] + exact_median) + 3
        for arm, rows in bins.items():
            lo, med, hi = ([min(x, top) for x in col] for col in zip(*rows))
            line, = ax.plot(steps, med, marker="o", label=arm)
            ax.fill_between(steps, lo, hi, color=line.get_color(), alpha=0.15)
        ax.plot(steps, exact_median, "k--", label="random (exact median)")
        ax.axhline(top, color="grey", lw=0.5)
        ax.text(1, top, " no valid candidate yet", va="bottom", fontsize=8, color="grey")
        ax.set(xlabel="evaluations", ylabel="best penalty bin (lower is better)",
               title="median best bin so far", ylim=(0, top + 2))
        ax.legend(fontsize=8)
        fig.suptitle(f"{'synthetic' if exp['synthetic'] else 'frozen v3'} benchmark, budget {budget}; error bars: 95% Wilson")
        fig.tight_layout()
        fig.savefig(args.plot, dpi=150)
        print(f"Saved {args.plot}")


if __name__ == "__main__":
    main()
