# Reply to SYNC_ADEM_13 and Claude's contract response: live-path fixes done

22 October 2026, from Adem. Branch `work/agent-experiments`. Offline only: no API calls and no PET-MAD
runs. The 450-run archive is unchanged, and `--production` still gives identical results.

## 1. Source validation on the decision path

`interphaise/pilot.py` now holds one shared evidence interface, used by both the pilot and
`analyse_mlip_comparison.py`. Before any value can reach a prompt:
- every `valid` run is re-checked against its sources (arithmetic, provenance, convergence, forces,
  finite values including W_sep and area, fixed count);
- an integrity mismatch becomes `invalid_evidence` and blocks consumption, while a genuine `failed`
  calculation is still reported, with its reason and cost;
- planned primary run IDs are frozen at start, so a deleted run is `Pending`, not dropped;
- registries must share build ID and hash, atoms, area, fixed rule, mask and checkpoint before the
  lowest joined energy is selected.

Regressions: the 999 J/m² edit is `Blocked` and the deleted registry is `Pending`, both **before the
mock call**. A relabelled build is `Blocked`.

## 2. Durable attempt cap

- **Reservation:** worst-case attempts (3) are reserved on disk before transport and settled
  afterwards. An unknown outcome keeps the full reservation.
- **Client errors:** `llm.py` now records metadata for a non-JSON response body and for
  timeouts/OSError too.
- **Your repro (429, 429, invalid JSON):** each call is charged 3; the stage stops at 6; resuming stays
  stopped and spends nothing.
- **Interrupted calls:** the counter on disk reads 3, 6, 9, then the cap refuses the next call.
- **Ordinary 429 then success:** charged exactly 2.
- **Resume guards:** a `.lock` file gives a single owner; mode and settings are pinned (a mock state
  can't be resumed live); a stopped stage stays stopped.

## 3. The model revisits its own prediction

- `previous_decisions` (hypothesis, ranges, trigger, shortlist) are in every later prompt; a test
  checks that a sentinel from choose_2 appears at choose_3.
- `choose_3` and `summary` require `prior_prediction_assessment`: does the feedback support or
  contradict the earlier prediction, and does the choice change?
- Feedback is snapshotted on first reveal and reused by hash; a test checks that a late change to
  the index doesn't alter it.
- Record, snapshot and frozen-table contents (`verify_hash`) are re-verified on resume.

## Contract and smaller fixes

- **Contract:** v2 in `data/experiments/llm_petmad_pilot_v1/CONTRACT.md`. Claude's six additions are
  in, plus the full status table: `not_run_*` rows are shown as `unavailable: <reason>`, and
  `consistency` rows are ignored.
- **Claude's real index loads** (41 runs; fixture `tests/fixtures/coating_comparison_v1_index_38e4872.json`).
  The genuine LiNbF₆ feedback passes every source check: cathode R3 3.6171, electrolyte R1 1.6334,
  weaker contact electrolyte.
- **Prediction intervals:** finite and ordered; negatives allowed; the 0–20 clamp is removed.
- **Unknown compute** stays unknown (counted separately). Primary bundles exclude sensitivity costs.
- **F3:** a successful recorded call with missing metadata is now rejected. The genuine archive
  passes; failed-attempt metadata remains a documented historical exception.

## Mocked trace with genuine reference feedback

`data/experiments/llm_petmad_pilot_v1/MOCK_state_genuine_reference.json`: prior, then choose_2 on the
genuine LiNbF₆ snapshot (the mock picks LiTaF₆), then a clean `Pending` stop (exit 2), because
coating-2 physics doesn't exist yet. The CLI exits 3 on blocked evidence and sends nothing.

## Cost (list-price estimates, not billed)

- **Prompt sizes:** the genuine choose_2 prompt is about 2.9k tokens. Prompts are now capped at 16,000
  characters, about 9.2k tokens.
- **Enforced ceiling:** 10 HTTP attempts × (9.2k input + 4,096 output) ≈ **USD 0.030**.
- **Expected:** about 4 calls, ≈ **USD 0.006**.

Tests: 72 passed across the pilot, comparison reader, environment study, client, discovery and
analysis.

## Next

1. Your review of this live path and the live command:
   `python scripts/run_llm_petmad_pilot.py --state data/experiments/llm_petmad_pilot_v1/state.json --index data/petmad/coating_comparison_v1/index.json --live`
2. Your approval for live calls under the cap.
3. Then I send Claude the selected ID and record hash after choose_2.
