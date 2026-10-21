"""Replay saved query outcomes and summarize the paired acceptance contrast offline."""
import argparse
import json
from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from interphaise.benchmark import BenchmarkQueries
from scripts.analyse_discovery_experiment import load_experiments, wilson


def paired_acceptance(left, right):
    """Exact binomial McNemar test on discordant seed pairs; descriptive follow-up.

    Reference: https://www.statsmodels.org/stable/generated/statsmodels.stats.contingency_tables.mcnemar.html
    """
    if set(left) != set(right):
        raise ValueError('Paired comparison requires identical seed sets')
    counts = {'both':0, 'left_only':0, 'right_only':0, 'neither':0}
    for seed in left:
        a,b = left[seed],right[seed]
        key = 'both' if a and b else 'left_only' if a else 'right_only' if b else 'neither'
        counts[key] += 1
    b,c = counts['left_only'],counts['right_only']
    p = min(1., 2*sum(comb(b+c,k) for k in range(min(b,c)+1))/2**(b+c))
    return {**counts, 'difference_in_success_rate':(b-c)/len(left),
            'exact_two_sided_mcnemar_p':p, 'n_pairs':len(left)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('experiment', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    exp, _, runs, _ = load_experiments([args.experiment])
    outcomes, summary, replayed = {}, {}, 0
    for arm, states in runs.items():
        outcomes[arm] = {}
        invalid, attempts = 0, 0
        for state in states:
            q = BenchmarkQueries(ROOT / exp['pool'], ROOT / exp['benchmark'], budget=exp['budget'])
            for h in state['history']:
                actual = q.query(h['proposal']['candidate_id'])
                if actual != h['result']:
                    raise ValueError(f'{arm}/{state["seed"]}: saved query result differs from replay')
                replayed += 1
                invalid += actual['status'] != 'ok'
            for attempt in state['proposal_attempts']:
                meta = attempt.get('llm_metadata') or {}
                if meta.get('returned_model') not in (None,'claude-haiku-5-5'):
                    raise ValueError('Unexpected returned model')
                attempts += 1
            outcomes[arm][state['seed']] = any(h['result'].get('acceptable',False) for h in state['history'])
        n = len(states); successes = sum(outcomes[arm].values()); p = successes/n
        lo,hi = wilson(p,n)
        summary[arm] = {'runs':n,'successes':successes,'rate':p,'wilson_95':[p-lo,p+hi],
                        'failed_runs':sum(s['status']=='failed' for s in states),
                        'failed_queries':invalid,'proposal_attempts':attempts}
    pairs = {}
    if 'iterative' in outcomes:
        for control in ('sequential','upfront','random'):
            if control in outcomes:
                pairs['iterative_vs_'+control] = paired_acceptance(outcomes['iterative'],outcomes[control])
    report = {'replayed_queries':replayed,'arms':summary,'paired_acceptance':pairs,
              'note':'Paired tests are supplementary; the frozen primary outcome is acceptable found by budget 10.'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
