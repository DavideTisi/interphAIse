# Environment production review and final presentation handoff

21 October 2026. Reviewed `work/agent-experiments` at `06a4271` in an isolated
tracked-file snapshot. Execution was pinned to `710d346`. No live API call
or branch merge was made during review.

**The production result passes review. Stop data collection and proceed to
slides and the joint integration review.** The headline is that the value of
LLM feedback depends on the environment. It improves selection on sulfide;
random exploration wins on LLZO. Keep both in the main presentation.

## Verified evidence

- All 450 runs are complete, with exactly five arms × seeds 200–229 × three
  frozen environment tables, budget 10, and matching source hashes/settings.
- Independently replayed all 4,500 charged queries and reproduced all 2,800
  archived prompts, full run states, traces and shuffled-feedback source maps.
  Replay used the recorded parsed responses and, for the two JSON-parse
  failures, the recorded exceptions; it does not reproduce the stochastic
  model or recover unarchived malformed response text.
- Workflow hashes match the execution manifest. Every recorded requested and
  returned model is `claude-haiku-5-5`, temperature 1.0, max tokens 4096.
  No draft override, smoke cohort or setting substitution is present.
- Recomputed the production summary; it is identical to the archived JSON.
  Independently recomputed the six paired exact McNemar tests and Holm
  adjustment. `--production` passes, including all six comparisons.
- The twelve environment/experiment-analysis tests pass in the isolated
  snapshot. Completeness guard, best-bin intervals, first-hit quartiles and
  per-run fluoride summaries requested in SYNC_ADEM_8 are present.
- Recounted 2,800 calls and ten format retries, 24,304,759 input tokens and
  2,399,805 output tokens, including 1,518,160 thinking tokens. No missing
  usage or caching. Largest input/output: 12,281 / 2,388 tokens.
  Using the archived protocol rates gives **USD 3.6303784**, an estimate,
  not a billed amount. No fresh pricing or account-billing check was made.

## Main result: preserve the heterogeneity

Counts are successes within ten queries, out of 30 runs per arm.

| Environment | Iterative | Sequential | Shuffled | Upfront | Sampled random | Exact random |
|---|---:|---:|---:|---:|---:|---:|
| Li6PS5Cl | 20 | 2 | 6 | 0 | 8 | 25.7% |
| Li3InCl6 | 30 | 30 | 30 | 30 | **29** | 99.4% |
| LLZO | 12 | 0 | 4 | 1 | 24 | 73.6% |

The chloride shorthand “every arm succeeds” needs precision: every LLM arm
is 30/30, sampled random is 29/30. It is still the predeclared ceiling case.

| Planned paired contrast | Discordant pairs (iterative only / control only) | Raw p | Holm p |
|---|---:|---:|---:|
| Sulfide: iterative–sequential | 18 / 0 | 0.000007629 | 0.00004578 |
| Sulfide: iterative–shuffled | 15 / 1 | 0.0005188 | 0.002441 |
| Chloride: iterative–sequential | 0 / 0 | 1 | 1 |
| Chloride: iterative–shuffled | 0 / 0 | 1 | 1 |
| LLZO: iterative–sequential | 12 / 0 | 0.0004883 | 0.002441 |
| LLZO: iterative–shuffled | 11 / 3 | 0.05737 | 0.1721 |

The sulfide comparison supports useful correctly attributed feedback. LLZO
shows improvement over the sequential policy, but does not establish a
feedback-attribution benefit against shuffled at the corrected threshold.
The lack of significance is not evidence of equivalence. Random's higher
LLZO rate is a descriptive comparison; do not add an unplanned “primary”
significance claim. Keep the exact random expectation alongside the sampled
24/30 result.

LLZO's iterative fluoride share drops 0.18 → 0.09, while sulfide rises
0.28 → 0.65. This is consistent with environment-dependent adaptation, not
proof of its chemical mechanism. Trace evidence must support any stronger
claim. Sequential retains its own earlier hypotheses; shuffled has partial
identity leakage and can contradict past rationales. Those known control
limitations still apply.

Use acceptability as the frozen primary outcome. Do not relabel it finding
the optimum: sulfide iterative reaches the best bin in 6/30 runs, compared
with sampled random 5/30; LLZO has no best-bin success in any LLM arm, versus
random 2/30. Do not pool all environments into an apparent universal win.
The equal-weight contrasts remain descriptive secondary summaries.

## What the LLM substitutes

It chooses the next material to test, writes a chemical hypothesis, and
revises subsequent selections from calculation results—the candidate
selection and hypothesis-update work normally done by a researcher. The
fixed evaluator computes the outcome; its numerical ranking rules do not
come from the model. This experiment demonstrates useful feedback-dependent
selection in one landscape and a limitation of that policy in another. It
supports neither universal superiority to random search nor proof that the
model uses human-like mechanistic reasoning.

The exhaustive thermodynamic tables are a benchmark, so evaluation counts
here are not measured MLIP time savings. PET-MAD remains a separate feasibility
and sensitivity demonstration. No experimentally validated new coating or
lithium-transport claim follows from either part.

## Slide and integration handoff

A new overview figure is available as
`figures/environment_acceptance_review_20261021.png` and editable SVG, with
95% Wilson intervals and exact random references. Reproduce with
`python scripts/plot_environment_review.py`. The inputs are the independently
audited JSON, so the figure can be rebuilt on `davide` before branch integration.
Keep the existing per-environment trajectories as the budget-vs-success
figure; this overview shows the endpoint comparison.

Suggested main story: the LLM's selection role and five controls; frozen
three-environment design; this overview; the sulfide feedback effect; the
LLZO failure and what it limits; then one supporting PET-MAD slide and demo.
Use the newest physics: cathode 3.62 / 5.17 J/m² at (1/3,1/3); electrolyte
seed 0 1.63 / 2.97, with seed-4 shifts 0.12 / 0.16 above tolerance. Both are
formally polar and provisional. See SYNC_CLAUDE_7.md. Presentation v4 and the
viewer current-cathode pointer still need their updates.

Before merging to main, integrate the two branches while preserving both
logs, run the combined tests, and check final artifact/source links. The
production archive should remain unchanged. Clarify one archival sentence
in a follow-up note: primary analysis definitions were fixed before running
at `0072f3d`; the final analyser additionally includes the requested completeness
and secondary-reporting changes committed in `abab0a2`. Do not claim the final
analysis file is byte-identical to the earlier revision.

No additional cohort, prompt change or seed-4 simulation is needed for this
release. A future policy with mandatory exploration is a new experiment,
not a retrofit to these results. This note is saved for Davide to relay;
Adem was not messaged directly.

Evidence: `data/reviews/environment_results_review_20261021.json`, and the
unchanged production archive on `work/agent-experiments` at `06a4271`.
