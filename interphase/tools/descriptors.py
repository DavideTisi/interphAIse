"""Structural descriptors of a relaxed interface, for the LLM judge.

These are the things a human looks at in OVITO before trusting an interface
model, reduced to numbers the LLM can read.
"""

from __future__ import annotations

import numpy as np
from ase.neighborlist import NeighborList, natural_cutoffs


def _cn(atoms) -> np.ndarray:
    nl = NeighborList(natural_cutoffs(atoms, mult=1.15), self_interaction=False, bothways=True)
    nl.update(atoms)
    return np.array([len(nl.get_neighbors(i)[0]) for i in range(len(atoms))])


def interface_descriptors(start, relaxed, film_idx, sub_idx, window: float = 3.0) -> dict:
    film_idx, sub_idx = list(film_idx), list(sub_idx)
    z0, z1 = start.positions[:, 2], relaxed.positions[:, 2]

    disp = np.linalg.norm(relaxed.positions - start.positions, axis=1)

    sub_top0 = z0[sub_idx].max()
    film_bot0 = z0[film_idx].min()
    plane0 = 0.5 * (sub_top0 + film_bot0)
    sub_top1, film_bot1 = z1[sub_idx].max(), z1[film_idx].min()

    near = [i for i in range(len(start)) if abs(z0[i] - plane0) < window]
    cn0, cn1 = _cn(start), _cn(relaxed)

    d = relaxed.get_all_distances(mic=True)
    np.fill_diagonal(d, np.inf)

    film_into_sub = int((z1[film_idx] < sub_top1 - 0.5).sum())
    sub_into_film = int((z1[sub_idx] > film_bot1 + 0.5).sum())

    return {
        "n_atoms": len(relaxed),
        "max_displacement_A": float(disp.max()),
        "mean_displacement_interface_region_A": float(disp[near].mean()) if near else 0.0,
        "gap_before_A": float(film_bot0 - sub_top0),
        "gap_after_A": float(film_bot1 - sub_top1),
        "film_atoms_penetrating_substrate": film_into_sub,
        "substrate_atoms_penetrating_film": sub_into_film,
        "min_distance_after_A": float(d.min()),
        "mean_CN_interface_region_before": float(cn0[near].mean()) if near else None,
        "mean_CN_interface_region_after": float(cn1[near].mean()) if near else None,
        "mean_CN_bulk_like_film": float(cn1[[i for i in film_idx if i not in near]].mean())
        if any(i not in near for i in film_idx) else None,
        "mean_CN_bulk_like_substrate": float(cn1[[i for i in sub_idx if i not in near]].mean())
        if any(i not in near for i in sub_idx) else None,
    }
