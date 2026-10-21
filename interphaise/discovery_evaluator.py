"""Pinned-entry thermodynamic objective, independent of the agent/search loop.

All energies are eV per non-Li atom at one imposed Li chemical potential.
Contact driving forces include endpoint decomposition. No MLIP energies enter
this phase diagram. Pure-Li endpoints require a different normalization and
are deliberately rejected by this cathode-coating evaluator.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math

import numpy as np
from pymatgen.analysis.phase_diagram import GrandPotPDEntry, GrandPotentialPhaseDiagram, PhaseDiagram
from pymatgen.core import Element

from .tools.reactivity import li_chemical_potential


@dataclass(frozen=True)
class Objective:
    version: str = "v2-draft"
    min_band_gap_eV: float = 2.0
    bin_width_eV: float = 0.020
    acceptable_penalty_eV: float = 0.050

    def __post_init__(self):
        for name, value in asdict(self).items():
            if name != "version" and (not math.isfinite(value) or value < 0):
                raise ValueError(f"Invalid objective setting: {name}")
        if self.bin_width_eV == 0:
            raise ValueError("bin_width_eV must be positive")


def penalty_bin(penalty: float, width: float) -> int:
    """Fixed half-open bins [0,w), [w,2w), ...; boundaries snap at 1e-12.

    This preserves transitive ties; nearby values across a boundary can differ.
    """
    if not math.isfinite(penalty) or penalty < 0 or not math.isfinite(width) or width <= 0:
        raise ValueError("Expected finite nonnegative penalty and positive width")
    return math.floor(penalty / width + 1e-12)


def ranking_key(result: dict, *, require_adhesion: bool = False) -> tuple:
    """Larger is better. No raw-energy tiebreak within a fixed bin."""
    if result.get("status") != "ok" or not result.get("insulating"):
        return (0, 0, 0.0)
    adhesion = result.get("weakest_adhesion_J_m2")
    if require_adhesion and (adhesion is None or not math.isfinite(adhesion)):
        return (0, 0, 0.0)
    return (1, -result["penalty_bin"], float(adhesion) if require_adhesion else 0.0)


def _project(entry, mu):
    projected = GrandPotPDEntry(entry, {Element("Li"): mu})
    if projected.composition.num_atoms <= 0:
        raise ValueError("Pure Li is unsupported by the non-Li-atom objective")
    if not math.isfinite(projected.energy_per_atom):
        raise ValueError("Nonfinite entry energy")
    return projected


def _contact(gpd, first, second):
    """Exact minimum along a piecewise-linear hull, including both endpoints."""
    c1, c2 = first.composition.fractional_composition, second.composition.fractional_composition
    delta = np.array([c2[e] - c1[e] for e in gpd.elements])
    norm2 = float(delta @ delta)
    points = []
    if norm2 < 1e-24:
        # Same projected composition, different Li stoichiometry/entry energy.
        samples = [(c1, 0.0), (c2, 1.0)]
    else:
        samples = []
        for comp in gpd.get_critical_compositions(c1, c2):
            comp = comp.fractional_composition
            offset = np.array([comp[e] - c1[e] for e in gpd.elements])
            samples.append((comp, float(np.clip(offset @ delta / norm2, 0, 1))))
    for comp, x in samples:
        reference = (1 - x) * first.energy_per_atom + x * second.energy_per_atom
        energy = float(gpd.get_hull_energy_per_atom(comp) - reference)
        products = sorted({e.original_entry.composition.reduced_formula for e in gpd.get_decomposition(comp)})
        points.append({"second_non_Li_fraction": x, "reaction_energy": energy, "products": products})
    return min(points, key=lambda item: item["reaction_energy"])


def evaluate_candidate(candidate_id: str, coating_entry, *, electrode_entry,
                       electrolyte_entry, entries, voltage: float,
                       band_gap_eV: float | None, energy_source: str,
                       objective: Objective = Objective()) -> dict:
    """Evaluate pinned, consistently corrected entries from ONE energy dataset.

    Caller must resolve IDs and ensure a common compatibility/functional scheme.
    The supplied entries must contain all three pinned entries and elemental
    references. Missing entries fail instead of silently substituting polymorphs.
    """
    entries = list(entries)
    if not candidate_id or not energy_source or not math.isfinite(voltage):
        raise ValueError("Candidate ID, energy provenance and finite voltage required")
    for entry in (coating_entry, electrode_entry, electrolyte_entry):
        if not any(e.composition == entry.composition and abs(e.energy - entry.energy) < 1e-9
                   and getattr(e, "entry_id", None) == getattr(entry, "entry_id", None) for e in entries):
            raise ValueError("Pinned entry missing from the phase-diagram dataset")
    pd = PhaseDiagram(entries)
    mu = li_chemical_potential(pd, voltage)
    gpd = GrandPotentialPhaseDiagram(entries, {Element("Li"): mu})
    coat, electrode, electrolyte = [_project(e, mu) for e in (coating_entry, electrode_entry, electrolyte_entry)]
    self_penalty = max(0.0, float(coat.energy_per_atom - gpd.get_hull_energy_per_atom(coat.composition)))
    contacts = [_contact(gpd, electrode, coat), _contact(gpd, coat, electrolyte)]
    penalty = max(self_penalty, *[max(0.0, -c["reaction_energy"]) for c in contacts])
    gap_known = band_gap_eV is not None and math.isfinite(band_gap_eV) and band_gap_eV >= 0
    insulating = bool(gap_known and band_gap_eV >= objective.min_band_gap_eV)
    return {
        "candidate_id": candidate_id, "status": "ok" if gap_known else "incomplete",
        "objective": asdict(objective), "objective_version": objective.version,
        "energy_source": energy_source, "energy_units": "eV/non-Li atom",
        "entries": {role: {"entry_id": getattr(entry, "entry_id", None),
                           "formula": entry.composition.reduced_formula,
                           "energy_eV": float(entry.energy)}
                    for role, entry in [("coating", coating_entry), ("electrode", electrode_entry),
                                        ("electrolyte", electrolyte_entry)]},
        "voltage_V": voltage, "mu_Li_eV": mu,
        "band_gap_eV": float(band_gap_eV) if gap_known else None,
        "insulating": insulating, "self_decomposition_penalty": self_penalty,
        "contacts": contacts,
        "contact_reaction_energies": [c["reaction_energy"] for c in contacts],
        "penalty": penalty, "penalty_bin": penalty_bin(penalty, objective.bin_width_eV),
        "acceptable": insulating and penalty <= objective.acceptable_penalty_eV,
        "warnings": [] if gap_known else ["Band gap unknown; candidate cannot pass"],
    }
