"""Deterministic energetics: registry scan, relaxation, work of adhesion.

W_adh = (E_film + E_substrate - E_interface) / A, with each slab relaxed
separately in the same cell (same vacuum), so k-sampling/cell errors cancel.
Positive W_adh = the two slabs bind. Interface energy gamma_int needs surface
energies and chemical potentials on top of this (TODO, see README).

Every energy evaluation is counted; the "relaxations saved vs brute force"
headline number comes from these counters.
"""

from __future__ import annotations

import copy
import itertools

import numpy as np
from ase.constraints import FixAtoms
from ase.optimize import FIRE
from pymatgen.core.interface import Interface
from pymatgen.io.ase import AseAtomsAdaptor

from ..context import Candidate, EnergeticsResult

EV_PER_A2_TO_J_PER_M2 = 16.0217663


class Counter:
    single_points = 0
    relaxations = 0


def to_atoms(struct):
    atoms = AseAtomsAdaptor.get_atoms(struct)
    atoms.pbc = True
    return atoms


def bottom_fixed_indices(atoms, substrate_indices, fraction: float = 0.34, depth: float | None = None) -> list[int]:
    """Fix the bottom ``fraction`` of the substrate (bulk-like region), or a fixed ``depth`` in Å.

    A fixed depth keeps the frozen region the same when the slab is made thicker.
    """
    sub = np.array(list(substrate_indices))
    z = atoms.positions[sub, 2]
    cut = z.min() + (depth if depth is not None else fraction * (z.max() - z.min()))
    return [int(i) for i in sub[z <= cut + 1e-6]]


def single_point(atoms, calc) -> float:
    atoms = atoms.copy()
    atoms.calc = calc
    Counter.single_points += 1
    return float(atoms.get_potential_energy())


def relax(atoms, calc, fixed: list[int] | None = None, fmax: float = 0.05, steps: int = 300):
    """Relax and report convergence; an exhausted step budget is never silently accepted.

    Returns (atoms, energy, converged). ``converged`` is re-checked on the final free-atom
    forces and finite values, not taken from the optimizer's exit flag alone.
    """
    atoms = atoms.copy()
    if fixed:
        atoms.set_constraint(FixAtoms(indices=fixed))
    atoms.calc = calc
    finished = bool(FIRE(atoms, logfile=None).run(fmax=fmax, steps=steps))
    Counter.relaxations += 1
    energy = float(atoms.get_potential_energy())
    forces = atoms.get_forces()
    converged = (finished and np.isfinite(energy) and bool(np.isfinite(forces).all())
                 and float(np.linalg.norm(forces, axis=1).max()) <= fmax)
    return atoms, energy, converged


def registry_scan(
    iface: Interface,
    calc,
    n_xy: int = 3,
    gaps: tuple[float, ...] = (1.8, 2.2, 2.6),
) -> list[tuple[tuple[float, float], float, float]]:
    """Single-point energies on an n_xy × n_xy grid of in-plane offsets × gaps.

    Offsets are fractional coordinates of the interface supercell. Returns a
    list of ((dx, dy), gap, energy) sorted by energy.
    """
    results = []
    for (i, j), g in itertools.product(itertools.product(range(n_xy), repeat=2), gaps):
        trial = copy.deepcopy(iface)
        trial.in_plane_offset = (i / n_xy, j / n_xy)
        trial.gap = g
        results.append(((i / n_xy, j / n_xy), g, single_point(to_atoms(trial), calc)))
    return sorted(results, key=lambda r: r[2])


def work_of_adhesion(
    cand: Candidate,
    iface: Interface,
    calc,
    n_xy: int = 3,
    gaps: tuple[float, ...] = (1.8, 2.2, 2.6),
    fmax: float = 0.05,
    steps: int = 300,
    do_relax: bool = True,
) -> tuple[EnergeticsResult, object, object]:
    """Registry scan → relax best registry → W_adh.

    Returns (result, relaxed interface Atoms, starting interface Atoms) so the
    judge can compare before/after.
    """
    sp0, rx0 = Counter.single_points, Counter.relaxations
    scan = registry_scan(iface, calc, n_xy=n_xy, gaps=gaps)
    (dx, dy), gap, _ = scan[0]

    best = copy.deepcopy(iface)
    best.in_plane_offset = (dx, dy)
    best.gap = gap
    start = to_atoms(best)
    fixed = bottom_fixed_indices(start, best.substrate_indices)

    film_idx = list(best.film_indices)
    sub_idx = list(best.substrate_indices)
    film0, sub0 = start[film_idx], start[sub_idx]
    sub_fixed = [sub_idx.index(i) for i in fixed]

    if do_relax:
        relaxed, e_int, ok_int = relax(start, calc, fixed=fixed, fmax=fmax, steps=steps)
        _, e_film, ok_film = relax(film0, calc, fixed=None, fmax=fmax, steps=steps)
        _, e_sub, ok_sub = relax(sub0, calc, fixed=sub_fixed, fmax=fmax, steps=steps)
        failed = [name for name, ok in (("interface", ok_int), ("film", ok_film), ("substrate", ok_sub)) if not ok]
        status = "validated" if not failed else "unconverged"
    else:
        relaxed = start
        e_int, e_film, e_sub = single_point(start, calc), single_point(film0, calc), single_point(sub0, calc)
        failed, status = [], "unrelaxed"

    w = (e_film + e_sub - e_int) / cand.area * EV_PER_A2_TO_J_PER_M2
    # Only converged relaxations give a validated work of adhesion; the raw number is kept for diagnosis.
    if status == "validated" and not np.isfinite(w):
        status = "nonfinite"
    validated = status == "validated"
    res = EnergeticsResult(
        candidate=cand,
        best_offset=(dx, dy),
        best_gap=gap,
        e_interface=e_int,
        e_film=e_film,
        e_substrate=e_sub,
        w_adh=float(w) if validated else None,
        status=status,
        unconverged=failed,
        w_adh_unvalidated=float(w),
        n_single_points=Counter.single_points - sp0,
        n_relaxations=Counter.relaxations - rx0,
    )
    return res, relaxed, start
