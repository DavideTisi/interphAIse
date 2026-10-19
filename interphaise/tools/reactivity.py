"""Deterministic reactivity gate (the battery analogue of HELLMM's Pourbaix gate).

Question answered: at this electrode potential, is a sharp
electrode | electrolyte interface thermodynamically stable, and if not, what
does the convex hull say it reacts to?

Method (Richards et al., Chem. Mater. 28, 266 (2016); Zhu et al., ACS AMI 7,
23685 (2015)):
  * Li-metal anode: closed-system InterfacialReactivity(Li, SE).
  * Any other electrode: GrandPotentialInterfacialReactivity with Li open at
    mu_Li = mu_Li(bcc) - e*V, V vs Li/Li+.

The gate only *reports*. Deciding what actually forms (kinetics, what is seen
experimentally, layer order) is the LLM's job in reasoners/interphase_reasoner.
"""

from __future__ import annotations

from pymatgen.analysis.interface_reactions import (
    GrandPotentialInterfacialReactivity,
    InterfacialReactivity,
)
from pymatgen.analysis.phase_diagram import GrandPotentialPhaseDiagram, PhaseDiagram
from pymatgen.core import Composition, Element

from ..context import ReactionChannel, ReactivityReport

DEFAULT_THRESHOLD = -0.01  # eV/atom; below this a pair is called reactive


def li_chemical_potential(pd: PhaseDiagram, voltage: float, element: str = "Li") -> float:
    """mu_Li (eV/atom, MP energy scale) at ``voltage`` V vs Li/Li+."""
    return pd.el_refs[Element(element)].energy_per_atom - voltage


def _channels(ir: InterfacialReactivity) -> list[ReactionChannel]:
    out = []
    for _idx, x, e, rxn, _kj in ir.get_kinks():
        out.append(
            ReactionChannel(
                mixing_ratio=float(x),
                reaction_energy=float(e),
                products=sorted({p.reduced_formula for p in rxn.products}),
                equation=str(rxn),
            )
        )
    return out


def interfacial_reactivity(
    electrode: str,
    electrolyte: str,
    entries,
    voltage: float | None = None,
    open_element: str = "Li",
    threshold: float = DEFAULT_THRESHOLD,
) -> ReactivityReport:
    """Reaction energy curve between two phases.

    Args:
        electrode, electrolyte: compositions.
        entries: MP (or other) entries spanning both chemical systems.
        voltage: V vs Li/Li+. ``None`` → closed system (use for chemical
            compatibility between two interphase components).
        open_element: element held at fixed chemical potential.
        threshold: eV/atom below which the pair is called reactive.
    """
    pd = PhaseDiagram(entries)
    c1, c2 = Composition(electrode), Composition(electrolyte)
    only_open = {str(el) for el in c1.elements} == {open_element}

    if voltage is None or only_open:
        # Li metal *is* the reservoir: the closed system already fixes mu_Li.
        ir = InterfacialReactivity(c1, c2, pd, norm=True, use_hull_energy=True)
        mode_open = None
        note = "closed system" if voltage is None else f"closed system ({electrode} is the {open_element} reservoir)"
    else:
        mu = li_chemical_potential(pd, voltage, open_element)
        gpd = GrandPotentialPhaseDiagram(entries, {Element(open_element): mu})
        ir = GrandPotentialInterfacialReactivity(c1, c2, gpd, pd_non_grand=pd, norm=True, use_hull_energy=True)
        mode_open = open_element
        note = f"grand potential, mu_{open_element} = {mu:.3f} eV ({voltage:g} V vs {open_element}/{open_element}+)"

    channels = _channels(ir)
    best = min(channels, key=lambda c: c.reaction_energy) if channels else None
    emin = best.reaction_energy if best else 0.0
    return ReactivityReport(
        pair=(electrode, electrolyte),
        voltage=voltage if voltage is not None else float("nan"),
        open_element=mode_open,
        min_reaction_energy=emin,
        most_favourable=best,
        channels=channels,
        reactive=emin < threshold,
        threshold=threshold,
        note=note,
    )


def check_stack(stack: list[str], entries, voltage: float, threshold: float = DEFAULT_THRESHOLD):
    """Hard check for an interphase stack proposed by the LLM.

    Every adjacent pair must be mutually compatible. The pair touching the
    electrode is evaluated at the electrode potential; inner pairs are
    evaluated as closed systems (their local mu_Li lies between the two ends,
    so the closed check is the conservative common ground).

    Returns (ok, list of (pair, report)). ``ok`` is False if any adjacent pair
    is reactive.
    """
    results = []
    for i in range(len(stack) - 1):
        a, b = stack[i], stack[i + 1]
        v = voltage if i == 0 else None
        rep = interfacial_reactivity(a, b, entries, voltage=v, threshold=threshold)
        results.append(((a, b), rep))
    return all(not r.reactive for _, r in results), results


def elements_of(*formulas: str) -> list[str]:
    els: set[str] = set()
    for f in formulas:
        els |= {str(e) for e in Composition(f).elements}
    return sorted(els)
