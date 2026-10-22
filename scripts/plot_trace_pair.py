"""Side-by-side query traces of two discovery runs (e.g. a success and a failure) for slides.

    python scripts/plot_trace_pair.py data/experiments/integrated_v3_20261021_s100/iterative_r111.json \
        data/experiments/integrated_v3_20261021_s100/iterative_r114.json --out trace_pair.png

Penalty (eV per non-Li atom, log scale) per query, coloured by chemistry class, with the frozen
0.050 acceptance limit and the best-so-far line. Failed queries sit in a band above the plot.
"""
import argparse
import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from pymatgen.core import Composition

CLASSES = {"fluoride": "#2a78d6", "chloride / bromide": "#eb6834", "oxide / oxyanion": "#1baf7a"}
INK, MUTED = "#0b0b0b", "#52514e"
LIMIT = 0.050


def chem_class(formula):
    el = Composition(formula).get_el_amt_dict()
    return "fluoride" if "F" in el else "chloride / bromide" if {"Cl", "Br"} & set(el) else "oxide / oxyanion"


def pretty(formula):
    return re.sub(r"(\d+)", r"$_{\1}$", formula)


def draw(ax, run, title, top):
    hist = [h["result"] for h in run["history"]]
    fail_y = top * 1.25
    best, best_line = None, []
    for k, r in enumerate(hist, start=1):
        if r.get("status") == "ok" and r.get("insulating"):
            best = r["penalty"] if best is None else min(best, r["penalty"])
            ax.scatter(k, r["penalty"], s=60, color=CLASSES[chem_class(r["formula"])], zorder=3,
                       edgecolor="white", linewidth=1.5)
            label = pretty(r["formula"])
        else:
            ax.scatter(k, fail_y, s=60, marker="x", color=MUTED, zorder=3)
            label = pretty(r.get("formula") or "invalid ID") + " (failed)"
        valid = r.get("status") == "ok" and r.get("insulating")
        ax.annotate(label, (k, r["penalty"] if valid else fail_y), xytext=(0, 9) if valid else (0, -10),
                    textcoords="offset points", ha="left" if valid else "center", va="bottom" if valid else "top",
                    rotation=35 if valid else 0, fontsize=8, color=INK)
        best_line.append(best)
    ax.step(range(1, len(hist) + 1), best_line, where="post", color=MUTED, lw=1.2, zorder=1)
    ax.axhline(LIMIT, color=INK, lw=1, ls="--")
    ax.text(0.6, LIMIT * 0.86, "acceptance limit 0.050", fontsize=8, color=MUTED, va="top")
    ax.set_yscale("log")
    ax.set(ylim=(0.02, fail_y * 2.2), xlim=(0.4, len(hist) + 1.2), xticks=range(1, len(hist) + 1),
           xlabel="query", title=title)
    ax.set_yticks([0.03, 0.05, 0.1, 0.2, 0.5])
    ax.set_yticklabels(["0.03", "0.05", "0.1", "0.2", "0.5"])
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis="y", color="#e4e3df", lw=0.6)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("runs", type=Path, nargs=2)
    parser.add_argument("--titles", nargs=2, default=None)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    runs = [json.loads(p.read_text()) for p in args.runs]
    titles = args.titles or [f"{r['strategy']} seed {r['seed']}" for r in runs]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=False)
    top = 1.8 * max(h["result"]["penalty"] for r in runs for h in r["history"]
                    if h["result"].get("status") == "ok" and h["result"].get("insulating"))
    for ax, run, title in zip(axes, runs, titles):
        draw(ax, run, title, top)
    axes[0].set_ylabel("penalty, eV per non-Li atom (log; lower is better)")
    handles = [Line2D([], [], marker="o", ls="", color=c, markersize=8, label=n) for n, c in CLASSES.items()]
    handles += [Line2D([], [], marker="x", ls="", color=MUTED, markersize=8, label="failed query"),
                Line2D([], [], color=MUTED, lw=1.2, label="best so far")]
    fig.legend(handles=handles, loc="upper center", ncol=5, fontsize=9, frameon=False)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(args.out, dpi=200)
    print(f"Saved {args.out}")


if __name__ == "__main__":
    main()
