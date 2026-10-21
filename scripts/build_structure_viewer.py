#!/usr/bin/env python3
"""Build a self-contained, offline HTML viewer from saved structures (no API calls)."""
import argparse
from io import StringIO
import json
from pathlib import Path

from ase.constraints import FixAtoms
from ase.data import covalent_radii
from ase.data.colors import jmol_colors
from ase.io import read, write
from pymatgen.core import Structure
from pymatgen.io.ase import AseAtomsAdaptor

ROOT = Path(__file__).resolve().parents[1]


def record(atoms, title, source, kind):
    wrapped = atoms.copy()
    wrapped.wrap(pbc=(bool(atoms.pbc[0]), bool(atoms.pbc[1]), False))
    fixed = set()
    for constraint in atoms.constraints:
        if isinstance(constraint, FixAtoms):
            fixed.update(int(i) for i in constraint.get_indices())
    xyz = StringIO()
    # Do not export calculator results: this download is a geometry snapshot.
    write(xyz, atoms, format='extxyz', write_results=False)
    return {
        'title': title, 'source': source, 'kind': kind,
        'formula': atoms.get_chemical_formula(), 'cell': atoms.cell.array.tolist(),
        'pbc': atoms.pbc.tolist(), 'xyz': xyz.getvalue(),
        'atoms': [dict(element=s, position=p.tolist(), wrapped_position=wrapped.positions[i].tolist(),
                       color='#' + ''.join(f'{round(float(c)*255):02x}' for c in jmol_colors[z]),
                       radius=float(covalent_radii[z]), group=str(group), fixed=i in fixed)
                  for i, (s, z, p, group) in enumerate(zip(
                      atoms.get_chemical_symbols(), atoms.numbers, atoms.positions,
                      atoms.arrays.get('interface_label', ['bulk'] * len(atoms))))],
    }


def build_records(pool, pilot, extra=()):
    records = []
    pilots = [pilot] if isinstance(pilot, Path) else pilot
    for directory in pilots:
        metadata_path = directory / 'selected.json'
        metadata = json.loads(metadata_path.read_text()) if metadata_path.exists() else {}
        pair = metadata.get('candidate', {}).get('pair')
        contact = ' | '.join(pair) if pair else directory.name
        for filename, title, state in [
                ('initial.extxyz', 'Interface · initial', 'initial'),
                ('interface/final.extxyz', 'Interface · relaxed', 'relaxed'),
                ('film/final.extxyz', 'Coating slab · relaxed', 'film'),
                ('substrate/final.extxyz', 'Substrate slab · relaxed', 'substrate')]:
            path = directory / filename
            if path.exists():
                item = record(read(path), f'{contact} — {title}',
                              f'{directory.name}/{filename}', 'pilot')
                item.update(contact=contact, pilot=directory.name, state=state)
                records.append(item)
    for c in json.loads(pool.read_text())['candidates']:
        atoms = AseAtomsAdaptor.get_atoms(Structure.from_dict(c['structure']))
        records.append(record(atoms, f"{c['formula']} · {c['candidate_id']}",
                              f"{pool.name} / {c['candidate_id']}", 'bulk'))
    for path in extra:
        records.append(record(read(path), path.name, path.name, 'custom'))
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pool', type=Path, default=ROOT / 'data/pools/mp_candidates_v2.json')
    parser.add_argument('--pilot', type=Path, action='append',
                        help='Pilot directory; repeat to include several. Default: discover saved data/petmad pilots.')
    parser.add_argument('--structure', type=Path, action='append', default=[],
                        help='Additional ASE-readable geometry; repeat for multiple files')
    parser.add_argument('--output', type=Path, default=ROOT / 'runs/structure_viewer.html')
    args = parser.parse_args()
    pilots = args.pilot if args.pilot is not None else sorted(
        p.parent for p in (ROOT / 'data/petmad').glob('*/selected.json'))
    records = build_records(args.pool, pilots, args.structure)
    template = (ROOT / 'scripts/viewer/template.html').read_text()
    # Escape HTML delimiters inside JSON, including user-supplied filenames.
    data = json.dumps(records, allow_nan=False).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(template.replace('__STRUCTURES_JSON__', data))
    print(f'Wrote {args.output} ({len(records)} structures). Open it in a browser; no server required.')


if __name__ == '__main__':
    main()
