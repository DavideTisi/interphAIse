"""Versioned corrected MP entries, independent of legacy formula caches."""
from __future__ import annotations

from itertools import combinations
import gzip
import hashlib
import json
from pathlib import Path

from pymatgen.core import Composition
from pymatgen.entries.computed_entries import ComputedStructureEntry

THERMO_TYPE = 'GGA_GGA+U'


def digest(data):
    # Normalize JSON keys first: integer histogram bins become strings on disk.
    normalized = json.loads(json.dumps(data, allow_nan=False))
    return hashlib.sha256(json.dumps(normalized, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def verify_hash(data):
    body = {k:v for k,v in data.items() if k != 'sha256'}
    if data.get('sha256') != digest(body):
        raise ValueError('Dataset hash mismatch')


def canonical_id(value):
    # MP now serves alpha IDs as aliases for legacy numeric identifiers.
    from emmet.core.mpid import AlphaID
    return AlphaID(str(value)).string


def required_systems(pool, electrode, electrolyte):
    """Every subsystem of either contact; no phases requiring all three layers.

    Such phases cannot occur on a two-reactant tie line because their extra
    elements have zero inventory. Query each subsystem just once.
    """
    systems = set()
    for candidate in pool['candidates']:
        for endpoint in (electrode, electrolyte):
            els = sorted({str(e) for f in (candidate['formula'],endpoint)
                          for e in Composition(f).elements} | {'Li'})
            for size in range(1,len(els)+1):
                systems.update('-'.join(items) for items in combinations(els,size))
    return sorted(systems)


def resolve_entry(entries, material_id, structure=None):
    """No formula fallback: resolve exact material ID and optional structure."""
    from pymatgen.analysis.structure_matcher import StructureMatcher
    target = canonical_id(material_id)
    matches = [e for e in entries if canonical_id(e.data['material_id']) == target]
    if not matches:
        raise ValueError(f'No {THERMO_TYPE} entry for pinned material {target}')
    if structure is not None:
        matcher = StructureMatcher()
        matches = [e for e in matches if matcher.fit(structure,e.structure)]
        if not matches:
            raise ValueError(f'Pinned structure does not match thermo entry {target}')
    return min(matches,key=lambda e:(e.energy_per_atom,str(e.entry_id)))


def load_entries(path):
    path = Path(path)
    if path.suffix == '.gz':
        with gzip.open(path, 'rt') as stream:
            data = json.load(stream)
    else:
        data = json.loads(path.read_text())
    verify_hash(data)
    if data['thermo_type'] != THERMO_TYPE:
        raise ValueError('Only corrected GGA/GGA+U is supported')
    for entry in data['entries']:
        if entry.get('data', {}).get('thermo_type') != THERMO_TYPE:
            raise ValueError('Entry thermo type does not match dataset')
        if entry.get('data', {}).get('run_type') not in {'GGA', 'GGA_U', 'GGA+U'}:
            raise ValueError('Unexpected calculation functional')
    return data, [ComputedStructureEntry.from_dict(e) for e in data['entries']]


def serialize_entry(entry):
    """Normalize MP typed identifiers/Element dictionary keys without energy edits."""
    from monty.json import MontyEncoder
    def keys(value):
        if isinstance(value,dict):
            return {str(k):keys(v) for k,v in value.items()}
        if isinstance(value,(list,tuple)):
            return [keys(v) for v in value]
        return value
    # Construct a plain CSE to avoid mutating client objects or their hash keys.
    data=keys(entry.data)
    for field in ('material_id','task_id','thermo_type'):
        if field in data:
            data[field]=str(data[field])
    clone=ComputedStructureEntry(entry.structure,entry.uncorrected_energy,
        energy_adjustments=entry.energy_adjustments, parameters=keys(entry.parameters),
        data=data,entry_id=str(entry.entry_id))
    if abs(clone.energy-entry.energy)>1e-9:
        raise ValueError('Serialization changed corrected energy')
    return json.loads(json.dumps(clone.as_dict(),cls=MontyEncoder))
