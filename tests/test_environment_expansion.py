import pytest
from pymatgen.core import Lattice, Structure

from scripts.prepare_environment_expansion import audit_coverage, select_endpoint
from interphaise.tools.thermo_dataset import canonical_id, required_systems


def example():
    pool = {'candidates': [{'candidate_id': 'mp-1', 'material_id': 'mp-1', 'formula': 'LiF'}]}
    environment = {'environment_id': 'synthetic', 'endpoints': {
        'electrode': {'material_id': 'mp-2', 'formula': 'LiCoO2'},
        'electrolyte': {'material_id': 'mp-3', 'formula': 'Li3InCl6'},
    }}
    required = set(required_systems(pool, 'LiCoO2', 'Li3InCl6'))
    known = {canonical_id(mid) for mid in ['mp-1', 'mp-2', 'mp-3']}
    return pool, environment, required, known


def test_present_endpoints_do_not_mask_missing_competing_phase_system():
    pool, environment, required, known = example()
    missing = 'Cl-F-In-Li'
    assert missing in required
    report = audit_coverage(pool, environment, required - {missing}, known)
    assert report['missing_systems'] == [missing]
    assert report['candidates_with_complete_ids_and_query_coverage'] == 0


def test_queried_systems_do_not_substitute_for_missing_pinned_id():
    pool, environment, required, known = example()
    known.remove(canonical_id('mp-1'))
    report = audit_coverage(pool, environment, required, known)
    assert report['missing_system_count'] == 0
    assert report['coating_ids_present'] == 0
    assert report['candidates_with_complete_ids_and_query_coverage'] == 0


def test_missing_endpoint_blocks_every_candidate_and_complete_queries_count():
    pool, environment, required, known = example()
    report = audit_coverage(pool, environment, required, known - {canonical_id('mp-3')})
    assert report['missing_endpoint_ids'] == ['mp-3']
    assert report['candidates_with_complete_ids_and_query_coverage'] == 0
    # A query with no entries is still a completed chemical-system query.
    assert audit_coverage(pool, environment, required, known)[
        'candidates_with_complete_ids_and_query_coverage'] == 1


def test_endpoint_requires_matching_formula_and_ordered_structure():
    disordered = Structure(Lattice.cubic(6), [{'Li': .5}, 'F'], [[0, 0, 0], [.5, .5, .5]])
    source = {'documents': [{'formula_pretty': 'LiF2', 'material_id': 'mp-1',
                           'energy_above_hull': 0., 'structure': disordered.as_dict()}]}
    with pytest.raises(ValueError, match='No ordered endpoint'):
        select_endpoint(source, 'LiF2')
    source['documents'][0]['formula_pretty'] = 'LiF'
    with pytest.raises(ValueError, match='formula/structure mismatch'):
        select_endpoint(source, 'LiF')
