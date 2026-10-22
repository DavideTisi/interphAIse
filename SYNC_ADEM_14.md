# Adem: initial live selection approved on the reviewed inputs

## Physics checkpoint — six LiTaF6 jobs complete

Claude has already executed the archived choice using source `207f879`:
cathode R1/R2/R3 are jobs **11017049/11017050/11017051**; electrolyte
R1/R2/R3 are **11017052/11017053/11017054**. All six Slurm records are
`COMPLETED`, exit `0:0`; each used one RTX 3090 and four CPUs for 2:44–2:57.
All 18 relaxations report convergence and no overlaps. Reported calculation
cost is 1,502 runner calls plus 12 rigid-fragment single points.

Codex checked the remote manifest hash, choice-record hash, registry offsets,
fixed depths, atom/fixed counts, checkpoint and device metadata against the
selection receipt. This was read-only and did not duplicate Claude's batch.
The full source/structure/force/energy validation has not been replaced by
these metadata checks. Claude owns packaging; Adem validates all six outcomes
and their sources before continuing the same state at choose-3. Preserve the
existing prediction and total attempt cap. No further approval is needed for
that already-authorized continuation.

Evidence: [completion check](data/reviews/litaf6_primary_completion_20261022.json).
The pending-physics descriptions below are earlier checkpoints.

## Live checkpoint — 22 October 2026

The published live archive at `work/agent-experiments:1875726` now confirms
**LiTaF6 (`mp-aaacjmqp`) as coating 2**. This is the actual Haiku decision,
distinct from the earlier mock choosing the same ID. The choose-2 record hash
is `010ad614ea26bd57b30fe9b085301b36001e630f162102813a38d060d6805c01`.

| Pre-calculation prediction | Archived value |
|---|---|
| Cathode W_adh | 3.2–3.9 J/m² |
| Electrolyte W_adh | 1.4–1.9 J/m² |
| Weaker contact | Electrolyte |
| Remaining shortlist order | LiCaAlF6, then LiF |

Three HTTP attempts were charged: an invalid prior shortlist, the corrected
prior, and choose-2. Seven attempts remain under the same total cap. Logged
usage is 4,544 input and 2,327 output tokens, about **USD 0.0016179** at the
recorded list rates, not billed cost. The state, individual record and feedback
hashes verify. An offline resume of the published state raises `Pending` for
LiTaF6 without invoking a model or changing the state.

Adem reports manifest-derived checks/regressions in **`d1ec1b0`**, with **77
tests passing**. At this review the shared branch still ended at `1875726`, and
`d1ec1b0` was unavailable; these fixes/tests are therefore reported, not yet
independently verified. Publish that commit before choose-3 so its source and
regressions can be checked. This does not invalidate the reviewed first choice.

Next: Claude completes the **six LiTaF6 primary jobs**; Adem validates every
terminal outcome against the manifest and source files, then resumes the same
state for choose-3 after the remaining checks pass. No new budget approval is
needed within the authorized scope. Do not rerun the first choice or launch a
duplicate batch. Sensitivity and optional consistency results remain separate.

Scientific interpretation: the model used LiNbF6 as an analogue for a testable
adhesion forecast; its shortlist did not change from its prior. This is a live
prospective hypothesis, not yet evidence that feedback improved selection.
Its recorded trigger mentions changing thermodynamic labels or a future LiCaAlF6
result; neither permits changing the frozen objective or exposing an uncomputed
candidate. Preserve that text and evaluate only the allowed observed feedback.

Audit: [live_selection_review_20261022.json](data/reviews/live_selection_review_20261022.json).
The approval and initial preflight below remain the execution record.

## Davide's approval — 22 October 2026

Davide explicitly approved: **"i approve adem starts the calculations"**, in
response to the reviewed proposal for the prior and first selection, ten HTTP
attempts total across the pilot and a USD 0.05 allowance at the reported rates.
**Adem may start the live prior and choose-2 now** on the pinned package below.
Use direct Anthropic `claude-haiku-5-5`, temperature 1.0 and 4,096 maximum output
tokens. All retries count toward the same total ten-attempt cap; retain one
live state and never reset the budget when resuming. The allowance is approved;
it does not turn the estimated list-price cost into a measured bill.

Archive the selected ID, predictions, record hash and feedback hashes, then
pause for Claude's six declared primary jobs. Finish the manifest/source checks
and independently validate that complete physical package before choose-3.
The approval covers the proposed bounded pilot sequence under those gates;
reconfirming the same budget is unnecessary. A changed scope or increased cap
is not covered. Adem owns execution; Codex has not launched a duplicate run.
Approval is recorded here, but actual live execution is not yet confirmed.

## Reviewed starting point

22 October 2026. Reviewed `work/agent-experiments:f8abbc0`, including `3a2801b`,
and Claude's current `work/petmad-comparison:b199608`. **188 tests pass in
20.80 s** with the pinned environment. The real 450-run archive passes
`--production`, with unchanged results and six Holm comparisons.

The original retry/interrupt/resume, 999-value, deleted-after-start registry,
negative forecast, missing successful-call metadata and prediction-history
regressions now pass. The new report generator is covered. This is sufficient
progress to recommend the **initial live prior and choose-2** on the exact
reviewed inputs. Davide has now given the approval recorded above. The review
does not claim that all general-purpose validation is complete.

## Exact starting package and command

The live command needs Claude's real campaign files in the execution checkout,
not just the index fixture in your tests. I tested an isolated overlay of his
campaign directory on your code; no contributor branch was merged or edited.

- Agent code: `f8abbc0`.
- Physics/data snapshot: `b199608`.
- Frozen manifest SHA256:
  `99ef2dc199b730b53728fcbb3eb5eee71bcf4e75a9e19d9d0102cfe07280c19f`.
- Initial index file SHA256:
  `b02750feffeefb0d3e7875d18bc693a3b2e4e6a5294091a21d59aee6501aa937`.

Independent preflight confirms all **23 primary IDs** against the actual
manifest: five reused reference records and 18 pending records for the three
options. All six prospective contact builds agree with their manifest and
index hashes/counts/fixed rules. For the five reference packages, I checked
source hashes, provenance, actual fixed-atom indices against the physical depth
rule, and free-atom forces from all saved final structures. The reference
feedback remains cathode **3.6170509** and electrolyte **1.6333941 J/m²**.

Use a fresh live state, separate from every mock. Preserve the planned menu and
hashes; archive exact code/data identity alongside the state. Approved command:

```sh
python scripts/run_llm_petmad_pilot.py \
  --state data/experiments/llm_petmad_pilot_v1/state.json \
  --index data/petmad/coating_comparison_v1/index.json \
  --live
```

The exact command with `--mock` produced prior and choose-2 and exited **2** at
pending coating-2 physics. Its synthetic choice of LiTaF6 is only a test output.
At the live pause, archive the actual selected ID, predictions, record hash and
feedback hashes before Claude calculates its six primary registries. Do not
calculate the third unselected option or change a selection after seeing energy.

## Remaining validation boundary before the second choice

Two focused cases still pass the generic runner:

1. Removing a reference registry **before initializing a fresh state** lets
   choose-2 proceed with four reference records. Planned IDs are copied from
   the index rather than independently derived from the frozen manifest.
2. Giving all cathode reference rows the same wrong build ID/hash, fixed-depth
   rule and fixed-species label (while retaining the real fixed count) passes.
   Index rows agree with each other, but those identities are not verified
   against the expected build and saved physical mask.

These cases do not corrupt the exact starting package: the independent
preflight above closes that boundary for its initial decision. Before choose-3,
enforce manifest-derived coverage/identity and real source checks on the new
package, using Claude's strengthened producer as an independent cross-check.
Pin/verify the manifest hash and each run's planned build/registry; checking
equality of arbitrary index labels alone is insufficient. Keep the declared
historical reference exception explicit. Add the two focused regressions rather
than a broad refactor. No changed scientific objective or new large experiment.

Pause for the complete selected-coating package, then validate it against the
frozen manifest and sources before resuming. An integrity issue blocks; a
genuine terminal calculation failure is reported and consumes the slot. Keep
the same live state and **same total 10-attempt budget** across all resumes.
Optional consistency and sensitivity results stay outside decision snapshots.
Claude's additional reference checks are already archived separately; they
have not replaced the frozen reference values used in this review.

## Cost wording and approved scope

The durable **10-HTTP-attempt cap** and **16,000-character user-prompt cap**
are implemented. The estimate of **about USD 0.006** is plausible under your
recorded rates. However, average characters per token cannot establish a strict
USD 0.030 ceiling. The 642-byte system prompt and provider message overhead also
count. A conservative scenario of 17k input and 4,096 output tokens per attempt
would be **USD 0.03748** for ten attempts at those recorded rates.

Davide approved **up to 10 HTTP attempts with a USD 0.05 budget allowance**,
explicitly an allowance under the recorded pricing assumptions, not a claim
that the code enforces a dollar meter. No current pricing or actual account
billing was independently verified in this code review.

Approved execution scope: initial prior + choose-2 now, then a physics pause;
later calls remain within the same cap and require the completed package checks
above. No live call, cluster calculation or external message was made by this
review or by recording the approval; Adem must archive the actual execution.

Evidence: [live_pilot_review_20261022.json](data/reviews/live_pilot_review_20261022.json).
The latest runner fixes supersede the broad hold in note 13 for this exact
initial package; its remaining source/manifest requirements still apply.
