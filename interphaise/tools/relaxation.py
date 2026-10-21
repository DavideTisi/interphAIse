"""Convergence-aware relaxations (fixed-cell and full bulk) and per-calculation accounting."""
from __future__ import annotations
import time
import numpy as np
from ase.calculators.calculator import Calculator, all_changes
from ase.constraints import FixAtoms, FixSymmetry
from ase.filters import FrechetCellFilter
from ase.io import write
from ase.optimize import FIRE
from ase.spacegroup.symmetrize import check_symmetry
from ase.units import GPa


class CountedCalculator(Calculator):
    """Count actual ASE calculator executions, excluding property-cache hits."""
    def __init__(self, calculator):
        super().__init__()
        self.inner = calculator
        self.implemented_properties = calculator.implemented_properties
        self.calls = 0
        self.wall_seconds = 0.0

    def calculate(self, atoms=None, properties=('energy',), system_changes=all_changes):
        super().calculate(atoms, properties, system_changes)
        start = time.monotonic()
        self.calls += 1
        try:
            self.inner.calculate(atoms, properties, system_changes)
            self.results = self.inner.results.copy()
        finally:
            self.wall_seconds += time.monotonic() - start


def relax_record(atoms, calculator, output, *, fixed=(), fmax=.05, steps=300):
    """Return final atoms and an explicit convergence record; never hide exhaustion."""
    output.mkdir(parents=True, exist_ok=True)
    current = atoms.copy()
    current.set_constraint(FixAtoms(indices=list(fixed)) if fixed else [])
    current.calc = calculator
    start = time.monotonic()
    calls = calculator.calls
    initial = float(current.get_potential_energy())
    optimizer = FIRE(current, logfile=str(output/'fire.log'), trajectory=str(output/'relaxation.traj'))
    converged = bool(optimizer.run(fmax=fmax, steps=steps))
    energy = float(current.get_potential_energy())
    forces = current.get_forces()
    raw_forces = current.get_forces(apply_constraint=False)
    finite = bool(np.isfinite(energy) and np.isfinite(forces).all() and np.isfinite(current.positions).all())
    max_force = float(np.linalg.norm(forces, axis=1).max())
    write(output/'final.extxyz', current)
    return current, {'converged': converged and finite and max_force <= fmax,
        'finite': finite, 'steps':optimizer.nsteps,'step_limit':steps,'fmax_target_eV_A':fmax,
        'initial_energy_eV':initial,'final_energy_eV':energy,
        'max_free_force_eV_A':max_force,
        'max_unconstrained_force_eV_A':float(np.linalg.norm(raw_forces,axis=1).max()),
        'fixed_atom_indices':list(fixed),'calculator_calls':calculator.calls-calls,
        'wall_seconds':time.monotonic()-start}


def space_group(atoms, symprec=1e-3):
    data = check_symmetry(atoms, symprec)
    return f'{data.international} ({data.number})' if data else None


def relax_cell_record(atoms, calculator, output, *, fmax=.01, smax_GPa=.05, steps=1000, symmetry=True):
    """Relax positions and lattice; converged only if forces AND stress meet their targets.

    ``symmetry`` keeps the starting space group (FixSymmetry); convergence then uses the
    symmetry-projected forces and stress, and the raw (unprojected) maxima are recorded.
    The optimizer's exit flag is not trusted: FrechetCellFilter scales the stress term by
    the atom count, so the run is restarted with a halved optimizer fmax until both
    criteria hold on the actual forces and stress, or the step budget is spent.
    """
    output.mkdir(parents=True, exist_ok=True)
    current = atoms.copy()
    current.set_constraint(FixSymmetry(current) if symmetry else [])
    current.calc = calculator
    start = time.monotonic()
    calls = calculator.calls
    symprecs = (1e-3, 1e-2, 1e-1)

    def state():
        forces, stress = current.get_forces(), current.get_stress() / GPa
        raw_forces, raw_stress = current.get_forces(apply_constraint=False), current.get_stress(apply_constraint=False) / GPa
        energy = float(current.get_potential_energy())
        return {'energy_eV': energy, 'energy_per_atom_eV': energy/len(current),
                'cell_A': current.cell.array.tolist(), 'cellpar': current.cell.cellpar().tolist(),
                'volume_A3': float(current.get_volume()),
                'max_force_eV_A': float(np.linalg.norm(forces, axis=1).max()),
                'max_raw_force_eV_A': float(np.linalg.norm(raw_forces, axis=1).max()),
                'stress_GPa': stress.tolist(), 'max_abs_stress_GPa': float(np.abs(stress).max()),
                'raw_stress_GPa': raw_stress.tolist(), 'max_abs_raw_stress_GPa': float(np.abs(raw_stress).max()),
                'finite': bool(np.isfinite(energy) and np.isfinite(raw_forces).all() and np.isfinite(raw_stress).all()
                               and np.isfinite(current.cell.array).all()),
                'space_group': {p: space_group(current, p) for p in symprecs}}

    def met(s):
        return s['finite'] and s['max_force_eV_A'] <= fmax and s['max_abs_stress_GPa'] <= smax_GPa

    initial = state()
    write(output/'initial.extxyz', current)
    optimizer = FIRE(FrechetCellFilter(current), logfile=str(output/'fire.log'),
                     trajectory=str(output/'relaxation.traj'))
    optimizer_fmax, rounds, final = fmax, 0, initial
    while not met(final) and optimizer.nsteps < steps and optimizer_fmax >= 1e-4:
        rounds += 1
        optimizer.run(fmax=optimizer_fmax, steps=steps-optimizer.nsteps)
        final = state()
        optimizer_fmax /= 2
    current.set_constraint()
    write(output/'final.extxyz', current)
    return current, {'converged': met(final), 'finite': final['finite'], 'symmetry_constrained': symmetry,
        'steps': optimizer.nsteps, 'step_limit': steps, 'optimizer_rounds': rounds,
        'last_optimizer_fmax': optimizer_fmax*2 if rounds else None,
        'fmax_target_eV_A': fmax, 'smax_target_GPa': smax_GPa, 'n_atoms': len(current),
        'initial': initial, 'final': final,
        'calculator_calls': calculator.calls-calls, 'wall_seconds': time.monotonic()-start}
