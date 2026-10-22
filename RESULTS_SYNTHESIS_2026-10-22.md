# interphAIse: results synthesis and review against the original design

**22 October 2026.** This consolidates the 21 October search experiments and the
completed 22 October PET-MAD pilot. It supersedes preliminary ten-run summaries,
smoke-only environment status and early interface-pilot energies for purposes
of the final presentation. It does not modify any frozen experiment or result.

The main result is **conditional evidence that correctly attributed computational
feedback improves Haiku's materials choices**. That benefit is substantial for
the sulfide task, limited by a ceiling in the chloride task, and insufficient
to beat random exploration on LLZO. The physical pilot adds a prospective test
of chemical analogy: the LiTaF6 forecasts held, while both LiCaAlF6 forecasts
failed. We have demonstrated and audited a bounded scientific decision process;
we have not discovered or experimentally validated a superior battery coating.

## Deliverables and source boundary

- [New presentation](presentations/results_2026-10-22/interphAIse_results_synthesis_2026-10-22_v2.pptx):
  18 main slides plus six technical backup slides, editable charts/tables and
  source notes. The older 21 October presentation is preserved. A
  [static PDF](presentations/results_2026-10-22/interphAIse_results_synthesis_2026-10-22_v2.pdf)
  is included for sharing.
- [Presentation evidence](presentations/source/results_synthesis_2026-10-22.json)
  contains the exact plotted values, reconstructed success curves, contrasts,
  selected physical rows and immutable source references.
- [Presentation builder](presentations/source/build_results_synthesis_2026-10-22.mjs)
  records the slide narrative and layout.

Sources are `davide` at `750b382`, agent branch at
[`800ba03`](https://github.com/DavideTisi/interphAIse/tree/800ba0378779ce7df9038bc4857719a29c2fe0a7)
and physics branch at
[`1b76eeb`](https://github.com/DavideTisi/interphAIse/tree/1b76eeb0330ae1ddee3720d76145c2b308725245).
The latest agent change adds interpretation/reporting, not new experimental
outcomes. The final physics index SHA-256 is
`47d69f7dd75dff89e1d2e5191f2f1d31fad002581521c39eeee7593c90d83c41`.
The source branches were read without merging them into this checkout.

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

## The three-environment production study

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
| Substitute human intuition in proposing the next calculation | LLM selects, interprets feedback and forecasts physical results | Achieved within a bounded known-material menu |
| Separate feedback use from literature recall | Upfront, sequential, shuffled and random controls; repeated seeds | Substantially stronger evidence, with residual control limitations |
| Use a meaningful candidate pool | Six-candidate prototype grew to 50, then 141 structures | Achieved; polymorph duplication and overlapping pools disclosed |
| Repair the evaluator before decisive runs | Self-stability, insulation, bins, equilibrated-contact objective and provenance | Achieved for the frozen proxy; practical blind spots remain |
| Use cheap thermodynamics as a fully known benchmark | Exhaustive tables, exact random, acceptance and best-bin endpoints | Achieved; no compute-saving claim from this layer |
| Compare 3–5 coatings under a shared MLIP protocol | Three coatings across two contacts with sensitivity evidence | Lower end achieved; conventional LiF comparator not evaluated |
| Demonstrate useful closed-loop expensive discovery | Two prospective choices and forecast assessments | Partial; order unchanged, no repeated expensive-policy control |
| Find better candidates than random | Strong sulfide result, LLZO loss, chloride ceiling | Conditional, not general |
| Discover a novel functional coating or validate a battery | Known materials, proxy thermodynamics and polar contact models | Not established; transport and experiment remain outside scope |

The initial broad ambition was a full discovery loop. The agreed design A was
already more restrained: a rigorous cheap benchmark followed by limited MLIP
evaluation. Relative to design A, the project achieved the main implementation
and a three-coating follow-up, and exceeded the early plan in controls,
environment coverage and provenance. Relative to the broader ambition, it has
not demonstrated general search acceleration, novel composition discovery or
physical performance improvement.

The strongest story is therefore **an auditable test of scientific selection
under feedback**, with both a success and a failure, followed by a real prospective
calculation that can falsify the LLM's chemical intuition. That is more defensible
than presenting the project as an autonomous discovery of the best coating.

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
patch is still outstanding at the inspected agent head; it affects final offline
report integration, not the preserved primary energies or live decisions.

## Accounting, reproducibility and remaining work

Environment production used 2,800 API calls, about **USD 3.63** at the recorded
list rates. The physical pilot used **five of ten HTTP attempts**, 17,365 input
and 8,463 output tokens, about **USD 0.005968**. These are logged usage estimates,
not verified bills or a new check of current provider pricing.

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
reader patch remains a separate integration task at the inspected agent head.

Recommended next work, in order:

1. Apply the final-index reader patch, run integrated checks, review the combined
   branch diff, and synchronize the viewer and final figures. No additional
   paid calls or physics runs are needed to close this bounded pilot.
2. Present the frozen primary results and later robustness separately. Keep the
   failed forecasts, LLZO random advantage, polar-surface caveat and missing
   sensitivity slots visible.
3. For a new research iteration, preregister an exploration-aware policy against
   stronger simple chemistry baselines and new/disjoint tasks. Do not retune the
   completed benchmark and relabel it confirmatory evidence.
4. Improve physical and practical validity before declaring a coating winner:
   transport and processing criteria, more defensible surface/electrostatic
   treatment, and targeted higher-fidelity or experimental checks.

No new live LLM call, MLIP calculation or cluster submission occurred during
this synthesis. The final presentation's package and visual validation are
recorded in the development log.
