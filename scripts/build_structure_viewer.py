#!/usr/bin/env python3
"""Build a self-contained offline catalogue of saved structures; never calls APIs or MLIPs."""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
from io import StringIO
import json
from pathlib import Path

import numpy as np
from ase.constraints import FixAtoms
from ase.data import covalent_radii
from ase.data.colors import jmol_colors
from ase.io import read, write
from pymatgen.core import Structure
from pymatgen.io.ase import AseAtomsAdaptor

ROOT = Path(__file__).resolve().parents[1]
ENVIRONMENTS = {
    'lco_lpscl_4v': 'Sulfide · LiCoO2 / Li6PS5Cl',
    'lco_lic_4v': 'Chloride · LiCoO2 / Li3InCl6',
    'lco_llzo_4v': 'LLZO · LiCoO2 / Li7La3Zr2O12',
}
STUDIES = {
    'cathode_thickness_v1': 'Cathode coating thickness',
    'thickness_v1': 'Electrolyte thickness / constraints',
    'constraint_test_v1': 'Initial constraint study',
    'thickness_gaps_v1': 'Additional thickness checks',
    'bulk_relaxation_v1': 'Bulk relaxation',
    'bulk_multistart_v1': 'Bulk multistart',
    'final_checks_v1': 'Final geometry checks',
    'niflheim_batch1': 'Niflheim · registries and bulk references',
}
# Explicit selections reviewed in SYNC_CLAUDE_7.md, not an automatic energy ranking.
# Retain earlier references only as fallbacks for partial/older checkouts.
WORKING_CONTACTS = (
    ('niflheim_batch1/cathode_reg_third_third', 'cathode_thickness_v1/run_F4'),
    ('niflheim_batch1/electrolyte_seed0_ref', 'thickness_gaps_v1/run_electrolyte_S4_F4', 'thickness_v1/run_L4'),
)
COMPARISONS = (
    ('cathode_registry', 'Cathode · reference → selected registry',
     'niflheim_batch1/cathode_ref', 'niflheim_batch1/cathode_reg_third_third',
     'Selected by the lowest relaxed joined energy among three sampled distinct registries, not a full registry search. Earlier thickness and constraint brackets used (0, 0).'),
    ('cathode_alternative', 'Cathode · alternative → selected registry',
     'niflheim_batch1/cathode_reg_sixth_0', 'niflheim_batch1/cathode_reg_third_third',
     'Two distinct sampled registries in the same matched cell. Neither the unrelaxed ordering nor a small energy spread establishes polar-surface accuracy.'),
    ('electrolyte_seeds', 'Electrolyte · seed 0 → seed 4',
     'niflheim_batch1/electrolyte_seed0_ref', 'niflheim_batch1/electrolyte_seed4',
     'Same mapped Cl cut and layer/depth rules, but bulk arrangement, cell, area, strain, matching basis and fixed-atom count differ. Registry (0, 0) need not represent the same physical alignment. This is combined construction sensitivity, not an isolated disorder effect or error bar.'),
    ('electrolyte_registry', 'Electrolyte · reference → alternate registry (CPU)',
     'thickness_gaps_v1/run_electrolyte_S4_F4', 'final_checks_v1/electrolyte_reg_0_0.5',
     'Seed 0 in the same cell: adhesion is similar, but fixed-geometry separation is more sensitive. Keep this registry comparison separate from the two-seed comparison.'),
)


def offset_label(offset):
    def component(value):
        fraction = Fraction(float(value)).limit_denominator(12)
        return str(fraction) if abs(float(fraction) - value) < 1e-8 else f'{value:.4g}'
    return '(' + ', '.join(component(v) for v in offset) + ')'


def evidence_comparisons(records):
    """Publish comparisons only when both exact, valid relaxed archives exist."""
    runs = {r['run']: r for r in records if r.get('results')}
    comparisons = []
    for key, label, left_run, right_run, note in COMPARISONS:
        if left_run not in runs or right_run not in runs:
            continue
        left, right = runs[left_run], runs[right_run]
        delta = {metric: right['results'][metric] - left['results'][metric]
                 for metric in ('W_adh_J_m2', 'W_sep_J_m2')
                 if left['results'].get(metric) is not None and right['results'].get(metric) is not None}
        comparisons.append(dict(id=key, label=label, left=left['id'], right=right['id'],
                                note=note, delta_right_minus_left=delta))
    return comparisons


def load_json(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def source(path, root=ROOT):
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return path.name  # A portable export must not expose the owner's home directory.


def provenance(path, root=ROOT):
    return {'path': source(path, root), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def record(atoms, title, source, kind):
    wrapped = atoms.copy()
    wrapped.wrap(pbc=(bool(atoms.pbc[0]), bool(atoms.pbc[1]), False))
    fixed = set()
    for constraint in atoms.constraints:
        if isinstance(constraint, FixAtoms):
            fixed.update(int(i) for i in constraint.get_indices())
    xyz = StringIO()
    # Downloads contain saved coordinates and verified labels/masks, never calculator results.
    write(xyz, atoms, format='extxyz', write_results=False)
    return {
        'title': title, 'source': source, 'kind': kind,
        'formula': atoms.get_chemical_formula(), 'cell': atoms.cell.array.tolist(),
        'pbc': atoms.pbc.tolist(), 'xyz': xyz.getvalue(), 'n_fixed': len(fixed),
        'atoms': [dict(element=s, position=p.tolist(), wrapped_position=wrapped.positions[i].tolist(),
                       color='#' + ''.join(f'{round(float(c)*255):02x}' for c in jmol_colors[z]),
                       radius=float(covalent_radii[z]), group=str(group), fixed=i in fixed)
                  for i, (s, z, p, group) in enumerate(zip(
                      atoms.get_chemical_symbols(), atoms.numbers, atoms.positions,
                      atoms.arrays.get('interface_label', ['bulk'] * len(atoms))))],
    }


def same_order(first, second):
    return np.array_equal(first.numbers, second.numbers)


def restore_metadata(atoms, initial, state, relaxations):
    """Use this run's ordered initial geometry and this state's local constraint indices."""
    labels = initial.arrays.get('interface_label')
    expected = initial
    if state in ('film', 'substrate'):
        if labels is None:
            raise ValueError('cannot verify separated-slab labels without initial interface_label')
        expected = initial[np.asarray(labels) == state]
    if not same_order(atoms, expected):
        raise ValueError(f'{state}: saved element order does not match the initial geometry')
    if not np.allclose(atoms.cell, initial.cell, atol=1e-6):
        raise ValueError(f'{state}: cell does not match this fixed-cell interface run')
    expected_labels = expected.arrays.get('interface_label')
    if expected_labels is not None:
        if 'interface_label' in atoms.arrays and not np.array_equal(atoms.arrays['interface_label'], expected_labels):
            raise ValueError(f'{state}: conflicting interface labels')
        atoms.set_array('interface_label', expected_labels.copy())
    stage = 'interface' if state in ('initial', 'relaxed') else state
    mask = relaxations.get(stage, {}).get('fixed_atom_indices')
    if mask is not None:
        if len(set(mask)) != len(mask) or any(i < 0 or i >= len(atoms) for i in mask):
            raise ValueError(f'{state}: invalid archived constraint mask')
        stored = {int(i) for c in atoms.constraints if isinstance(c, FixAtoms) for i in c.get_indices()}
        if stored and stored != set(mask):
            raise ValueError(f'{state}: stored and archived constraints disagree')
        atoms.set_constraint(FixAtoms(indices=mask))
    return atoms


def study_label(run):
    name = run.split('/')[0]
    if name.startswith('linbf6_'):
        return 'Historical pilots · MP lattices'
    if name.startswith('contact_v1_'):
        return 'Contact construction'
    return STUDIES.get(name, name.replace('_', ' '))


def matched_build(selected, initial, builds):
    """Associate build settings by full selection AND matching saved geometry, never folder name."""
    for directory, saved in builds:
        if saved != selected:
            continue
        other = read(directory / 'initial.extxyz')
        if not (same_order(initial, other) and np.allclose(initial.cell, other.cell, atol=1e-6)):
            continue
        labels = initial.arrays.get('interface_label')
        if labels is None or not np.array_equal(labels, other.arrays.get('interface_label')):
            continue
        # Registry selection translates the film and wraps a/b. Slab-internal
        # coordinates must still agree atom-for-atom modulo the in-plane cell.
        delta = (initial.positions - other.positions) @ np.linalg.inv(initial.cell.array)
        valid = True
        for group in ('film', 'substrate'):
            values = delta[labels == group]
            if not len(values):
                valid = False
                break
            residual = values - values[0]
            residual[:, :2] -= np.round(residual[:, :2])
            if not np.allclose(residual @ initial.cell.array, 0, atol=1e-6):
                valid = False
        if valid:
            return directory
    return None


def interface_records(directory, petmad, builds=(), root=ROOT):
    directory, petmad = directory.resolve(), petmad.resolve()
    result_path, selected_path = directory / 'result.json', directory / 'selected.json'
    result = load_json(result_path) if result_path.exists() else {}
    selected = result.get('selected') or (load_json(selected_path) if selected_path.exists() else {})
    initial_path = directory / 'initial.extxyz'
    if not initial_path.exists() or not selected.get('candidate'):
        return []
    initial = read(initial_path)
    run = source(directory, petmad)
    build_dir = directory if (directory / 'build.json').exists() else matched_build(selected, initial, builds)
    build_path = build_dir / 'build.json' if build_dir else None
    build = load_json(build_path) if build_path and build_path.exists() else {}
    candidate = selected['candidate']
    if candidate.get('n_atoms', len(initial)) != len(initial):
        raise ValueError('selected atom count does not match the initial structure')
    contact = ' | '.join(candidate.get('pair', [])) or directory.name
    settings = build.get('settings', {})
    layers = {k: settings[k] for k in ('film_layers', 'substrate_layers') if k in settings}
    seed = None
    bulk_source = selected.get('substrate_file', '')
    if 'Li6PS5Cl/stability_check/' in bulk_source:
        seed = 0
    elif 'Li6PS5Cl/seed_' in bulk_source:
        seed = int(bulk_source.split('/seed_')[1].split('/')[0])
    relaxations = result.get('relaxations', {})
    relaxation_path = directory / 'relaxation_records.json'
    if not relaxations and relaxation_path.exists():
        relaxations = load_json(relaxation_path)
    complete = bool(result) and all((directory / x / 'final.extxyz').exists() for x in ('interface', 'film', 'substrate'))
    valid = complete and result.get('numerically_valid') is True and all(
        relaxations.get(x, {}).get('converged') is True and relaxations[x].get('finite') is True
        and not relaxations[x].get('overlap_violations')
        and np.isfinite(relaxations[x].get('final_energy_eV', np.nan))
        and relaxations[x].get('max_free_force_eV_A', np.inf) <= relaxations[x].get('fmax_target_eV_A', 0)
        for x in ('interface', 'film', 'substrate'))
    status = 'Converged · provisional' if valid else 'Incomplete or invalid run' if result else 'Built only · no calculation'
    historical = 'pilot_v1' in run
    details = []
    if layers:
        details.append(f"{layers.get('substrate_layers', '?')} substrate + {layers.get('film_layers', '?')} coating layers")
    if seed is not None:
        details.append(f'seed {seed}')
    if result.get('fixed_depth_A') is not None:
        details.append(f"frozen depth {result['fixed_depth_A']:.3f} Å")
    elif result.get('fixed_fraction') is not None:
        details.append(f"fixed fraction {result['fixed_fraction']:g} of substrate z span")
    registry = result.get('best_registry', {})
    if registry.get('offset') is not None:
        details.append(f"registry {offset_label(registry['offset'])}")
    if result.get('device'):
        details.append('GPU' if result['device'].startswith('cuda') else result['device'].upper())
    variant = ' · '.join(details) or directory.name
    metadata_paths = [p for p in (initial_path, result_path, selected_path, build_path, relaxation_path) if p and p.exists()]
    separation_path = directory / 'fixed_geometry_separation.json'
    separation = load_json(separation_path) if separation_path.exists() else {}
    if separation:
        # Rigid separation values must refer to the same model, area and joined energy.
        if not (result and separation.get('checkpoint_sha256') == result.get('checkpoint_sha256')
                and np.isclose(separation['area_A2'], result['area_A2'])
                and np.isclose(separation['E_interface_eV'], relaxations['interface']['final_energy_eV'], rtol=0, atol=1e-6)):
            raise ValueError('rigid-separation record does not match this run')
        for key, stage in [('E_film_relaxed_eV', 'film'), ('E_substrate_relaxed_eV', 'substrate')]:
            if not np.isclose(separation[key], relaxations[stage]['final_energy_eV'], rtol=0, atol=1e-6):
                raise ValueError('rigid-separation slab energies do not match this run')
        if not np.isclose(separation['W_adh_relaxed_J_m2'], result['work_of_adhesion_J_m2'], rtol=0, atol=1e-6):
            raise ValueError('rigid-separation adhesion does not match this run')
        metadata_paths.append(separation_path)
    items = []
    for filename, state, label in [
        ('initial.extxyz', 'initial', 'Initial interface'),
        ('interface/final.extxyz', 'relaxed', 'Relaxed interface'),
        ('film/final.extxyz', 'film', 'Separated coating · relaxed'),
        ('substrate/final.extxyz', 'substrate', 'Separated substrate · relaxed'),
    ]:
        path = directory / filename
        if not path.exists():
            continue
        atoms = restore_metadata(read(path), initial, state, relaxations)
        item = record(atoms, f'{contact} — {variant} — {label}', source(path, petmad), 'interface')
        item.update(id=f'interface:{run}:{state}', contact=contact, pilot=run, run=run,
                    study=study_label(run), state=state, state_label=label, variant=variant,
                    environments=['lco_lpscl_4v'], materials=candidate.get('pair', []),
                    layers=layers, seed=seed, status=status, historical=historical,
                    registry=registry, device=result.get('device'),
                    fixed_depth_A=result.get('fixed_depth_A'), fixed_fraction=result.get('fixed_fraction'),
                    featured=False,
                    candidate=candidate, warnings=selected.get('warnings', []),
                    source_path=source(path, root), provenance=[provenance(path, root)] + [provenance(p, root) for p in metadata_paths if p != path],
                    model=result.get('model'), checkpoint_sha256=result.get('checkpoint_sha256'),
                    metadata_note='Labels verified against this run’s initial atom order; constraints from the matching relaxation record.' if result else 'Build-only geometry; no relaxation constraint or energy is implied.',
                    fixed_origin='Recorded run mask (planned for initial geometry)' if state == 'initial' and result else 'Stored or verified state-local constraint mask')
        if result and state != 'initial':
            stage = 'interface' if state == 'relaxed' else state
            item['relaxation'] = {k: v for k, v in relaxations.get(stage, {}).items() if k != 'fixed_atom_indices'}
        if valid and state == 'relaxed':
            item['results'] = {
                'W_adh_J_m2': result.get('work_of_adhesion_J_m2'),
                'W_sep_J_m2': separation.get('W_sep_fixed_geometry_J_m2'),
                'calculator_calls': result.get('calculator_calls'),
                'area_A2': result.get('area_A2'),
            }
        items.append(item)
    return items


def candidate_records(pools, environments=None, root=ROOT):
    records, seen = [], {}
    environments = environments or {}
    for pool in pools:
        for c in load_json(pool)['candidates']:
            # IDs distinguish polymorphs; a changed snapshot of the same ID is also retained.
            atoms = AseAtomsAdaptor.get_atoms(Structure.from_dict(c['structure']))
            geometry = json.dumps([atoms.numbers.tolist(), atoms.positions.round(7).tolist(), atoms.cell.array.round(7).tolist()])
            key = (c['candidate_id'], hashlib.sha256(geometry.encode()).hexdigest())
            if key in seen:
                seen[key]['pool_sources'].append(source(pool, root))
                seen[key]['provenance'].append(provenance(pool, root))
                continue
            item = record(atoms, f"{c['formula']} · {c['candidate_id']} · MP structure", f"{source(pool, root)} / {c['candidate_id']}", 'candidate')
            item.update(id=f'mp:{key[0]}:{key[1][:12]}', material_id=c['candidate_id'], materials=[c['formula']],
                        formula_label=c['formula'], family=c.get('family'), state='mp', state_label='Original MP structure',
                        study='Candidate pool', environments=environments.get(c['candidate_id'], []),
                        status='Saved MP structure · not PET-MAD relaxed', pool_sources=[source(pool, root)],
                        source_path=source(pool, root), provenance=[provenance(pool, root)],
                        variant=c['candidate_id'], run=f'mp:{key[0]}', contact='', historical=False)
            seen[key] = item
            records.append(item)
    return records


def endpoint_records(dataset, root=ROOT):
    records, seen = [], {}
    for environment in load_json(dataset)['environments']:
        env_id = environment['environment_id']
        for role, endpoint in environment['endpoints'].items():
            mid = endpoint['material_id']
            if mid in seen:
                seen[mid]['environments'].append(env_id)
                continue
            atoms = AseAtomsAdaptor.get_atoms(Structure.from_dict(endpoint['structure']))
            item = record(atoms, f"{endpoint['formula']} · {mid} · {role} endpoint", source(dataset, root), 'endpoint')
            item.update(id=f'endpoint:{mid}', material_id=mid, materials=[endpoint['formula']], formula_label=endpoint['formula'],
                        state='mp', state_label='Original MP endpoint', study='Battery endpoints', environments=[env_id],
                        status='Saved ordered MP endpoint', role=role, variant=mid, run=f'endpoint:{mid}', contact='',
                        source_path=source(dataset, root), provenance=[provenance(dataset, root)],
                        metadata_note=endpoint.get('source', ''), historical=False)
            seen[mid] = item
            records.append(item)
    return records


def bulk_records(petmad, root=ROOT):
    records = []
    summary_path = petmad / 'bulk_relaxation_v1/summary.json'
    if not summary_path.exists():
        return records
    summary = load_json(summary_path)
    for formula, material in summary['materials'].items():
        for stage, label in [('symmetric', 'Symmetry held'), ('stability_check', 'Symmetry released · seed 0')]:
            for state in ('initial', 'relaxed'):
                path = summary_path.parent / formula / stage / ('initial.extxyz' if state == 'initial' else 'final.extxyz')
                if not path.exists():
                    continue
                info = material[stage]
                suffix = 'initial' if state == 'initial' else 'PET-MAD relaxed'
                item = record(read(path), f'{formula} · {label} · {suffix}', source(path, root), 'reference')
                item.update(id=f'bulk:{formula}:{stage}:{state}', material_id=material['material_id'], materials=[formula],
                            formula_label=formula, state=state, state_label=suffix, study='Bulk relaxation',
                            variant=label, run=f'bulk:{formula}:{stage}', contact='', seed=0 if stage == 'stability_check' else None,
                            status='Converged PET-MAD minimum' if info['converged'] and state == 'relaxed' else 'Initial geometry' if state == 'initial' else 'Unconverged',
                            environments=[], model=summary['model'], checkpoint_sha256=summary['checkpoint_sha256'],
                            provenance=[provenance(path, root), provenance(summary_path, root)], source_path=source(path, root), historical=False,
                            metadata_note='Local PET-MAD reference, not an established experimental phase. IDs are those recorded by the bulk study.')
                if stage == 'stability_check' and formula in ('Li6PS5Cl', 'LiZr2(PO4)3') and state == 'relaxed':
                    item['reference_role'] = 'Selected seed-0 reference'
                records.append(item)
    for multi_path in sorted((petmad / 'bulk_multistart_v1').glob('*/multistart.json')):
        multi = load_json(multi_path)
        formula = multi['material']
        for seed, info in multi['seeds'].items():
            if seed == '0':
                continue  # Same geometry is already exported from stability_check above.
            for state in ('initial', 'relaxed'):
                path = multi_path.parent / f'seed_{seed}' / ('initial.extxyz' if state == 'initial' else 'final.extxyz')
                if not path.exists():
                    continue
                suffix = 'initial' if state == 'initial' else 'PET-MAD relaxed'
                item = record(read(path), f'{formula} · seed {seed} · {suffix}', source(path, root), 'reference')
                item.update(id=f'multistart:{formula}:{seed}:{state}', material_id=multi['material_id'], materials=[formula], formula_label=formula,
                            state=state, state_label=suffix, study='Bulk multistart', variant=f'seed {seed}', seed=int(seed),
                            run=f'multistart:{formula}:{seed}', contact='', environments=[],
                            status='Initial geometry' if state == 'initial' else 'Converged PET-MAD minimum' if info['converged'] else 'Unconverged · excluded from references',
                            checkpoint_sha256=multi['checkpoint_sha256'], model=summary['model'],
                            provenance=[provenance(path, root), provenance(multi_path, root)], source_path=source(path, root), historical=False,
                            metadata_note='Independent rattled start. Local minima do not identify an experimental phase.')
                if state == 'relaxed' and (formula, int(seed)) in [('Li6PS5Cl', 4), ('LiZr2(PO4)3', 1)]:
                    item['reference_role'] = 'Selected alternative reference'
                records.append(item)
    return records


def build_records(pool, pilot, extra=()):
    """Compatibility entry point for an explicit pool and one or more saved contacts."""
    pilots = [pilot] if isinstance(pilot, Path) else pilot
    records = []
    for directory in pilots:
        records.extend(interface_records(directory, directory.parent))
    records.extend(candidate_records([pool]))
    for path in extra:
        records.append(record(read(path), path.name, path.name, 'custom'))
    return records


def build_catalog(root=ROOT, pools=None, pilots=None, extra=()):
    petmad = root / 'data/petmad'
    warnings = []
    membership = {}
    tables = sorted((root / 'data/benchmarks/environment_v1').glob('lco_*.json'))
    for path in tables:
        table = load_json(path)
        for row in table['results']:
            membership.setdefault(row['candidate_id'], []).append(table['environment_id'])
    selected_files = sorted(petmad.rglob('selected.json'))
    builds = []
    for path in selected_files:
        if not (path.parent / 'initial.extxyz').exists():
            continue
        try:
            builds.append((path.parent, load_json(path)))
        except (ValueError, OSError) as error:
            warnings.append(f'{source(path, root)}: incomplete build metadata omitted: {error}')
    directories = pilots if pilots is not None else sorted(set([p.parent for p in selected_files] + [p.parent for p in petmad.rglob('result.json')]))
    records = []
    for directory in directories:
        try:
            records.extend(interface_records(directory, petmad, builds, root))
        except (ValueError, KeyError, OSError) as error:
            warnings.append(f'{source(directory, root)}: omitted because provenance/geometry validation failed: {error}')
    default_pools = [root / 'data/exploration/environment_expansion_v1/pool.json', root / 'data/pools/mp_candidates_v2.json']
    records.extend(candidate_records(pools if pools is not None else [p for p in default_pools if p.exists()], membership, root))
    dataset = root / 'data/exploration/environment_expansion_v2/dataset.json.gz'
    if dataset.exists():
        records.extend(endpoint_records(dataset, root))
    else:
        warnings.append('Expanded endpoint structures unavailable: cached environment dataset is missing.')
    references = bulk_records(petmad, root)
    for item in references:
        item['environments'] = membership.get(item['material_id'], [])
        if item['formula_label'] == 'Li6PS5Cl':
            item['environments'] = ['lco_lpscl_4v']
        elif item['formula_label'] == 'LiCoO2':
            item['environments'] = list(ENVIRONMENTS)
    records.extend(references)
    for path in extra:
        item = record(read(path), path.name, path.name, 'custom')
        item.update(id=f'custom:{path.name}', materials=[item['formula']], environments=[], study='Custom', state='custom', state_label='Custom geometry',
                    status='User-supplied geometry', variant=path.name, run=f'custom:{path.name}', contact='', provenance=[provenance(path, root)])
        records.append(item)
    if not records:
        raise ValueError('No saved structures found')
    for order, choices in enumerate(WORKING_CONTACTS):
        selected = next((r for run in choices for r in records if r.get('run') == run and r.get('results')), None)
        if selected:
            selected['featured'] = True
            selected['featured_order'] = order
            selected['working_role'] = ('Selected cathode · lowest sampled joined energy'
                                        if selected['run'] == 'niflheim_batch1/cathode_reg_third_third'
                                        else 'Electrolyte · seed-0 GPU reference'
                                        if selected['run'] == 'niflheim_batch1/electrolyte_seed0_ref'
                                        else 'Earlier reference · latest selected archive unavailable')
    records.sort(key=lambda r: (not r.get('featured', False), r.get('featured_order', 9), r.get('historical', False), r['kind'], r.get('study', ''), r['title']))
    summary = {
        'total': len(records), 'by_kind': dict(Counter(r['kind'] for r in records)),
        'candidate_ids': len({r['material_id'] for r in records if r['kind'] == 'candidate'}),
        'interface_runs': len({r['run'] for r in records if r['kind'] == 'interface'}),
        'calculated_runs': len([r for r in records if r.get('results')]),
        'warnings': warnings,
        'limitations': [
            'No saved atomistic chloride or LLZO contact is available. Their bulk endpoints and candidate structures can be viewed.',
            'Environment membership means inclusion in a thermodynamic benchmark, not an interface calculation or a performance claim.',
            'Both contacts are formally polar and provisional. Current archived settings are the 696-atom cathode at registry (1/3, 1/3) and the 880-atom seed-0 electrolyte at (0, 0); partial checkouts may show a labelled earlier reference.',
            'Final-geometry constraint brackets passed at the reference registries. Cathode thickness and constraint checks used (0, 0), not the newly selected (1/3, 1/3). Three of nine distinct cathode registries were relaxed.',
            'Electrolyte seed-4 shifts exceed the 0.1 J/m² reporting tolerance and combine bulk-reference and interface-construction effects. They are not a statistical error bar or an isolated disorder effect.',
            'Vacuum checks isolate periodic images within the finite-range model; they do not address polar electrostatics. No explicit applied voltage is present in these atomistic calculations.',
            'Historical pilots used different lattices, facets or cuts. Do not compare their energies as a coating ranking.',
            'Only completed result.json archives are associated with energies. Live or JSON-only studies without saved geometries are not added.',
        ],
    }
    return {'records': records, 'summary': summary, 'environments': ENVIRONMENTS,
            'comparisons': evidence_comparisons(records)}


def write_viewer(catalog, output):
    template = (ROOT / 'scripts/viewer/template.html').read_text()
    def safe_json(data):
        return json.dumps(data, allow_nan=False, separators=(',', ':')).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(template.replace('__STRUCTURES_JSON__', safe_json(catalog['records'])).replace('__CATALOG_JSON__', safe_json({k: v for k, v in catalog.items() if k != 'records'})))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pool', type=Path, action='append', help='Override candidate pools; repeat. Default: expanded and original pools, deduplicated by ID and geometry.')
    parser.add_argument('--pilot', type=Path, action='append', help='Restrict contact folders; default: recursively discover saved completed runs and builds.')
    parser.add_argument('--structure', type=Path, action='append', default=[], help='Additional ASE-readable geometry')
    parser.add_argument('--output', type=Path, default=ROOT / 'runs/structure_viewer.html')
    args = parser.parse_args()
    catalog = build_catalog(pools=args.pool, pilots=args.pilot, extra=args.structure)
    write_viewer(catalog, args.output)
    print(f"Wrote {args.output} ({catalog['summary']['total']} structures; {catalog['summary']['candidate_ids']} candidate IDs). Open or share this one HTML file; no server required.")
    for warning in catalog['summary']['warnings']:
        print('WARNING:', warning)


if __name__ == '__main__':
    main()
