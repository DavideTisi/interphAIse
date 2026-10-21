"""Success probability vs evaluations per arm, with the exact random baseline.

    python scripts/analyse_discovery_experiment.py runs/<stamp>_experiment --accept -0.05

A candidate is acceptable when its evaluation is ok and worst_reaction_energy >= --accept
(eV/atom). The threshold is provisional until the objective is frozen. Failed or short runs
are kept and count as no success at the steps they did not reach. Error bars: binomial SE.
"""
import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from interphaise.discovery import random_success_curve


def acceptable(result, threshold):
    energy = result.get("worst_reaction_energy")
    return result.get("status") == "ok" and energy is not None and energy >= threshold


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("experiment", type=Path)
    parser.add_argument("--accept", type=float, required=True, help="Min worst-contact reaction energy, eV/atom")
    parser.add_argument("--plot", type=Path, help="Write the success-curve figure here")
    args = parser.parse_args()

    exp = json.loads((args.experiment / "experiment.json").read_text())
    budget, steps = exp["budget"], range(1, exp["budget"] + 1)
    curves = {}
    for arm in exp["arms"]:
        runs = [json.loads(p.read_text()) for p in sorted(args.experiment.glob(f"{arm}_r*.json"))]
        if not runs:
            continue
        first = [next((i + 1 for i, h in enumerate(r["history"]) if acceptable(h["result"], args.accept)), None)
                 for r in runs]
        p = [sum(f is not None and f <= k for f in first) / len(runs) for k in steps]
        se = [math.sqrt(x * (1 - x) / len(runs)) for x in p]
        curves[arm] = (p, se, len(runs), sum(r["status"] != "complete" for r in runs))
    if exp.get("table"):
        n_ok = sum(acceptable(e, args.accept) for e in exp["table"].values())
        curves["random (exact)"] = (random_success_curve(len(exp["table"]), n_ok, budget), None,
                                    f"{n_ok}/{len(exp['table'])} acceptable", 0)

    print(f"{'arm':<16}{'runs':>8}{'failed':>8}  P(success) at k = 1..{budget}")
    for arm, (p, _, n, failed) in curves.items():
        print(f"{arm:<16}{str(n):>8}{failed:>8}  " + " ".join(f"{x:.2f}" for x in p))

    if args.plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(6, 4))
        for arm, (p, se, n, _) in curves.items():
            if se is None:
                ax.plot(steps, p, "k--", label=arm)
            else:
                ax.errorbar(steps, p, yerr=se, marker="o", capsize=3, label=f"{arm} (n={n})")
        ax.set(xlabel="evaluations", ylabel="P(acceptable candidate found)", ylim=(0, 1.05),
               title=f"{exp['mode']} pool, accept >= {args.accept} eV/atom")
        ax.legend()
        fig.tight_layout()
        fig.savefig(args.plot, dpi=150)
        print(f"Saved {args.plot}")


if __name__ == "__main__":
    main()
