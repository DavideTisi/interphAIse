#!/usr/bin/env python3
"""Check orientation sensitivity of the two saved symmetry-breaking energy drops.

Single points only; this neither finds minima nor validates physical phases.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

import numpy as np
from ase.io import read
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bulk', type=Path, default=ROOT/'data/petmad/bulk_relaxation_v1')
    parser.add_argument('--checkpoint', type=Path,
                        default=Path.home()/'.cache/interphaise/pet-mad-s-v1.6.0.ckpt')
    parser.add_argument('--output', type=Path, default=ROOT/'runs/bulk_rotation_check.json')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Output exists; choose a fresh path')
    summary = json.loads((args.bulk/'summary.json').read_text())
    checkpoint_hash = hashlib.sha256(args.checkpoint.read_bytes()).hexdigest()
    if checkpoint_hash != summary['checkpoint_sha256']:
        parser.error('Checkpoint does not match the saved bulk calculation')
    import torch
    from upet.ase import UPETCalculator
    torch.set_num_threads(2)
    calculator = UPETCalculator(checkpoint_path=str(args.checkpoint), device='cpu')
    rotations = [np.eye(3), *Rotation.random(3, random_state=20261021).as_matrix()]
    started = time.monotonic()
    results, calls, inputs = {}, 0, {}
    for formula in ['Li6PS5Cl', 'LiZr2(PO4)3']:
        states = {}
        for state in ['symmetric', 'stability_check']:
            path = args.bulk/formula/state/'final.extxyz'
            inputs[f'{formula}/{state}/final.extxyz'] = hashlib.sha256(path.read_bytes()).hexdigest()
            atoms = read(path)
            energies = []
            for rotation in rotations:
                rotated = atoms.copy()
                rotated.set_constraint()
                rotated.cell = atoms.cell.array @ rotation.T
                rotated.positions = atoms.positions @ rotation.T
                rotated.calc = calculator
                energies.append(float(rotated.get_potential_energy())/len(rotated))
                calls += 1
            if not np.isfinite(energies).all():
                raise ValueError('Nonfinite single-point energy')
            states[state] = {'energy_per_atom_eV': energies,
                            'rotation_range_meV_atom': 1000*(max(energies)-min(energies))}
        differences = 1000*(np.array(states['stability_check']['energy_per_atom_eV'])
                            - np.array(states['symmetric']['energy_per_atom_eV']))
        states['distorted_minus_symmetric_meV_atom'] = differences.tolist()
        results[formula] = states
        print(formula, json.dumps(states), flush=True)
    body = {
        'checkpoint_sha256': checkpoint_hash, 'model': summary['model'],
        'device': 'cpu', 'threads': 2, 'rotation_seed': 20261021,
        'rotations': [r.tolist() for r in rotations], 'single_point_calls': calls,
        'input_file_sha256': inputs,
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'wall_seconds': time.monotonic()-started, 'results': results,
        'limitations': ['Four orientations, not a bound on all rotational error.',
                       'Single-point comparison only; no new relaxation or physical phase validation.'],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(body, indent=2, allow_nan=False)+'\n')


if __name__ == '__main__':
    main()
