import pytest
from pymatgen.core import Lattice, Structure, Element
from pymatgen.entries.computed_entries import ComputedStructureEntry
from interphaise.tools.thermo_dataset import canonical_id, digest, verify_hash, required_systems, serialize_entry, resolve_entry


def test_alpha_id_alias():
    assert canonical_id('mp-aaaaabru')==canonical_id('mp-1138')


def test_hash_detects_changes():
    data={'hello':'world'};data['sha256']=digest(data)
    verify_hash(data)
    data['hello']='changed'
    with pytest.raises(ValueError,match='hash'):verify_hash(data)


def test_systems_include_elemental_references_and_cross_phases():
    systems=required_systems({'candidates':[{'formula':'Li3PO4'}]},'LiCoO2','Li6PS5Cl')
    assert 'Li' in systems and 'Co' in systems and 'Cl-Li-O-P-S' in systems
    assert 'Cl-Co-Li-O-P-S' not in systems  # requires all three layers
    assert len(systems)==len(set(systems))


def test_serialization_preserves_correction_and_normalizes_element_keys():
    structure=Structure(Lattice.cubic(4),['Li','F'],[[0,0,0],[.5,.5,.5]])
    entry=ComputedStructureEntry(structure,-10,correction=-.5,entry_id='mp-1138-GGA',
        data={'material_id':'mp-1138','oxidation_states':{Element('Li'):1}})
    saved=serialize_entry(entry)
    restored=ComputedStructureEntry.from_dict(saved)
    assert restored.energy==pytest.approx(entry.energy)
    assert restored.data['oxidation_states']=={'Li':1}
    assert resolve_entry([restored],'mp-aaaaabru',structure).entry_id=='mp-1138-GGA'
    with pytest.raises(ValueError,match='No GGA'):resolve_entry([restored],'mp-149')


def test_hash_survives_json_roundtrip_with_integer_histogram_keys():
    import json
    data={'bins':{2:5,10:3}}
    data['sha256']=digest(data)
    verify_hash(json.loads(json.dumps(data)))
