# Recommended next run after ea0326d

21 October 2026. Prepared for Davide to share with Adem; not sent automatically.
This records a recommendation, not a launched experiment.

## Decisions

**Run shuffled feedback next: 30 repeats on the original frozen v3 benchmark.**
Use seeds 100–129, budget 10, direct Anthropic Haiku 5.5, temperature 1.0, output
cap 4096, and the unchanged `v3-2026-10-21c-charged-ids` prompt. Pin the control
implementation to ea0326d (or record a successor and its changes). Preserve all
attempts, charged failures, true outcomes and displayed-source maps. About 300
proposal calls before retries; run the declared 30 regardless of the outcome.

```bash
python scripts/run_discovery_experiment.py \
  --arms shuffled --repeats 30 --start-seed 100 --budget 10 \
  --temperature 1.0 --max-tokens 4096 --workers 3 \
  --out runs/shuffled_v3_followup
```

Use the existing authorized local credential configuration. Keep this new batch
separate from the original archive, replay its true query results, and combine
only at analysis time with the matched integrated 30-run cohort. The old ten-run
cohort remains separate. Record returned model ID and complete usage metadata.
There is no need to rerun the existing four arms solely to add this control.

**Defer IDs-only.** Its comparison against sequential isolates the effect of
retaining earlier rationales, making it a useful diagnostic of anchoring. It is
secondary to whether informative feedback helps and would add about 300 calls.
If pursued later, define it as a separate fixed follow-up; do not use the shuffled
result as a reason to change endpoints or keep running until one arm looks good.
Reserve the next budget decision for that diagnostic versus the broader environment
study after its phase-data coverage and endpoints are validated.

**Prepare the figure and r111/r114 examples now.** Show the full 30-run denominator,
95% Wilson intervals for success, IQR for best-bin spread, exact random and the
post-hoc fluoride-first rule. Label r111 as a selected successful example and r114
as a selected failure. The numerical feedback can be checked; proposed chemical
mechanisms remain hypotheses. Do not overwrite the original archived figure.

## Interpretation of the new control

The main question is whether correct associations between queried candidates and
their results improve selection. This shuffled implementation corrupts those
associations but also changes earlier displayed outcomes while preserving old
rationales. Products/errors can reveal source chemistry, and the first result
cannot be shuffled. These limits are already disclosed in the branch and should
remain in the analysis and slides.

A lower success rate with corrupted feedback supports dependence on informative
feedback in this prompt/history setup; it is not a unique proof of chemical
reasoning. An uncertain or absent difference is inconclusive, especially because
some information remains usable. Report the comparison either way, with the
uncertainty, and quantify how many displayed slots actually changed source at
each turn from the logged maps. Do not describe the control as fully blinding all
chemical information.

Retain acceptance by query 10 as the original endpoint and the best-bin/threshold
sensitivities as labelled secondary results. The iterative-versus-shuffled contrast
is a planned follow-up to the already observed iterative-versus-sequential result,
not part of a blind original preregistration. State this chronology.

## Review performed here

Fetched ea0326d and inspected SYNC_DAVIDE_3.md and the code diff. Tested an isolated
git archive to leave shared working files intact: **41 tests passed** across
discovery, analysis, batch audit, benchmark, Anthropic restrictions and viewer.
The analysis reproduced acceptance 19/10/4/4 and best-bin counts 7/6/0/1 for
iterative/random/sequential/upfront. The three-panel plot was generated and visually
inspected. Deterministic smoke comparisons against b210db0 showed identical prompt
payloads, histories and traces for all original four arms. No paid calls occurred.

One robustness issue for later expansion: the new exact-median expression uses
`next(...)` without a default. When fewer than half the pool is eligible at an
early budget, no finite bin reaches cumulative probability 0.5 and it raises
StopIteration. Represent that median as no eligible result (infinity internally,
null in JSON and the labelled plot level), including an all-ineligible table.
Add sparse/all-ineligible fixture coverage. This does not block the current v3
run, which has 47 eligible candidates out of 50.

The agent branch was not merged into the local davide checkout by this review.
No experiment, cross-session message, commit or push was initiated here.
