"""Environment study analysis as declared in ENVIRONMENT_PROTOCOL.md section 4.

    python scripts/analyse_environment_study.py runs/<env1_experiment> runs/<env2_experiment> ... \
        --json environment_summary.json

Directories are grouped by electrolyte (from each manifest's benchmark) and loaded with the strict
loader of analyse_discovery_experiment.py (complete runs, matching hashes, frozen tables).

Primary, per environment: acceptable found within the budget. Contrasts iterative-sequential and
iterative-shuffled, paired by seed, exact two-sided McNemar; Holm across all environment x contrast
tests at family-wise alpha 0.05.

Secondary definitions (fixed before production results):
- first_acceptable: query index of the first acceptable result; runs with none count as budget + 1;
- best_bin_found: some queried result reaches the pool's best ranking_key (ties count), 95% Wilson;
- fluoride_fraction: share of queries that returned a pool candidate whose formula contains F,
  over queries 1..budget/2 and budget/2+1..budget (charged invalid IDs are excluded and counted);
- aggregate: equal-weight mean over environments of the per-environment difference in
  acceptance rate (descriptive only, no pooled test).

Uncertainty and per-run detail (SYNC_ADEM_8): 95% Wilson intervals for acceptance and best-bin
rates; first_acceptable counts per query index and quartiles (order statistics v[(n-1)//4],
v[(n-1)//2], v[ceil(3(n-1)/4)], as in the curve plots); per_run records with early/late fluoride
counts and change = late fraction - early fraction.

Handling: failed or short runs stay in every denominator; queries they did not reach count as no
success (first_acceptable = budget + 1 if none was found). Fluoride denominators count only queries
that returned a pool candidate formula; an empty half gives null for that run's fraction and change,
and such runs are excluded from fluoride_change_mean (the number used is reported).

--production enforces the frozen study (ENVIRONMENT_PROTOCOL.md): exactly the three frozen table
hashes, all five arms, budget 10, seeds 200..229 for every arm and environment, Holm family of 6.
Without it the analyser accepts subsets (useful for checks); never publish such output as final.
"""
import argparse
import json
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pymatgen.core import Composition
from scipy.stats import binomtest

from interphaise.discovery_evaluator import ranking_key
from scripts.analyse_discovery_experiment import load_experiments, wilson

CONTRASTS = [("iterative", "sequential"), ("iterative", "shuffled")]
PRODUCTION = dict(
    hashes={"Li6PS5Cl": "f70342c9aae0bd0e95f588bfb8c2f956815b3cf336c24e866119f7ab7f45f510",
            "Li3InCl6": "a95dc6fb78a0f295784ca004f77fc02a04005fe106f7fa35296cc51a424117e2",
            "Li7La3Zr2O12": "9bdef5811bafc0b24f6ae55140f74f0be592a0f4367ca253310e0544ebb8e060"},
    arms={"random", "upfront", "sequential", "iterative", "shuffled"}, budget=10, seeds=list(range(200, 230)),
    holm_family_size=6)


def wilson_interval(k, n):
    lo, hi = wilson(k / n, n)
    return [k / n - lo, k / n + hi]


def quartiles(values):
    v, n = sorted(values), len(values)
    return [v[(n - 1) // 4], v[(n - 1) // 2], v[math.ceil(3 * (n - 1) / 4)]]


def check_production(out):
    """Problems that stop this output from being the final frozen-study analysis (empty = complete)."""
    problems = []
    if set(out["environments"]) != set(PRODUCTION["hashes"]):
        problems.append(f"environments {sorted(out['environments'])} != {sorted(PRODUCTION['hashes'])}")
    for env, e in out["environments"].items():
        if e["hashes"]["benchmark_sha256"] != PRODUCTION["hashes"].get(env):
            problems.append(f"{env}: benchmark hash is not the frozen one")
        if e["budget"] != PRODUCTION["budget"]:
            problems.append(f"{env}: budget {e['budget']}")
        if set(e["arms"]) != PRODUCTION["arms"]:
            problems.append(f"{env}: arms {sorted(e['arms'])}")
        for arm, a in e["arms"].items():
            if a["seeds"] != PRODUCTION["seeds"]:
                problems.append(f"{env}/{arm}: seeds are not exactly 200..229")
    if out["holm_family_size"] != PRODUCTION["holm_family_size"]:
        problems.append(f"Holm family size {out['holm_family_size']} != 6")
    return problems


def holm(pvalues, alpha=0.05):
    """Holm step-down adjusted p-values (monotone, capped at 1) and rejection flags, input order."""
    order = sorted(range(len(pvalues)), key=lambda i: pvalues[i])
    adjusted, running = [0.0] * len(pvalues), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(pvalues) - rank) * pvalues[i]))
        adjusted[i] = running
    return adjusted, [a <= alpha for a in adjusted]


def mcnemar(left, right):
    """Exact two-sided McNemar on paired booleans (same seed order)."""
    b = sum(l and not r for l, r in zip(left, right))
    c = sum(r and not l for l, r in zip(left, right))
    p = 1.0 if b + c == 0 else float(binomtest(b, b + c, 0.5).pvalue)  # plain float keeps the JSON serialisable
    return dict(both=sum(l and r for l, r in zip(left, right)), left_only=b, right_only=c,
                neither=sum(not l and not r for l, r in zip(left, right)), p=p,
                difference=(sum(left) - sum(right)) / len(left))


def is_fluoride(formula):
    return "F" in Composition(formula).get_el_amt_dict()


def electrolyte(directory):
    exp = json.loads((directory / "experiment.json").read_text())
    path = Path(exp["benchmark"])
    return json.loads((path if path.is_absolute() else ROOT / path).read_text())["endpoints"]["electrolyte"]["formula"]


def arm_summary(runs, best, budget):
    first = [next((i + 1 for i, h in enumerate(r["history"]) if h["result"].get("acceptable")), budget + 1)
             for r in runs]
    accepted = [f <= budget for f in first]
    best_found = [any(ranking_key(h["result"]) == best for h in r["history"]) for r in runs]
    half, fluor, invalid, per_run = budget // 2, {"early": [0, 0], "late": [0, 0]}, 0, []
    for r, f in zip(runs, first):
        own = {"early": [0, 0], "late": [0, 0]}
        for i, h in enumerate(r["history"]):
            formula = h["result"].get("formula")
            if not formula:
                invalid += 1
                continue
            for counts in (fluor, own):
                part = counts["early" if i < half else "late"]
                part[0] += is_fluoride(formula)
                part[1] += 1
        frac = {k: v[0] / v[1] if v[1] else None for k, v in own.items()}
        per_run.append(dict(seed=r["seed"], status=r["status"], first_acceptable=f, accepted=f <= budget,
                            fluoride_early=own["early"], fluoride_late=own["late"],
                            fluoride_change=None if None in frac.values() else frac["late"] - frac["early"]))
    changes = [x["fluoride_change"] for x in per_run if x["fluoride_change"] is not None]
    n = len(runs)
    return dict(
        runs=n, seeds=[r["seed"] for r in runs], failed_runs=sum(r["status"] != "complete" for r in runs),
        acceptable=sum(accepted), acceptable_rate=sum(accepted) / n,
        acceptable_wilson95=wilson_interval(sum(accepted), n),
        first_acceptable_mean=statistics.mean(first), first_acceptable_median=statistics.median(first),
        first_acceptable_quartiles=quartiles(first),
        first_acceptable_counts={str(k): first.count(k) for k in range(1, budget + 2)},
        best_bin_found=sum(best_found), best_bin_rate=sum(best_found) / n,
        best_bin_wilson95=wilson_interval(sum(best_found), n),
        fluoride_fraction_early=fluor["early"][0] / fluor["early"][1] if fluor["early"][1] else None,
        fluoride_fraction_late=fluor["late"][0] / fluor["late"][1] if fluor["late"][1] else None,
        fluoride_change_mean=statistics.mean(changes) if changes else None, fluoride_change_runs=len(changes),
        queries_without_formula=invalid, per_run=per_run, _accepted=accepted)


def analyse(directories):
    groups = {}
    for d in directories:
        groups.setdefault(electrolyte(d), []).append(d)
    envs, tests = {}, []
    for env, dirs in sorted(groups.items()):
        exp, table, runs, notes = load_experiments(dirs)
        best = max(ranking_key(r) for r in table)
        arms = {arm: arm_summary(states, best, exp["budget"]) for arm, states in sorted(runs.items())}
        contrasts = {}
        for left, right in CONTRASTS:
            if left in arms and right in arms:
                if arms[left]["seeds"] != arms[right]["seeds"]:
                    raise ValueError(f"{env}: {left} and {right} are not paired on the same seeds")
                contrasts[f"{left}-{right}"] = mcnemar(arms[left]["_accepted"], arms[right]["_accepted"])
                tests.append((env, f"{left}-{right}"))
        envs[env] = dict(directories=[str(d) for d in dirs], budget=exp["budget"], hashes=exp["hashes"],
                         analysis_notes=notes, arms=arms, contrasts=contrasts)
    adjusted, reject = holm([envs[e]["contrasts"][c]["p"] for e, c in tests])
    for (env, c), a, rj in zip(tests, adjusted, reject):
        envs[env]["contrasts"][c].update(p_holm=a, reject_holm_0_05=rj)
    aggregate = {c: statistics.mean(envs[e]["contrasts"][c]["difference"] for e in envs if c in envs[e]["contrasts"])
                 for c in {c for _, c in tests}}
    for env in envs.values():
        for arm in env["arms"].values():
            arm.pop("_accepted")
    return dict(environments=envs, holm_family_size=len(tests), aggregate_equal_weight_difference=aggregate)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("experiments", type=Path, nargs="+")
    parser.add_argument("--json", type=Path)
    parser.add_argument("--production", action="store_true", help="Require the complete frozen study (final analysis)")
    args = parser.parse_args()
    out = analyse(args.experiments)
    out["production_check"] = check_production(out)
    if args.production and out["production_check"]:
        raise SystemExit("Not the complete frozen study:\n  " + "\n  ".join(out["production_check"]))
    for env, e in out["environments"].items():
        print(f"\n== {env} (budget {e['budget']})")
        print(f"{'arm':<12}{'runs':>5}{'accept':>8}{'rate':>7}{'first(mean/med)':>17}{'best bin':>9}{'F early/late':>15}")
        for arm, a in e["arms"].items():
            fe = "-" if a["fluoride_fraction_early"] is None else f"{a['fluoride_fraction_early']:.2f}"
            fl = "-" if a["fluoride_fraction_late"] is None else f"{a['fluoride_fraction_late']:.2f}"
            print(f"{arm:<12}{a['runs']:>5}{a['acceptable']:>8}{a['acceptable_rate']:>7.2f}"
                  f"{a['first_acceptable_mean']:>10.2f}/{a['first_acceptable_median']:<6}{a['best_bin_found']:>9}"
                  f"{fe + '/' + fl:>15}")
        for c, t in e["contrasts"].items():
            print(f"  {c:<22} both {t['both']} left-only {t['left_only']} right-only {t['right_only']} "
                  f"neither {t['neither']}  diff {t['difference']:+.2f}  p {t['p']:.4g}  "
                  f"Holm {t['p_holm']:.4g} {'REJECT' if t['reject_holm_0_05'] else ''}")
    print(f"\nHolm family size: {out['holm_family_size']}; equal-weight mean difference across environments:",
          {k: round(v, 3) for k, v in out["aggregate_equal_weight_difference"].items()})
    print("production check:", "COMPLETE frozen study" if not out["production_check"]
          else "NOT the final analysis: " + "; ".join(out["production_check"]))
    if args.json:
        args.json.write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
