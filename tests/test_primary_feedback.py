"""Feedback bundle gates: completeness, comparability and arithmetic (SYNC_CLAUDE_10.md)."""
import json
import shutil
from pathlib import Path

import pytest
from ase.io import read

from scripts.build_primary_feedback import FeedbackError, assemble

ROOT = Path(__file__).resolve().parents[1]
SHA = '3f52e97c459b2a28a94fc49b8a2f9a92551231a0ea4f5b5db2396f12d8ffa1e9'
SOURCES = {('cathode', 'R1'): 'data/petmad/niflheim_batch1/cathode_ref',
           ('cathode', 'R2'): 'data/petmad/niflheim_batch1/cathode_reg_sixth_0',
           ('cathode', 'R3'): 'data/petmad/niflheim_batch1/cathode_reg_third_third',
           ('electrolyte', 'R1'): 'data/petmad/niflheim_batch1/electrolyte_seed0_ref',
           ('electrolyte', 'R2'): 'data/petmad/final_checks_v1/electrolyte_reg_0_0.5'}
OFFSETS = {('cathode', 'R1'): [0, 0], ('cathode', 'R2'): [1 / 6, 0], ('cathode', 'R3'): [1 / 3, 1 / 3],
           ('electrolyte', 'R1'): [0, 0], ('electrolyte', 'R2'): [0, 0.5]}


def expected(run):
    r = json.loads((run / 'result.json').read_text())
    atoms = read(run / 'interface/final.extxyz')
    fixed = r['relaxations']['interface']['fixed_atom_indices']
    species = sorted({atoms[i].symbol for i in fixed})
    return {'candidate': {k: r['selected']['candidate'][k] for k in ('pair', 'film_miller', 'substrate_miller', 'termination')},
            'n_atoms': len(atoms), 'area_A2': r['area_A2'], 'formula': atoms.get_chemical_formula(),
            'n_fixed': len(fixed), 'fixed_species': {s: [atoms[i].symbol for i in fixed].count(s) for s in species}}


@pytest.fixture
def setup(tmp_path):
    runs = {}
    for key, src in SOURCES.items():
        dest = tmp_path / f'{key[0]}_{key[1]}'
        shutil.copytree(ROOT / src, dest)
        runs[key] = dest
    manifest = {'protocol': {'checkpoint_sha256': SHA, 'force_target_eV_A': 0.05, 'step_limit': 400},
                'coatings': {'mp-aaacjjwh': {'formula': 'LiNbF6', 'sensitivity': {'thickness_increment': 'pending'},
                    'contacts': {c: {'expected': expected(runs[(c, 'R1')]),
                                     'registries': [{'id': rid, 'offset': OFFSETS[(c, rid)], 'gap_A': 2.0}
                                                    for (cc, rid) in SOURCES if cc == c]}
                                 for c in ('cathode', 'electrolyte')}}}}
    return manifest, runs


def supplied(runs, skip=()):
    return [(key, str(path)) for key, path in runs.items() if key not in skip]


def test_complete_valid_set_reproduces_reviewed_values(setup):
    manifest, runs = setup
    b = assemble(manifest, 'mp-aaacjjwh', supplied(runs))
    assert b['consumable_by_agent'] and not b['observed_failures']
    assert b['contacts']['cathode']['selected']['registry_id'] == 'R3'
    assert b['contacts']['cathode']['selected']['W_adh_J_m2'] == pytest.approx(3.61705, abs=1e-5)
    assert b['contacts']['electrolyte']['selected']['W_adh_J_m2'] == pytest.approx(1.63339, abs=1e-5)
    assert b['summary']['weaker_contact'] == 'electrolyte'
    assert b['costs']['new_jobs'] == 5 and b['costs']['separation_single_points'] == 10


def test_missing_registry_is_pending_and_bundle_not_consumable(setup):
    manifest, runs = setup
    b = assemble(manifest, 'mp-aaacjjwh', supplied(runs, skip={('cathode', 'R2'), ('cathode', 'R3')}))
    assert not b['consumable_by_agent'] and b['summary']['weaker_contact'] == 'unresolved'
    assert b['contacts']['cathode']['n_pending'] == 2 and b['costs']['pending_jobs'] == 2


def test_unplanned_and_duplicate_runs_are_refused(setup):
    manifest, runs = setup
    with pytest.raises(FeedbackError, match='not a planned'):
        assemble(manifest, 'mp-aaacjjwh', supplied(runs) + [(('cathode', 'R9'), str(runs[('cathode', 'R1')]))])
    with pytest.raises(FeedbackError, match='duplicate'):
        assemble(manifest, 'mp-aaacjjwh', supplied(runs) + [(('cathode', 'R1'), str(runs[('cathode', 'R2')]))])


def test_mislabelled_contact_fails_and_cannot_win_selection(setup):
    manifest, runs = setup
    runs[('cathode', 'R2')] = runs[('electrolyte', 'R1')]   # electrolyte run passed off as a cathode registry
    del runs[('electrolyte', 'R1')]
    b = assemble(manifest, 'mp-aaacjjwh', supplied(runs))
    r2 = next(r for r in b['contacts']['cathode']['registries'] if r['registry_id'] == 'R2')
    assert r2['status'] == 'failed' and r2['W_adh_J_m2'] is None
    assert b['contacts']['cathode']['selected']['registry_id'] == 'R3'


def test_tampered_stored_values_are_rejected(setup):
    manifest, runs = setup
    path = runs[('cathode', 'R1')] / 'result.json'
    data = json.loads(path.read_text()); data['work_of_adhesion_J_m2'] = 999.0; path.write_text(json.dumps(data))
    sep = runs[('cathode', 'R3')] / 'fixed_geometry_separation.json'
    data = json.loads(sep.read_text()); data['W_sep_fixed_geometry_J_m2'] = 9.0; sep.write_text(json.dumps(data))
    b = assemble(manifest, 'mp-aaacjjwh', supplied(runs))
    regs = {r['registry_id']: r for r in b['contacts']['cathode']['registries']}
    assert regs['R1']['status'] == 'failed' and 'recomputed' in regs['R1']['failure']
    assert regs['R3']['status'] == 'valid' and regs['R3']['W_sep_J_m2'] is None
    assert regs['R3']['separation_status'].startswith('invalid')


def test_failed_run_cost_is_kept(setup):
    manifest, runs = setup
    path = runs[('cathode', 'R2')] / 'relaxation_records.json'
    data = json.loads(path.read_text()); data['film']['converged'] = False; path.write_text(json.dumps(data))
    b = assemble(manifest, 'mp-aaacjjwh', supplied(runs))
    r2 = next(r for r in b['contacts']['cathode']['registries'] if r['registry_id'] == 'R2')
    assert r2['status'] == 'failed' and r2['calculator_calls'] == 132
    valid_calls = sum(r['calculator_calls'] for c in b['contacts'].values() for r in c['registries'] if r['status'] == 'valid')
    assert b['costs']['calculator_calls_known'] == valid_calls + 132
