"""Bulk structures and thermodynamic entries from the Materials Project.

Both are cached under data/ so a team can pre-fetch everything once (e.g. on
Wednesday morning) and then work offline or on a cluster without API access.
Requires MY_MP_API_KEY (same variable as HELLMM) for anything not cached.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from pymatgen.core import Composition, Structure
from pymatgen.entries.computed_entries import ComputedStructureEntry
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

DATA_DIR = Path(os.environ.get("INTERPHASE_DATA_DIR", Path(__file__).resolve().parents[2] / "data"))


def _mp():
    key = os.environ.get("MY_MP_API_KEY")
    if not key:
        raise EnvironmentError("MY_MP_API_KEY is not set and the item is not cached under data/.")
    from pymatgen.ext.matproj import MPRester  # delegates to mp-api when installed

    return MPRester(key)


def get_bulk(formula: str, mp_id: str | None = None, conventional: bool = True) -> Structure:
    """Ordered ground-state bulk structure for ``formula``.

    Picks the lowest-energy *ordered* entry unless ``mp_id`` is given.
    Disordered experimental structures (e.g. argyrodite Li6PS5Cl with S/Cl
    site mixing) are represented by MP's ordered approximants — record which
    one you used, it matters for the interface.
    """
    tag = mp_id or Composition(formula).reduced_formula
    path = DATA_DIR / "bulk" / f"{tag}.json"
    if path.exists():
        return Structure.from_dict(json.loads(path.read_text()))

    with _mp() as mpr:
        if mp_id:
            s = mpr.get_structure_by_material_id(mp_id)
        else:
            entries = mpr.get_entries(Composition(formula).reduced_formula, inc_structure=True)
            entries = [e for e in entries if e.structure.is_ordered]
            if not entries:
                raise ValueError(f"No ordered MP entry for {formula}")
            s = min(entries, key=lambda e: e.energy_per_atom).structure
    if conventional:
        s = SpacegroupAnalyzer(s).get_conventional_standard_structure()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(s.as_dict()))
    return s


def get_entries(elements: list[str]) -> list[ComputedStructureEntry]:
    """All MP entries in the chemical system spanned by ``elements`` (cached)."""
    chemsys = "-".join(sorted(set(elements)))
    path = DATA_DIR / "entries" / f"{chemsys}.json"
    if path.exists():
        return [ComputedStructureEntry.from_dict(d) for d in json.loads(path.read_text())]
    with _mp() as mpr:
        entries = mpr.get_entries_in_chemsys(sorted(set(elements)))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([e.as_dict() for e in entries]))
    return entries
