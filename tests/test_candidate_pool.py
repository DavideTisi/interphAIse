import importlib.util
from pathlib import Path

import pytest
from pymatgen.core import Lattice, Structure

spec = importlib.util.spec_from_file_location('pool_builder', Path(__file__).resolve().parents[1]/'scripts/build_candidate_pool.py')
pool_builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pool_builder)


def snapshot():
    docs = []
    for i, species in enumerate([['Li','O'], ['Li','P','O'], ['Li','B','O'], ['Li','F'], ['Li','Si','O'], ['Li','Fe','O']]):
        structure = Structure(Lattice.cubic(5),species,[[j/len(species)]*3 for j in range(len(species))])
        docs.append({'material_id':f'mp-test{i}', 'formula_pretty':structure.composition.reduced_formula,
                     'structure':structure.as_dict(),'band_gap':0 if i==0 else None,
                     'energy_above_hull':0.01})
    return {'documents':docs,'retrieved_at':'synthetic','requests':[]}


def test_reproducible_pool_preserves_unknown_and_metal():
    source = snapshot()
    pool = pool_builder.select_pool(source,size=5)
    assert pool == pool_builder.select_pool(source,size=5)
    assert len(pool['counts']['families']) == 5
    assert pool['rejected'] == [{'material_id':'mp-test5','reason':'chemical_scope'}]
    assert pool['candidates'][0]['band_gap_eV'] == 0
    assert pool['candidates'][1]['band_gap_eV'] is None
    assert pool['sha256'] != pool_builder.select_pool(source,size=4)['sha256']


def test_small_pool_fails_instead_of_relaxing_filters():
    with pytest.raises(ValueError,match='Only 5'):
        pool_builder.select_pool(snapshot(),size=50)
