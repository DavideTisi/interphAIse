"""Protect scientific geometry and atom labels during viewer export."""
from io import StringIO
import json
from pathlib import Path
import shutil

import numpy as np
import pytest
from ase.constraints import FixAtoms
from ase.io import read

from scripts.build_structure_viewer import build_records

ROOT = Path(__file__).resolve().parents[1]


def test_saved_geometries_round_trip_and_constraints_survive_display_export():
    records = build_records(ROOT / 'data/pools/mp_candidates_v2.json',
                            ROOT / 'data/petmad/linbf6_cathode_pilot_v1')
    assert len(records) == 54
    assert sum(a['fixed'] for a in records[1]['atoms']) == 64
    assert sum(a['group'] == 'film' for a in records[1]['atoms']) == 32
    source = read(ROOT / 'data/petmad/linbf6_cathode_pilot_v1/interface/final.extxyz')
    np.testing.assert_allclose([a['position'] for a in records[1]['atoms']], source.positions)
    for record in records:
        restored = read(StringIO(record['xyz']), format='extxyz')
        assert restored.get_chemical_symbols() == [a['element'] for a in record['atoms']]
        np.testing.assert_allclose(restored.positions, [a['position'] for a in record['atoms']], atol=1e-7)
        np.testing.assert_allclose(restored.cell, record['cell'])
        assert restored.pbc.tolist() == record['pbc']


def test_multiple_contacts_keep_identity_and_geometry_separate():
    pilots = [ROOT / 'data/petmad' / name for name in
              ('linbf6_cathode_pilot_v1', 'linbf6_electrolyte_pilot_v1')]
    records = build_records(ROOT / 'data/pools/mp_candidates_v2.json', pilots)
    assert len(records) == 58
    assert records[1]['contact'] == 'LiCoO2 | LiNbF6'
    assert records[5]['contact'] == 'Li6PS5Cl | LiNbF6'
    assert records[1]['state'] == records[5]['state'] == 'relaxed'
    assert len(records[1]['atoms']) == 224
    assert len(records[5]['atoms']) == 216
    for item in records[4:8]:
        restored = read(StringIO(item['xyz']), format='extxyz')
        source = read(ROOT / 'data/petmad' / item['source'])
        np.testing.assert_allclose(restored.positions, source.positions, atol=1e-7)
        np.testing.assert_allclose(restored.cell, source.cell)
        assert restored.get_chemical_symbols() == source.get_chemical_symbols()

from scripts.build_structure_viewer import (
    build_catalog, candidate_records, interface_records, load_json,
    restore_metadata, write_viewer, evidence_comparisons,
)


@pytest.fixture(scope='module')
def catalog():
    return build_catalog()


def test_expanded_pool_and_endpoints_preserve_identity_without_environment_duplicates(catalog):
    candidates = [r for r in catalog['records'] if r['kind'] == 'candidate']
    assert len(candidates) == len({r['material_id'] for r in candidates}) == 141
    assert all(set(r['environments']) == {'lco_lpscl_4v', 'lco_lic_4v', 'lco_llzo_4v'} for r in candidates)
    assert sum(len(r['pool_sources']) == 2 for r in candidates) == 50
    assert len([r for r in candidates if r['formula_label'] == 'LiZr2(PO4)3']) == 4
    endpoints = [r for r in catalog['records'] if r['kind'] == 'endpoint']
    assert {r['formula_label'] for r in endpoints} == {'LiCoO2', 'Li6PS5Cl', 'Li3InCl6', 'Li7La3Zr2O12'}
    assert all('results' not in r for r in endpoints + candidates)
    assert all(r['environments'] == ['lco_lpscl_4v'] for r in catalog['records'] if r['kind'] == 'interface')
    assert not catalog['summary']['warnings']


def test_nested_runs_use_exact_energies_and_layers_but_builds_have_none(catalog):
    items = {r['id']: r for r in catalog['records']}
    cathode = items['interface:cathode_thickness_v1/run_F4:relaxed']
    electrolyte = items['interface:thickness_v1/run_L4:relaxed']
    assert len(cathode['atoms']) == 696
    assert cathode['layers'] == {'film_layers': 4, 'substrate_layers': 2}
    assert cathode['n_fixed'] == 104
    assert cathode['results']['W_adh_J_m2'] == pytest.approx(3.600135993716124)
    assert cathode['results']['W_sep_J_m2'] == pytest.approx(5.127539830521539)
    assert electrolyte['layers'] == {'film_layers': 2, 'substrate_layers': 4}
    assert electrolyte['n_fixed'] == 38
    assert electrolyte['results']['W_adh_J_m2'] == pytest.approx(1.5317258429078906)
    assert electrolyte['results']['W_sep_J_m2'] == pytest.approx(2.8578983052814912)
    assert sum(r.get('featured', False) for r in items.values()) == 2
    assert all('results' not in r for r in items.values() if r['state'] != 'relaxed')
    built = items['interface:contact_v1_electrolyte_seed4_Cl:initial']
    assert built['seed'] == 4 and built['status'] == 'Built only · no calculation'
    assert not built['n_fixed']
    assert all(r['historical'] for r in items.values() if r.get('pilot', '').startswith('linbf6_'))
    assert any(p['path'].endswith('build_F4/build.json') for p in cathode['provenance'])


def test_final_labels_and_state_local_masks_can_be_recovered_without_changing_geometry():
    run = ROOT / 'data/petmad/cathode_thickness_v1/run_F4'
    initial = read(run / 'initial.extxyz')
    relaxations = load_json(run / 'result.json')['relaxations']
    for state, file in [('relaxed', 'interface'), ('film', 'film'), ('substrate', 'substrate')]:
        saved = read(run / file / 'final.extxyz')
        original_positions = saved.positions.copy()
        del saved.arrays['interface_label']
        saved.set_constraint()
        restored = restore_metadata(saved, initial, state, relaxations)
        np.testing.assert_array_equal(restored.positions, original_positions)
        expected_fixed = relaxations[file]['fixed_atom_indices']
        assert restored.constraints[0].get_indices().tolist() == expected_fixed
        expected_labels = initial.arrays['interface_label'] if file == 'interface' else [file] * len(restored)
        assert restored.arrays['interface_label'].tolist() == list(expected_labels)
    # Global joined indices are not reused on the separated substrate.
    assert relaxations['interface']['fixed_atom_indices'] != relaxations['substrate']['fixed_atom_indices']


def test_mismatched_atom_order_or_constraint_mask_is_rejected():
    run = ROOT / 'data/petmad/cathode_thickness_v1/run_F4'
    initial = read(run / 'initial.extxyz')
    relaxations = load_json(run / 'result.json')['relaxations']
    final = read(run / 'interface/final.extxyz')
    final.numbers[0] = 1
    with pytest.raises(ValueError, match='element order'):
        restore_metadata(final, initial, 'relaxed', relaxations)
    final = read(run / 'interface/final.extxyz')
    final.set_constraint(FixAtoms(indices=[0]))
    with pytest.raises(ValueError, match='constraints disagree'):
        restore_metadata(final, initial, 'relaxed', relaxations)


def test_partial_runs_do_not_publish_adhesion_and_mismatched_separation_is_rejected(tmp_path):
    run = tmp_path / 'run'
    shutil.copytree(ROOT / 'data/petmad/cathode_thickness_v1/run_F4', run)
    (run / 'film/final.extxyz').unlink()
    items = interface_records(run, tmp_path)
    assert all('results' not in r for r in items)
    assert all(r['status'] == 'Incomplete or invalid run' for r in items)
    separation = load_json(run / 'fixed_geometry_separation.json')
    separation['E_interface_eV'] += 1
    (run / 'fixed_geometry_separation.json').write_text(json.dumps(separation))
    with pytest.raises(ValueError, match='does not match this run'):
        interface_records(run, tmp_path)


def test_same_formula_is_not_deduplicated_and_changed_geometry_keeps_a_snapshot(tmp_path):
    original = load_json(ROOT / 'data/pools/mp_candidates_v2.json')['candidates'][0]
    second = json.loads(json.dumps(original))
    second['candidate_id'] = 'same-formula-different-id'
    third = json.loads(json.dumps(original))
    third['structure']['sites'][0]['abc'][0] += 0.01
    paths = []
    for i, candidate in enumerate([original, second, third]):
        path = tmp_path / f'pool{i}.json'
        path.write_text(json.dumps({'candidates': [candidate]}))
        paths.append(path)
    items = candidate_records(paths + paths[:1], root=tmp_path)
    assert len(items) == 3
    assert len({r['id'] for r in items}) == 3
    assert len(items[0]['pool_sources']) == 2


def test_bulk_references_keep_original_and_relaxed_states_and_excluded_seed(catalog):
    items = {r['id']: r for r in catalog['records'] if r['kind'] == 'reference'}
    assert len(items) == 40
    assert items['bulk:Li6PS5Cl:stability_check:relaxed']['reference_role'] == 'Selected seed-0 reference'
    assert items['multistart:Li6PS5Cl:4:relaxed']['reference_role'] == 'Selected alternative reference'
    assert 'Unconverged' in items['multistart:LiZr2(PO4)3:5:relaxed']['status']
    assert all('results' not in r for r in items.values())


def test_export_roundtrips_all_saved_coordinates_masks_and_escapes_html(catalog, tmp_path):
    for item in catalog['records']:
        restored = read(StringIO(item['xyz']), format='extxyz')
        np.testing.assert_allclose(restored.positions, [a['position'] for a in item['atoms']], atol=1e-7)
        np.testing.assert_allclose(restored.cell, item['cell'])
        assert restored.get_chemical_symbols() == [a['element'] for a in item['atoms']]
        fixed = {int(i) for c in restored.constraints if isinstance(c, FixAtoms) for i in c.get_indices()}
        assert fixed == {i for i, a in enumerate(item['atoms']) if a['fixed']}
    hostile = {'records': [{'title': '</script><script>alert(1)</script>&'}], 'summary': {}, 'environments': {}}
    output = tmp_path / 'viewer.html'
    write_viewer(hostile, output)
    html = output.read_text()
    assert '</script><script>alert(1)' not in html
    assert '\\u003c/script\\u003e' in html
    assert '__STRUCTURES_JSON__' not in html and '__CATALOG_JSON__' not in html
    assert '<script src=' not in html and 'fetch(' not in html


def test_latest_committed_electrolyte_setting_replaces_only_the_shortcut(catalog):
    items = {r['id']: r for r in catalog['records']}
    current = items['interface:niflheim_batch1/electrolyte_seed0_ref:relaxed']
    cpu = items['interface:thickness_gaps_v1/run_electrolyte_S4_F4:relaxed']
    baseline = items['interface:thickness_v1/run_L4:relaxed']
    assert current['featured'] and not baseline['featured'] and not cpu['featured']
    assert len(current['atoms']) == 880 and current['n_fixed'] == 38
    assert current['layers'] == {'film_layers': 4, 'substrate_layers': 4}
    assert current['results']['W_adh_J_m2'] == pytest.approx(1.6333940812860246)
    assert current['results']['W_sep_J_m2'] == pytest.approx(2.9672197308623063)
    assert current['device'] == 'cuda'
    assert cpu['results']['W_adh_J_m2'] == pytest.approx(1.6329358066032293)
    assert len(baseline['atoms']) == 544 and baseline['results']['W_adh_J_m2'] == pytest.approx(1.5317258429078906)


def test_selected_registry_and_seed_comparison_match_exact_archives(catalog):
    items = {r['id']: r for r in catalog['records']}
    cathode = items['interface:niflheim_batch1/cathode_reg_third_third:relaxed']
    old = items['interface:cathode_thickness_v1/run_F4:relaxed']
    assert cathode['featured'] and not old['featured']
    assert cathode['registry']['offset'] == pytest.approx([1 / 3, 1 / 3])
    assert 'registry (1/3, 1/3)' in cathode['title']
    assert len(cathode['atoms']) == 696 and cathode['n_fixed'] == 104
    assert cathode['layers'] == {'film_layers': 4, 'substrate_layers': 2}
    assert cathode['results']['W_adh_J_m2'] == pytest.approx(3.6170508624496)
    assert cathode['results']['W_sep_J_m2'] == pytest.approx(5.167624545488891)
    comparisons = {c['id']: c for c in catalog['comparisons']}
    assert len(comparisons) == 4
    seeds = comparisons['electrolyte_seeds']
    left, right = (items[seeds[k]] for k in ('left', 'right'))
    assert (left['seed'], right['seed']) == (0, 4)
    assert (left['n_fixed'], right['n_fixed']) == (38, 36)
    assert left['results']['area_A2'] != right['results']['area_A2']
    assert right['results']['W_adh_J_m2'] == pytest.approx(1.5120118610940148)
    assert seeds['delta_right_minus_left']['W_adh_J_m2'] == pytest.approx(-0.1213822201920098)
    assert seeds['delta_right_minus_left']['W_sep_J_m2'] == pytest.approx(-0.1618563421082997)
    assert 'not an isolated disorder effect' in seeds['note']
    # A partial catalogue must not substitute a different seed/cell for missing evidence.
    partial = [r for r in catalog['records'] if r['run'] != 'niflheim_batch1/electrolyte_seed4']
    assert 'electrolyte_seeds' not in {c['id'] for c in evidence_comparisons(partial)}
