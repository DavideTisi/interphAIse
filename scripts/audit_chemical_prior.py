#!/usr/bin/env python3
"""Offline review audit; never supply its output to a search agent."""
import json
from collections import Counter
from math import comb
from pathlib import Path
import sys

from pymatgen.core import Composition

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from interphaise.benchmark import BenchmarkQueries


def main():
    # The ordering uses public composition and ID only, never benchmark outcomes.
    query = BenchmarkQueries(ROOT / 'data/pools/mp_candidates_v2.json',
                             ROOT / 'data/benchmarks/coating_v3.json', budget=50)
    candidates = query.available()
    fluorinated = {c['candidate_id'] for c in candidates
                   if 'F' in Composition(c['formula']).get_el_amt_dict()}
    order = sorted(candidates, key=lambda c: (c['candidate_id'] not in fluorinated,
                                            c['candidate_id']))
    trace = []
    for step, c in enumerate(order, 1):
        r = query.query(c['candidate_id'])
        trace.append({'evaluation': step, **c, 'acceptable': r.get('acceptable', False),
                      'penalty_bin': r.get('penalty_bin'),
                      'insulating': r.get('insulating'), 'band_gap_eV': r.get('band_gap_eV')})
    n = len(fluorinated)
    m = sum(r['acceptable'] for r in trace if r['candidate_id'] in fluorinated)
    counts = Counter(c['formula'] for c in candidates)
    report = {
        'purpose': 'Review-motivated chemical heuristic; fixed before main LLM runs, not a blind prior',
        'ordering': 'F-containing formulas first, then lexicographic candidate_id within each group',
        'task': query.task(), 'distinct_formula_strings': len(counts),
        'repeated_formulas': {f: k for f, k in counts.items() if k > 1},
        'fluorinated_candidates': n, 'acceptable_fluorinated': m,
        'acceptable_nonfluorinated': sum(r['acceptable'] for r in trace if r['candidate_id'] not in fluorinated),
        'first_acceptable_evaluation': next((r['evaluation'] for r in trace if r['acceptable']), None),
        'random_order_within_fluorinated_success': [
            {'evaluations': k, 'probability': 1 - comb(n - m, k) / comb(n, k)}
            for k in range(n + 1)],
        'deterministic_trace': trace,
    }
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
