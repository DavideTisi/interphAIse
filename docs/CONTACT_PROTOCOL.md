# Primary contacts — termination mapping, builds and constraint check

21 October 2026, `davide`. Follows [SYNC_CLAUDE_1.md](https://github.com/DavideTisi/interphAIse/blob/786029128ad234e34aaa880d2bff5250c79277ed/SYNC_CLAUDE_1.md) and
[BULK_RELAXATION.md](BULK_RELAXATION.md). Two separate contact models with a common coating
orientation, LiNbF6(001): **LiCoO2(001) | LiNbF6(001)** and **Li6PS5Cl(111) | LiNbF6(001)**.
They are not one continuous film: each contact has its own matched supercell and strain.

## Inputs

These are the unconstrained bulk minima, in their parent conventional basis:
- LiCoO2 and LiNbF6: the stability-check minima in `data/petmad/bulk_relaxation_v1/`.
- Li6PS5Cl: seed 0 is the primary reference, and seed 4 (`data/petmad/bulk_multistart_v1/`)
  is the bulk-sensitivity alternative.

Matching gates are unchanged (ZSL 5 % / 3 %, strain ≤ 6 %), with area ≤ 300 Å², ≤ 512 atoms,
2 + 2 layers and 15 Å vacuum over the film.

## Termination selection

**Explicit selection before the cap.** `enumerate_interfaces` now accepts `terminations`,
applied *before* the 60-candidate cap, and a `report` that records the available
terminations, the ZSL match count and whether the cap truncated the enumeration. An unknown
label raises an error. Regression test: `test_explicit_termination_is_enumerated_before_the_cap`.
None of the builds below was truncated.

**Mapping equivalent electrolyte cuts across bulk minima.** Termination labels depend on the
symmetry of each relaxed minimum, so they do not identify the same surface in both seeds. Both
seeds were relaxed from the same symmetric parent and keep its atom order. Each parent site
therefore has a (111) height u = (x + y + z) mod 1 in parent fractional coordinates. This
height is invariant under the parent's face-centring translations. A cut is identified by the
framework (P, S, Cl) groups (species, u) on each face, ranked by mean z. This signature does
not depend on a distance window and ignores Li, which is exactly what differs between the
minima. Atom-index sets and fixed 1–1.5 Å windows were tried first and were unreliable: the
seeds use different surface supercells and distorted layer spacings.

| Seed 0 label | Seed 4 label | Contact-side framework | Far-side framework | PS4 cut | Substrate \|p\|/A (e/Å) |
|---|---|---|---|---:|---|
| `Li6Cl_P1_7` | `Cl2_P-1_2` | Cl(0.00)×8, S(0.85)×8, S(0.75)×8 | S(0.38)×24, P(0.50)×8, S(0.75)×8 | 0 | 0.174 / 0.129 |
| `S_P-1_2` | `S_P1_4` | S(0.85)×8, S(0.75)×8, P(0.50)×8 | Cl(0.00)×8, S(0.38)×24, P(0.50)×8 | 0 | 0.375 / 0.402 |
| `LiS3_P1_8` | `LiS2_P1_18` | S(0.38) on top | P(0.50) | 4 | 1.197 / 1.065 |
| `P_C2/m_2` | `P_P1_4` | P(0.50) + S(0.38) on top | — | 4 | 0.174 / 0.261 |

(The first two rows come from the window-free signature on the built contacts. The last two
are summaries of the exploratory mapping. Counts such as ×8 are slab totals for each
(species, height) group across all periods, not surface-layer counts. The order of the
groups' mean z fixes where the cut lies within the period, and the equivalence test compares
group identities and order.)

**Rule** (fixed before any interface energy was computed; applied to both seeds alike):
1. no cut PS4 tetrahedra;
2. an equivalent cut must exist in both seeds;
3. then the lowest formal substrate polarity.

The rule selects the **Cl cut**: seed 0 `Li6Cl_P1_7`, seed 4 `Cl2_P-1_2`. The earlier
minimum-polarity pick (seed 0 `P_C2/m_2`) cut four PS4 units and had no equivalent among the
seed-4 Cl terminations. The S cut is retained as an unrun alternative
(`data/petmad/contact_v1_alternatives/`).

For the cathode, the termination is explicit: `F2_P-6_3` / `Li_P6/mmm_1`. This is the
lower-polarity of the two LiCoO2(001) terminations returned (Li 2.06 vs O 6.17 e/Å) with the
F-terminated coating. Under the old global cap it was hidden.

## Built contacts (unrelaxed; `scripts/build_contact.py`)

| Contact | Atoms (sub + film) | Area Å² | Strain | Substrate side at contact | Coating side at contact | \|p\|/A sub / film | Fixed (0.34) |
|---|---|---:|---:|---|---|---|---:|
| LiCoO2(001) \| LiNbF6(001) | 504 (312 + 192) | 88.800 | 1.952 % | Li layer, then O, Co | F layer, NbF6 intact | 2.058 / 0.613 | 104 |
| Li6PS5Cl(111) \| LiNbF6(001), seed 0 | 440 (104 + 336) | 170.708 | 3.006 % | Cl/Li/S layer, PS4 intact | F layer | 0.174 / 0.558 | 38 |
| same cut, seed 4 | 440 (104 + 336) | 172.926 | 2.864 % | same framework cut | F layer | 0.129 / 0.551 | 36 |

All slabs are formally neutral and stoichiometric: LiCoO2 Li78Co78O156, Li6PS5Cl
Li48P8S40Cl8 (8 f.u.), and LiNbF6. ZSL transformations: cathode film [[2,0],[0,2]] /
substrate [[1,4],[0,13]]. Each `build.json` records the full strain tensor, both
transformation matrices, cut shifts, layer compositions, cut-polyhedra counts, input hashes
and the enumeration report. Rebuilding from the same inputs reproduces each `build.json`
exactly.

Points to note:
- The **fixed-atom rule** (bottom 34 % of the substrate z span) fixes 38 atoms in seed 0 and
  36 in seed 4, because the distorted layer spacings differ. The seed comparison therefore
  does not hold the constraint set exactly fixed.
- The electrolyte substrate is thin: 104 atoms (two (111) slab units) under 336 coating
  atoms. This matters for the thickness tests.
- The 0.174 / 0.129 e/Å values are formal, oxidation-state diagnostics (pymatgen convention),
  not electronic dipoles. LiCoO2(001) is strongly formally polar at both terminations; this is
  an unresolved property of the primary cathode contact, not something the build fixes.

Saved for the viewer: `data/petmad/contact_v1_cathode_primary`,
`contact_v1_electrolyte_seed0_Cl` and `contact_v1_electrolyte_seed4_Cl`. Each holds
`initial.extxyz` (as built: offset (0,0), gap 2 Å, before the registry scan),
`interface.json`, `selected.json` and `build.json`.
`scripts/build_structure_viewer.py` discovers them automatically.

## Constraint dependence

Design (declared before running): both primary contacts (cathode; electrolyte seed-0 Cl cut),
fixed substrate fraction 0.17, 0.34 (default) and 0.50, everything else as in the pilot
protocol: 12-point registry scan, FIRE to 0.05 eV/Å on free atoms, joined and both separated
references with the same constraints. `run_petmad_interface.py` now takes `--fixed-fraction`
and `--threads`; the defaults reproduce the pilot settings.

All 18 relaxations converged on free atoms (≤ 0.05 eV/Å). There are no overlap violations,
and the call accounting reconciles. Every run picked the same registry: offset (0,0), gap 2.0 Å.
Cost: 1,208 calculator calls plus 12 single points. The six runs ran concurrently with two
threads each, 236–309 s per run.

`scripts/fixed_geometry_separation.py` splits the relaxed joined interface into its two parts
without re-relaxing them (two single points). This gives the fixed-geometry work of
separation. Its difference from W_adh is exactly the separated slabs' relaxation energy.

| Contact | Fixed fraction (atoms) | W_adh relaxed (J/m²) | W_sep fixed geometry | Film relaxation on separation | Substrate relaxation | Max force on fixed atoms (eV/Å) |
|---|---|---:|---:|---:|---:|---:|
| Cathode | 0.17 (52) | 3.4883 | 5.0558 | 1.4868 | 0.0807 | 2.474 |
| Cathode | 0.34 (104) | 3.4792 | 5.0550 | 1.4861 | 0.0897 | 2.446 |
| Cathode | 0.50 (156) | 3.4708 | 5.0441 | 1.4797 | 0.0936 | 2.445 |
| Electrolyte s0 | 0.17 (26) | 1.2878 | 2.4683 | 0.5655 | 0.6150 | 0.473 |
| Electrolyte s0 | 0.34 (38) | 1.3291 | 2.5190 | 0.5744 | 0.6155 | 0.936 |
| Electrolyte s0 | 0.50 (52) | 1.4114 | 2.5604 | 0.5833 | 0.5657 | 0.880 |

**Cathode: insensitive within the tested constraint bracket.** W_adh spans 0.017 J/m² and
W_sep 0.012 J/m². Forces on fixed atoms stay at about 2.45 eV/Å at every fraction, and
equally in the separated LiCoO2 slab (2.45–2.46 eV/Å). This suggests a residual force
pattern belonging to the formally polar LiCoO2(001) slab rather than to the contact. Similar
forces do not prove that polar-surface energy errors cancel exactly in W_adh. The polarity
remains unresolved. The
separated LiNbF6 slab relaxes by about 1.49 J/m² once the contact is removed, so relaxed
adhesion and fixed-geometry separation differ by about 1.6 J/m². The LiCoO2 side tracks its
joined geometry (RMS 0.06–0.07 Å).

**Electrolyte: sensitive to the constraint.** W_adh rises monotonically by 0.123 J/m² across
the bracket: +0.041 from 0.17 to 0.34, and +0.082 from 0.34 to 0.50. That exceeds the
proposed 0.1 J/m² tolerance. Decomposition from 0.17 to 0.50: +0.092 from the change in
fixed-geometry separation energy (a difference involving the joined structure and both
rigid fragments, not the joined-interface total energy alone); +0.049 from smaller
substrate relaxation; −0.018 from the film. The algebra is exact. It does not establish the
relaxation path or which minimum an isolated fragment would reach. The separated Li6PS5Cl slab relaxes into a different arrangement from the one
in the joined interface: Li RMS 0.55–0.65 Å (maximum 1.7 Å), Cl 0.18–0.30 Å, P ≤ 0.08 Å. That
relaxation is worth about 0.6 J/m², so W_adh here includes Li/Cl rearrangement at the newly
free argyrodite surface as well as adhesion. The substrate has only 104 atoms, of which 26–52
are fixed. A thin slab whose free region shrinks as the fixed fraction grows is the likeliest
cause. **Substrate thickness is therefore the first convergence test for the electrolyte
contact.**

These values are not comparable with the earlier pilots (2.10 and 0.43 J/m²). Facets,
terminations, bulk references and cells all changed, so the differences cannot be attributed
to any single change.

Evidence: `data/petmad/constraint_test_v1/` (per run: result, relaxation records, registry
scan, inspection, fixed-geometry separation, initial/final structures and FIRE logs). The
inspection replays identically from the archive.

## Original sequence before the thickness study

Step 1 is now complete and reported below. The current next-step handoff is
[SYNC_CLAUDE_3.md](https://github.com/DavideTisi/interphAIse/blob/786029128ad234e34aaa880d2bff5250c79277ed/SYNC_CLAUDE_3.md).

1. Electrolyte substrate thickness (3 and 4 layers) at a fixed fixed-*thickness* rule rather
   than a fixed fraction, so the free region near the contact grows with thickness. Then
   repeat the constraint bracket at the converged thickness.
2. Cathode film thickness, given the 1.49 J/m² film relaxation on separation. Then vacuum and
   a denser registry scan (the 2×2 scan gave the same offset everywhere).
3. Seed-4 electrolyte at the chosen settings (bulk sensitivity; the input is prepared).
   Report both relaxed W_adh and fixed-geometry W_sep. Treat the polar cathode as unresolved,
   even if numerically converged.

## Electrolyte substrate thickness (SYNC_CLAUDE_2.md)

Only the substrate thickness changes: seed 0, Cl cut, LiNbF6(001), two coating layers,
the same in-plane transformations, strain tensor and area (170.708 Å²), 15 Å vacuum, FIRE to
0.05 eV/Å. Cap 600 atoms. Fixed **depth** 3.257602 Å from the substrate bottom, which fixes
38 atoms at every thickness (`--fixed-depth`; mutually exclusive with `--fixed-fraction`,
whose default stays 0.34). The same mask is applied to the joined interface and the separated
substrate. The registry is held at offset (0,0), gap 2 Å (`--registry 0 0 2`); the 12-point
scan is still run and saved. `build_contact.py` gains `--substrate-layers`/`--film-layers`;
all builds match the v1 termination, transformations, area and strain tensor. PET-MAD S 1.6.0,
CPU, 4 threads per run, three runs concurrent.

| Layers | Atoms (sub) | Sub span Å | Formal \|p\|/A sub | W_adh relaxed | Δ | W_sep fixed geometry | Δ | Film / sub relaxation on separation | Max force on fixed atoms (interface / separated sub) | Calls | Wall |
|---|---|---:|---:|---:|---:|---:|---:|---|---|---:|---:|
| 2 | 440 (104) | 9.58 | 0.174 | 1.3291 | — | 2.5190 | — | 0.574 / 0.616 | 0.94 / 1.74 | 267 | 287 s |
| 3 | 492 (156) | 15.43 | 0.260 | 1.4644 | +0.135 | 2.8052 | +0.286 | 0.625 / 0.716 | 1.19 / 1.49 | 322 | 375 s |
| 4 | 544 (208) | 21.28 | 0.347 | 1.5317 | **+0.067** | 2.8579 | **+0.053** | 0.636 / 0.690 | 1.28 / 1.39 | 411 | 449 s |

Energies are in J/m², forces in eV/Å. All nine relaxations converged on free atoms, with no
overlap violations, and the accounting reconciles. The 2-layer run reproduces the archived
0.34-fraction run: identical fixed set, film/substrate energies identical, interface energy
−2.4×10⁻⁴ eV (thread-count float noise), W_adh 1.32913 vs 1.32911 J/m².

- **Tolerance:** between the final two settings (3 → 4 layers), both observables change by
  less than 0.1 J/m². **Four layers is the chosen thickness** by the predeclared criterion.
  W_adh is still increasing (+0.135 then +0.067), so this meets the tolerance; it does not
  show a plateau.
- **Registry:** at 3 layers the unrelaxed scan optimum moved to (0, 0.5). The gap from (0,0)
  is 0.1887 eV = 0.0177 J/m² at the single-point level. At 2 and 4 layers (0,0,2 Å) is the
  optimum. This supports holding the registry fixed for the controlled thickness test. It
  does not show that competing registries relax to equivalent energies; relaxed registry
  checks are still needed.
- **Separated-slab rearrangement persists at every thickness:** Li RMS 0.57–0.65 Å and Cl
  0.20–0.33 Å versus the joined substrate, P ≤ 0.08 Å. This supports a free-surface
  contribution. It does not prove that all remaining finite-thickness effects are absent.
- **Formal polarity grows linearly with thickness** (0.174 → 0.260 → 0.347 e/Å): the two
  faces of this Cl cut are inequivalent (Cl/S contact face, S/P far face), so each (111)
  period adds a net formal dipole. This is a formal oxidation-state diagnostic, not a computed
  electronic dipole. Like the cathode, this contact is formally polar, and the polarity grows
  with slab thickness.

Evidence: `data/petmad/thickness_v1/`.

### Constraint check at four layers (declared before running)

Fixed depths 1.628801, 3.257602 (done above) and 6.515204 Å, i.e. half, the same as, and
double the thickness-study depth. These fix 26, 38 and 68 of 208 substrate atoms. Everything
else as in the thickness study, including the registry held at (0,0,2 Å). Criterion: report
the W_adh and W_sep spread. With the frozen depth doubled, both should stay within 0.1 J/m² of
the 3.2576 Å value for the constraint to count as not controlling the result.

**Result.** All nine relaxations converged on free atoms, with no overlap violations; the
accounting reconciles and the scan optimum was (0,0,2 Å) in each run.

| Fixed depth Å (atoms) | W_adh relaxed | W_sep fixed geometry | Film / sub relaxation | Max force on fixed atoms (interface / separated sub) | Calls | Wall |
|---|---:|---:|---|---|---:|---:|
| 1.628801 (26) | 1.5069 | 2.8448 | 0.634 / 0.705 | 0.54 / 0.48 | 395 | 378 s |
| 3.257602 (38) | 1.5317 | 2.8579 | 0.636 / 0.690 | 1.28 / 1.39 | 411 | 449 s |
| 6.515204 (68) | 1.5549 | 2.8688 | 0.638 / 0.676 | 1.12 / 1.27 | 432 | 398 s |

Energies are in J/m², forces in eV/Å. **Both bracket values are within 0.03 J/m² of the
3.2576 Å reference.** Spreads: W_adh 0.048 J/m² (0.123 at two layers), W_sep 0.024 J/m². At
four layers the result is **insensitive within the tested constraint bracket at the 0.1 J/m²
tolerance**, not independent of the constraint: a small monotonic trend with frozen depth
remains. The 3.2576 Å reference run belongs to both tables; the five unique runs used 1,827
calls. Li/Cl rearrangement of the
separated slab is unchanged (Li RMS 0.57–0.59 Å).

**Current electrolyte protocol:** four substrate layers (544 atoms), fixed depth 3.2576 Å,
registry (0,0,2 Å). Provisional values: W_adh 1.53 J/m², W_sep 2.86 J/m². These are
numerical-protocol results for one PET-MAD model and one formally polar Cl cut, not
experimental adhesion.

**Next (not run):** cathode coating thickness (the separated LiNbF6 relaxes by about
1.49 J/m²), then vacuum and denser registry checks for both contacts. Then seed 4 with this
protocol and the equivalent Cl cut, recording any seed-dependent fixed count. The polar
cathode stays provisional.

The bounded cathode plan in [SYNC_CLAUDE_3.md](https://github.com/DavideTisi/interphAIse/blob/786029128ad234e34aaa880d2bff5250c79277ed/SYNC_CLAUDE_3.md) uses two, three
and four coating layers at unchanged substrate geometry and an 800-atom cap.
Geometry-only checks give 504, 600 and 696 atoms. These are not additional
relaxation results.

## Cathode coating thickness (SYNC_CLAUDE_3.md)

Only the number of LiNbF6 layers changes: LiCoO2(001) | LiNbF6(001), termination
`F2_P-6_3`/`Li_P6/mmm_1`, two substrate layers (312 atoms), the same bulk inputs,
transformations, strain (1.952 %), area (88.800 Å²) and 15 Å vacuum. Cap 800 atoms. Registry
held at (0,0,2 Å); the scan is saved. The constraint is a 0.34 fraction of the unchanged
substrate. It was checked by **substrate-relative** site correspondence, because global
indices change when coating atoms are added: the same 104 substrate sites at every thickness,
identical to the archived constraint-test mask. Substrate internal geometry is identical to
10⁻⁸ Å; in the thicker cells the whole substrate is rigidly shifted along z (0.75 and 1.29 Å),
which does not change the energy in a vacuum-padded periodic cell. All three cases were run
with the same script. The 2-layer run reproduces the archived 0.34-fraction run (energies
within 2.4×10⁻⁴ eV).

| Coating layers | Atoms (film) | Formal \|p\|/A film / sub | W_adh relaxed | Δ | W_sep fixed geometry | Δ | Film / sub relaxation | Max force on fixed atoms | Calls | Wall |
|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|
| 2 | 504 (192) | 0.613 / 2.058 | 3.4794 | — | 5.0551 | — | 1.486 / 0.090 | 2.446 | 144 | 138 s |
| 3 | 600 (288) | 0.920 / 2.058 | 3.5855 | +0.106 | 5.1090 | +0.054 | 1.443 / 0.081 | 2.446 | 146 | 154 s |
| 4 | 696 (384) | 1.226 / 2.058 | 3.6001 | **+0.015** | 5.1275 | **+0.019** | 1.441 / 0.086 | 2.446 | 136 | 166 s |

Energies are in J/m², forces in eV/Å. All nine relaxations converged on free atoms, with no
overlap violations; the accounting reconciles and the scan optimum was (0,0,2 Å) at every
thickness. Cost: 426 calls plus 6 separation single points; 4 threads, 3 concurrent.

- **Between the final two settings (3 → 4) both observables change by less than 0.1 J/m²**,
  and the trend flattens (+0.106 → +0.015 for W_adh). **Four coating layers is chosen** by the
  same rule as the electrolyte. Flattening across two increments is not proof of a plateau.
- The separated LiNbF6 slab relaxes by about 1.44–1.49 J/m² at every thickness, moving
  0.14–0.20 Å RMS (0.7 Å maximum) from its joined geometry. That is consistent with a
  contribution from the freed F-terminated surface rather than from finite thickness.
- Fixed-atom forces in the LiCoO2 substrate stay at 2.446 eV/Å. The coating's formal polarity
  grows linearly with thickness. **Both contacts remain formally polar and provisional.** The
  cathode statement stays "insensitive within the tested constraint bracket".

**Current cathode protocol:** two substrate layers, four coating layers (696 atoms), 0.34
fraction, registry (0,0,2 Å). Provisional values: W_adh 3.60, W_sep 5.13 J/m².

**Next (not run):** vacuum, then **relaxed** registry checks for both contacts (relax a small
declared set of competing registries; single-point ranking alone is insufficient), then
seed 4 at the selected electrolyte protocol with the equivalent Cl cut. The cathode substrate
thickness has not been varied.

Evidence: `data/petmad/cathode_thickness_v1/` (builds and runs).

### Review and next-step qualification

The independent review at `84f1c76` confirms the archived coating-thickness
energies, nine converged relaxations, accounting and physical fixed-mask
correspondence. See [SYNC_CLAUDE_4.md](https://github.com/DavideTisi/interphAIse/blob/786029128ad234e34aaa880d2bff5250c79277ed/SYNC_CLAUDE_4.md) for the bounded vacuum
check and remaining thickness gaps: LiCoO2 substrate thickness and the coating
thickness at the electrolyte contact have not been varied independently.
The cathode constraint bracket belongs to the original two-coating-layer
geometry. Four coating layers is the selected working setting, not a claim
that the whole contact is thickness-converged or its polarity resolved.

## Vacuum (SYNC_CLAUDE_4.md)

Working geometries: cathode with 2 substrate + 4 coating layers (`cathode_thickness_v1/run_F4`);
electrolyte seed 0 with 4 substrate + 2 coating layers (`thickness_v1/run_L4`). For vacuum
15 / 20 / 25 Å, the normal cell vector was lengthened by (vacuum − 15 Å) without scaling
coordinates. Single points were evaluated on the saved relaxed interface, both relaxed
references (same fixed masks) and both rigid fragments of the relaxed interface
(`scripts/vacuum_check.py`; 30 single points). The 15 Å recomputation reproduces the stored
energies (≤ 2.4×10⁻⁴ eV).

| Contact | Vacuum Å | Actual empty gap (interface) Å | W_adh | W_sep | Max free force interface / film / sub (eV/Å) |
|---|---:|---:|---:|---:|---|
| Cathode | 15 / 20 / 25 | 15.51 / 20.51 / 25.51 | 3.600092 / 3.600136 / 3.600136 | 5.127540 / 5.127496 / 5.127540 | 0.0448 / 0.0371 / 0.0455 (unchanged) |
| Electrolyte | 15 / 20 / 25 | 15.74 / 20.74 / 25.74 | 1.531726 (all) | 2.857898 / 2.857875 / 2.857898 | 0.0499 / 0.0300 / 0.0496 (unchanged) |

Energies are in J/m². Changes are at most 4.4×10⁻⁵ J/m² (float noise), and free forces are
identical and within the 0.05 eV/Å target, so no further relaxation was needed. This outcome
is expected by construction: PET-MAD S 1.6.0 builds its graph from an 8.0 Å neighbour list
(model interaction range 24 Å through message passing). With every empty gap above 15 Å, no
edge crosses the vacuum. **This is a numerical periodic-image isolation check for a
finite-range model. It does not describe or resolve real polar-surface electrostatics, which
this model does not contain.** 15 Å is kept.

Evidence: `data/petmad/vacuum_v1/`.

## Remaining thickness directions (SYNC_CLAUDE_4.md)

**Cathode substrate thickness** (coating 4 layers held; 2 / 3 / 4 LiCoO2 layers). Frozen
**depth** 9.10044154 Å, which reproduces the baseline's 104 physical bottom-plane atoms in
every build (checked by species and height above the substrate bottom). Registry held at
(0,0,2 Å). Cap 1,200 atoms for this study, above the earlier 800, stated explicitly.
Formal LiCoO2 |p|/A grows 2.058 / 3.088 / 4.117 e/Å.

| LiCoO2 layers | Atoms | W_adh | W_sep | Film / sub relaxation | Max force on fixed atoms | Calls | Wall |
|---|---:|---:|---:|---|---:|---:|---:|
| 2 (`cathode_thickness_v1/run_F4`) | 696 | 3.6001 | 5.1275 | 1.441 / 0.086 | 2.446 | 136 | 166 s |
| 3 | 852 | 3.6011 | 5.1278 | 1.441 / 0.086 | 2.445 | 136 | 356 s |
| 4 | 1,008 | 3.6009 | 5.1275 | 1.441 / 0.086 | 2.445 | 136 | 401 s |

Changes are ≤ 0.001 J/m². **Two LiCoO2 layers is kept.** The fixed-atom forces and the large
LiNbF6 relaxation on separation do not depend on substrate thickness.

**Electrolyte coating thickness** (4 argyrodite layers held, seed-0 Cl cut, frozen depth
3.257602 Å = 38 atoms with the same physical planes; 2 / 3 / 4 LiNbF6 layers; registry held).
Coating formal |p|/A 0.558 / 0.837 / 1.116 e/Å.

| LiNbF6 layers | Atoms | W_adh | Δ | W_sep | Δ | Film / sub relaxation | Calls | Wall |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| 2 (`thickness_v1/run_L4`) | 544 | 1.5317 | — | 2.8579 | — | 0.636 / 0.690 | 411 | 449 s |
| 3 | 712 | 1.6198 | +0.088 | 2.9525 | +0.095 | 0.619 / 0.714 | 366 | 621 s |
| 4 | 880 | 1.6329 | **+0.013** | 2.9669 | **+0.014** | 0.617 / 0.718 | 416 | 753 s |

Energies are in J/m², forces in eV/Å. Between the final two settings both observables
change by about 0.01 J/m², so **four coating layers is chosen** (same rule as the cathode
side). All 12 relaxations converged on free atoms, with no overlaps; the accounting
reconciles and the scan optimum was (0,0,2 Å) in each run. The separated-argyrodite Li
rearrangement persists (substrate RMS 0.41 Å vs joined). Cost: 1,054 calls plus 8
single points; 3 threads × 4 concurrent.

**Working protocols and provisional values:**
- Cathode: 2 LiCoO2 + 4 LiNbF6 layers (696 atoms), 0.34 fraction = 104 atoms (= depth
  9.10 Å), registry (0,0,2 Å), 15 Å vacuum. **W_adh 3.60, W_sep 5.13 J/m².**
- Electrolyte (seed 0, Cl cut): 4 Li6PS5Cl + 4 LiNbF6 layers (880 atoms), depth 3.2576 Å =
  38 atoms, registry (0,0,2 Å), 15 Å vacuum. **W_adh 1.63, W_sep 2.97 J/m².**

Scope: these are model results for two separate strained contact cells, not one
continuous film and not experimental adhesion. Each constraint bracket was measured at
two coating layers: cathode at 2 + 2, electrolyte at 4 + 2. Neither was repeated at the
working geometry. Both contacts are formally polar, with polarity growing with slab
thickness. That is unresolved by any of these numerical checks. **Next (not run):**
relaxed checks of a small declared set of competing registries, then seed 4 at the
working electrolyte protocol with the equivalent Cl cut.

Evidence: `data/petmad/thickness_gaps_v1/`.

## Final-geometry constraint endpoints and relaxed registry set (SYNC_CLAUDE_5.md; declared before running)

**Scope note on vacuum.** The vacuum sweep above used the 544-atom electrolyte (4 + 2 layers).
The final 880-atom interface has a 15.73 Å empty gap, but it has not been swept separately.
A 15-vs-25 Å single-point confirmation on it follows below.

**Reused references** (settings verified: checkpoint, registry (0,0,2 Å), constraint rule,
FIRE 0.05 eV/Å, 400-step limit; only the thread count differs):
`cathode_thickness_v1/run_F4` (696 atoms, 0.34 fraction = 104 atoms) and
`thickness_gaps_v1/run_electrolyte_S4_F4` (880 atoms, depth 3.257602 Å = 38 atoms).

**Constraint endpoints, four new runs.** Cathode 696 atoms: fractions 0.17 and 0.50 of the
unchanged two-layer substrate. Electrolyte 880 atoms: depths 1.628801 and 6.515204 Å.
Registry (0,0,2 Å) and all other working settings unchanged. Criterion: the full-bracket
spread of W_adh and of W_sep, reported against 0.1 J/m². A failure is kept and reported
before any registry gain is interpreted.

**Relaxed registry set, six new runs.** For each final contact: fractional matched-cell
in-plane offsets (0,0) [reused], (0,0.5), (0.5,0), (0.5,0.5), all at an initial gap of 2 Å,
with the reference constraint (cathode 0.34 fraction; electrolyte depth 3.257602 Å). This is
a coarse relaxed check on the existing lateral grid, not a search over translations, gaps,
terminations or facets. Failed and converged outcomes are both kept, and we record whether
distinct starts relax to the same arrangement.

**Selection rule:** among converged runs with the same atom count, composition and cell,
select the **lowest relaxed joined-interface energy**, not the largest W_adh. For every
registry we report the joined energy relative to the lowest, W_adh, W_sep and both
separated-reference energies. Reference policy: each run uses its own separated references,
relaxed from its own starting geometry, as `run_petmad_interface.py` does. These are in-plane
translations of the same slabs, so their energies should agree; any difference is reported
as a reference-minimum difference.

**Then seed 4:** same layer counts (4 + 4), mapped Cl cut, fixed-depth rule and the *same*
selected fractional registry as seed 0, with cell, strain and fixed-count differences
recorded.

### Results

All 30 new relaxations (10 runs) converged on free atoms, with no overlap violations; the
accounting reconciles. Cost: 2,826 calculator calls plus 20 separation single points. One
thread per run, ten runs concurrent.

**Constraint endpoints at the final geometries** (energies in J/m²):

| Contact | Setting | W_adh | W_sep |
|---|---|---:|---:|
| Cathode 696 | fraction 0.17 / **0.34** / 0.50 | 3.6094 / **3.6001** / 3.5962 | 5.1272 / **5.1275** / 5.1277 |
| Electrolyte 880 | depth 1.6288 / **3.2576** / 6.5152 Å | 1.6083 / **1.6329** / 1.6565 | 2.9552 / **2.9669** / 2.9781 |

Spreads: cathode 0.013 / 0.0005; electrolyte 0.048 / 0.023 J/m². Both contacts are
**insensitive within the tested constraint bracket at the 0.1 J/m² tolerance**, now at
their working geometries. A small monotonic trend remains on the electrolyte side.

**Registry set: degenerate by construction.** The declared offsets are fractions of the
matched supercell, and several of them are lattice translations of one slab:
- **Cathode:** the film supercell is [[2,0],[0,2]] LiNbF6 cells, so (0,0), (0,0.5), (0.5,0)
  and (0.5,0.5) are the same structure. The unrelaxed scan energies are bit-identical
  (−4687.49561 eV) and all relaxed results coincide (W_adh 3.600136). **One physical registry
  was sampled.** The same holds for every earlier cathode registry scan, which carried no
  registry information.
- **Electrolyte:** the substrate supercell is [[2,0],[0,1]], so (0.5,0) ≡ (0,0) and
  (0.5,0.5) ≡ (0,0.5). **Two distinct registries were sampled**, each relaxed twice.

| Electrolyte registry | Joined energy above lowest | W_adh | W_sep |
|---|---:|---:|---:|
| A (0,0) | +0.0010 eV | 1.6329 | 2.9669 |
| A (0.5,0) | 0 (lowest) | 1.6331 | 2.9672 |
| B (0,0.5) | +0.0151 eV (0.0014 J/m²) | 1.6316 | 3.0647 |
| B (0.5,0.5) | +0.0181 eV (0.0017 J/m²) | 1.6313 | 3.0640 |

Registry B starts 0.70 eV (0.066 J/m²) higher before relaxation, but relaxes to within
0.018 eV of A. **Review correction:** the repeated A runs differ by 0.000977 eV;
the repeated B runs differ by 0.002930 eV, not less than 0.001 eV. These are observed
optimizer/numerical variations, not a general uncertainty bound. The separated references
are identical across registries (within 4×10⁻⁴
eV), as expected for translated copies. **Selection (lowest joined energy): registry A,
i.e. (0,0) is kept.** W_adh is registry-robust (±0.002 J/m²). W_sep differs by about
0.1 J/m² between A and B, because the two registries relax into different joined
arrangements at nearly equal energy. Fixed-geometry W_sep is therefore the less robust
observable.

**Cathode registry diagnostic** (unrelaxed single points on a 6 × 6 offset grid at 2 Å; not
part of the declared set): the 36 offsets fall into 9 distinct registries. Their energies
span 0.045 eV = **0.008 J/m²**, with (0,0) the lowest. The cathode registry landscape is
flat at this level. A relaxed follow-up could use the two most distinct classes, (1/3,1/3)
and (1/6,0); it is proposed, not run.

**Vacuum at the final electrolyte geometry** (880 atoms, 15 vs 25 Å, single points): W_adh
1.632936 and W_sep 2.966905 J/m² at both; relaxed forces within target; stored energies
reproduced. Evidence: `data/petmad/vacuum_v1/electrolyte_final880.json`.

**Working values (unchanged):** cathode **3.60 / 5.13 J/m²** (696 atoms); electrolyte
**1.63 / 2.97 J/m²** (880 atoms). Both are formally polar and provisional. **Next:** seed 4
at 4 + 4 layers with the mapped Cl cut, depth rule and registry (0,0).

Evidence: `data/petmad/final_checks_v1/`.

## Niflheim batch 1: seed 4, distinct cathode registries, GPU references (SYNC_CLAUDE_6.md; declared before running)

Five runs, no more. All on RTX 3090 (`sm3090el9_devel`, 1 GPU, 4 CPUs), using the isolated
env, checkpoint `3f52e97c…` and one immutable code snapshot per job (`CODE=code_<commit>`).
Runner plus rigid-fragment separation in the same job on CUDA. 15 Å vacuum, initial gap
2 Å, FIRE 0.05 eV/Å, 400-step limit. Outputs go to
`/home/scratch12/davti/OSI_Hackathon/runs/niflheim_batch1/<name>`.

| # | Name | Input build | Constraint | Registry |
|---|---|---|---|---|
| 1 | `cathode_ref` | `cathode_thickness_v1/build_F4` (696) | fraction 0.34 = 104 atoms | (0, 0) |
| 2 | `cathode_reg_third_third` | same | same | (1/3, 1/3) |
| 3 | `cathode_reg_sixth_0` | same | same | (1/6, 0) |
| 4 | `electrolyte_seed0_ref` | `thickness_gaps_v1/build_electrolyte_S4_F4` (880) | depth 3.257602 Å | (0, 0) |
| 5 | `electrolyte_seed4` | `contact_v2_electrolyte_seed4_S4F4` (880) | depth 3.257602 Å | (0, 0) |

The cathode offsets (1/3,1/3) and (1/6,0) are the most distinct registry classes in the 6 × 6
unrelaxed diagnostic: +0.0081 and +0.0031 J/m² relative to (0,0), with no overlap
violations. Runs 1 and 4 are GPU references, so each comparison uses one device.

**Seed-4 input** (`scripts/build_contact.py`; seed-4 bulk, termination `Cl2_P-1_2`,
4 + 4 layers). Its framework signature on both faces is identical to the seed-0 4 + 4 build
(contact Cl(0.00)/S(0.85)/S(0.75); far S(0.38)/P(0.50)/S(0.75)). Same composition
(Li96P16S80Cl16 + Li84Nb84F504), no cut PS4 or NbF6, no overlaps. Differences from seed 0:
area 172.926 vs 170.708 Å²; strain 2.864 vs 3.006 %; formal substrate |p|/A 0.257 vs 0.347
e/Å; fixed atoms at 3.2576 Å are 36 (Li12P4S20) vs 38 (Cl2Li12P4S20). The matcher chose
different supercell bases (film [[1,5],[0,7]] / substrate identity vs [[1,3],[0,7]] /
[[2,0],[0,1]]). The same fractional registry (0,0) is therefore not guaranteed to be the same
physical lateral alignment. The seed comparison holds the cut, layer counts, depth rule and
fractional registry fixed; it does not hold the supercell basis fixed.

**Rules.** Cathode registries: compare relaxed joined energies only within the identical
cell, composition and mask, keeping each run's own references. Seeds: compare both works at
the same fractional registry, report every geometry difference, and do not rank seeds by
total energy. 0.1 J/m² is the reporting tolerance, not a trigger for more settings.
Failures and exhausted runs are kept and reported.

### Batch 1 results

Code `279e2b1`, checkpoint `3f52e97c…`. Jobs 11013920–11013924 on s001 (`sm3090el9_devel`,
1 RTX 3090, 4 CPUs each), all COMPLETED in 2:43–2:57. Both the relaxations and the
rigid-fragment separation ran on CUDA. All 15 relaxations converged on free atoms, with no
overlap violations; the accounting reconciles. The off-grid registries added exactly one
scan point each (13 instead of 12). Cost: 1,216 calculator calls plus 10 separation single
points; runner wall time 61–85 s per run.

**Device check.** GPU seed-0 electrolyte reference: W_adh 1.6334 / W_sep 2.9672, against
1.6329 / 2.9669 J/m² from local CPU. GPU cathode reference: 3.6004 / 5.1277, against
3.6001 / 5.1275. Differences ≤ 5×10⁻⁴ J/m².

**Cathode registries** (same 696-atom cell, composition and 104-atom mask; all on GPU):

| Registry | Unrelaxed rank (6 × 6 grid) | Relaxed joined energy vs (0,0) | W_adh | W_sep | Film / sub relaxation |
|---|---|---:|---:|---:|---|
| (0,0) | lowest | 0 | 3.6004 | 5.1277 | 1.441 / 0.086 |
| (1/6,0) | +0.0031 J/m² | +0.0186 eV | 3.5970 | 5.0908 | 1.409 / 0.085 |
| **(1/3,1/3)** | highest (+0.0081 J/m²) | **−0.0927 eV (−0.0167 J/m²)** | **3.6171** | **5.1676** | 1.443 / 0.107 |

The separated references agree within 2×10⁻⁴ eV (in-plane translations). The relaxed order
inverts the unrelaxed one: the highest-ranked unrelaxed registry relaxes to the lowest
joined energy. **By the declared rule, (1/3,1/3) becomes the working cathode registry.**
Across the three relaxed registries, W_adh spans 3.597–3.617 and W_sep 5.091–5.168 J/m²,
both within 0.1 J/m². Three distinct relaxed registries out of nine classes is a coarse
check, not a registry search.

**Seed sensitivity** (both on GPU, same mapped Cl cut, 4 + 4 layers, depth 3.2576 Å,
fractional registry (0,0)):

| Bulk reference | Area Å² | Strain | Fixed atoms | W_adh | W_sep | Film / sub relaxation |
|---|---:|---:|---:|---:|---:|---|
| Seed 0 | 170.708 | 3.006 % | 38 | 1.6334 | 2.9672 | 0.616 / 0.717 |
| Seed 4 | 172.926 | 2.864 % | 36 | **1.5120** | **2.8054** | 0.595 / 0.699 |

Seed 4 is lower by **0.121 (W_adh) and 0.162 (W_sep) J/m², which exceeds the 0.1 J/m²
reporting tolerance.** It is a combined sensitivity: bulk Li/Cl arrangement, strain, area,
supercell basis and fixed count all differ. The fractional registry (0,0) is not
guaranteed to be the same physical alignment in the two bases. Seed 4's unrelaxed scan
preferred (0,0.5), and its registry was not explored, by design. Total energies of the two
seeds are not compared.

**Working values after batch 1** (provisional; formally polar contacts):
- Cathode, registry (1/3,1/3): **W_adh 3.62, W_sep 5.17 J/m²**; registry range 3.60–3.62 /
  5.09–5.17.
- Electrolyte, seed 0, registry (0,0): **W_adh 1.63, W_sep 2.97 J/m²**; registry range of
  W_sep 2.97–3.06. **Bulk-reference (seed) sensitivity is about 0.12 (W_adh) and 0.16 (W_sep)
  J/m²**, which is now the largest documented uncertainty on the electrolyte side.

Evidence: `data/petmad/niflheim_batch1/` (results, records, scans, separation, structures,
FIRE logs, filtered job logs, `sacct`).

### Independent batch review and scope qualification

The archive review at `f1861ef` confirms the five runs, 15 relaxation force
records, fixed masks, geometry gates, work arithmetic and call accounting.
See [SYNC_CLAUDE_7.md](https://github.com/DavideTisi/interphAIse/blob/786029128ad234e34aaa880d2bff5250c79277ed/SYNC_CLAUDE_7.md). “Largest documented uncertainty” above
should be read as **largest quantified sensitivity tested so far**: the
polar-model error is unquantified. The seed difference is a combined
bulk-reference/construction effect, not an isolated disorder effect or an
ensemble error estimate. Earlier cathode constraint/thickness brackets were
measured at (0,0), not the newly selected (1/3,1/3); retain that scope.
Recommendation: publish the bounded study and defer further seed-4 registry
runs. Numerical tolerance failure is a reportable outcome, not a trigger to
extend the sample until it passes.
