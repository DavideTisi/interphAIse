"""Protect scientific geometry and atom labels during viewer export."""
from io import StringIO
from pathlib import Path

import numpy as np
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
