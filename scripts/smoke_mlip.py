"""Small real-model check; no API credentials or materials database required."""
import argparse
import json
import sys
import time
from importlib.metadata import version
from pathlib import Path

import numpy as np
from ase.build import bulk
from ase.optimize import FIRE

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from interphaise.tools.mlip import load_mlip


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', default='upet:pet-mad-s@1.6.0')
    parser.add_argument('--device', default='cpu')
    parser.add_argument('--out', type=Path, default=Path('runs/petmad_smoke.json'))
    args = parser.parse_args()
    started = time.monotonic()
    atoms = bulk('Li', 'bcc', a=3.44, cubic=True)
    atoms.positions[0, 0] += 0.05
    atoms.calc = load_mlip(args.model, device=args.device)
    energy_before = float(atoms.get_potential_energy())
    forces = atoms.get_forces()
    stress = atoms.get_stress()
    assert np.isfinite(energy_before) and np.isfinite(forces).all() and np.isfinite(stress).all()
    assert forces.shape == (len(atoms), 3) and stress.shape == (6,)
    optimizer = FIRE(atoms, logfile=None)
    converged = optimizer.run(fmax=0.02, steps=5)
    energy_after = float(atoms.get_potential_energy())
    assert np.isfinite(energy_after) and np.isfinite(atoms.get_forces()).all()
    assert energy_after <= energy_before + 1e-5, 'Short relaxation increased energy'
    result = dict(model=args.model, device=args.device, formula=atoms.get_chemical_formula(),
                  purpose='software smoke test, not scientific validation',
                  packages={p: version(p) for p in ['upet', 'torch', 'ase', 'metatrain']},
                  energy_before_eV=energy_before, energy_after_eV=energy_after,
                  max_initial_force_eV_per_A=float(np.linalg.norm(forces, axis=1).max()),
                  max_final_force_eV_per_A=float(np.linalg.norm(atoms.get_forces(), axis=1).max()),
                  stress_finite=True, relaxation_steps=optimizer.nsteps,
                  converged=bool(converged), elapsed_seconds=time.monotonic()-started)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
