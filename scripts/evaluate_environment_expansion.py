#!/usr/bin/env python3
"""Score every planned combination and audit exploratory environment differences."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations
from importlib.metadata import version
import json
import math
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pymatgen.core import Composition, Structure, Element
from interphaise.discovery_evaluator import Objective, evaluate_candidate, _project, _contact
from interphaise.tools.thermo_dataset import digest, load_entries, resolve_entry, verify_hash
from scripts.fetch_environment_dataset import validate_coverage, write_hashed


def success_probability(n, m, k):
    if not 0 <= m <= n or not 0 <= k <= n:
        raise ValueError('Invalid without-replacement population or budget')
    return 1 - (math.comb(n-m, k) / math.comb(n, k) if k <= n-m else 0)


def eligible(row):
    return row.get('status') == 'ok' and row.get('insulating', False)


def component_summary(row):
    values = {'coating_self': row['self_decomposition_penalty'],
              'cathode_contact': max(0., -row['contact_reaction_energies'][0]),
              'electrolyte_contact': max(0., -row['contact_reaction_energies'][1])}
    dominant = [name for name, value in values.items() if abs(value - row['penalty']) <= 1e-8]
    return {'penalties': values, 'dominant_components': dominant,
            'dominance_tolerance_eV_non_Li_atom': 1e-8}


def diagnostics(results):
    n = len(results)
    valid = [r for r in results if eligible(r)]
    best = min((r['penalty_bin'] for r in valid), default=None)
    winners = [r for r in valid if r['penalty_bin'] == best]
    acceptable = [r for r in valid if r['acceptable']]
    hist = Counter(r['penalty_bin'] for r in valid)
    curve = []
    for k in range(n+1):
        probabilities = {}; previous = 0.; cumulative_count = 0; median = None
        for b, count in sorted(hist.items()):
            cumulative_count += count
            cumulative = success_probability(n, cumulative_count, k)
            probabilities[b] = cumulative - previous
            if median is None and cumulative >= .5:
                median = b
            previous = cumulative
        p_eligible = success_probability(n, len(valid), k)
        curve.append({'evaluations': k,
            'probability_acceptable': success_probability(n, len(acceptable), k),
            'probability_best_bin': success_probability(n, len(winners), k),
            'probability_no_eligible_result': 1-p_eligible,
            'median_best_bin': median,
            'expected_best_bin_regret_conditional_on_eligible': (
                sum(p*(b-best) for b,p in probabilities.items())/p_eligible
                if p_eligible and best is not None else None)})
    ordered = sorted(results, key=lambda r: (
        'F' not in Composition(r['formula']).get_el_amt_dict(), r['candidate_id']))
    heuristic = []; found_best = None; found_acceptable = False
    for k, row in enumerate(ordered, 1):
        if eligible(row):
            found_best = row['penalty_bin'] if found_best is None else min(found_best, row['penalty_bin'])
            found_acceptable = found_acceptable or row['acceptable']
        heuristic.append({'evaluations': k, 'candidate_id': row['candidate_id'],
            'acceptable_found': found_acceptable, 'best_bin_so_far': found_best,
            'bin_regret': found_best-best if found_best is not None and best is not None else None})
    return {'total': n, 'status_counts': dict(Counter(r['status'] for r in results)),
        'eligible': len(valid), 'acceptable': len(acceptable),
        'acceptable_ids': [r['candidate_id'] for r in acceptable],
        'best_bin': best, 'best_ids': [r['candidate_id'] for r in winners],
        'eligible_bin_counts': dict(sorted(hist.items())),
        'dominant_component_counts_eligible_ties_counted_in_each': dict(Counter(
            c for r in valid for c in r['component_analysis']['dominant_components'])),
        'dominant_component_combinations_eligible': dict(Counter(
            '+'.join(r['component_analysis']['dominant_components']) for r in valid)),
        'exact_random_without_replacement': curve,
        'fluorides_first': {'provenance': 'Rule chosen post hoc on original v3; unchanged before expansion scores',
            'ordering': 'contains fluorine first, then lexicographic candidate_id',
            'first_acceptable_query': next((r['evaluations'] for r in heuristic if r['acceptable_found']), None),
            'first_optimum_bin_query': next((r['evaluations'] for r in heuristic if r['bin_regret'] == 0), None),
            'trajectory': heuristic},
        'review_findings': (["No acceptable candidates at the unchanged threshold"] if not acceptable else [])
            + (["No eligible candidates; optimum and regret are undefined"] if not valid else [])}


def compare_environments(packages):
    from scipy.stats import spearmanr
    comparisons = []
    for a, b in combinations(packages, 2):
        ma = {r['candidate_id']:r for r in a['results']}
        mb = {r['candidate_id']:r for r in b['results']}
        ids = sorted(i for i in ma.keys() & mb.keys() if eligible(ma[i]) and eligible(mb[i]))
        x = [ma[i]['penalty_bin'] for i in ids]; y = [mb[i]['penalty_bin'] for i in ids]
        corr = float(spearmanr(x, y).statistic) if len(set(x)) > 1 and len(set(y)) > 1 else None
        counts = Counter()
        for i, j in combinations(ids, 2):
            da = ma[i]['penalty_bin']-ma[j]['penalty_bin']
            db = mb[i]['penalty_bin']-mb[j]['penalty_bin']
            counts['reversed' if da*db < 0 else 'tie_changed' if (da == 0) != (db == 0)
                   else 'tied_both' if da == db == 0 else 'same_order'] += 1
        comparisons.append({'environments': [a['environment_id'], b['environment_id']],
            'common_eligible': len(ids), 'spearman_binned_penalty': corr,
            'candidate_pair_order_counts': dict(counts),
            'changed_penalty_bins': sum(ma[i]['penalty_bin'] != mb[i]['penalty_bin'] for i in ids),
            'changed_acceptability': sum(ma[i]['acceptable'] != mb[i]['acceptable'] for i in ids),
            'shared_best_ids': sorted(set(a['diagnostics']['best_ids']) & set(b['diagnostics']['best_ids'])),
            'rows': [{'candidate_id':i, 'formula':ma[i]['formula'],
                      'penalty_bins':[ma[i]['penalty_bin'],mb[i]['penalty_bin']],
                      'penalties':[ma[i]['penalty'],mb[i]['penalty']]} for i in ids]})
    return comparisons


def replay_original(original, new):
    actual = {r['candidate_id']:r for r in new['results']}
    numeric = ['penalty', 'self_decomposition_penalty', 'mu_Li_eV', 'band_gap_eV']
    maximum = 0.; mismatches = []
    for old in original['results']:
        row = actual[old['candidate_id']]
        for key in ('status', 'acceptable', 'insulating', 'penalty_bin', 'entries'):
            if row.get(key) != old.get(key):
                mismatches.append({'candidate_id':old['candidate_id'], 'field':key})
        if old['status'] == row['status'] == 'ok':
            differences = [abs(old[k]-row[k]) for k in numeric]
            differences += [abs(x-y) for x,y in zip(old['contact_reaction_energies'], row['contact_reaction_energies'])]
            differences += [abs(old['endpoint_decomposition_penalties'][k]-row['endpoint_decomposition_penalties'][k])
                            for k in ('electrode', 'electrolyte')]
            maximum = max(maximum, *differences)
            if max(differences) > 1e-8:
                mismatches.append({'candidate_id':old['candidate_id'], 'field':'numeric', 'max_difference':max(differences)})
    return {'original_benchmark_sha256':original['sha256'], 'rows':len(original['results']),
        'max_numeric_difference': maximum, 'tolerance':1e-8, 'mismatches':mismatches,
        'passed':not mismatches,
        'comparison_ignores':['dataset provenance', 'evaluation timing', 'unused phase count',
                              'degenerate product assemblages/mixing fractions']}


def endpoint_review(plan, entries):
    reviews = []; pinned = {}
    for env in plan['environments']:
        pinned[env['environment_id']] = {}
        for role, doc in env['endpoints'].items():
            structure = Structure.from_dict(doc['structure'])
            if not structure.is_ordered or structure.composition.fractional_composition != Composition(doc['formula']).fractional_composition:
                raise ValueError('Endpoint order/composition check failed')
            distances = structure.distance_matrix
            for i in range(len(structure)):
                distances[i,i] = float('inf')
            if float(distances.min()) < .5:
                raise ValueError('Endpoint coincident or implausibly close sites')
            entry = resolve_entry(entries, doc['material_id'], structure)
            pinned[env['environment_id']][role] = entry
            reviews.append({'environment_id':env['environment_id'], 'role':role,
                'material_id':doc['material_id'], 'formula':doc['formula'],
                'space_group':list(structure.get_space_group_info()), 'ordered':True,
                'primitive_nsites':len(structure.get_primitive_structure()),
                'min_distance_A':float(distances.min()), 'structure_sha256':digest(doc['structure']),
                'summary_origins':doc['origins'], 'matched_entry_id':str(entry.entry_id),
                'matched_entry_material_id':str(entry.data['material_id']),
                'matched_entry_task_id':str(entry.data.get('task_id')),
                'corrected_energy_eV':entry.energy, 'structure_matcher_default_fit':True,
                'decision':'retain preselected ordered 0 K computational model; no transport validation'})
    return reviews, pinned


def qhull_checks(packages, pool, entries, pinned, objective):
    """Independent small-system hull construction for predetermined LiF contacts."""
    from pymatgen.analysis.phase_diagram import GrandPotentialPhaseDiagram
    candidate = min((c for c in pool['candidates'] if c['formula'] == 'LiF'), key=lambda c:c['candidate_id'])
    coating = resolve_entry(entries, candidate['material_id'], Structure.from_dict(candidate['structure']))
    checks = []
    for package in packages:
        result = next(r for r in package['results'] if r['candidate_id'] == candidate['candidate_id'])
        mu = result['mu_Li_eV']; coat = _project(coating, mu)
        for index, role in enumerate(('electrode', 'electrolyte')):
            endpoint = pinned[package['environment_id']][role]
            other = _project(endpoint, mu)
            pair = (other, coat) if index == 0 else (coat, other)
            allowed = set(endpoint.composition.elements) | set(coating.composition.elements) | {Element('Li')}
            subset = [e for e in entries if set(e.composition.elements) <= allowed]
            gpd = GrandPotentialPhaseDiagram(subset, {Element('Li'):mu})
            self_coat = max(0., -_contact(gpd, coat, coat)['reaction_energy'])
            self_endpoint = max(0., -_contact(gpd, other, other)['reaction_energy'])
            hc, he = coat.energy_per_atom-self_coat, other.energy_per_atom-self_endpoint
            refs = (he,hc) if index == 0 else (hc,he)
            value = _contact(gpd, *pair, refs)['reaction_energy']
            expected = result['contact_reaction_energies'][index]
            checks.append({'environment_id':package['environment_id'], 'candidate_id':candidate['candidate_id'],
                'contact':role, 'qhull':value, 'linprog':expected, 'abs_difference':abs(value-expected),
                'self_coating_abs_difference':abs(self_coat-result['self_decomposition_penalty']),
                'self_endpoint_abs_difference':abs(self_endpoint-result['endpoint_decomposition_penalties'][role]),
                'entry_count':len(subset)})
    return {'selection':'lexicographically first pinned LiF, both contacts in every environment',
            'tolerance':1e-8, 'checks':checks, 'passed':all(max(r['abs_difference'],
                r['self_coating_abs_difference'],r['self_endpoint_abs_difference']) <= 1e-8 for r in checks)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pool', type=Path, default=ROOT/'data/exploration/environment_expansion_v1/pool.json')
    ap.add_argument('--plan', type=Path, default=ROOT/'data/exploration/environment_expansion_v1/plan.json')
    ap.add_argument('--dataset', type=Path, default=ROOT/'data/exploration/environment_expansion_v2/dataset.json.gz')
    ap.add_argument('--original', type=Path, default=ROOT/'data/benchmarks/coating_v3.json')
    ap.add_argument('--output', type=Path, default=ROOT/'data/exploration/environment_expansion_v2/evaluation')
    args = ap.parse_args()
    if args.output.exists():
        ap.error('Output exists; choose a fresh directory')
    pool = json.loads(args.pool.read_text()); verify_hash(pool)
    plan = json.loads(args.plan.read_text()); verify_hash(plan)
    original = json.loads(args.original.read_text()); verify_hash(original)
    dataset, entries = load_entries(args.dataset)
    validate_coverage(pool, plan, dataset)
    if original['sha256'] != plan['original_benchmark_sha256']:
        ap.error('Original benchmark provenance mismatch')
    if plan['objective'] != original['objective'] or digest(plan['objective']) != plan['objective_sha256']:
        ap.error('Objective differs from frozen v3')
    objective = Objective(**plan['objective'])
    reviews, pinned = endpoint_review(plan, entries)
    args.output.mkdir(parents=True)
    review = write_hashed(args.output/'endpoint_review.json', {
        'plan_sha256':plan['sha256'], 'dataset_sha256':dataset['sha256'],
        'decision_before_scoring':'retain every preselected model', 'reviews':reviews})
    packages = []; started = time.monotonic()
    for env in plan['environments']:
        results = []; ep = pinned[env['environment_id']]
        for candidate in pool['candidates']:
            tick = time.monotonic()
            try:
                coating = resolve_entry(entries, candidate['material_id'], Structure.from_dict(candidate['structure']))
                allowed = {e for entry in [coating,*ep.values()] for e in entry.composition.elements}
                subset = [e for e in entries if set(e.composition.elements) <= allowed]
                result = evaluate_candidate(candidate['candidate_id'], coating,
                    electrode_entry=ep['electrode'], electrolyte_entry=ep['electrolyte'],
                    entries=subset, voltage=env['voltage_V'], band_gap_eV=candidate['band_gap_eV'],
                    energy_source=f"MP {dataset['db_version']} {dataset['thermo_type']}; dataset {dataset['sha256']}",
                    objective=objective)
                result['thermo_entry_count'] = len(subset)
                result['component_analysis'] = component_summary(result)
            except ValueError as exc:
                result = {'candidate_id':candidate['candidate_id'], 'status':'failed',
                          'error_type':type(exc).__name__, 'error':str(exc)}
            result.update(formula=candidate['formula'], family=candidate['family'],
                          evaluation_wall_seconds=time.monotonic()-tick)
            results.append(result)
        diag = diagnostics(results)
        for row in results:
            row['bin_regret'] = row['penalty_bin']-diag['best_bin'] if eligible(row) else None
        package = {'schema_version':'exploratory-environment-results-v1',
            'status':'exploratory-exhaustive-not-frozen', 'environment_id':env['environment_id'],
            'pool_sha256':pool['sha256'], 'plan_sha256':plan['sha256'],
            'dataset_sha256':dataset['sha256'], 'endpoint_review_sha256':review['sha256'],
            'objective':plan['objective'], 'objective_sha256':plan['objective_sha256'],
            'endpoints':{r:{'material_id':d['material_id'], 'formula':d['formula']} for r,d in env['endpoints'].items()},
            'voltage_V':env['voltage_V'], 'results':results, 'diagnostics':diag}
        package = write_hashed(args.output/(env['environment_id']+'.json'), package)
        packages.append(package)
        print(json.dumps({'environment_id':env['environment_id'], **{k:diag[k] for k in (
            'status_counts','eligible','acceptable','best_bin','best_ids')}}), flush=True)
    replay = replay_original(original, next(p for p in packages if p['environment_id'] == 'lco_lpscl_4v'))
    replay['same_database_vintage'] = dataset['source_dataset_sha256'] == original['dataset_sha256']
    if replay['same_database_vintage'] and not replay['passed']:
        raise ValueError('Original v3 replay failed; preserve outputs for diagnosis, do not use as validated')
    crosscheck = qhull_checks(packages, pool, entries, pinned, objective)
    if not crosscheck['passed']:
        raise ValueError('Independent hull audit failed')
    summary = write_hashed(args.output/'summary.json', {
        'schema_version':'environment-expansion-audit-v1', 'status':'exploratory-audited-not-frozen',
        'created_at':datetime.now(timezone.utc).isoformat(), 'pool_sha256':pool['sha256'],
        'plan_sha256':plan['sha256'], 'dataset_sha256':dataset['sha256'],
        'objective_sha256':plan['objective_sha256'],
        'versions':{p:version(p) for p in ('pymatgen','pymatgen-core','scipy','mp-api')},
        'source_file_hashes':{str(p.relative_to(ROOT)):__import__('hashlib').sha256(p.read_bytes()).hexdigest()
            for p in (Path(__file__),ROOT/'scripts/fetch_environment_dataset.py',
                      ROOT/'interphaise/discovery_evaluator.py',ROOT/'interphaise/tools/thermo_dataset.py')},
        'results_sha256':{p['environment_id']:p['sha256'] for p in packages},
        'combination_count':sum(len(p['results']) for p in packages),
        'elapsed_seconds':time.monotonic()-started, 'llm_calls':0, 'mlip_calls':0,
        'original_v3_comparison':replay, 'independent_qhull_checks':crosscheck,
        'cross_environment_comparisons':compare_environments(packages),
        'limitations':plan['limitations'], 'ready_for_llm_runs':False})
    print(json.dumps({'summary_sha256':summary['sha256'], 'original_replay':replay['passed'],
                      'qhull_checks':crosscheck['passed'], 'elapsed_seconds':summary['elapsed_seconds']}))


if __name__ == '__main__':
    main()
