"""Exploratory LLZO audit across models (Davide's request after the DeepSeek repeat). Descriptive only.

    python scripts/audit_llzo_models.py --archive "Haiku 5.5=data/experiments/environment_v1/llzo" \
        --archive "DeepSeek V3.2=data/experiments/deepseek_v1/llzo" \
        --json data/experiments/deepseek_v1/llzo_audit.json --md data/experiments/deepseek_v1/llzo_audit.md

For each archive and LLM arm (seeds 200-229, budget 10):
- which acceptable formulas the runs found, and how many picks are flagged oxyhalogens (the explicit review set of
  scripts/audit_llzo_chemistry.py: LiIO3, LiClO4, Li5IO6; a narrow annotation, not a hazard classifier);
- successful runs split into flagged-only and runs with an unflagged acceptable hit;
- diversity: distinct formulas per run, distinct formulas over all runs, mean pairwise Jaccard similarity of run
  formula sets (1 = every run picks the same set), and the anion class of every pick.
Post-hoc and exploratory: it does not change any score, eligibility or primary result.
"""
import argparse
import itertools
import json
import statistics
from collections import Counter
from pathlib import Path

from pymatgen.core import Composition

from scripts.audit_llzo_chemistry import FLAGS, HAZARD_TERMS

ARMS = ("upfront", "iterative", "sequential", "shuffled")


def anion_class(formula):
    if formula in FLAGS:
        return "oxyhalogen (flagged)"
    elements = {e.symbol for e in Composition(formula).elements}
    halides = [x for x in ("F", "Cl", "Br", "I") if x in elements]
    if len(halides) > 1:
        return "mixed halide"
    if halides:
        return halides[0] + ("+O" if "O" in elements else "")
    return "S" if "S" in elements else "O only" if "O" in elements else "other"


def audit_arm(directory, arm):
    runs = []
    for seed in range(200, 230):
        state = json.loads((directory / f"{arm}_r{seed}.json").read_text())
        assert state["status"] == "complete", f"{directory}/{arm}_r{seed}: {state['status']}"
        picks = [h["result"].get("formula") for h in state["history"]]
        good = [h["result"]["formula"] for h in state["history"] if h["result"].get("acceptable")]
        text = " ".join(str(h["proposal"].get(k, "")) for h in state["history"] for k in ("hypothesis", "motivation"))
        runs.append(dict(seed=seed, formulas=sorted({f for f in picks if f}), acceptable=good,
                         flagged=[f for f in good if f in FLAGS], hazard_mention=bool(HAZARD_TERMS.search(text))))
    sets = [set(r["formulas"]) for r in runs]
    jaccard = [len(a & b) / len(a | b) for a, b in itertools.combinations(sets, 2) if a | b]
    picks = Counter(f for r in runs for f in r["formulas"])
    return dict(
        successful_runs=sum(bool(r["acceptable"]) for r in runs),
        unflagged_hit_runs=sum(any(f not in FLAGS for f in r["acceptable"]) for r in runs),
        flagged_only_successful_runs=sum(bool(r["acceptable"]) and not any(f not in FLAGS for f in r["acceptable"])
                                         for r in runs),
        acceptable_formula_counts=dict(Counter(f for r in runs for f in r["acceptable"]).most_common()),
        flagged_acceptable_picks=sum(len(r["flagged"]) for r in runs),
        distinct_formulas_per_run_mean=statistics.mean(len(s) for s in sets),
        distinct_formulas_all_runs=len(picks),
        mean_pairwise_jaccard=statistics.mean(jaccard),
        anion_class_counts=dict(Counter(anion_class(f) for r in runs for f in r["formulas"]).most_common()),
        runs_mentioning_hazard_keywords=sum(r["hazard_mention"] for r in runs),
        per_run=[dict(seed=r["seed"], acceptable=r["acceptable"], flagged=r["flagged"]) for r in runs])


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--archive", action="append", required=True, help="label=path to an LLZO archive directory")
    p.add_argument("--json", type=Path, required=True)
    p.add_argument("--md", type=Path, required=True)
    args = p.parse_args()
    out = dict(status="post-hoc exploratory audit; primary results unchanged", flag_definition=sorted(FLAGS), models={})
    for spec in args.archive:
        label, path = spec.split("=", 1)
        out["models"][label] = {arm: audit_arm(Path(path), arm) for arm in ARMS}
    args.json.write_text(json.dumps(out, indent=2) + "\n")

    lines = ["# LLZO exploratory audit (post-hoc, descriptive)", "",
             "Flagged = explicit oxyhalogen review set (LiIO3, LiClO4, Li5IO6), a narrow annotation, not a hazard "
             "classifier. Diversity: formulas per run (of 10 queries), distinct formulas over 30 runs, and mean "
             "pairwise Jaccard similarity of run formula sets (1 = identical shortlists).", "",
             "| Model | Arm | Successful runs | Unflagged-hit runs | Flagged-only runs | Flagged picks | Formulas/run | "
             "Distinct (30 runs) | Mean Jaccard |", "|---|---|---|---|---|---|---|---|---|"]
    for label, arms in out["models"].items():
        for arm, a in arms.items():
            lines.append(f"| {label} | {arm} | {a['successful_runs']}/30 | {a['unflagged_hit_runs']} | "
                         f"{a['flagged_only_successful_runs']} | {a['flagged_acceptable_picks']} | "
                         f"{a['distinct_formulas_per_run_mean']:.1f} | {a['distinct_formulas_all_runs']} | "
                         f"{a['mean_pairwise_jaccard']:.2f} |")
    lines += ["", "## Acceptable formulas found (acceptable picks over 30 runs); anion classes of distinct formulas per run, summed", ""]
    for label, arms in out["models"].items():
        for arm in ("upfront", "iterative"):
            a = arms[arm]
            found = ", ".join(f"{f}{' (flagged)' if f in FLAGS else ''} ×{n}" for f, n in a["acceptable_formula_counts"].items())
            classes = ", ".join(f"{c} {n}" for c, n in a["anion_class_counts"].items())
            lines += [f"- **{label}, {arm}**: {found or 'none'}.", f"  Anion classes: {classes}."]
    args.md.write_text("\n".join(lines) + "\n")
    print(args.md.read_text())


if __name__ == "__main__":
    main()
