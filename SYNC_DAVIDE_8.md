# Agent side: F3/F4 polish done, pilot contract, mocked loop and capped cost

21 October 2026, late. From Adem. Replies to SYNC_ADEM_11/12 and JOINT_REVIEW_AND_HANDOFF.md.
Branch `work/agent-experiments`, which now includes `davide` at `3cb606b`. No paid calls and no PET-MAD
runs. The 450-run archive is unchanged.

## F3 and F4 (committed `352e6f6`)

**F3.** `analyse_environment_study.py --production` now also validates the evidence:
- Manifests, run files and every recorded call's metadata must match the frozen spec: model,
  temperature 1.0, 4096 tokens, prompt version, pool, archived execution commit `710d346`, the
  workflow hashes, and frozen status.
- The spec is an explicit versioned policy, `environment_v1`, applied to this archive only.
- Every charged query is replayed through `BenchmarkQueries`, and every trace is recomputed.
- Separate tests reject an altered outcome, a manifest temperature of 0.0, wrong call metadata and
  an altered trace.
- The real archive passes, with identical counts and identical six Holm tests (about 11 s).

**F4.** `llm.py` now records every HTTP attempt (status, provider `request-id`, elapsed time), transport
retries and the final error, with no credentials or headers, plus a bounded malformed-output field.
- `usage_report.py` separates proposal attempts, format retries, HTTP attempts and transport
  retries.
- The 2,800 historical calls show HTTP as **unknown**, never inferred.
- Tests cover 429-then-success, exhausted retries and malformed output.

## Pilot preparation (for the 10:00 checkpoint)

1. **Field contract (draft):** `data/experiments/llm_petmad_pilot_v1/CONTRACT.md`. It covers the
   campaign index, the primary-feedback bundle and the decision records, and is based on the
   existing `result.json` names. **Claude needs to confirm it** before emitting
   `data/petmad/coating_comparison_v1/index.json`.
2. **Runner:** `interphaise/pilot.py` plus `scripts/run_llm_petmad_pilot.py` (`--mock` / `--live`).
   It is resumable and stops with exit code 2 while primary physics is pending. It enforces:
   - menu, duplicate and shortlist-order checks, and finite ordered W_adh ranges for both contacts;
   - no unrevealed results in prompts, and sensitivity values withheld as `pending`;
   - a failed contact consumes its slot, and a menu with fewer than 3 alternatives is refused;
   - at most 2 format attempts per stage, and a **hard cap of 10 HTTP attempts**: a call is
     refused if its worst-case internal retries (3) could exceed the cap.

   All records are hashed. 9 offline tests pass.
3. **Mocked end-to-end trace:** `data/experiments/llm_petmad_pilot_v1/MOCK_state.json`, run on a
   synthetic fixture index labelled `MOCK_` (prior → choose_2 → choose_3 → summary, 4 HTTP attempts,
   assessment generated). Not a result.
4. **Capped cost** (Haiku 5.5 public list price; an estimate, not billed): mocked prompts are 1.3k–3.1k
   input tokens, about 6k allowed for real bundles.
   - Expected, 4 calls: about 14k in and 8k out, **≈ USD 0.005**.
   - Hard ceiling, 10 HTTP attempts × 6k in × 4096 out: **≈ USD 0.03**.

   Requesting approval for live pilot calls under that cap.

## Not done yet

- `scripts/analyse_mlip_comparison.py`: the comparison table and figure with separate
  cathode/electrolyte panels, the thermodynamic join, registry and sensitivity separation, and
  new-versus-reused compute. The core index validation already exists in `load_index` and will be
  reused. Next on my list.
- Slides: unchanged until the 20:00 freeze rules apply.
- A side finding for the pymatgen test failures: your PET-MAD runs record pymatgen 2026.9.24,
  while my env has 2026.4.16. That supports the version explanation for the 4 matcher failures,
  which happen here only.

## Requests

1. Claude: confirm or amend the field names in `CONTRACT.md`.
2. Davide: approve live pilot calls under the 10-HTTP-attempt cap (≈ USD 0.03 ceiling).
3. Menu size from Claude's screening: the runner refuses fewer than 3 alternatives.

## Addendum: MLIP comparison reader done

`scripts/analyse_mlip_comparison.py` (7 offline tests) reads the campaign index's `cohort`; it never
globs runs.

- **Status per contact:** each coating × contact is `validated`, `pending`, `failed`, `missing` or
  `non-comparable cells`. Missing work is never zero.
- **Source checks for every valid run:** checkpoint, convergence and free-force targets, area and
  atom count, W_adh arithmetic from the final energies, and the W_sep arithmetic against the
  separation file. A failed check invalidates the run, which is kept with its reasons.
- **Registry choice:** lowest relaxed joined energy within one comparable cell. On the real LiNbF₆
  packages it selects the (1/3, 1/3) cathode registry, 3.617 J/m², matching your review.
- **Other parts:** sensitivity is reported as differences from the selected run; new and reused
  compute are kept separate; thermodynamics is joined by exact ID with the frozen-table hash
  checked; no combined score or threshold.

Outputs: `summary.json`, `table.md` and `comparison.png` (separate cathode and electrolyte panels).

Layout preview: `data/experiments/llm_petmad_pilot_v1/MOCK_comparison_layout/`. It shows the real
LiNbF₆ reference and two `FIXTURE` placeholders (LiCaAlF₆ pending, LiZr₂(PO₄)₃ failed), with no
invented energies. The figure was not viewed here (image viewing is blocked).

`CONTRACT.md` now also lists `cohort`, `area_A2`, `n_atoms`, `separation_path` and `reused_from`.
Claude should emit these.
