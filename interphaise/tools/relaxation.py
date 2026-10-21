"""Convergence-aware fixed-cell relaxations and per-calculation accounting."""
from __future__ import annotations
import time
import numpy as np
from ase.calculators.calculator import Calculator, all_changes
from ase.constraints import FixAtoms
from ase.io import write
from ase.optimize import FIRE


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
