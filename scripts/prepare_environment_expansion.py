#!/usr/bin/env python3
"""Prepare an offline, unscored expansion and audit competing-phase data coverage.

No APIs, LLMs, energy calculations or automatic benchmark freeze. Existing data
are never relabelled as a complete phase diagram for an expanded chemical system.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pymatgen.core import Composition, Structure
from scripts.build_candidate_pool import select_pool
from interphaise.tools.thermo_dataset import (
    canonical_id, digest, load_entries, required_systems, verify_hash,
)


def select_endpoint(snapshot, formula):
    """Outcome-independent ordered endpoint selection within the cached snapshot.

    The summary cache has its own near-hull prefilter: this is not a claim to have
    searched every MP polymorph, nor proof of the experimentally conductive phase.
    """
    target = Composition(formula).fractional_composition
    eligible = []
    for doc in snapshot['documents']:
        if Composition(doc['formula_pretty']).fractional_composition != target:
            continue
        structure = Structure.from_dict(doc['structure'])
        hull = doc.get('energy_above_hull')
        if structure.composition.fractional_composition != target:
            raise ValueError('Endpoint formula/structure mismatch')
        if structure.is_ordered and hull is not None and math.isfinite(hull):
            eligible.append(doc)
    if not eligible:
        raise ValueError(f'No ordered endpoint in cached summary for {formula}')
    return min(eligible, key=lambda doc: (doc['energy_above_hull'], doc['material_id']))


def endpoint_record(doc, *, source, phase_review_required):
    structure = Structure.from_dict(doc['structure'])
    return {
        'material_id': canonical_id(doc['material_id']),
        'formula': structure.composition.reduced_formula,
        'structure': structure.as_dict(),
        'summary_energy_above_hull_eV_atom': doc.get('energy_above_hull'),
        'ordered': structure.is_ordered,
        'primitive_nsites': len(structure.get_primitive_structure()),
        'space_group': list(structure.get_space_group_info()),
        'source': source,
        'phase_review_required': phase_review_required,
        'origins': doc.get('origins', []),
    }


def audit_coverage(pool, environment, covered_systems, known_material_ids):
    """Audit queried chemical systems AND exact IDs; zero rows is not zero energy.

    A cached query returning no entries still counts as queried. This checks data
    coverage at the recorded MP version, not completeness of experimental chemistry.
    Exact structure matching and energy compatibility validation remain mandatory.
    """
    endpoints = environment['endpoints']
    electrode, electrolyte = (endpoints[r]['formula'] for r in ('electrode', 'electrolyte'))
    missing_endpoints = [endpoints[r]['material_id'] for r in ('electrode', 'electrolyte')
                         if canonical_id(endpoints[r]['material_id']) not in known_material_ids]
    rows = []
    all_required = set()
    for candidate in pool['candidates']:
        required = set(required_systems({'candidates': [candidate]}, electrode, electrolyte))
        all_required.update(required)
        missing = sorted(required - covered_systems)
        present = canonical_id(candidate['material_id']) in known_material_ids
        rows.append({
            'candidate_id': candidate['candidate_id'], 'formula': candidate['formula'],
            'pinned_coating_id_present': present,
            'missing_endpoint_ids': missing_endpoints,
            'missing_system_count': len(missing),
            'all_required_systems_queried': not missing,
            'ids_and_query_coverage_complete': present and not missing_endpoints and not missing,
        })
    return {
        'environment_id': environment['environment_id'],
        'required_system_count': len(all_required),
        'missing_systems': sorted(all_required - covered_systems),
        'missing_system_count': len(all_required - covered_systems),
        'missing_endpoint_ids': missing_endpoints,
        'candidate_count': len(rows),
        'coating_ids_present': sum(r['pinned_coating_id_present'] for r in rows),
        'candidates_with_complete_ids_and_query_coverage': sum(
            r['ids_and_query_coverage_complete'] for r in rows),
        'candidates': rows,
    }


def write_hashed(path, data):
    data = deepcopy(data)
    data.pop('sha256', None)
    data['sha256'] = digest(data)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + '\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--snapshot', type=Path, default=ROOT/'runs/mp_pool_snapshot.json')
    ap.add_argument('--dataset', type=Path, default=ROOT/'data/thermo/mp_gga_v2.json.gz')
    ap.add_argument('--original-pool', type=Path, default=ROOT/'data/pools/mp_candidates_v2.json')
    ap.add_argument('--benchmark', type=Path, default=ROOT/'data/benchmarks/coating_v3.json')
    ap.add_argument('--output', type=Path, default=ROOT/'data/exploration/environment_expansion_v1')
    args = ap.parse_args()
    if args.output.exists():
        ap.error('Output exists; use a fresh versioned directory')
    snapshot = json.loads(args.snapshot.read_text())
    original = json.loads(args.original_pool.read_text()); verify_hash(original)
    benchmark = json.loads(args.benchmark.read_text()); verify_hash(benchmark)
    dataset, entries = load_entries(args.dataset)
    if dataset['pool_sha256'] != original['sha256'] or benchmark['pool_sha256'] != original['sha256']:
        ap.error('Original pool provenance mismatch')
    if benchmark['dataset_sha256'] != dataset['sha256']:
        ap.error('Original benchmark/dataset mismatch')
    pool = select_pool(snapshot, size=None, seed=original['seed'])
    original_ids = {c['candidate_id'] for c in original['candidates']}
    if not original_ids <= {c['candidate_id'] for c in pool['candidates']}:
        ap.error('Expanded snapshot does not preserve all original candidates')
    electrode = endpoint_record(dataset['endpoints']['electrode'], source='frozen v3 endpoint',
                                phase_review_required=False)
    electrolytes = [
        ('lco_lpscl_4v', 'sulfide', endpoint_record(dataset['endpoints']['electrolyte'],
         source='frozen v3 ordered approximant', phase_review_required=False)),
        ('lco_lic_4v', 'chloride', endpoint_record(select_endpoint(snapshot, 'Li3InCl6'),
         source='lowest-summary-hull ordered record in cached snapshot', phase_review_required=True)),
        ('lco_llzo_4v', 'oxide', endpoint_record(select_endpoint(snapshot, 'Li7La3Zr2O12'),
         source='lowest-summary-hull ordered record in cached snapshot', phase_review_required=True)),
    ]
    environments = [{'environment_id': name, 'electrolyte_family': family,
                     'voltage_V': benchmark['voltage_V'],
                     'endpoints': {'electrode': electrode, 'electrolyte': endpoint}}
                    for name, family, endpoint in electrolytes]
    plan = {
        'schema_version': 'environment-expansion-plan-v1',
        'status': 'exploratory-preparation-not-frozen',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'original_benchmark_sha256': benchmark['sha256'],
        'original_pool_sha256': original['sha256'],
        'pool_sha256': pool['sha256'], 'existing_dataset_sha256': dataset['sha256'],
        'source_snapshot_sha256': hashlib.sha256(args.snapshot.read_bytes()).hexdigest(),
        'source_snapshot_retrieved_at': snapshot['retrieved_at'],
        'existing_dataset_db_version': dataset['db_version'],
        'objective': benchmark['objective'], 'objective_sha256': benchmark['objective_sha256'],
        'candidate_count': len(pool['candidates']),
        'distinct_formula_count': len({c['formula'] for c in pool['candidates']}),
        'original_candidate_count': len(original_ids),
        'combination_count': len(pool['candidates']) * len(environments),
        'environments': environments,
        'no_llm_calls': True, 'no_scores_computed': True,
        'limitations': [
            'Endpoint phase review and complete compatible-energy retrieval precede scoring.',
            'An ordered MP polymorph is not a validation of experimental ion transport.',
            'Voltage is imposed Li chemical potential, not a modeled cathode state of charge.',
            'Existing v3 remains unchanged; this expansion is not independent replication of it.',
            'The score omits Li transport, synthesis, finite-temperature and kinetic effects.',
            'PET-MAD energies must not be inserted into the corrected MP phase diagrams.',
        ],
    }
    covered = {system for batch in dataset['batches'] for system in batch['systems']}
    known = {canonical_id(e.data['material_id']) for e in entries}
    reports = [audit_coverage(pool, environment, covered, known) for environment in environments]
    coverage = {
        'schema_version': 'expansion-coverage-v1', 'status': 'coverage-audit-only-not-scores',
        'pool_sha256': pool['sha256'], 'dataset_sha256': dataset['sha256'],
        'db_version': dataset['db_version'], 'thermo_type': dataset['thermo_type'],
        'existing_queried_system_count': len(covered), 'environments': reports,
        'missing_systems_union': sorted({s for report in reports for s in report['missing_systems']}),
        'missing_coating_ids': sorted(c['material_id'] for c in pool['candidates']
                                     if canonical_id(c['material_id']) not in known),
        'structure_matching_checked': False, 'ready_for_llm_runs': False,
    }
    args.output.mkdir(parents=True)
    write_hashed(args.output/'pool.json', pool)
    write_hashed(args.output/'plan.json', plan)
    write_hashed(args.output/'coverage.json', coverage)
    print(json.dumps({
        'output': str(args.output), 'candidates': plan['candidate_count'],
        'distinct_formulas': plan['distinct_formula_count'], 'combinations': plan['combination_count'],
        'families': dict(Counter(c['family'] for c in pool['candidates'])),
        'missing_systems_union': len(coverage['missing_systems_union']),
        'environments': [{k: r[k] for k in ('environment_id', 'missing_system_count',
                          'missing_endpoint_ids', 'candidates_with_complete_ids_and_query_coverage')}
                         for r in reports],
    }, indent=2))


if __name__ == '__main__':
    main()
