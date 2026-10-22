"""Cross-model tables for the DeepSeek repeat (DEEPSEEK_PROTOCOL.md section 4). Descriptive only.

    python scripts/compare_models_environment.py \
        --haiku data/experiments/environment_v1/environment_summary.json \
        --deepseek data/experiments/deepseek_v1/environment_summary.json \
        --haiku-usage data/experiments/environment_v1/usage.json --deepseek-usage data/experiments/deepseek_v1/usage.json \
        --out data/experiments/deepseek_v1/model_comparison.md

Each summary comes from scripts/analyse_environment_study.py --production under its own policy, so each
model's six McNemar tests are Holm-corrected within that model's family. The random arm is reused from
the Haiku archive. No cross-model significance test is made. This compares model configurations, not
matched reasoning compute.
"""
import argparse
import json
from pathlib import Path

ENVS = ("Li6PS5Cl", "Li3InCl6", "Li7La3Zr2O12")
ARMS = ("random", "upfront", "sequential", "iterative", "shuffled")


def cell(arm):
    lo, hi = (max(0.0, x) for x in arm["acceptable_wilson95"])   # avoid "-0.00" from float rounding
    return f"{arm['acceptable']}/{arm['runs']} ({lo:.2f}–{hi:.2f})"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for name in ("haiku", "deepseek", "haiku-usage", "deepseek-usage"):
        p.add_argument(f"--{name}", type=Path, required=name in ("haiku", "deepseek"))
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    h, d = (json.loads(path.read_text()) for path in (args.haiku, args.deepseek))
    if d.get("production_check") or h.get("production_check"):
        raise SystemExit("Both summaries must come from a passing --production analysis")
    models = {"Haiku 5.5": h, "DeepSeek V3.2": d}

    lines = ["# Haiku 5.5 vs DeepSeek V3.2: three-environment study",
             "", "A comparison of **model configurations**, not matched reasoning compute. Random is reused from the "
             "Haiku archive. Entries: acceptable runs / 30, with 95% Wilson interval. Descriptive across models.", ""]
    lines += ["## Acceptance within 10 queries", "",
              "| Environment | Arm | Haiku 5.5 | DeepSeek V3.2 |", "|---|---|---|---|"]
    for env in ENVS:
        for arm in ARMS:
            ha = h["environments"][env]["arms"].get(arm)
            da = d["environments"][env]["arms"].get(arm)
            lines.append(f"| {env} | {arm} | {cell(ha) if ha else '—'} | "
                         f"{cell(da) if da else ('reused (Haiku archive)' if arm == 'random' else '—')} |")

    lines += ["", "## Planned comparisons (paired by seed, exact McNemar, Holm within each model's family of 6)", "",
              "| Environment | Contrast | Model | iterative-only / other-only | Difference | p | p (Holm) | Holm 0.05 |",
              "|---|---|---|---|---|---|---|---|"]
    for env in ENVS:
        for c in ("iterative-sequential", "iterative-shuffled"):
            for model, s in models.items():
                t = s["environments"][env]["contrasts"][c]
                lines.append(f"| {env} | {c} | {model} | {t['left_only']} / {t['right_only']} | {t['difference']:+.2f} | "
                             f"{t['p']:.3g} | {t['p_holm']:.3g} | {'reject' if t['reject_holm_0_05'] else 'not rejected'} |")

    random = h["environments"]["Li7La3Zr2O12"]["arms"]["random"]
    lines += ["", "## LLZO against the reused random baseline", "",
              f"Random (Haiku archive): {cell(random)}.", "",
              "| Model | Arm | Acceptable | Difference vs random |", "|---|---|---|---|"]
    for model, s in models.items():
        for arm in ("iterative", "upfront"):
            a = s["environments"]["Li7La3Zr2O12"]["arms"][arm]
            lines.append(f"| {model} | {arm} | {cell(a)} | {(a['acceptable'] - random['acceptable']) / 30:+.2f} |")
    lines += ["", "LLZO interpretation keeps the chemistry-audit caveat (SYNC_ADEM_10): the acceptable set includes "
              "flagged oxyhalogen candidates with different evidence levels."]

    if args.haiku_usage and args.deepseek_usage:
        lines += ["", "## Usage (LLM arms, three environments)", "",
                  "| Model | Calls | Input tokens | Output tokens (incl. reasoning) | Reasoning | Cost (USD) | Cost basis |",
                  "|---|---|---|---|---|---|---|"]
        for model, path, basis in (("Haiku 5.5", args.haiku_usage, "list-price estimate"),
                                   ("DeepSeek V3.2", args.deepseek_usage, "OpenRouter-reported charge")):
            t = json.loads(path.read_text())["total"]
            lines.append(f"| {model} | {int(t['calls'])} | {int(t['input_tokens']):,} | {int(t['output_tokens']):,} | "
                         f"{int(t['thinking_tokens']):,} | {t['usd']:.2f} | {basis} |")
    args.out.write_text("\n".join(lines) + "\n")
    print(args.out.read_text())


if __name__ == "__main__":
    main()
