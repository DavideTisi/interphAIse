# interphAIse: results synthesis and review against the original design

**22 October 2026, updated after the validated DeepSeek repeat.** This joins the
21 October search experiments, the completed PET-MAD pilot and the final
DeepSeek results at `550391b`. Final counts replace all interim summaries. The
report changes the interpretation and presentation plan without modifying any
frozen experiment, result, prompt or statistical analysis.

The main finding is that **useful chemical priors and useful use of feedback
are distinct capabilities, whose value depends on the model configuration and
environment**. Haiku benefits clearly from correct feedback on sulfide.
DeepSeek shows the same direction there, without significance after the planned
correction. On LLZO, DeepSeek's upfront shortlists succeed in 20/30 runs, against
Haiku's 1/30, while both iterative arms remain below random. Chloride is at
ceiling. The physical pilot makes chemical analogy testable: the LiTaF6 forecasts
held and both LiCaAlF6 forecasts failed. We have demonstrated a bounded scientific
decision workflow and measured its limits. We have not established human-level
judgment, general search acceleration or a superior functional battery coating.

## Deliverables and source boundary

- [Haiku and PET-MAD presentation checkpoint](presentations/results_2026-10-22/interphAIse_results_synthesis_2026-10-22_v2.pptx):
  18 main slides plus six technical backup slides, editable charts/tables and
  source notes. The older 21 October presentation is preserved. A
  [static PDF](presentations/results_2026-10-22/interphAIse_results_synthesis_2026-10-22_v2.pdf)
  is included for sharing. These files predate the DeepSeek repeat and have
  **not** been rewritten in this analysis. The revision plan below applies to
  their narrative, not to the correctness of their archived Haiku numbers.
- [Presentation evidence](presentations/source/results_synthesis_2026-10-22.json)
  contains the exact plotted values, reconstructed success curves, contrasts,
  selected physical rows and immutable source references.
- [Presentation builder](presentations/source/build_results_synthesis_2026-10-22.mjs)
  records the slide narrative and layout.

The existing deck was built from `davide` at `750b382`, agent branch at
[`800ba03`](https://github.com/DavideTisi/interphAIse/tree/800ba0378779ce7df9038bc4857719a29c2fe0a7)
and physics branch at
[`1b76eeb`](https://github.com/DavideTisi/interphAIse/tree/1b76eeb0330ae1ddee3720d76145c2b308725245).
The final physics index SHA-256 is
`47d69f7dd75dff89e1d2e5191f2f1d31fad002581521c39eeee7593c90d83c41`.
The Haiku/physics code and final-index reader fix have since been integrated in
`work/final-integration-20261022`; the [integration record](FINAL_INTEGRATION.md)
supersedes earlier pending-integration statements. DeepSeek comes from
[`550391b`](https://github.com/DavideTisi/interphAIse/tree/550391b86fa18aee72a4738838936066b388655a),
read as immutable Git objects. Its code/archive merge remains separate.

The [independent review receipt](data/reviews/deepseek_results_review_20261022.json)
records all 360 DeepSeek run hashes and reproduces counts, paired tests and
selected LLZO audit statistics. It is a results recount, not a second execution
of Adem's complete production validator. This update also reads the existing
24-slide deck's text to identify exactly which arguments need revision.

## Why the LLM is central

The scientific task is to decide **what is worth calculating next**, not simply
to invoke a calculator. We delegate four pieces of human judgment to the LLM:

1. Connect chemical knowledge to a promising material choice.
2. Interpret a failed or promising result and formulate a revised direction.
3. Allocate the next evaluation within a finite budget.
4. Make a numerical forecast that the next calculation can contradict.

Deterministic code orchestrates calls, validates IDs, enforces budgets and
constructs feedback. Materials Project thermodynamics and PET-MAD provide the
numerical results. Human researchers still define the candidate space, objective,
construction rules and final scientific interpretation. The LLM is therefore
central **as the decision policy being tested**. It is neither the source of
the reported energies nor a substitute for the whole scientist.

The repeat sharpens the distinction between proposing a useful starting set
and changing direction productively after observations. A model can do the first
well and fail to improve through the second. Interpreting feedback is an assigned
role, not proof that every rationale is sound. There is no matched human-expert
arm, so delegation of a human task must not be described as demonstrated
equivalence to, or superiority over, human intuition.

The five-arm experiment tests observable consequences of feedback. It cannot
prove an internal reasoning mechanism or distinguish every contribution of
recall, pattern matching and reasoning. Chemical rationales are hypotheses,
not self-validating evidence. The sequential control retains its own history,
and the shuffled control can retain some correct assignments or contradict
earlier rationales; those limitations remain part of the interpretation.

### Relation to HELLMM

The supplied HELLMM paper describes an LLM selecting transformation rules,
enumerating intermediates and filtering chemical plausibility, followed by
deterministic graph constraints, atomistic calculations and electrochemical
scoring. Its described stages are sequential, without a feedback loop.

interphAIse follows the same division of scientific labor: the LLM decides
which hypotheses deserve numerical investigation. Its hypothesis space is
narrower: it selects known material IDs and makes property forecasts rather
than proposing a mechanism graph. Its distinctive contribution is repeated,
controlled evaluation of how result feedback changes selection. This is not
a basis for declaring one project universally better. HELLMM delegates a richer
generative chemical task; interphAIse more directly tests feedback-dependent
decision-making. Both expose the risk that a proxy objective can reward choices
that do not match the intended physical problem.

## The original 50-structure benchmark

The frozen v3 pool contains 50 structure IDs representing 43 formulas, with
two acceptable structures. Different polymorphs remain distinct choices. Haiku
5.5 used temperature 1.0 and a ten-query budget, with 30 runs per arm.

| Arm | Successful runs / 30 |
|---|---:|
| Iterative, true feedback | 19 |
| Sequential, no result feedback | 4 |
| Shuffled feedback | 6 |
| Upfront shortlist | 4 |
| Sampled random | 10 |

The exact random success probability at ten queries is **36.33%**. Iterative
versus shuffled has 16 iterative-only and three shuffled-only successful seeds,
with exact paired McNemar p approximately **0.0044**, unadjusted. This supports
the usefulness of correct feedback on this task. It does not establish that
the LLM is the strongest possible policy: the archived **post-hoc fluoride-first
rule succeeds by query 2**. The original ten-run preview is superseded by these
30-run results and should not be added to them.

## The Haiku three-environment production study

The expansion contains 141 structure IDs and 100 formulas, evaluated against
LiCoO2 at 4.0 V with three electrolyte choices. It includes the original pool,
so the sulfide result is an expanded test, not an independent replication on
disjoint chemistry. Five arms, three environments and 30 runs give **450 runs**
and **4,500 charged evaluations**. Runs start with fresh histories; this is
environment-dependent performance, not learning transferred between environments.

| Electrolyte | Acceptable pool | Iterative | Sequential | Shuffled | Upfront | Sampled random | Exact random at 10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Li6PS5Cl | 4 / 141 | 20 / 30 | 2 / 30 | 6 / 30 | 0 / 30 | 8 / 30 | 25.7% |
| Li3InCl6 | 55 / 141 | 30 / 30 | 30 / 30 | 30 / 30 | 30 / 30 | **29 / 30** | 99.4% |
| LLZO | 17 / 141 | 12 / 30 | 0 / 30 | 4 / 30 | 1 / 30 | 24 / 30 | 73.6% |

The chloride random count corrects the shorthand claim that every arm succeeded
in every run. It remains the predeclared near-ceiling condition.

The primary planned tests are paired exact McNemar, with Holm correction across
six comparisons. Three survive the 0.05 threshold:

| Environment | Iterative compared with | Raw p | Holm p |
|---|---|---:|---:|
| Sulfide | Sequential | 0.000007629 | **0.00004578** |
| Sulfide | Shuffled | 0.0005188 | **0.002441** |
| Chloride | Sequential | 1 | 1 |
| Chloride | Shuffled | 1 | 1 |
| LLZO | Sequential | 0.0004883 | **0.002441** |
| LLZO | Shuffled | 0.05737 | 0.1721 |

The supported conclusion is narrower than “LLM search beats random.” In sulfide,
feedback produces a strong advantage over the controls and a higher observed
success rate than random. In LLZO it improves on sequential selection but loses
to random. Chloride does not discriminate between policies at this budget.

### What the chemical trajectories show

In the selected sulfide trace (seed 202), Haiku refines fluoride chemistry:
Li3AlF6 at query 6 has penalty 0.160, LiMgAlF6 at query 7 has 0.057, and
LiCaAlF6 at query 8 has 0.048 and passes. The penalties are in eV/non-Li atom.
This makes the delegated judgment concrete: connect a near miss to a different
chemical composition and spend the next query on it. The chemical explanation
is still a model hypothesis, not a demonstrated causal mechanism.

For LLZO, random samples 95 distinct formulas across 300 picks. Iterative
samples 33, upfront 22 and sequential 19. Random makes 33 acceptable picks,
iterative 29, but **28 of iterative's 29 acceptable picks occur in queries 6–10**,
and 26 are LiAlSiO4 polymorphs. Ten of its 12 successful runs first succeed at
queries 8–10. Feedback helps it escape a poor starting direction, but the escape
is late and narrow. These are pooled descriptive patterns, not proof of the
model's private cognitive process.

### The LLZO evaluator caveat

The post-hoc audit flags five of 17 acceptable structures across LiIO3, LiClO4
and Li5IO6 for practical chemical review. The first two have supplier oxidizer
classifications; Li5IO6 was flagged at the chemical-family level without a
verified compound-specific classification. This is not a comprehensive safety
or synthesis screen.

Of random's 24 successful runs, **18 also find an unflagged acceptable candidate**
and six succeed only through flagged candidates. This partition does not change
the primary 24-versus-12 result and is not a rerun under a revised objective.
There is no evidence that Haiku deliberately avoided these compounds on safety
grounds. The evaluator includes O2 products, so it is also incorrect to explain
the caveat by saying it cannot form gas or that oxidized anions cannot react.
The actual limitation is the gap between a 0 K thermodynamic proxy and practical
temperature, processing, gas evolution, transport and cycling behavior.

## What the completed DeepSeek repeat changes

The repeat adds 360 LLM runs using the same pools, prompts, arms, seeds and
ten-query budget. The original 90 random runs are reused. The combined
environment study therefore contains **810 distinct runs: 720 LLM runs and
90 random runs**, not 900. The original 150-run benchmark is separate historical
evidence with overlapping chemistry, not another independent replication.

| Electrolyte | Model configuration | Iterative | Sequential | Shuffled | Upfront | Shared random |
|---|---|---:|---:|---:|---:|---:|
| Li6PS5Cl | Haiku | 20 | 2 | 6 | 0 | 8 |
| Li6PS5Cl | DeepSeek | 12 | 2 | 3 | 2 | same 8 |
| Li3InCl6 | Haiku | 30 | 30 | 30 | 30 | 29 |
| Li3InCl6 | DeepSeek | 30 | 30 | 30 | 30 | same 29 |
| LLZO | Haiku | 12 | 0 | 4 | 1 | 24 |
| LLZO | DeepSeek | 10 | 4 | 12 | 20 | same 24 |

Entries are successful runs out of 30. Success means at least one coating
passing the frozen criterion within ten queries, not a measured improvement
in a battery. The exact random probabilities remain 25.7%, 99.4% and 73.6%.
The sampled LLZO random outcome is 80%; neither percentage should replace
the other without a label.

### Sulfide: strong Haiku evidence, a weaker DeepSeek trend

Haiku's 20/30 versus 2/30 sequential and 6/30 shuffled remains the strongest
controlled feedback result. DeepSeek's 12/30 versus 2/30 and 3/30 has the same
direction. Its adjusted p values are 0.07764 and 0.11230, so the repeat does not
provide a second statistically significant confirmation at the declared 0.05
threshold. It also does not establish the absence of a DeepSeek feedback effect.

Each configuration has its own preregistered six-test Holm family:

| Environment | Iterative compared with | Haiku Holm p | DeepSeek Holm p |
|---|---|---:|---:|
| Sulfide | Sequential | 0.00004578 | 0.07764 |
| Sulfide | Shuffled | 0.002441 | 0.11230 |
| Chloride | Sequential | 1 | 1 |
| Chloride | Shuffled | 1 | 1 |
| LLZO | Sequential | 0.002441 | 0.4375 |
| LLZO | Shuffled | 0.1721 | 1 |

Three Haiku comparisons and no DeepSeek comparisons survive correction.
Significance in one configuration and not the other does not establish a
statistically significant difference between configurations. Cross-model
contrasts were declared descriptive, and remain so.

### LLZO: a useful prior can outperform the same model's adaptive policy

The major new observation is DeepSeek upfront at **20/30**, compared with
Haiku upfront at **1/30**. DeepSeek proposes LiAlSiO4 before receiving results,
whereas Haiku's iterative arm tends to reach it late. The acceptable DeepSeek
upfront picks are LiAlSiO4 (18), LiMgPO4 (3) and LiAl(SiO3)2 (1): 22 picks
across 20 successful runs. This demonstrates that useful starting choices are
available to an LLM under this setup. Haiku's poor upfront performance is not
a general property of every LLM configuration tested.

The iterative results are still only **10/30 for DeepSeek and 12/30 for Haiku**,
against random's 24/30. DeepSeek's sequential and shuffled controls are 4/30
and 12/30, with no significant planned feedback contrast. Useful starting
knowledge therefore does not guarantee useful sequential adaptation. Upfront
versus iterative also changes batch planning versus sequential selection, so
20/30 versus 10/30 does **not isolate a causal harm from feedback**. Likewise,
12/30 shuffled versus 10/30 iterative is not evidence that incorrect feedback
is beneficial.

This revises the previous explanation of LLZO. Haiku's narrow, late trajectory
is real, but cannot explain both configurations. DeepSeek's iterative selections
cover 45 formulas across runs versus 38 for upfront, yet average only 8.7 distinct
formulas per run versus 10.0 upfront. Across-run variety and within-run coverage
are different quantities. More aggregate variety by itself does not demonstrate
better exploration or explain why the ten-query policy succeeds less often.

### Practical annotation: retain the primary score and qualify it

| LLZO policy | Frozen-criterion successes | Runs finding an unflagged acceptable candidate | Successes only through flagged candidates |
|---|---:|---:|---:|
| Random | 24 | 18 | 6 |
| Haiku iterative | 12 | 12 | 0 |
| DeepSeek upfront | 20 | 20 | 0 |
| DeepSeek iterative | 10 | 9 | 1 |

All counts are out of 30. The annotation uses the same narrow oxyhalogen review
set described above. DeepSeek upfront does not need those flagged compounds to
succeed. This weakens an explanation that the random advantage is entirely an
artifact of questionable compounds or that all LLMs must avoid the accepted set
for chemical reasons. Random still wins on the frozen primary outcome.
The descriptive 20-versus-18 unflagged comparison must not be promoted to a
new confirmatory claim that DeepSeek beats random. Unflagged is not a guarantee
of practical suitability, safe processing or lithium transport.

### Chloride and the scope of the model comparison

All four LLM arms in both configurations succeed in all 30 chloride runs.
With 55/141 acceptable structures and a 99.4% exact random success probability,
this is a weak discriminator at the chosen budget, as predicted before running.
An aggregate across the three environments would obscure this ceiling and the
opposing sulfide/LLZO patterns. Keep the environment-specific results central.

DeepSeek V3.2 used OpenRouter, SiliconFlow fp8, no provider fallback, a 3,072-token
reasoning cap within a 4,096-token total, and temperature 1.0. Haiku used the
Anthropic configuration with a 4,096-token requested output cap. These are
comparisons of **model configurations, not matched reasoning compute**. The
archives report about 6.43 million reasoning tokens for DeepSeek versus 1.52
million for Haiku. Extra reasoning usage did not produce a uniform advantage;
the experiment does not isolate the effect of reasoning tokens themselves.

There was no DeepSeek repeat of the prospective PET-MAD pilot. The physical
predictions and their failures below belong to Haiku only.

## The three-coating physical pilot

The agreed cheap-benchmark design called for a limited MLIP follow-up. The
subsequent pilot amendment made that follow-up prospective: one known reference,
two LLM choices, and forecasts archived before the corresponding interface
energies. PET-MAD S 1.6.0 trained on r²SCAN supplied the numerical model.

LiNbF6 was the reference. The feasible alternatives were LiTaF6, LiCaAlF6 and
LiF, after a documented pre-energy atom-cap amendment to 1,250. LiF did not pass
the frozen thermodynamic criterion. LiZr2(PO4)3 was not buildable on both contacts
within the common limits. Haiku chose LiTaF6, then LiCaAlF6. The second choice
matched its original shortlist and was the only remaining acceptable option.

For each new coating, three geometrically distinct registry positions per contact
were evaluated. Selection minimized relaxed joined-interface energy. “Common
protocol” means common construction/selection/relaxation rules, not identical
facets, slab counts, cells or strain for every composition.

| Coating | Cathode W_adh / W_sep | Electrolyte W_adh / W_sep | Role |
|---|---:|---:|---|
| LiNbF6 | 3.617 / 5.168 | 1.633 / 2.967 | Reference |
| LiTaF6 | 3.339 / 4.728 | 1.577 / 2.911 | LLM choice 2 |
| LiCaAlF6 | 1.427 / 4.322 | 0.744 / 1.490 | LLM choice 3 |

Units are J/m². The electrolyte is the weaker contact in all three cases.
W_adh allows the separated slabs to relax under the defined constraints;
W_sep separates fragments at their joined geometry. They are different model
observables. Neither is measured adhesion or fracture toughness.

### What the LLM predicted

| Coating / contact | Prospective W_adh range | Observed | Outcome |
|---|---:|---:|---|
| LiTaF6 / cathode | 3.2–3.9 | 3.339 | Within range |
| LiTaF6 / electrolyte | 1.4–1.9 | 1.577 | Within range |
| LiCaAlF6 / cathode | 3.0–3.8 | 1.427 | Below range |
| LiCaAlF6 / electrolyte | 1.4–1.9 | 0.744 | Below range |

Haiku correctly predicted the weaker contact twice and acknowledged the Ca–Al
miss. The forecasts are not calibrated confidence intervals. Two material choices
cannot establish prediction reliability or expensive-search superiority. The
choice order never changed, so the physical pilot does **not** demonstrate an
adaptive-selection advantage. It demonstrates a testable analogy, a substantial
failure of that analogy on a less similar coating, and subsequent assessment.

The summary confused `min_W_adh_J_m2`, which means the weaker of the selected
contact values, with a minimum across registries. The accompanying interpretation
corrects that reading; the original response remains archived. A future protocol
should rename the field `weaker_contact_W_adh_J_m2`.

### How robust is the physical ordering?

LiNbF6 exceeds LiTaF6 by only **0.056 J/m²** at the weaker contact. Changing
the electrolyte bulk reference shifts their W_adh by approximately **−0.121**
and **−0.114 J/m²**, respectively. Those finite construction sensitivities
exceed the primary gap. They are not statistical uncertainty bars and combine
bulk arrangement, cell, strain, area and fixed-atom differences. A robust winner
between Nb and Ta has not been established.

LiCaAlF6 has substantially lower primary adhesion in the tested constructions.
Its electrolyte registry range is **0.523–0.744 J/m²**. Four available robustness
checks change W_adh by at most 0.014, but its **electrolyte thickness and bulk
structure sensitivities remain unquantified**. Those unavailable slots were
declared before its energies; they are not zero-valued uncertainties.

Both contacts remain formally polar. Bulk relaxation, thickness, constraint,
registry and device checks improve numerical credibility but do not remove
that physical limitation. Vacuum independence is an isolation check within
an 8 Å finite-range model, not proof that polar electrostatics are converged.
The early 2.10 / 0.43 J/m² pilots used different bulk references and constructions
and must not be compared as if they were measurements in the final series.

## Comparison with the original design

| Original aim or design element | Outcome | Assessment |
|---|---|---|
| Delegate human intuition in proposing the next calculation | LLM selects, interprets feedback and forecasts physical results | Implemented within a known-material menu; human-level performance untested |
| Separate starting knowledge from the value of feedback | Upfront, sequential, shuffled and random controls in two configurations | Stronger evidence that these contributions can differ; internal reasoning remains unobserved |
| Use a meaningful candidate pool | Six-candidate prototype grew to 50, then 141 structures | Achieved; polymorph duplication and overlapping pools disclosed |
| Repair the evaluator before decisive runs | Self-stability, insulation, bins, equilibrated-contact objective and provenance | Achieved for the frozen proxy; practical blind spots remain |
| Use cheap thermodynamics as a fully known benchmark | Exhaustive tables, exact random, acceptance and best-bin endpoints | Achieved; no compute-saving claim from this layer |
| Compare 3–5 coatings under a shared MLIP protocol | Three coatings across two contacts with sensitivity evidence | Lower end achieved; conventional LiF comparator not evaluated |
| Demonstrate useful closed-loop expensive discovery | Two prospective choices and forecast assessments | Partial; order unchanged, no repeated expensive-policy control |
| Find better candidates than random | Haiku sulfide advantage; both iterative arms lose on LLZO; chloride ceiling | Conditional on configuration, task and policy |
| Discover a novel functional coating or validate a battery | Known materials, proxy thermodynamics and polar contact models | Not established; transport and experiment remain outside scope |

The initial broad ambition was a full discovery loop. The agreed design A was
already more restrained: a rigorous cheap benchmark followed by limited MLIP
evaluation. Relative to design A, the project achieved the main implementation
and a three-coating follow-up, and exceeded the early plan in controls,
environment coverage and provenance. Relative to the broader ambition, it has
not demonstrated general search acceleration, novel composition discovery or
physical performance improvement.

DeepSeek makes a broad claim that feedback reliably improves LLM discovery less
defensible. It makes the assessment of the original idea more informative:
chemical prior knowledge can be useful without effective adaptation, and correct
feedback can rescue a poor starting direction in some tasks. We should describe
where that happens rather than claim a universally superior model or strategy.

The strongest story is **a controlled test of LLM scientific selection and
forecasting**. The numerical tools make intuition accountable to observations.
The study measures both when that judgment helps and when simpler exploration
does better. The human researcher still chooses which objectives represent
useful science and judges the physical limitations of the answers.

## Engineering review and what was deliberately not claimed

The project progressed beyond a working demo to an inspectable experiment:
charged IDs and invalid-query accounting, replay of production queries,
per-attempt HTTP records, a durable live-call cap, manifest-derived coverage,
source-file validation before prompts, convergence gates, checkpoint consistency,
and separate decision-time versus robustness records. These controls matter
because an apparent LLM improvement is uninformative if failures are free,
future outcomes leak into prompts or the physical packages mix models.

Earlier reviews identified and corrected concrete problems: hidden termination
choices under enumeration cutoffs, non-equivalent electrolyte cuts, duplicate
physical registries, fixed-atom selections changing with cell construction,
and mixing total energies from different constraint regions. Those corrections
are part of the methodology, not additional discovery successes. The pinned
pymatgen versions also resolve the reported environment-dependent matcher tests.

The supporting modeling-decision comparison and the optional IDs-only control
are not part of the completed confirmatory results presented here. We should
not imply that every proposed arm was run. The final-index reader compatibility
patch and the completed Haiku/physics branches are now integrated. Earlier
pending-patch statements are superseded by FINAL_INTEGRATION.md. The incoming
DeepSeek archive has been independently recounted, but its provider/client and
analysis changes still require the separate integration review.

## Revised project narrative and presentation plan

### Suggested project description

interphAIse asks whether an LLM can take over part of the scientific judgment
used to choose battery coatings. The model proposes candidates and revises its
choices using computed evidence. Materials Project thermodynamics and PET-MAD
evaluate the candidates. Across three battery environments and two LLM
configurations, useful prior knowledge and useful feedback prove to be distinct
strengths. Correct feedback substantially improves Haiku's sulfide search.
DeepSeek proposes useful LLZO candidates upfront, but neither iterative model
matches random exploration there within ten queries. A prospective three-coating
pilot then tests numerical predictions against atomistic calculations: the
LiTaF6 analogy holds and the LiCaAlF6 forecasts fail. The result is a reproducible
way to delegate and test scientific choices, with explicit limits on both LLM
judgment and the physical models.

### Changes to the existing 24-slide checkpoint

This is a revision plan, not a claim that the PowerPoint/PDF has been edited.
The existing deck's Haiku and PET-MAD numbers remain valid, but its overall
story needs revision. Adding only a DeepSeek appendix would leave the main
LLZO explanation incomplete.

| Current slide(s) | Required narrative change |
|---|---|
| 2, “Feedback helps. The advantage is conditional.” | Lead with the distinction between useful chemical priors and useful feedback. Make the tested configuration and task explicit. |
| 3, delegated selection judgment | Retain the central LLM role. Distinguish assigned interpretation from demonstrated reliable judgment and avoid human-equivalence claims. |
| 4, HELLMM comparison | Move to backup in a short hackathon pitch. Keep its role as inspiration, not a second project to explain. |
| 5–7, study design | Show two configurations, three environments, four LLM arms plus shared random, and 810 distinct environment runs. Explain the frozen proxy and the separate Holm families. |
| 8, original 50-structure benchmark | Move to backup/history. The expanded two-configuration study is the main evidence; overlapping pools are not independent replication. |
| 9, environment outcomes | Replace the Haiku-only view with both configurations and the common random reference. Use the same arm colours, per-environment panels and labelled uncertainty. Chloride remains the declared ceiling condition. |
| 10–12, chemical trajectories and LLZO explanation | Retain one illustrative Haiku sulfide trace. Contrast Haiku reaching LiAlSiO4 late with DeepSeek proposing it upfront. State that both iterative policies remain below random. |
| 13–16, physical pilot | Keep as a supporting prospective test, explicitly labelled Haiku. Show both forecast hits and both misses; retain the small Nb/Ta gap, formal polarity and missing Ca–Al sensitivity checks. |
| 17–18, design review and conclusion | Conclude that selection and forecasts can be delegated and tested, with conditional value. General acceleration, human-level judgment and an experimentally superior coating remain open. |
| 19, planned statistical tests | Show both six-test families. Three Haiku contrasts and zero DeepSeek contrasts pass; do not interpret that difference as a cross-model significance test. |
| 20–21, proxy and LLZO audit | Add the unflagged-hit annotation, clearly post-hoc. Preserve random's 24/30 primary result and distinguish unflagged candidates from practically validated coatings. |
| 22–23, physical definitions and structures | Preserve the archived physical evidence. No DeepSeek interface data exist; the public viewer's values are unchanged. |
| 24, reproducibility and integration | Replace the old pending-reader-patch status with the completed Haiku/physics integration, the public viewer and the remaining DeepSeek merge/release work. |

For a short presentation, use nine main slides and retain the technical detail
in backup:

1. **Battery coatings and the selection problem.** State the reaction-protection
   purpose and the separate need for transport and physical contact. Introduce
   the specific judgment delegated to the LLM.
2. **The LLM's scientific decisions.** Show candidate choice and interpretation
   alongside the deterministic evaluators. Human researchers define the objective.
3. **Controlled search experiment.** Define acceptability, the ten-query budget,
   the two configurations and the controls. Cheap exhaustive tables provide
   ground truth; they do not demonstrate saved computing cost.
4. **Results across environments.** Show the full comparison with random and
   labelled uncertainty. Explain the chloride ceiling briefly.
5. **Correct feedback helps Haiku on sulfide.** Show the relevant planned
   comparisons and one concrete trajectory; include the weaker DeepSeek trend.
6. **DeepSeek's upfront knowledge works better on LLZO.** Show 20/30 versus
   Haiku's 1/30, alongside iterative 10/30 and 12/30 and random 24/30. Add the
   practical annotation without redefining success.
7. **Prospective atomistic forecasts.** Present the two material predictions and
   their outcomes with the measured model values. The Ta success and Ca–Al miss
   belong on the same slide.
8. **What remains unproven.** State the practical proxy limitations, polar
   contact models, unresolved Nb/Ta ordering and lack of a human benchmark.
9. **Reproducible scientific judgment.** Close with the conditional conclusion,
   source evidence and the public structure viewer. Candidate prioritization is
   demonstrated; validated battery improvement is future work.

The Word overview and graphical abstract need the same narrative update when
the presentation is revised. A new image is optional; an honest comparison
chart is more informative than an illustration suggesting universal improvement.
The viewer continues to show the six computed interfaces and needs no scientific
data change for this repeat. LiF stays explicitly uncomputed in every deliverable.

## Accounting, reproducibility and remaining work

Haiku environment production used 2,800 API calls, about **USD 3.63** at the recorded
list rates. The physical pilot used **five of ten HTTP attempts**, 17,365 input
and 8,463 output tokens, about **USD 0.005968**. These are logged usage estimates,
not verified bills or a new check of current provider pricing.

DeepSeek production reports 2,793 calls and **USD 8.99** charged as recorded by
OpenRouter. The key total including the stopped duplicate launch is **USD 9.19**,
under its USD 12 ceiling. The duplicate is excluded from the analysis. Keep
provider-recorded charges distinct from Haiku's list-price estimates; the study
does not compare equal reasoning budgets or establish a universal cost winner.

The new physical campaign completed **26 of the 36-job ceiling**: 12 primaries,
ten sensitivities and four reference consistency checks. It used 6,632 runner
calculator calls and 52 additional rigid-fragment single points. Runner times
sum to 25.4 minutes, while summed completed Slurm elapsed times are 47.5 minutes.
Neither includes queue time. Six reused saved cases and bulk preparation are
separate from the 26-job total.

Decision-time packets remain unchanged. The robustness-inclusive final index
was released after the LLM summary and was not used to improve the recorded
predictions. The summary-only character limit was amended from 16,000 to 20,000
after an uncharged stop. The amendment is recorded and hashed; the exact earlier
unsent text was not archived, so byte-identical content before and after the
stop cannot be independently demonstrated.

The [final review](FINAL_PILOT_REVIEW.md) already independently checked source
energies, 32 saved runs and 96 free-force maxima. This synthesis re-extracts the
reported data and verifies chart endpoints and selected minima; it does not
repeat MLIP calculations or claim a new full code review. The tested final-index
reader patch is now integrated. This narrative revision reuses that physical
review and the independent DeepSeek recount; it does not repeat simulations
or the complete software test suite for documentation edits.

Recommended next work, in order:

1. Review and integrate DeepSeek's code/archive, then run the relevant integrated
   checks under the pinned dependencies. The earlier Haiku/physics integration
   is complete. No further paid calls or physics runs are required for this study.
2. Revise the main presentation, overview and write-up using the plan above.
   Preserve frozen scores and separate prospective decisions from later
   robustness. Keep the LLZO random advantage, failed forecasts and physical
   limitations visible. Davide retains control of repository publication.
3. For a new research iteration, preregister an exploration-aware policy against
   stronger simple chemistry baselines and new/disjoint tasks. Do not retune the
   completed benchmark and relabel it confirmatory evidence.
4. Improve physical and practical validity before declaring a coating winner:
   transport and processing criteria, more defensible surface/electrostatic
   treatment, and targeted higher-fidelity or experimental checks.

No new live LLM call, MLIP calculation or cluster submission occurred during
this synthesis. The existing presentation's package and visual validation are
recorded in the development log. The DeepSeek narrative update is documented
here; its PowerPoint, PDF, Word and illustration updates remain to be made.
