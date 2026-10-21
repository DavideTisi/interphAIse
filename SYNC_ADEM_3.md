# Handoff after Adem's 0889d0e update

21 October 2026. Prepared for Davide to share; not sent automatically.
Read origin/work/agent-experiments at 0889d0e. The new changes since 40e79c3 are
shuffled feedback, a median-best-bin plot, and the expanded interpretation in
SYNC_DAVIDE_2.md. They have been fetched and inspected, not merged or run here.

## Current shared baseline

Please start from the integrated `davide` branch at **703f4d9**. Your earlier branch
through 40e79c3 was merged there. We corrected invalid/repeated-ID query accounting,
added strict experiment validation, and completed a separate batch: 30 repeats per
arm, budget 10, seeds 100–129, Haiku 5.5, temperature 1.0, max output 4096, prompt
v3-2026-10-21c-charged-ids. All 120 runs completed and all 1,200 query results replay
exactly. The full sanitized archive and report are already pushed.

Acceptance: iterative 19/30, upfront 4/30, sequential 4/30, random 10/30.
Best bin: iterative 7/30, upfront 1/30, sequential 0/30, random 6/30.
The post-hoc fluoride-first baseline succeeds at query 2. Keep the older ten-run
batch separately labelled; prompt, accounting and output-limit settings differ.

Your anchoring diagnosis is worth testing, but the claim that sequential never
chooses LiZr2(PO4)3 is specific to your original batch. In the newer archive it
chooses that formula in **10/30 runs** (12 selections), compared with upfront
25/30 runs (25 selections) and iterative 4/30 runs (7 selections). Do not transfer
the old trace diagnosis to the new batch without inspecting it.

## Adem: controls and analysis

1. Integrate the new shuffled arm and best-bin analysis with the latest davide
   code. Preserve charged invalid/repeated queries, metadata fixes, portable paths,
   repeat-file validation, explicit duplicate replacement, baseline and summaries.
   The scripts overlap, so review the resolved diff rather than replacing either
   version wholesale. Re-run offline tests before any paid control.
2. Inspect the shuffled-control semantics. It currently reassigns earlier displayed
   feedback as new results arrive; that can contradict the older rationales still
   present in history. Products and error strings may also reveal the true source
   despite relabelling the top-level formula/ID. Record these limitations or refine
   the design before freezing it. Interpret it as sensitivity to corrupted feedback,
   not a uniquely clean proof of chemical reasoning. The first observed result
   cannot be shuffled with another already-queried result.
3. Handle malformed-ID attempts in the merged shuffled arm. Current code uses
   `formula.get(h['proposal']['candidate_id'])`; a non-string unhashable ID can now
   reach history under the corrected charging policy and make this lookup crash.
   Use safe ID handling and add unknown/non-string/repeated-ID tests, plus tests
   for source-map logging, true-score preservation and absence of unqueried results.
4. Add the IDs-only sequential variant as a diagnostic: it sees earlier IDs but
   no outcomes or earlier rationales. Match the same choice request and scientific
   task. Comparing it with sequential tests rationale-history dependence; iterative
   versus IDs-only still changes both outcomes and rationale visibility, so it is
   not a fully matched feedback ablation. A full 2x2 rationale-history/feedback
   design is optional future work, not required for the two-day project.
5. Recommended next paid control is shuffled feedback, **30 runs**, seeds 100–129,
   budget 10 and the same provider/settings as the archived integrated batch. That
   is about **300 proposal calls**, not 100, before retries. Freeze the control
   definition and record its version; if shared iterative behavior changes, do not
   silently compare to the old iterative cohort. The IDs-only variant would cost
   another ~300 calls at 30 runs and can follow if time/budget permits. This handoff
   recommends the next experiment; no new paid calls were launched in this review.
6. Reproduce the figures from the 30-run archive and add the best-bin trajectory.
   Keep the 0.050 primary threshold, explicitly labelled bin<=2 sensitivity,
   exact random curves, and post-hoc heuristic visible. Verify any median/quantile
   convention in the caption and distinguish interquartile spread from confidence
   intervals. Show a failed trace as well as a successful one, and check chemical
   claims in the selected examples. Archive the original ten-run data separately
   if it is to appear in the presentation or report.

## Interpretation to retain

Both the current iterative and sequential arms see their own earlier proposals
and rationales. Their deliberate difference is scientific feedback. Escaping
self-reinforcing rationale history may therefore be a mechanism of the feedback
benefit rather than an additional uncontrolled treatment. The result remains
specific to this prompt/history design. Upfront also changes the number of calls
and whether choices are planned jointly, so it is not an unqualified cleaner
causal comparison.

Suggested current headline: **Computed feedback helped Haiku reach the frozen
coating criterion more often than its no-feedback arms on this benchmark. The
benefit appeared late, did not establish better optimum finding than random,
and was outperformed by a review-motivated fluoride-first heuristic.**

## Davide: materials validation and shared review

Davide keeps ownership of PET-MAD bulk preparation, slab/constraint/polarity and
convergence checks, the two-contact viewer and scientific limitations. Keep the
predeclared shortlist unchanged. Both people review the combined diff and claims
before merging to main. No need to rerun the already archived four-arm production
batch merely because the additional control has been implemented.
