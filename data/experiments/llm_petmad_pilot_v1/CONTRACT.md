# Field contract: PET-MAD campaign index ↔ LLM pilot runner (DRAFT, needs Claude's agreement)

21 October 2026, Adem. Implemented and tested in `interphaise/pilot.py` (`load_index`, `feedback_bundle`,
`validate_decision`) and `tests/test_pilot.py`. Field names are proposals: change them here and in the code
together, before Claude emits final records.

## 1. Campaign index (written by the PET-MAD side): `data/petmad/coating_comparison_v1/index.json`

```json
{"schema_version": "coating_comparison_v1",
 "checkpoint_sha256": "<PET-MAD S 1.6.0 checkpoint>",
 "menu": [{"candidate_id": "mp-aaacjjwh", "formula": "LiNbF6", "feasible": true,
           "exclusion_reason": null, "descriptors": {"facets": "...", "n_atoms": 696}, "limitations": ["polar slab"]}],
 "runs": [{"run_id": "unique", "candidate_id": "mp-...", "contact": "cathode|electrolyte",
           "role": "primary|sensitivity", "sensitivity_kind": null,
           "registry": [x, y], "thickness_layers": 4, "fixed_fraction": 0.34, "bulk_seed": 0,
           "status": "valid|failed|pending", "failure_reason": null,
           "W_adh_J_m2": 3.6, "W_sep_J_m2": 5.17, "joined_energy_eV": -4687.49,
           "checkpoint_sha256": "<same as top>", "result_path": "...", "result_sha256": "...",
           "source_commit": "...", "job_id": "...", "device": "cuda",
           "calculator_calls": 136, "wall_seconds": 61.3, "reused_from": null, "warnings": ["..."]}]}
```

Validation enforced by `load_index`:
- unique `run_id`s;
- every run's candidate is on the menu;
- contact, role and status are from the allowed sets;
- every run's checkpoint equals the campaign checkpoint;
- `valid` runs need a finite `W_adh_J_m2` and `joined_energy_eV`;
- `failed` runs need a `failure_reason`;
- non-valid runs carry no `W_adh_J_m2`, so missing work is never treated as zero.

## 2. Primary-feedback bundle (built by `feedback_bundle`, hashed before each decision)

For each revealed coating, it contains:
- the frozen sulfide thermodynamic card, joined by exact ID from `environment_v1/lco_lpscl_4v.json`;
- per contact: status, the selected registry (lowest `joined_energy_eV` among valid primary runs of that
  contact), W_adh, W_sep, every primary registry with its status and failure reason, and the warnings;
- `weaker_contact`, which is `unresolved` if either contact is invalid or the gap is below 0.1 J/m²;
- `min_W_adh_J_m2`, or null;
- the sensitivity runs listed with `status: "pending"` (their values are never shown);
- calculator calls and wall time;
- limitations.

A primary run that is still `pending` blocks the decision (`Pending`), and the loop resumes later.

## 3. Decision records (written by the runner): `data/experiments/llm_petmad_pilot_v1/state.json`

Stages are `prior` (optional), `choose_2`, `choose_3` and `summary`. Each choice must include:
- `ordered_shortlist`, which ranks every unevaluated feasible ID exactly once;
- `selected_id`, which must equal the shortlist's first ID;
- `hypothesis`;
- `predicted_weaker_contact`: cathode, electrolyte or unresolved;
- `predicted_W_adh_J_m2`, with cathode and electrolyte ranges given as `[low, high]`, where
  0 ≤ low ≤ high ≤ 20;
- `change_trigger`;
- for `choose_3`, a non-empty `supporting_observations`.

Each record stores the prompt, response, parsed decision, any error, `llm_metadata` (HTTP attempts and
request IDs), the feedback hashes it saw, a timestamp, and `record_sha256`.

**Accounting:**
- The hard cap is 10 HTTP attempts.
- A call is refused if its worst-case retries (3) could exceed the cap.
- There are at most 2 format attempts per stage, all charged.

**Rules:**
- A failed contact still consumes its material slot.
- The menu hash is fixed at start.
- A menu with fewer than 3 alternatives is refused unless `allow_small_menu` is set.

`MOCK_*` files are an offline end-to-end trace with synthetic fixture energies. They are not results.
