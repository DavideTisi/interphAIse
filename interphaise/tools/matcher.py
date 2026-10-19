"""Deterministic lattice matching (ZSL) and termination enumeration.

Thin wrapper around pymatgen's CoherentInterfaceBuilder. It enumerates
*every* (termination, supercell match) for one facet pair — the brute-force
baseline is just this function called over all low-index facet pairs.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from pymatgen.analysis.interfaces.coherent_interfaces import CoherentInterfaceBuilder
from pymatgen.analysis.interfaces.zsl import ZSLGenerator
from pymatgen.core import Structure
from pymatgen.core.interface import Interface

from ..context import Candidate


@dataclass
class MatchSettings:
    max_area: float = 250.0          # Å^2, supercell area cap
    max_length_tol: float = 0.04     # ~ max linear strain
    max_angle_tol: float = 0.02
    max_area_ratio_tol: float = 0.10
    film_thickness: int = 3          # layers (in_layers=True)
    substrate_thickness: int = 3
    gap: float = 2.0                 # Å, initial; refined by the registry scan
    vacuum_over_film: float = 15.0   # Å; >0 → one interface + free surfaces
    max_candidates: int = 200        # safety cap per facet pair


def enumerate_interfaces(
    substrate: Structure,
    film: Structure,
    substrate_miller: tuple[int, int, int],
    film_miller: tuple[int, int, int],
    names: tuple[str, str],
    settings: MatchSettings | None = None,
) -> list[tuple[Candidate, Interface]]:
    """All lattice-matched interfaces for one facet pair, every termination.

    ``names`` = (substrate_name, film_name) for logging. Returns an empty
    list (not an error) when no match exists within tolerance — the
    orchestrator treats that as a signal to go back to facet selection.
    """
    s = settings or MatchSettings()
    zsl = ZSLGenerator(
        max_area=s.max_area,
        max_length_tol=s.max_length_tol,
        max_angle_tol=s.max_angle_tol,
        max_area_ratio_tol=s.max_area_ratio_tol,
    )
    builder = CoherentInterfaceBuilder(
        substrate_structure=substrate,
        film_structure=film,
        film_miller=tuple(film_miller),
        substrate_miller=tuple(substrate_miller),
        zslgen=zsl,
    )
    out: list[tuple[Candidate, Interface]] = []
    seen: set = set()
    for term in builder.terminations:
        gen = builder.get_interfaces(
            term,
            gap=s.gap,
            vacuum_over_film=s.vacuum_over_film,
            film_thickness=s.film_thickness,
            substrate_thickness=s.substrate_thickness,
            in_layers=True,
        )
        for idx, iface in enumerate(gen):
            props = iface.interface_properties
            a, b, _ = iface.lattice.matrix
            area = float(np.linalg.norm(np.cross(a, b)))
            cand = Candidate(
                pair=names,
                film_miller=tuple(int(x) for x in film_miller),
                substrate_miller=tuple(int(x) for x in substrate_miller),
                termination=tuple(term),
                n_atoms=len(iface),
                area=area,
                von_mises_strain=float(props.get("von_mises_strain", float("nan"))),
                index=idx,
            )
            # ZSL returns many symmetry-equivalent supercells; keep one of each.
            key = (cand.termination, cand.n_atoms, round(area, 1), round(cand.von_mises_strain, 4))
            if key in seen:
                continue
            seen.add(key)
            out.append((cand, iface))
            if len(out) >= s.max_candidates:
                return out
    return out


def low_index_millers(structure: Structure, max_index: int = 1) -> list[tuple[int, int, int]]:
    """Symmetry-distinct Miller indices up to ``max_index`` (brute-force baseline)."""
    from pymatgen.core.surface import get_symmetrically_distinct_miller_indices

    return [tuple(int(x) for x in m) for m in get_symmetrically_distinct_miller_indices(structure, max_index)]
