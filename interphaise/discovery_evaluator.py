"""Pinned-entry thermodynamic objective, independent of the agent/search loop.

All energies are eV per non-Li atom at one imposed Li chemical potential.
By default contact driving forces include endpoint decomposition; the explicit
equilibrated-reference variant measures additional mixing reactivity instead. No MLIP energies enter
this phase diagram. Pure-Li endpoints require a different normalization and
are deliberately rejected by this cathode-coating evaluator.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math

import numpy as np
from pymatgen.analysis.phase_diagram import GrandPotPDEntry, GrandPotentialPhaseDiagram
from pymatgen.core import Element



@dataclass(frozen=True)
class Objective:
    version: str = "v2-draft"
    contact_reference: str = "pinned"
    min_band_gap_eV: float = 2.0
    bin_width_eV: float = 0.020
    acceptable_penalty_eV: float = 0.050

    def __post_init__(self):
        for name, value in asdict(self).items():
            if name not in {"version", "contact_reference"} and (not math.isfinite(value) or value < 0):
                raise ValueError(f"Invalid objective setting: {name}")
        if self.contact_reference not in {"pinned", "equilibrated"}:
            raise ValueError("Unknown contact energy reference")
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


def _contact(gpd, first, second, reference_energies=None):
    """Exact minimum along a piecewise-linear hull, including both endpoints."""
    e1,e2 = reference_energies or (first.energy_per_atom,second.energy_per_atom)
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
        reference = (1 - x) * e1 + x * e2
        energy = float(gpd.get_hull_energy_per_atom(comp) - reference)
        products = sorted({e.original_entry.composition.reduced_formula for e in gpd.get_decomposition(comp)})
        points.append({"second_non_Li_fraction": x, "reaction_energy": energy, "products": products})
    return min(points, key=lambda item: item["reaction_energy"])


def _lp_contact(entries, mu, first, second, reference_energies=None):
    """Exact convex-hull minimum with a variable reactant mixing fraction.

    Minimize sum(y_i * grand_energy_i) - [(1-x)*e1 + x*e2],
    subject to non-Li element conservation, y_i >= 0 and 0 <= x <= 1.
    This is the same hull problem without constructing high-dimensional facets.
    """
    from scipy.optimize import linprog

    e1,e2 = reference_energies or (first.energy_per_atom,second.energy_per_atom)
    elements = sorted(set(first.composition.elements) | set(second.composition.elements))
    allowed = set(elements) | {Element("Li")}
    projected = [_project(e, mu) for e in entries
                 if set(e.composition.elements) <= allowed
                 and set(e.composition.elements) != {Element("Li")}]
    c1 = np.array([first.composition.get_atomic_fraction(e) for e in elements])
    c2 = np.array([second.composition.get_atomic_fraction(e) for e in elements])
    matrix = np.array([[p.composition.get_atomic_fraction(e) for p in projected] for e in elements])
    a_eq = np.column_stack((matrix, c1-c2))
    energies = np.array([p.energy_per_atom for p in projected] +
                        [e1-e2])
    solution = linprog(energies, A_eq=a_eq, b_eq=c1,
                      bounds=[(0,None)]*len(projected)+[(0,1)], method="highs")
    if not solution.success or np.max(np.abs(a_eq @ solution.x - c1)) > 1e-7:
        raise ValueError("Grand-potential optimization failed conservation/solver checks")
    energy = float(solution.fun-e1)
    return {"second_non_Li_fraction":float(solution.x[-1]), "reaction_energy":energy,
            "products":sorted({p.original_entry.composition.reduced_formula
                               for p,y in zip(projected,solution.x[:-1]) if y > 1e-8})}


def evaluate_candidate(candidate_id: str, coating_entry, *, electrode_entry,
                       electrolyte_entry, entries, voltage: float,
                       band_gap_eV: float | None, energy_source: str,
                       objective: Objective = Objective(), backend: str = "linprog") -> dict:
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
    needed = {e for item in (coating_entry,electrode_entry,electrolyte_entry)
              for e in item.composition.elements} | {Element("Li")}
    references = {e:min(item.energy_per_atom for item in entries
                       if set(item.composition.elements)=={e}) for e in needed}
    mu = references[Element("Li")] - voltage
    coat, electrode, electrolyte = [_project(e, mu) for e in (coating_entry, electrode_entry, electrolyte_entry)]
    if backend == "linprog":
        contact = lambda first,second,refs=None: _lp_contact(entries,mu,first,second,refs)
    elif backend == "qhull":
        # Retained as an independent cross-check on small chemical systems.
        gpd = GrandPotentialPhaseDiagram(entries, {Element("Li"): mu})
        contact = lambda first,second,refs=None: _contact(gpd,first,second,refs)
    else:
        raise ValueError("Unknown thermodynamic backend")
    self_penalty = max(0.0,-contact(coat,coat)["reaction_energy"])
    endpoint_penalties = {role:max(0.0,-contact(entry,entry)["reaction_energy"])
                          for role,entry in [("electrode",electrode),("electrolyte",electrolyte)]}
    absolute_contacts = [contact(electrode,coat),contact(coat,electrolyte)]
    contacts = absolute_contacts
    if objective.contact_reference == "equilibrated":
        # Extra reaction on mixing already equilibrated endpoint assemblages;
        # coating self-instability remains an explicit separate penalty.
        hc = coat.energy_per_atom-self_penalty
        he = electrode.energy_per_atom-endpoint_penalties["electrode"]
        hs = electrolyte.energy_per_atom-endpoint_penalties["electrolyte"]
        contacts = [contact(electrode,coat,(he,hc)),contact(coat,electrolyte,(hc,hs))]
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
        "voltage_V": voltage, "mu_Li_eV": mu, "backend": backend,
        "endpoint_decomposition_penalties": endpoint_penalties,
        "band_gap_eV": float(band_gap_eV) if gap_known else None,
        "insulating": insulating, "self_decomposition_penalty": self_penalty,
        "contacts": contacts, "contact_reference":objective.contact_reference,
        "absolute_contact_reaction_energies": [c["reaction_energy"] for c in absolute_contacts],
        "contact_reaction_energies": [c["reaction_energy"] for c in contacts],
        "penalty": penalty, "penalty_bin": penalty_bin(penalty, objective.bin_width_eV),
        "acceptable": insulating and penalty <= objective.acceptable_penalty_eV,
        "warnings": [] if gap_known else ["Band gap unknown; candidate cannot pass"],
    }
