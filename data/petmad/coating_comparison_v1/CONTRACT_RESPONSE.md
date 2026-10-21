# Reply to the field contract (Adem's `data/experiments/llm_petmad_pilot_v1/CONTRACT.md`, `2d2cac3`)

22 October 2026, Claude (PET-MAD side), branch `work/petmad-comparison`.

**Agreed:** the campaign index `data/petmad/coating_comparison_v1/index.json` with your schema; your
`feedback_bundle` as the consumer-side bundle; selection by lowest valid `joined_energy_eV` within
one comparable cell; `weaker_contact = unresolved` below 0.1 J/m² or when either contact is
invalid; sensitivity values withheld; pending primary runs block the decision; missing work is
never zero. Your reader's independent re-checks (checkpoint, convergence, area/atoms, W_adh and
W_sep recomputed from source files) are exactly what Codex's review asks for on the consumer side.

## Requested additions (I will emit these; please accept them in `load_index`)

1. **Exact coverage.** The index will contain one run entry for *every* planned primary and
   sensitivity job from the frozen manifest, written before any energy as `status: "pending"`.
   Please refuse to build a decision bundle unless every planned primary entry for the revealed
   coating is `valid` or `failed` (your "pending blocks" rule), and refuse unknown or duplicate
   `run_id`s. Each entry also carries `registry_id` (`R1`–`R3`), `planned_in_manifest_sha256` and
   `gap_A`.
2. **Fixed rule.** `fixed_fraction` cannot express the electrolyte rule (a fixed **depth**). Replace
   it with `fixed_rule: {"fraction": 0.34}` *or* `{"depth_A": 3.257602}`. Add `n_fixed` and
   `fixed_species` (a dict) so the physical mask is part of the comparability check, not just
   `n_atoms`/`area_A2`.
3. **Comparable cell.** Add `build_sha256` (of the frozen `interface.json`) and `contact_build_id`.
   Registries of one contact share these by construction. A sensitivity build has its own ID and
   is never grouped with the primary registries.
4. **Costs.** Add `separation_single_points` (2 for a valid separation). A failed run keeps its
   known `calculator_calls`/`wall_seconds`, or `null` if unknown, never 0. `reused_from` marks
   reused archive work.
5. **Unavailable sensitivity.** `status` may also be `not_run_resource_limit` (the LiCaAlF6
   electrolyte thickness increment needs 1,302 atoms, above the 1,250 cap). Treat it as terminal
   and non-numeric.
6. **Warnings vs limitations.** `warnings` holds observed numerical/geometry notes for that run
   (e.g. broken Al–F bonds at the cut, formal polarity). Model-wide limitations stay in the menu
   `limitations`.

## Menu (revalidated at the uniform 1,250-atom cap; see SCREENING_REPORT.md and the manifest)

LiNbF6 reference plus **three** unevaluated alternatives: LiTaF6 (001), LiCaAlF6 (100) and LiF (110).
LiZr2(PO4)3 is excluded. Your runner's ≥ 3 check passes without `allow_small_menu`.

## Producer-side gates (already implemented)

`scripts/build_primary_feedback.py` (schema `petmad-primary-feedback-v2`) enforces the same contract
on my side before I hand over a package: exact manifest coverage, comparability (registry,
force target/step limit, candidate/contact identity, atom count, area, composition, fixed
mask), and recomputed W_adh/W_sep. Tests: `tests/test_primary_feedback.py`. Please treat my
bundle as a cross-check of yours, not a replacement. The decision prompt should use your
bundle built from the index.
