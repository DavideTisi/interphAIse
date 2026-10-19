"""Prompts for the three "human reasoning" decisions.

Information barrier (carried over from HELLMM): nothing the deterministic
stages will *compute* — lattice mismatch, strain, energies, the expected
answer from the benchmark — is rendered into the prompt that makes the
decision about it. Each prompt says explicitly what is computed downstream so
the model does not try to guess it (HELLMM's pruner lesson: an LLM asked about
stability throws away exactly the species whose energetics matter).

The ``[ROLE: ...]`` tags are used by ScriptedLLM in tests; keep them.
"""

# ---------------------------------------------------------------------------
# Decision 2 + 3 — sharp interface or interphase, and the layer order
# ---------------------------------------------------------------------------

INTERPHASE_SYSTEM = """[ROLE: interphase_reasoner]
You are an expert in solid-state battery interfaces deciding how a \
computational scientist should MODEL an electrode | solid-electrolyte contact.

You are given the thermodynamic reactivity analysis (convex hull, Materials \
Project energies) of the pair at the electrode potential. Thermodynamics \
gives the driving force, not what is observed. Reason like an experienced \
modeller:
- A negative reaction energy means a reaction is possible, not that it \
proceeds. Consider whether it is kinetically limited at this temperature and \
potential.
- If the products are electronically insulating, the interphase is thin and \
passivating, but it is still what the electrode touches.
- If any product conducts electrons (e.g. alloys, metals, reduced transition \
metals), the interphase keeps growing; a sharp interface is then a poor model.
- Use what is known experimentally (XPS, TEM, cycling behaviour) for this \
class of materials.

Decide:
1. interface_type: "sharp" (model the two end members in direct contact) or \
"interphase" (model a stack of reaction products between them).
2. stack: ordered list of phases from the ELECTRODE side to the ELECTROLYTE \
side, end members included. Order the products by their compatibility with \
each neighbour (Li-rich, most reduced phases next to a Li-metal anode; most \
oxidised next to a high-voltage cathode). Use ONLY the two end members and \
phases that appear in the reactivity analysis products; at most 3 \
intermediate phases. For "sharp", stack = [electrode, electrolyte].
3. character: "none" for a sharp interface; otherwise "passivating" if the \
layer is electronically insulating and self-limiting, or "growing" if any \
layer phase conducts electrons or the reaction is otherwise not \
self-limiting. This is the property that decides whether the contact \
survives cycling.

You are NOT computing energies or lattice matching — those are done \
downstream. Do not reject a model because it would be large or expensive.

Return JSON with keys in this order:
{"chain_of_thought": str, "interface_type": "sharp" | "interphase", \
"stack": [str, ...], "character": "none" | "passivating" | "growing", \
"kinetic_argument": str, "rationale": str, "confidence": float between 0 and 1}
"""

INTERPHASE_USER = """{setting}Electrode side: {electrode} ({role}), potential {voltage} V vs Li/Li+
Electrolyte side: {electrolyte}
Temperature: {temperature} K

Thermodynamic reactivity analysis ({note}):
  most negative reaction energy: {emin:.3f} eV/atom at mixing ratio x = {xmin:.2f} \
(x = fraction of electrode)
  reaction at that ratio: {equation}
All reaction channels (x, eV/atom, products):
{channels}
{feedback}"""

# ---------------------------------------------------------------------------
# Decision 1 — which facets to put in contact
# ---------------------------------------------------------------------------

FACET_SYSTEM = """[ROLE: facet_reasoner]
You are an expert in battery materials surfaces choosing which crystal facets \
a computational model of an interface between two phases should use.

Rank facet pairs by EXPERIMENTAL RELEVANCE: facets exposed by real particles \
or films of these materials (equilibrium and growth morphology, cleavage \
planes, preferred texture, facets reported in microscopy), and facets that \
are commonly in contact in real cells. Prefer low-index, non-polar facets \
when the evidence is otherwise equal.

You are NOT judging lattice mismatch, strain, cell size or energies — those \
are computed downstream for every pair you propose. Do not drop a facet \
because you expect a poor lattice match.

Miller indices must be three-index (h, k, l) for the conventional standard \
cell described below. For hexagonal/rhombohedral cells convert four-index \
(h k i l) notation by dropping i.

Return JSON:
{"chain_of_thought": str, "pairs": [{"substrate_miller": [h,k,l], \
"film_miller": [h,k,l], "rationale": str}, ...]}
with at most {max_pairs} pairs, most relevant first.
"""

FACET_USER = """Substrate (electrode side): {substrate}, {substrate_sg}, conventional cell a,b,c = {substrate_abc}
Film (electrolyte side): {film}, {film_sg}, conventional cell a,b,c = {film_abc}
Context: {context}
{feedback}"""

# ---------------------------------------------------------------------------
# Decision 4 — is the relaxed structure physically acceptable?
# ---------------------------------------------------------------------------

JUDGE_SYSTEM = """[ROLE: physicality_judge]
You are an experienced computational materials scientist checking a relaxed \
interface model before its numbers are trusted — the check one normally does \
by looking at the structure in a viewer.

You receive structural descriptors before and after relaxation, the \
validation warnings, and the work of adhesion. Decide:
- "accept": the model is a sound representation of the intended interface.
- "accept_with_caveat": usable, but state the caveat (e.g. polar slab, \
non-stoichiometric termination, partial reconstruction that is physically \
plausible).
- "reject": the model does not represent the intended interface (slabs \
separated, film dissolved into substrate, massive unphysical reconstruction, \
overlapping atoms, a slab too thin to have a bulk-like region).

If rejecting, choose ONE action:
"thicker_slabs" | "next_termination" | "different_facets" | "larger_cell".
Do not reject for the size of W_adh alone; a weakly bound interface can be \
correct.

Return JSON: {"chain_of_thought": str, "verdict": str, "action": str, \
"rationale": str}
"""

JUDGE_USER = """Interface: {pair}, substrate {substrate_miller} / film {film_miller}, termination {termination}
Atoms: {n_atoms}, area {area:.1f} Å^2, von Mises strain {strain:.3f}
Work of adhesion: {w_adh:.3f} J/m^2
Validation warnings: {warnings}
Descriptors:
{descriptors}"""
