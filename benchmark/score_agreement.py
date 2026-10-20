"""Score agent decisions against benchmark/literature_cases.yaml.

    python benchmark/score_agreement.py runs/            # all decision logs under runs/
    python benchmark/score_agreement.py runs/ --only-verified

Metrics per case (decision numbers as in the README):
  type_ok     decision 2: sharp vs interphase matches
  phases_j    decision 3: Jaccard similarity of intermediate phases
  order_ok    decision 3: same intermediate phases in the same order
  facet_hit   decision 1: any expected facet among the agent's proposals
  agreement   self-consistency of the agent's consensus (from the log)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml
from pymatgen.core import Composition


def _f(x: str) -> str:
    return Composition(x).reduced_formula


def load_expected(path: Path, only_verified: bool) -> dict:
    data = yaml.safe_load(path.read_text())["cases"]
    return {(_f(c["electrode"]), _f(c["electrolyte"])): c for c in data if c.get("verified") or not only_verified}


def score_log(log: dict, expected: dict) -> dict | None:
    ev = log["events"]
    ctx = next((e["inputs"]["context"] for e in ev if e["stage"] == "reactivity"), None)
    if ctx is None:
        return None
    key = (_f(ctx["electrode"]), _f(ctx["electrolyte"]))
    exp = expected.get(key)
    if exp is None:
        return None
    dec = [e for e in ev if e["stage"] == "interface_type" and e["kind"] in ("decision", "llm_decision")]
    if not dec:
        return None
    first = dec[0]  # the decision before any stack-check feedback
    out = first["output"]
    inner = [_f(p) for p in out["stack"][1:-1]]
    exp_inner = [_f(p) for p in exp.get("interphase_phases") or []]
    a, b = set(inner), set(exp_inner)
    phases_j = 1.0 if not a and not b else len(a & b) / len(a | b)

    proposed = set()
    for e in ev:
        if e["stage"] == "facets" and e["kind"] in ("decision", "llm_decision"):
            for item in e["output"]:
                c = item["choice"]
                if _f(c["substrate"]) == key[0]:
                    proposed.add(("electrode", tuple(c["substrate_miller"])))
                if _f(c["film"]) == key[1]:
                    proposed.add(("electrolyte", tuple(c["film_miller"])))
    exp_f = {("electrode", tuple(m)) for m in exp.get("electrode_facets") or []} | {
        ("electrolyte", tuple(m)) for m in exp.get("electrolyte_facets") or []}

    return {
        "case": log["case"],
        "policy": first["inputs"].get("policy", "llm"),
        "type_ok": out["interface_type"] == exp["interface_type"],
        "phases_j": round(phases_j, 2),
        "order_ok": inner == exp_inner,
        "facet_hit": (bool(proposed & exp_f) if exp_f else None),
        "agreement": first["inputs"].get("agreement"),
    }


def score_ranking(ranking: dict, cases_yaml: Path, only_verified: bool = False) -> dict | None:
    """Pairwise check of a coating ranking against coating_screens in the yaml.

    Counts the expected coatings ranked above the uncoated baseline, for the
    arm's ranking (llm, rules or human) and for the thermodynamics-only ablation.
    """
    cfg = ranking["config"]
    for exp in yaml.safe_load(cases_yaml.read_text()).get("coating_screens", []):
        if only_verified and not exp.get("verified"):
            continue
        if (_f(exp["electrode"]), _f(exp["electrolyte"])) != (_f(cfg["electrode"]), _f(cfg["electrolyte"])):
            continue
        out = {}
        for key in ("ranking", "ranking_thermo_only"):
            pos = {r["coating"]: r["rank"] for r in ranking[key]}
            base = pos.get("none")
            hits = [c for c in exp["expected_above_uncoated"] if c in pos and base and pos[c] < base]
            tested = [c for c in exp["expected_above_uncoated"] if c in pos]
            out[key] = f"{len(hits)}/{len(tested)} expected coatings ranked above uncoated"
        out["policy"] = ranking.get("policy", "llm")
        return out
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", type=Path)
    ap.add_argument("--cases", type=Path, default=Path(__file__).with_name("literature_cases.yaml"))
    ap.add_argument("--only-verified", action="store_true")
    args = ap.parse_args()

    for p in sorted(args.runs.rglob("ranking.json")):
        r = score_ranking(json.loads(p.read_text()), args.cases, args.only_verified)
        if r:
            print(f"{p.parent.name}: {json.dumps(r)}")

    expected = load_expected(args.cases, args.only_verified)
    rows = []
    for p in sorted(args.runs.rglob("decision_log.json")):
        r = score_log(json.loads(p.read_text()), expected)
        if r:
            rows.append(r)
    for r in rows:
        print(json.dumps(r))
    if rows:
        n = len(rows)
        print(f"\ndecision 2 (type): {sum(r['type_ok'] for r in rows)}/{n}   "
              f"decision 3 (exact order): {sum(r['order_ok'] for r in rows)}/{n}   "
              f"mean phase Jaccard: {sum(r['phases_j'] for r in rows) / n:.2f}")


if __name__ == "__main__":
    main()
