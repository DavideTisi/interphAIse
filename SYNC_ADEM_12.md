# Adem: amend the comparison into a small LLM–PET-MAD feedback pilot

21 October 2026. This updates SYNC_ADEM_11.md after Davide clarified that the
LLM should choose new coatings using the physical feedback. Please read
[LLM_PETMAD_PILOT_PLAN.md](LLM_PETMAD_PILOT_PLAN.md) as the current plan.

Keep the completed 450-run environment study and its analysis unchanged.
Keep your F3/F4 polishing and MLIP reader/validator tasks. The change is that
the new cohort is **LiNbF6 as a known reference plus two adaptive choices**,
instead of three fixed coatings selected by us.

## What to implement now

1. Agree the candidate/build/feedback schema with Claude. He screens the five
   named candidates under the declared bounds and freezes a feasible menu.
   We need at least three unevaluated alternatives for both decision rounds to
   offer a real choice. Report a smaller menu before live calls.
2. Build a small resumable runner with mocked responses and existing reference
   archives. Optionally save a chemistry-only prior ranking; then reveal the
   complete LiNbF6 feedback and save an ordered shortlist with testable
   predictions. The first ID is coating 2.
3. Pause until Claude's coating-2 package passes validation. Reveal the full
   feedback and ask the LLM to choose coating 3, with a brief explanation tied
   to specific observations. Freeze that selection before its energies exist.
4. After coating 3, generate a decision timeline and comparison table showing
   predictions, outcomes, changes/retained choices and limitations. Save hashes,
   prompts/responses, settings, charges, failures and costs for deterministic
   replay of the orchestration.

The fixed brief is to explore the trade-off between frozen thermodynamic
penalty and the weaker of two valid W_adh values. Keep acceptance/insulation
labels and individual contacts visible. No weighted score or new acceptance
threshold. W_sep, reconstruction and uncertainty inform the discussion; strong
adhesion cannot make a thermodynamically rejected coating acceptable.

The ordered shortlist after LiNbF6 is our initial-choice comparison: did the
new feedback change the next selection? Do not call it a measured performance
baseline when the unchosen coating was never calculated. Three coating slots
are a demonstration of the physical-feedback loop, not statistical proof of
better search or a reason to revise the existing environment results.

## Cost and tests

Use the configured direct Anthropic Haiku 5.5 only. Plan at most four scientific
responses plus one smoke response if needed, with a proposed total ceiling of
10 HTTP attempts including retries. Send expected and conservative token/cost
estimates for that cap before starting paid execution. Do not launch another
30-run-per-arm experiment or treat the old production approval as covering it.
Offline implementation and coordination can proceed immediately.

Tests should cover state/resume, validation before feedback, out-of-menu and
duplicate IDs, no unrevealed result leakage, persisted ordered-shortlist
comparison, failed-contact handling and the total attempt cap. An interface
failure consumes a material slot; no silent replacement or retry until the
model gives a preferred answer. Continue the original F3/F4 regression tests
and verify that the completed production archive still gives the same numbers.

Claude owns physics and raw results; you own the LLM loop, validator and figures;
Davide/Codex owns scientific scope, independent review, viewer and integration.
Please first return the field contract, a mocked end-to-end trace and the capped
cost estimate. This replaces only the fixed-cohort/no-new-calls directions in
note 11; its safeguards, archival discipline and comparison outputs still apply.
