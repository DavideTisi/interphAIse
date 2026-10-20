"""Data models shared across stages.

Everything that crosses a stage boundary is a plain dataclass so it can be
logged to JSON and replayed. The orchestrator's decision log is built from
these objects; it is also what the benchmark scorer reads.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

Role = Literal["anode", "cathode"]


@dataclass
class InterfaceContext:
    """One electrode | electrolyte pair to model.

    Attributes:
        electrode: composition of the electrode phase, e.g. "Li", "LiCoO2".
        electrolyte: composition of the solid electrolyte, e.g. "Li6PS5Cl".
        role: "anode" or "cathode" — sets the sign conventions in prompts.
        voltage: electrode potential vs Li/Li+ in V. Sets the Li chemical
            potential: mu_Li = mu_Li(bcc) - e * voltage. Li metal is 0 V.
        temperature: K, used only for the optional MD anneal.
        max_atoms: hard budget for any interface cell built.
        max_strain: hard limit on von Mises strain of a lattice match.
        electrode_mp_id / electrolyte_mp_id: optional overrides for the bulk
            structure; otherwise the lowest-energy ordered MP entry is used.
    """

    electrode: str
    electrolyte: str
    role: Role
    voltage: float = 0.0
    temperature: float = 300.0
    max_atoms: int = 600
    max_strain: float = 0.04
    electrode_mp_id: str | None = None
    electrolyte_mp_id: str | None = None
    # Free-text description shown to the LLM, e.g. "LiNbO3 coating on a LiCoO2
    # cathode, contact with the Li6PS5Cl electrolyte". Lets the same machinery
    # handle coating | electrolyte contacts where "electrode" is the coating.
    setting: str = ""

    @property
    def name(self) -> str:
        return f"{self.electrode}|{self.electrolyte}@{self.voltage:g}V"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ReactionChannel:
    """One kink of the interfacial reaction curve (pymatgen InterfacialReactivity)."""

    mixing_ratio: float           # x in  x*electrode + (1-x)*electrolyte
    reaction_energy: float        # eV/atom (negative = favourable)
    products: list[str]
    equation: str = ""
    # atoms of each product per formula of reaction (from the balanced equation);
    # used by the rules arm to keep the dominant products
    product_atoms: dict[str, float] = field(default_factory=dict)


@dataclass
class ReactivityReport:
    """Output of the deterministic reactivity gate."""

    pair: tuple[str, str]
    voltage: float
    open_element: str | None      # "Li" when computed in the grand-potential ensemble
    min_reaction_energy: float    # eV/atom, most negative over all mixing ratios
    most_favourable: ReactionChannel | None
    channels: list[ReactionChannel] = field(default_factory=list)
    reactive: bool = False        # min_reaction_energy < threshold
    threshold: float = -0.01
    note: str = ""


@dataclass
class InterfaceTypeDecision:
    """LLM decision 2+3: sharp interface, or which interphase stack forms."""

    interface_type: Literal["sharp", "interphase"]
    # Ordered from electrode side to electrolyte side, endpoints included,
    # e.g. ["Li", "Li2S", "Li3P", "LiCl", "Li6PS5Cl"]. For "sharp" this is
    # just [electrode, electrolyte].
    stack: list[str]
    # Expert call on what the layer does over cycling:
    #   none        sharp interface, nothing forms
    #   passivating electronically insulating, self-limiting layer
    #   growing     electronically conducting (or otherwise non-self-limiting) layer
    character: Literal["none", "passivating", "growing"] = "none"
    rationale: str = ""
    confidence: float | None = None


@dataclass
class FacetChoice:
    """LLM decision 1 for one adjacent pair in the stack."""

    film: str                     # upper phase (closer to the electrolyte)
    substrate: str                # lower phase (closer to the electrode)
    film_miller: tuple[int, int, int]
    substrate_miller: tuple[int, int, int]
    rationale: str = ""


@dataclass
class Candidate:
    """One lattice-matched interface produced by the matcher."""

    pair: tuple[str, str]                       # (substrate, film)
    film_miller: tuple[int, int, int]
    substrate_miller: tuple[int, int, int]
    termination: tuple[str, str]
    n_atoms: int
    area: float                                 # Å^2
    von_mises_strain: float
    index: int = 0                              # position in the builder's iterator
    valid: bool = True
    reject_reasons: list[str] = field(default_factory=list)


@dataclass
class EnergeticsResult:
    candidate: Candidate
    best_offset: tuple[float, float]
    best_gap: float
    e_interface: float            # eV
    e_film: float                 # eV, isolated film slab in the same cell
    e_substrate: float            # eV, isolated substrate slab in the same cell
    w_adh: float                  # J/m^2, work of adhesion (>0 = bound)
    n_single_points: int = 0
    n_relaxations: int = 0


@dataclass
class JudgeVerdict:
    """LLM decision 4: is the relaxed structure physically acceptable?"""

    verdict: Literal["accept", "accept_with_caveat", "reject"]
    action: Literal[
        "none", "thicker_slabs", "next_termination", "different_facets", "larger_cell"
    ] = "none"
    rationale: str = ""
