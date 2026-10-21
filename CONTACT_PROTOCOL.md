# Primary contacts — termination mapping, builds and constraint check

21 October 2026, `davide`. Follows [SYNC_CLAUDE_1.md](SYNC_CLAUDE_1.md) and
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

## Next (not run)

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
  optimum.
- **Separated-slab rearrangement persists at every thickness:** Li RMS 0.57–0.65 Å and Cl
  0.20–0.33 Å versus the joined substrate, P ≤ 0.08 Å. It is a free-surface effect, not a
  thin-slab artefact.
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
3.2576 Å reference.** Spreads: W_adh 0.048 J/m² (0.123 at two layers), W_sep 0.024 J/m². The
criterion is met, so the constraint does not control the result at four layers within this
bracket. A small monotonic trend with frozen depth remains. Li/Cl rearrangement of the
separated slab is unchanged (Li RMS 0.57–0.59 Å).

**Current electrolyte protocol:** four substrate layers (544 atoms), fixed depth 3.2576 Å,
registry (0,0,2 Å). Provisional values: W_adh 1.53 J/m², W_sep 2.86 J/m². These are
numerical-protocol results for one PET-MAD model and one formally polar Cl cut, not
experimental adhesion.

**Next (not run):** cathode coating thickness (the separated LiNbF6 relaxes by about
1.49 J/m²), then vacuum and denser registry checks for both contacts. Then seed 4 with this
protocol and the equivalent Cl cut, recording any seed-dependent fixed count. The polar
cathode stays provisional.
