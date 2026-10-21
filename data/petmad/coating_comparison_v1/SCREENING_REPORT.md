# Coating construction screen — feasible menu (no interface energies)

22 October 2026, branch `work/petmad-comparison`. Implements step 1 of SYNC_CLAUDE_9.md under
the bounds of LLM_PETMAD_PILOT_PLAN.md / SYNC_CLAUDE_8.md. **No interface energy was computed
for any coating in this screen.** The only new PET-MAD calculations are the LiF and LiTaF6 bulk
references (389 calculator calls, 29.6 s, CPU).

## Result

| Coating | ID | Frozen sulfide penalty (eV/non-Li atom) | Acceptable | Both contacts constructible? | Facet used |
|---|---|---:|---|---|---|
| LiNbF6 | mp-aaacjjwh | 0.0288 | yes | **yes** (reference) | (001), F-terminated |
| LiTaF6 | mp-aaacjmqp | 0.0271 | yes | **yes** | (001), F-terminated |
| LiF | mp-aaaaabru | 0.3104 | no | **yes** | (110) |
| LiCaAlF6 | mp-aaaaajby | 0.0477 | yes | **no** | — |
| LiZr2(PO4)3 | mp-aaabevhd | 0.0563 | no | **no** | — |

**The feasible menu is LiNbF6 plus two unevaluated alternatives (LiTaF6, LiF), one fewer than the
three the adaptive design requires.** Per the plan, this is reported before any live LLM call.
With two alternatives, the round-2 choice is between two materials and the round-3 choice is
forced; a forced final choice must not be presented as adaptive selection.

## Frozen construction rules used

- **Substrates (reviewed, unchanged):** LiCoO2(001) `Li_P6/mmm_1`, 2 layers (26.77 Å), fixed
  depth 9.10044154 Å; seed-0 Li6PS5Cl(111) mapped Cl cut `Li6Cl_P1_7`, 4 layers (21.28 Å), fixed
  depth 3.257602 Å. Bulk inputs are the PET-MAD unconstrained minima (`bulk_relaxation_v1`,
  plus `bulk/` here for LiF and LiTaF6).
- **Coating facets:** all symmetry-distinct facets with index ≤ 1, with the same coating facet on
  both contacts.
- **Matching:** area tier 300 Å² first, then 600 Å²; ZSL length 5 %, angle 3 %, area ratio 10 %;
  strain ≤ 6 %; **cap 1,200 atoms**.
- **Coating thickness (shared rule):** the smallest layer count whose coating span is ≥ **40 Å**,
  about 3 LiNbF6(001) layers. This is where LiNbF6's own coating-thickness test changed by
  ≤ 0.02 J/m². No slab is thinned to pass the atom cap. The thickness-sensitivity job is one
  extra layer.
- **Gates:** formally neutral, stoichiometric film and substrate slabs; no overlaps; **no cut PS4
  or PO4**. Broken coating cation–ligand bonds are counted per area and reported, not
  automatically rejected.
- **Ordering among admissible builds (frozen):** fewest broken cation–ligand bonds per area,
  then lower total formal polarity, then fewer atoms, then lower strain, then termination label.
- **Each termination is enumerated separately with its own cap** (12 per termination per tier).
  An earlier pass with one shared cap hid the F-terminated LiNbF6(001) cathode cut; that pass
  (`runs/coating_screen_v2`) is superseded.

LiNbF6(001) F-terminated at 4 layers (53.4 Å) is exactly the archived reference geometry (696
cathode / 880 electrolyte atoms), so the archived LiNbF6 results are compatible with these
rules.

## Feasible builds (best by the ordering)

| Coating, contact | Atoms | Area Å² | Strain | Coating layers / span | Termination | Broken bonds per Å² | Formal \|p\|/A coating |
|---|---:|---:|---:|---|---|---:|---:|
| LiNbF6 (001), cathode | 696 | 88.8 | 1.95 % | 4 / 53.4 Å | F2_P-6_3 | 0 | 1.226 |
| LiNbF6 (001), electrolyte | 880 | 170.7 | 3.01 % | 4 / 53.4 Å | F2_P-6_3 | 0 | 1.116 |
| LiTaF6 (001), cathode | 696 | 88.8 | 1.45 % | 4 / 53.3 Å | F2_P-6_3 | 0 | 1.228 |
| LiTaF6 (001), electrolyte | 880 | 170.7 | 3.32 % | 4 / 53.3 Å | F2_P-6_3 | 0 | 1.118 |
| LiF (110), cathode | 708 | 82.0 | 3.14 % | 15 / 41.1 Å | LiF_Pmmm_2 | 0.342 (Li–F) | 0.006 |
| LiF (110), electrolyte | 1,108 | 170.7 | 1.55 % | 15 / 41.1 Å | LiF_Pmmm_2 | 0.351 (Li–F) | 0.006 |

Alternatives that were also admissible but rank lower: LiNbF6(101) on both contacts, and LiF(111)
on both (polar, 3.04 e/Å, 0.44 broken bonds per Å²). The LiCoO2 substrate is formally polar
(2.058 e/Å) at every contact.

## Failures (kept as records)

- **LiCaAlF6:** cathode builds exist on (100), (001), (110), (101) and (111), several with broken
  Al–F bonds. The electrolyte side fails on every facet. (110) has no lattice match within
  600 Å². (001) needs ≥ 2,320 atoms (≥ 427 Å²; truncated, but the smallest areas come first).
  (101) and (111) need ≥ 2,460 atoms. **(100) is a near miss: 256 Å², 10 layers reach 40 Å, and
  1,212 atoms exceed the 1,200 cap by 12.** No bound was changed to admit it; amending the cap is
  a scope decision for Davide/Codex, not part of this screen.
- **LiZr2(PO4)3:** no electrolyte lattice match except (001), which needs ≥ 2,456 atoms at
  598 Å². Cathode builds exceed the atom cap (two layers already span about 43 Å) and most
  facets cut PO4.

## Feedback contract (for Adem)

`scripts/build_primary_feedback.py` assembles schema `petmad-primary-feedback-v1` from completed
runs, using the F2 gate. Each contact records every planned registry (valid or failed, with null
works), the selected registry (lowest relaxed joined energy among valid runs), W_adh/W_sep and
their registry ranges, convergence and free/fixed forces, separated-versus-joined
reconstruction by element, device, calls and wall time. The bundle summary gives the weaker
contact (`unresolved` if the gap is < 0.1 J/m² or a value is null) and the minimum W_adh.
Sensitivity checks are `pending` with null values. Observed failures and model limitations
are listed separately. `feedback_example/` is the bundle built from the real archived LiNbF6
runs (cathode: 3 distinct registries on GPU; electrolyte: 2 distinct registries, one on GPU and
one on CPU, differing by ≤ 5×10⁻⁴ J/m²).

## Not done yet

The registry representatives for LiTaF6/LiF (geometric equivalence classes, no energies) and
the frozen manifest. Interface energies for a new coating will be computed only after Adem
archives its selection.
