"""Hard validation gates for candidate interfaces.

HELLMM principle carried over: validation is a gate, not a critic. Each check
is deterministic and returns a reason string. ``reject``-severity failures
remove the candidate; ``warn``-severity findings are kept on the candidate and
shown to the LLM judge later (they change how energies may be interpreted,
not whether the structure can be computed).
"""

from __future__ import annotations

import numpy as np
from ase.data import covalent_radii
from pymatgen.core import Composition, Structure
from pymatgen.core.interface import Interface

from ..context import Candidate

MIN_DIST_FACTOR = 0.6          # d_ij < factor * (r_cov_i + r_cov_j) → overlapping atoms
POLAR_DIPOLE_LIMIT = 0.05      # e/Å per Å^2 of interface area (|p_z| / A)


def _min_distance_violations(struct: Structure, factor: float = MIN_DIST_FACTOR) -> list[str]:
    out = []
    i_idx, j_idx, _offs, dists = struct.get_neighbor_list(r=2.5)
    z = np.array(struct.atomic_numbers)
    for i, j, d in zip(i_idx, j_idx, dists):
        if i < j and d < factor * (covalent_radii[z[i]] + covalent_radii[z[j]]):
            out.append(f"{struct[i].specie}-{struct[j].specie} at {d:.2f} Å")
            if len(out) >= 5:
                break
    return out


def _sub(struct: Structure, indices) -> Structure:
    return Structure.from_sites([struct[i] for i in indices])


def oxidation_map(bulk: Structure | Composition | str) -> dict[str, float]:
    """Element → formal oxidation state for ONE phase (Li is 0 in Li metal, +1 in Li2S)."""
    comp = bulk.composition if isinstance(bulk, Structure) else Composition(bulk)
    if len(comp.elements) == 1:
        return {str(comp.elements[0]): 0.0}
    guesses = comp.reduced_composition.oxi_state_guesses()
    if not guesses:
        return {}
    return {el: float(ox) for el, ox in guesses[0].items()}


def slab_charge_and_dipole(slab: Structure, oxi: dict[str, float]) -> tuple[float, float]:
    """Formal charge and z-dipole (e·Å) of a slab given formal oxidation states."""
    q = np.array([oxi.get(str(s.specie), 0.0) for s in slab])
    zc = np.array([s.coords[2] for s in slab])
    charge = float(q.sum())
    dipole = float(((zc - zc.mean()) * q).sum())
    return charge, dipole


def is_stoichiometric(slab: Structure, bulk_formula: str, tol: float = 1e-3) -> bool:
    a = slab.composition.fractional_composition
    b = Composition(bulk_formula).fractional_composition
    return all(abs(a[el] - b[el]) < tol for el in set(a) | set(b))


def validate(
    cand: Candidate,
    iface: Interface,
    *,
    max_atoms: int,
    max_strain: float,
    film_oxi: dict[str, float],
    substrate_oxi: dict[str, float],
    film_formula: str,
    substrate_formula: str,
) -> tuple[bool, list[str], list[str]]:
    """Run all gates. Returns (valid, reject_reasons, warnings)."""
    reject, warn = [], []

    if cand.n_atoms > max_atoms:
        reject.append(f"too many atoms: {cand.n_atoms} > {max_atoms}")
    if not np.isnan(cand.von_mises_strain) and cand.von_mises_strain > max_strain:
        reject.append(f"strain {cand.von_mises_strain:.3f} > {max_strain:.3f}")

    clashes = _min_distance_violations(iface)
    if clashes:
        reject.append("overlapping atoms: " + "; ".join(clashes))

    for label, idx, formula, oxi in (
        ("film", iface.film_indices, film_formula, film_oxi),
        ("substrate", iface.substrate_indices, substrate_formula, substrate_oxi),
    ):
        slab = _sub(iface, idx)
        if not oxi:
            warn.append(f"{label}: no oxidation-state guess for {formula}; charge/polarity not checked")
            continue
        charge, dipole = slab_charge_and_dipole(slab, oxi)
        if abs(charge) > 1e-6:
            reject.append(f"{label} slab carries formal charge {charge:+.2f} e")
        elif abs(dipole) / max(cand.area, 1e-9) > POLAR_DIPOLE_LIMIT:
            warn.append(f"{label} slab is polar: |p_z|/A = {abs(dipole) / cand.area:.3f} e/Å")
        if not is_stoichiometric(slab, formula):
            warn.append(f"{label} slab is non-stoichiometric ({slab.composition.reduced_formula} vs {formula}); "
                        "W_adh is still defined, interface energy needs chemical potentials")

    cand.valid = not reject
    cand.reject_reasons = reject
    return cand.valid, reject, warn
