# Multistart review and interface facet decision

21 October 2026, working branch `davide`. Saved recommendation for Davide to
share with Claude; no cross-session message was sent. No interface relaxation
or new PET-MAD evaluation was launched by this review.

## Choice

Use **LiNbF6(001) for both primary contacts**, retaining **LiCoO2(001)** on the
cathode side. Use Li6PS5Cl seed 0 as the primary model reference and seed 4 as the
alternative. Keep the 200-atom Li6PS5Cl(011)|LiNbF6(100) case as a separately
labelled orientation comparison, not a replacement chosen after seeing adhesion.
The initial construction cap remains 512 atoms; convergence tests can require
larger structures and must not be declared converged merely to fit this cap.

The reason is to hold the coating's plane orientation fixed across contacts.
This alone does **not** construct a single coherent film: the two calculations
have independently matched in-plane strain/supercells, and opposite coating
faces can have different terminations. Describe them as two separate contact
models with a common coating orientation. A literal continuous three-layer film
would additionally require compatible in-plane strain, rotations, opposing
surfaces and termination/stoichiometry bookkeeping.

## Important correction: the sensitivity pair changes termination

The saved lowest-strain/polarity 440-atom matches are:

| Electrolyte reference | LiNbF6 termination identifier | Li6PS5Cl termination identifier | Area | Strain |
|---|---|---|---:|---:|
| Seed 0 | F2_P-6_3 | P_C2/m_2 | 170.708 Å² | 2.9248% |
| Seed 4 | F2_P-6_3 | Cl2_P-1_2 | 172.926 Å² | 2.7397% |

The common facets and atom count do not demonstrate equivalent surfaces. These
are saved termination labels; a layer/site mapping is still needed to establish
the exposed chemistry. Independently picking the minimum-polarity termination
would confound bulk-configuration sensitivity with surface choice.

Before the sensitivity relaxation, map a common cleavage through the parent
framework, then document surface composition, broken framework bonds, layer
counts, stoichiometry, supercell mapping and fixed-atom rule in both structures.
The scans contain P-labelled alternatives in both seeds at 440 atoms (seed 4:
`P_P1_4`), so there is a concrete starting point for that inspection. Matching
labels or elemental names alone is insufficient. Let natural cell strain and
Li/Cl rearrangement vary with the selected bulk reference, but record them.
If equivalent cuts cannot be made within the resource limits, retain both as
**combined bulk-and-surface sensitivity**, rather than claim only one changed
variable. The same requirement applies to a seed comparison using the 200-atom
facet; using a common coating facet across contacts is not uniquely required for
controlling the bulk comparison within one contact.

## Use the existing unconstrained reference cells consistently

The reported scans use symmetric LiCoO2 and LiNbF6 cells. Their existing
unconstrained stability-check cells meet the raw bulk criteria; use those for
the final primary construction, preserving their parent basis. No additional
bulk relaxation is needed for this choice. A new geometry-only check using
those files confirms feasible 504-/440-atom matches:

- Cathode (001)|(001): 504 atoms, area 88.800 Å², strain 1.9520%, film/substrate
  labels `F2_P-6_3` / `Li_P6/mmm_1`; formal dipole/area 0.613 / 2.058 e/Å.
- Electrolyte seed 0 (111)|(001): 440 atoms, area 170.708 Å², strain 3.0056%.
- Electrolyte seed 4 (111)|(001): 440 atoms, area 172.926 Å², strain 2.8641%.

These are feasibility matches, not frozen termination choices for the electrolyte
pair or relaxed interfaces. Evidence:
`data/reviews/multistart_facet_review_20261021.json`.

**Apply explicit termination selection before the enumeration cap.** With the
unconstrained cathode/film inputs there are 113 ZSL matches and four termination
pairs. The current 60-candidate global cutoff ends before the F-terminated film
is reached. Explicitly enumerating `F2_P-6_3` / `Li_P6/mmm_1` recovers the
504-atom match above. Add a focused regression check when changing selection;
log truncation, transformation matrices, cut shifts and exact input hashes.
Do not interpret a truncated scan as physical absence of an interface.

## Next calculations, in order

1. Build and inspect the primary cathode and seed-0 electrolyte contacts with
   pinned orientation, surface choice, composition and constraints. Save them
   to the viewer. Prepare the mapped seed-4 sensitivity input using the same rule.
2. Check formal charge, surface polarity and constraint dependence before a
   large registry/convergence batch. Record forces on free and fixed atoms
   separately. The archived cathode scan has formal dipoles around **2.06 and
   6.17 e/Å** depending on termination; 2.06 is not the value of every termination.
3. Use the same strain, composition, geometry convention and constraints in
   joined/separated energy references. Distinguish fixed-geometry separation from
   independently relaxed adhesion. Record if separated references reconstruct
   into different basins.
4. Test thickness, vacuum and registry under the existing proposed numerical
   tolerance (change at most 0.1 J/m² across the final two settings). A relaxed
   geometry or flat vacuum curve does not validate the physical treatment of a
   polar surface. If the primary polar contact remains sensitive, report it as
   unresolved; do not quietly substitute the different facet or rank coatings.
5. Use the 200-atom contact as a bounded secondary geometry/protocol comparison
   if useful. It is below the repository's formal-polarity warning threshold in
   both seeds, not proof of exactly zero electronic polarization. Keep Claude's
   implementation and evidence in a bulk/interface commit separate from expansion.

The formal diagnostic is based on oxidation states, consistent with the
[pymatgen slab-polarity definition](https://pymatgen.org/pymatgen.core.html#pymatgen.core.surface.Slab.is_polar).
It is not a calculated electronic dipole or electrostatic correction. Keep the
same PET-MAD S 1.6.0 checkpoint and conservative energy/force evaluation.

## Multistart verification and interpretation

Re-read all twelve final structures using their saved single-point results.
Stored energies reproduce every reported energy drop; raw forces and stresses
reproduce all convergence flags. Li6PS5Cl has six converged seeds, LiZr2(PO4)3
five; its seed 5 has force 0.011387 eV/Å and is correctly excluded. Both selected
seed-0 structures are the lowest-energy converged members of this sampled set.
Additional multistart cost is 7,216 calculator calls and 1,567.47 summed seconds;
the two materials ran concurrently, so the sum is not elapsed batch wall time.

Six targeted relaxation tests pass; Claude's full-suite claim of 113 tests was
not rerun here. Original outputs remain intact. The earlier rotation diagnostic
found variations larger than the 0.295 meV/atom LiZr2(PO4)3 seed-0/seed-1 gap,
so do not claim that tiny ordering is numerically robust. Seed 0 is a reproducible
reference, not a uniquely established ground state. That earlier diagnostic is
not an uncertainty bound for these particular alternative structures.

These nearby relaxed structures do not sample equilibrium disorder, prove
dynamical stability or establish experimental phases. They do not change the
frozen MP benchmark, the shuffled-control result or the environment expansion.
The completed discovery release need not wait for validated polar adhesion.

Shared-log editing for this review is complete. Claude can append its own batch
provenance and stage explicit bulk-work paths; avoid staging the whole shared
checkout. No commit, push or actual branch merge was performed by this review.
