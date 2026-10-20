"""Compare the decision arms (llm, rules, human) of the same coating screen.

    python scripts/compare_arms.py runs/                 # latest screen per arm
    python scripts/compare_arms.py runs/ --out runs/compare.md

Prints and writes:
  1. the coating ranking of every arm side by side (rank and tier), plus the
     thermodynamics-only ablation;
  2. every contact where the arms disagree on the expert decision
     (sharp/interphase, layer stack, passivating/growing) — for the LLM vs the
     rules this is the override list: where the LLM's judgement departs from
     the deterministic rules;
  3. the score of each arm against benchmark/literature_cases.yaml.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from benchmark.score_agreement import score_ranking  # noqa: E402

ARMS = ("rules", "llm", "human")


def latest_per_arm(root: Path) -> dict[str, dict]:
    found: dict[str, tuple[str, dict]] = {}
    for p in sorted(root.rglob("ranking.json")):
        data = json.loads(p.read_text())
        arm = data.get("policy", "llm")
        key = p.parent.name                     # starts with a timestamp → sortable
        if arm not in found or key > found[arm][0]:
            found[arm] = (key, data)
    return {arm: d for arm, (_, d) in found.items()}


def _contacts(data: dict) -> dict[tuple[str, str], dict]:
    out = {}
    for row in data["ranking"]:
        for c in row["contacts"]:
            out[(row["coating"], " | ".join(c["pair"]))] = c
    return out


def _decision(c: dict) -> str:
    if c["interface_type"] == "sharp":
        return "sharp"
    return f"{c['character']}: {' | '.join(c['stack'])}"


def compare(arms: dict[str, dict], cases_yaml: Path) -> str:
    present = [a for a in ARMS if a in arms] + [a for a in arms if a not in ARMS]
    lines = ["## Coating ranking per arm (rank, tier)", ""]
    head = "| Coating | " + " | ".join(present) + " | thermodynamics only |"
    lines += [head, "|" + " --- |" * (len(present) + 2)]
    coatings = [r["coating"] for r in arms[present[0]]["ranking"]]
    thermo = {r["coating"]: r for r in arms[present[0]]["ranking_thermo_only"]}
    for coat in coatings:
        cells = []
        for a in present:
            r = next((r for r in arms[a]["ranking"] if r["coating"] == coat), None)
            cells.append(f"{r['rank']} (tier {r['tier']})" if r else "–")
        t = thermo.get(coat)
        tail = f" | {t['rank']} (tier {t['tier']}) |" if t else " | – |"
        lines.append(f"| {coat} | " + " | ".join(cells) + tail)

    lines += ["", "## Contacts where the arms disagree", ""]
    contacts = {a: _contacts(arms[a]) for a in present}
    keys = sorted(set().union(*[set(c) for c in contacts.values()]))
    rows = []
    for k in keys:
        ds = {a: _decision(contacts[a][k]) if k in contacts[a] else "–" for a in present}
        if len(set(ds.values())) > 1:
            rows.append(f"| {k[0]} | {k[1]} | " + " | ".join(ds[a] for a in present) + " |")
    if rows:
        lines += ["| Coating | Contact | " + " | ".join(present) + " |", "|" + " --- |" * (len(present) + 2), *rows]
    else:
        lines.append("All arms made the same decision on every contact.")
    if "llm" in contacts and "rules" in contacts:
        shared = set(contacts["llm"]) & set(contacts["rules"])
        overrides = [k for k in shared if _decision(contacts["llm"][k]) != _decision(contacts["rules"][k])]
        lines += ["", f"LLM overrides the rules on {len(overrides)}/{len(shared)} contacts. "
                      "Check each override against the literature to get the override accuracy."]

    lines += ["", "## Score against benchmark/literature_cases.yaml", ""]
    for a in present:
        s = score_ranking(arms[a], cases_yaml)
        lines.append(f"- **{a}**: {s['ranking'] if s else 'no matching coating_screens entry'}")
    s = score_ranking(arms[present[0]], cases_yaml)
    if s:
        lines.append(f"- **thermodynamics only**: {s['ranking_thermo_only']}")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", type=Path)
    ap.add_argument("--cases", type=Path, default=Path(__file__).resolve().parents[1] / "benchmark" / "literature_cases.yaml")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    arms = latest_per_arm(args.runs)
    if not arms:
        sys.exit(f"no ranking.json under {args.runs}")
    md = compare(arms, args.cases)
    print(md)
    if args.out:
        args.out.write_text(md)


if __name__ == "__main__":
    main()
