# Environment production readiness and measured-cost review

21 October 2026. Reviewed agent branch `710d346`, analysis commit `0072f3d`
and smoke execution commit `26beb73`. **Scientific recommendation: proceed
with the frozen production design once Davide explicitly approves spending.**
This document is not that approval, and no production was launched here.

## Shared package on `davide`

Davide requested publication of this handoff, the completed viewer, science
reviews and presentation checkpoint. Fetch `origin/davide` and merge it into
your `work/agent-experiments` branch, preserving your analysis additions and
both branches' development-log entries. The frozen tables and workflow
settings are unchanged. Rebuild the offline viewer with
`python scripts/build_structure_viewer.py`; share its generated HTML directly.
The completed viewer contains 278 geometries and the current 696/880-atom
contacts. See VIEWER_UPDATE.md for details and tests.

Presentation v4 is now available inside the repository under `presentations/`.
Its README lists newer physics results that are not yet in that saved deck.
Claude's ongoing final-constraint/registry code and outputs are not part of
this publication. Publishing these files does not approve production spending.

## Verified

- Fetched the published branch and inspected the analysis and smoke archive
  without merging or changing the shared checkout. Workflow files are unchanged
  since `26beb73`; the subsequent diff contains smoke evidence, analysis/tests
  and documentation. Pin and record the actual execution commit.
- The smoke manifests use the frozen table hashes, seed 999, temperature 1.0,
  4096 output tokens and no draft override. Every returned model recorded is
  `claude-haiku-5-5`.
- Recounted 31 attempts, one format retry, 57 queried candidates, 222,668 input
  and 27,416 output tokens, including 16,080 thinking tokens. No missing usage,
  caching or truncation. Maximum input/output lengths were 7,873 / 1,906 tokens.
- Smoke cost recomputes to USD **0.0359748 at public list rates**. This is not
  a provider-billed amount. Account-specific pricing remains unverified.
- Ran `tests/test_environment_study.py` and `tests/test_experiment_analysis.py`
  in an isolated tracked-file snapshot using Davide's `.venv`: **11 passed**.
  No API call was made. The pairing, exact McNemar arithmetic, Holm adjustment,
  first-hit convention and frozen-input loader agree with the intended design.

Public pricing was rechecked on 21 October 2026 at
https://platform.claude.com/docs/en/about-claude/pricing:
Haiku 5.5 is USD 0.10/M input and 0.50/M output for prompts up to 100k tokens.
Thinking is already included in the recorded output counts; do not add it twice.

## Concrete production scope and costs

Keep three environments × five arms × 30 runs = 450 runs, budget 10,
seeds 200–229, existing temperature/output cap/prompt, and fresh histories.
Random is offline; the four LLM arms require **2,790 planned calls before
retries**. Use all six planned primary contrasts and the frozen thresholds.

Recalculation from the displayed per-arm assumptions:

| Scenario | Estimated list-price cost, USD |
|---|---:|
| Expected: 24.2703M input + 2.50308M output | 3.68 |
| Input +20%, calls +10%, output/call +50% | 5.27 |
| Same input contingency; +10% calls, all outputs at 4096 | 9.49 |

The last line is **a high-output scenario, not an enforced hard ceiling**.
The 10% retry allowance and input growth are assumptions; the production
command has no dollar-limit flag. Rename that heading in SYNC_DAVIDE_4.md.
No additional billing access or different request path is needed for this
review, and there is no scientific reason to reduce the declared design on
the basis of these estimates. Report actual usage and failures after each
environment; if technical failures make cost substantially exceed the
projection, pause for a budget decision and retain all attempted-run records.
Any interruption is operational, never based on interim success rates.

## Small final-analysis safeguards

These do not change sampling, prompts, the objective or the primary statistics,
and need not prevent data collection once spending is approved. Finish them
before reporting production results:

1. Add or explicitly execute a **production completeness check** for the three
   exact frozen environment hashes, all five arms, budget 10, and exactly seeds
   200–229 per arm/environment. Require `holm_family_size == 6`. The current
   generic analyser accepts subsets and adjusts only the tests supplied; it
   correctly supports generic tests but does not itself enforce this study's
   complete six-comparison family. Do not publish a partial-environment output
   as the final analysis.
2. Retain the predeclared secondary uncertainty summaries: the per-environment
   plot script already supplies best-bin Wilson intervals, but the combined
   summary omits them despite its docstring. Add them there or clearly reference
   the companion output, and include the declared first-hit distribution/IQR.
   Save per-run early/late fluoride counts and changes as well as the pooled
   fractions, so the protocol's within-run prior-revision description is
   directly inspectable. Use the already fixed early/late split and invalid-ID
   exclusion; document failed-run and empty-denominator handling.

Keep the smoke cohort excluded. No threshold, seed, contrast, multiplicity
family or exclusion-rule changes are proposed. Record any analysis-only
completion commit separately from the unchanged workflow code.

## Approval state and coordination

Davide's last explicit spending approval was **smoke only**. The measured-cost
review is now complete; production still requires his go-ahead. Adem remains
the execution owner to avoid duplicate batches. No external message, merge,
commit, push, paid run or credential access occurred in this review.

Claude's PET-MAD checks and the completed viewer update are independent of
the environment production study. Supporting audit:
[environment_production_review_20261021.json](data/reviews/environment_production_review_20261021.json).
