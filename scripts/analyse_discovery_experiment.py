"""Success probability vs evaluations per arm, with exact random baselines.

    python scripts/analyse_discovery_experiment.py runs/<stamp>_experiment --plot curve.png
    python scripts/analyse_discovery_experiment.py runs/<main> runs/<rerun> --plot curve.png

With several directories, disjoint seeds are combined. Duplicate arm/seed pairs
require --replace-duplicates. Settings must match unless explicitly allowed.

Two targets (EVALUATOR_HANDOFF.md / SYNC_ADEM.md section 6):
  acceptable : some queried candidate has acceptable == True
  best bin   : some queried candidate reaches the best ranking_key in the pool (ties count)
Successes M are counted over the whole pool, failures included in N. Failed or short
runs are kept; an observed success persists after a run stops. Error bars: 95% Wilson.
"""
import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from interphaise.discovery import random_success_curve
from interphaise.discovery_evaluator import ranking_key
from interphaise.tools.thermo_dataset import verify_hash

TARGETS = {"acceptable": lambda r, best: bool(r.get("acceptable")),
           "best bin": lambda r, best: ranking_key(r) == best}


def wilson(p, n, z=1.96):
    """95% Wilson interval as (lower, upper) distances from p; nonzero width at p = 0 or 1."""
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0, p - (centre - half)), max(0, centre + half - p)


def load_experiments(directories, *, benchmark=None, replace_duplicates=False, allow_setting_mismatch=False):
    exps = [(d, json.loads((d / 'experiment.json').read_text())) for d in directories]
    exp = exps[0][1]
    runs, exclusions = {}, []
    fields = ('prompt_version', 'model', 'temperature', 'max_tokens')
    for directory, manifest in exps:
        if manifest['hashes'] != exp['hashes'] or manifest['budget'] != exp['budget']:
            raise ValueError(f'{directory}: hashes or budget differ')
        differences = [key for key in fields if manifest.get(key) != exp.get(key)]
        if differences and not allow_setting_mismatch:
            raise ValueError(f'{directory}: settings differ: {differences}')
        if differences:
            exclusions.append({'directory': str(directory), 'setting_differences': differences})
        expected = {f'{arm}_r{seed:02d}.json' for arm in manifest['arms']
                    for seed in range(manifest.get('start_seed', 0),
                                      manifest.get('start_seed', 0) + manifest['repeats'])}
        found = {p.name for p in directory.glob('*_r*.json')}
        if expected != found:
            raise ValueError(f'{directory}: missing={sorted(expected-found)}, unexpected={sorted(found-expected)}')
        for name in sorted(expected):
            state = json.loads((directory / name).read_text())
            arm, seed = state['strategy'], state['seed']
            if name != f'{arm}_r{seed:02d}.json' or state['hashes'] != manifest['hashes']:
                raise ValueError(f'{directory/name}: identity or hash mismatch')
            if state['prompt_version'] != manifest['prompt_version'] or state['budget'] != manifest['budget']:
                raise ValueError(f'{directory/name}: run settings mismatch')
            if state['status'] not in ('complete', 'failed'):
                raise ValueError(f'{directory/name}: run is unfinished')
            if len(state['history']) > state['budget'] or (state['status']=='complete' and len(state['history'])!=state['budget']):
                raise ValueError(f'{directory/name}: invalid history length')
            by_seed = runs.setdefault(arm, {})
            if seed in by_seed:
                if not replace_duplicates:
                    raise ValueError(f'Duplicate {arm}/{seed}; use --replace-duplicates for intentional reruns')
                exclusions.append({'replaced_arm':arm, 'seed':seed, 'replacement_directory':str(directory)})
            by_seed[seed] = state
    path = Path(benchmark or exp['benchmark'])
    if not path.is_absolute():
        path = ROOT / path
    data = json.loads(path.read_text())
    verify_hash(data)
    if data['sha256'] != exp['hashes']['benchmark_sha256']:
        raise ValueError('Analysis benchmark hash differs from runs')
    return exp, data['results'], {arm:[by_seed[s] for s in sorted(by_seed)] for arm,by_seed in runs.items()}, exclusions


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("experiments", type=Path, nargs="+")
    parser.add_argument("--plot", type=Path, help="Write the success-curve figure here")
    parser.add_argument('--benchmark', type=Path, help='Override a historical machine-specific path; hash is checked')
    parser.add_argument('--replace-duplicates', action='store_true')
    parser.add_argument('--allow-setting-mismatch', action='store_true')
    parser.add_argument('--summary', type=Path, help='Write machine-readable curves, denominators and audit details')
    args = parser.parse_args()

    exp, table, runs, exclusions = load_experiments(args.experiments, benchmark=args.benchmark,
        replace_duplicates=args.replace_duplicates, allow_setting_mismatch=args.allow_setting_mismatch)
    best = max(ranking_key(r) for r in table)
    budget = exp["budget"]
    steps = range(1, budget + 1)
    for arm, states in runs.items():
        print(f'{arm}: {len(states)} validated runs')

    # Review-motivated, deterministic chemical heuristic; chosen after seeing the
    # exhaustive benchmark, not an independent blind prior. No simulated repeats.
    from pymatgen.core import Composition
    heuristic = sorted(table, key=lambda r: ('F' not in Composition(r['formula']).get_el_amt_dict(), r['candidate_id']))

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
        if not exp['synthetic']:
            rows['fluorides first (post-hoc)'] = ([float(any(hit(r,best) for r in heuristic[:k])) for k in steps], None, 'fixed order', 0)
        curves[target] = rows

        print(f"\n{target}: P(success) at k = 1..{budget}")
        print(f"{'arm':<16}{'runs':>12}{'failed':>8}  curve")
        for arm, (p, _, n, failed) in rows.items():
            print(f"{arm:<16}{str(n):>12}{failed:>8}  " + " ".join(f"{x:.2f}" for x in p))

    if args.summary:
        usage = {}
        for arm, states in runs.items():
            attempts = [a for s in states for a in s['proposal_attempts']]
            usage[arm] = {'proposal_calls':len(attempts), 'runs':len(states),
                          'failed_runs':sum(s['status']!='complete' for s in states),
                          'missing_usage_records':sum(not (a.get('llm_metadata') or {}).get('usage') for a in attempts)}
            for token in ('input_tokens','output_tokens'):
                usage[arm][token] = sum(((a.get('llm_metadata') or {}).get('usage') or {}).get(token,0) for a in attempts)
        summary = {'hashes':exp['hashes'], 'curves':curves, 'usage':usage, 'analysis_notes':exclusions,
                   'settings':{k:exp.get(k) for k in ('prompt_version','model','temperature','max_tokens','budget')}}
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(json.dumps(summary, indent=2, allow_nan=False)+'\n')

    if args.plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
        for ax, (target, rows) in zip(axes, curves.items()):
            for arm, (p, se, n, _) in rows.items():
                if se is None:
                    ax.plot(steps, p, linestyle='--', label=f"{arm} {n}")
                else:
                    ax.errorbar(steps, p, yerr=se, marker="o", capsize=3, label=f"{arm} (n={n})")
            ax.set(xlabel="evaluations", title=f"P({target} found)", ylim=(0, 1.05))
            ax.legend(fontsize=8)
        axes[0].set_ylabel("probability")
        fig.suptitle(f"{'synthetic' if exp['synthetic'] else 'frozen v3'} benchmark, budget {budget}; error bars: 95% Wilson")
        fig.tight_layout()
        fig.savefig(args.plot, dpi=150)
        print(f"Saved {args.plot}")


if __name__ == "__main__":
    main()
