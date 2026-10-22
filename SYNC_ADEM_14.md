# Adem: initial live selection is ready for approval on the reviewed inputs

22 October 2026. Reviewed `work/agent-experiments:f8abbc0`, including `3a2801b`,
and Claude's current `work/petmad-comparison:b199608`. **188 tests pass in
20.80 s** with the pinned environment. The real 450-run archive passes
`--production`, with unchanged results and six Holm comparisons.

The original retry/interrupt/resume, 999-value, deleted-after-start registry,
negative forecast, missing successful-call metadata and prediction-history
regressions now pass. The new report generator is covered. This is sufficient
progress to recommend the **initial live prior and choose-2** on the exact
reviewed inputs, subject to Davide's explicit approval. It is not approval by
itself or a claim that all general-purpose validation is complete.

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
hashes; archive exact code/data identity alongside the state. Once approved:

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

## Cost wording and proposed approval scope

The durable **10-HTTP-attempt cap** and **16,000-character user-prompt cap**
are implemented. The estimate of **about USD 0.006** is plausible under your
recorded rates. However, average characters per token cannot establish a strict
USD 0.030 ceiling. The 642-byte system prompt and provider message overhead also
count. A conservative scenario of 17k input and 4,096 output tokens per attempt
would be **USD 0.03748** for ten attempts at those recorded rates.

Recommend asking for **up to 10 HTTP attempts with a USD 0.05 budget allowance**,
explicitly an allowance under the recorded pricing assumptions, not a new claim
that the code enforces a dollar meter. If USD 0.030 is a strict requirement,
implement a valid token/cost bound before live execution. No current pricing or
actual account billing was independently verified in this code review.

Proposed execution scope: initial prior + choose-2 now, then a physics pause;
later calls remain within the same cap and require the completed package checks
above. The estimate and this recommendation are **not** user approval. No live
call, cluster calculation or external message was made by this review.

Evidence: [live_pilot_review_20261022.json](data/reviews/live_pilot_review_20261022.json).
The latest runner fixes supersede the broad hold in note 13 for this exact
initial package; its remaining source/manifest requirements still apply.
