"""Offline fixtures: a toy Li–S chemistry with hand-made energies and structures.

Numbers are not physical; they only exercise the plumbing so the scaffold
runs without MP, LLM or MLIP access.
"""

import sys
from pathlib import Path

import pytest
from pymatgen.analysis.phase_diagram import PDEntry
from pymatgen.core import Composition, Lattice, Structure

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def _li():
    return Structure.from_spacegroup("Im-3m", Lattice.cubic(3.44), ["Li"], [[0, 0, 0]])


def _li2s():
    return Structure.from_spacegroup("Fm-3m", Lattice.cubic(5.69), ["S", "Li"], [[0, 0, 0], [0.25, 0.25, 0.25]])


def _lis2():
    # toy "electrolyte": fluorite-type with Li on the cation site
    return Structure.from_spacegroup("Fm-3m", Lattice.cubic(5.75), ["Li", "S"], [[0, 0, 0], [0.25, 0.25, 0.25]])


STRUCTS = {"Li": _li, "Li2S": _li2s, "LiS2": _lis2}


@pytest.fixture
def toy_bulk():
    def bulk(formula, mp_id=None):
        return STRUCTS[Composition(formula).reduced_formula]()

    return bulk


@pytest.fixture
def toy_entries():
    def entries(_elements):
        return [
            PDEntry("Li", -1.9),
            PDEntry("S", -4.1),
            PDEntry("Li2S", 2 * -1.9 - 4.1 - 4.5),
            PDEntry("LiS2", -1.9 - 2 * 4.1 - 2.0),
        ]

    return entries


@pytest.fixture
def structs():
    return {k: f() for k, f in STRUCTS.items()}
