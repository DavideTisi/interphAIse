# Field contract v2: PET-MAD campaign index ↔ LLM pilot (agreed with Claude, CONTRACT_RESPONSE.md at 38e4872)

22 October 2026, Adem. Implemented in `interphaise/pilot.py`, which provides the shared evidence interface
used by both the pilot and `scripts/analyse_mlip_comparison.py`. Tested in `tests/test_pilot.py` (real index
fixture `tests/fixtures/coating_comparison_v1_index_38e4872.json`) and `tests/test_mlip_comparison.py`.

## Index: `data/petmad/coating_comparison_v1/index.json` (written by Claude)

**Top level:** `schema_version`, `checkpoint_sha256`, `manifest_sha256`, `menu`, `runs` and `cohort`.

**Fields of each run:**
- identity: `run_id`, `candidate_id`, `contact`, `role`, `sensitivity_kind`, `registry_id`, `registry`, `gap_A`;
- build and mask: `fixed_rule` (`{"fraction": f}` or `{"depth_A": d}`), `n_fixed`, `fixed_species`, `n_atoms`,
  `area_A2`, `build_sha256`, `contact_build_id`, `planned_in_manifest_sha256`;
- outcome: `status`, `failure_reason`, `W_adh_J_m2`, `W_sep_J_m2`, `joined_energy_eV`;
- provenance: `checkpoint_sha256`, `result_path`, `result_sha256`, `separation_path`;
- costs: `separation_single_points`, `calculator_calls` (null if unknown, never 0 for a failed run),
  `wall_seconds`, `reused_from`, `device`;
- `warnings`: observed notes for that run. Model-wide limitations stay in the menu entry.

**Roles:**
- `primary`: decision feedback.
- `sensitivity`: withheld from decisions.
- `consistency`: ignored by the pilot and the reader.

| status | consumer action |
|---|---|
| `pending` | blocks the decision (`Pending`); every planned job is listed up front |
| `valid` | source re-checked; a failed check → `invalid_evidence` |
| `failed` | genuine calculation failure: reported as feedback, slot consumed, works null, cost and reason kept |
| `invalid_evidence` | integrity problem: blocks consumption (`Blocked`), never shown as chemistry |
| `not_run_resource_limit`, `not_run_no_admissible_construction` | sensitivity rows only, need a reason; shown as `unavailable: <reason>`, never pending or passed |

## Validation before a value can reach a prompt

1. **Structure** (`load_index`): unique run IDs; known candidates, contacts, roles and statuses; `not_run_*`
   only on sensitivity rows, with a reason; the checkpoint equals the campaign checkpoint; failed runs
   have a reason; non-valid runs carry no W_adh.
2. **Source re-check** of every `valid` run (`source_problems`):
   - finite index values;
   - the result hash;
   - the checkpoint;
   - `numerically_valid`;
   - convergence, finite values and free force at or below the target for interface, film and substrate;
   - area, atom count and fixed count against the index;
   - W_adh = (E_film + E_sub − E_int)/A against both the index and `result.json`;
   - W_sep against the separation file (checkpoint, area, interface energy and recomputed value).
3. **Coverage:** the primary run IDs for each feasible candidate are frozen when the pilot starts. A
   missing planned run → `Pending`; an unplanned primary run → `Blocked`.
4. **Comparability within one contact:** registries must share candidate, contact, `contact_build_id`,
   `build_sha256`, `n_atoms`, area, `fixed_rule`, `n_fixed`, `fixed_species` and checkpoint, with unique
   `registry_id`s. Lateral shifts and raw geometry hashes are not required to match. Only then is the
   lowest `joined_energy_eV` selected.

## Decision records: `state.json` (pilot v2)

**Stages** are `prior` (optional), `choose_2`, `choose_3` and `summary`.
- Choices need an `ordered_shortlist` of the unevaluated feasible IDs, with `selected_id` first.
- `predicted_W_adh_J_m2` must be finite ordered intervals; negative values are allowed.
- Also required: `predicted_weaker_contact` and `change_trigger`.
- `choose_3` additionally needs `supporting_observations` and `prior_prediction_assessment`; `summary`
  needs `prior_prediction_assessment`.

**Prompts:** later prompts contain `previous_decisions`, the structured earlier choices and predictions.
Primary feedback is snapshotted once, when first revealed, and reused by hash; later changes to the
index cannot rewrite it.

**Accounting:**
- The hard cap is 10 HTTP attempts.
- Worst-case attempts (3) are reserved on disk before every call and settled from `llm_metadata`.
- An unknown outcome keeps its reservation.
- Prompts are capped at 16,000 characters (about 9.2k tokens).

**Resume:**
- One owner of the state file (`.lock`).
- Mode and settings are pinned.
- A stopped stage stays stopped.
- Record, snapshot and frozen-table hashes are re-verified.

`MOCK_*` files are mocked LLM traces. `MOCK_state_genuine_reference.json` uses the genuine validated
LiNbF6 feedback from the real index; no live API call was made.
