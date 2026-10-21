"""Success vs query budget in all three environments, from the archived per-environment summaries.

    python scripts/plot_environment_curves.py --out figures/environment_success_vs_budget.png

Reads data/experiments/environment_v1/{lpscl,lic,llzo}/summary.json (written by
analyse_discovery_experiment.py). P(acceptable found by query k), n = 30 per arm, 95% Wilson
error bars, exact random curve (black dashed) and the post-hoc fluoride-first rule (grey dotted).
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from scripts.analyse_discovery_experiment import ARM_COLORS

ENVS = [("lpscl", "Li$_6$PS$_5$Cl (sulfide)"), ("lic", "Li$_3$InCl$_6$ (chloride)"), ("llzo", "LLZO (oxide)")]
ARMS = ["iterative", "random", "shuffled", "sequential", "upfront"]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--archive", type=Path, default=ROOT / "data/experiments/environment_v1")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=True)
    for ax, (env, title) in zip(axes, ENVS):
        curves = json.loads((args.archive / env / "summary.json").read_text())["curves"]["acceptable"]
        k = range(1, len(curves["iterative"][0]) + 1)
        for arm in ARMS:
            p, err, n, _ = curves[arm]
            ax.errorbar(k, p, yerr=err, marker="o", ms=4, lw=2, capsize=2, color=ARM_COLORS[arm], label=f"{arm} (n={n})")
            ax.annotate(f"{p[-1]:.0%}", (k[-1], p[-1]), xytext=(6, 0), textcoords="offset points",
                        va="center", fontsize=8, color="#52514e")
        ax.plot(k, curves["random (exact)"][0], color="k", ls="--", label="random (exact)")
        ax.plot(k, curves["fluorides first (post-hoc)"][0], color="grey", ls=":", label="fluorides first (post-hoc)")
        ax.set(title=f"{title}   {curves['random (exact)'][2]} acceptable", xlabel="queries (budget)",
               xticks=range(2, len(k) + 1, 2), xlim=(0.5, len(k) + 1.2), ylim=(0, 1.05))
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.grid(axis="y", color="#e4e3df", lw=0.6)
    axes[0].set_ylabel("P(acceptable coating found)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=7, fontsize=9, frameon=False)
    fig.suptitle("Frozen environment study: 30 runs per arm, budget 10; error bars 95% Wilson", y=0.995, fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(args.out, dpi=200)
    print(f"Saved {args.out}")


if __name__ == "__main__":
    main()
