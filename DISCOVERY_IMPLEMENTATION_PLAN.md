# interphAIse — implementation and experimental plan

20 October 2026. Planning document; the work below is not yet implemented unless
explicitly listed as existing. This plan supersedes the experimental design in
`DISCOVERY_REPORT.md` where they differ, and incorporates `DISCOVERY_REVIEW.md`.

**Implementation checkpoint — 21 October:** See [EVALUATOR_HANDOFF.md](EVALUATOR_HANDOFF.md).
The standalone v2 evaluator and 50-candidate draft pool now exist on `davide`;
consistent thermo-entry retrieval, full-pool validation and agent integration remain.

## 1. The scientific question

**Does computational feedback improve an LLM's selection of compatible battery
coating candidates beyond its initial chemical knowledge?**

Given a cathode, solid electrolyte, operating potential, candidate pool and
limited number of evaluations, the agent selects a coating, receives calculated
results, interprets them and chooses the next candidate. The main experiment is
on a frozen, exhaustively evaluated thermodynamic benchmark (design A). MLIP
calculations follow on a small, consistently chosen subset.

The output is a compatibility shortlist, not a prediction of the best functioning
battery coating. Lithium transport, synthesis, coating morphology and long-term
cycling performance are not established by the initial evaluator.

## 2. Why use an LLM? Where does it replace human intuition?

A researcher facing fifty possible coatings does not usually pick blindly. They
use chemical knowledge to decide which material families are promising, formulate
an explanation for their choice, and revise that explanation when calculations
contradict it. **This candidate-selection and hypothesis-revision work is the
human intellectual task the LLM is intended to substitute.**

| Human scientific activity | LLM activity | Observable evidence of usefulness |
|---|---|---|
| Form an initial chemical hypothesis | Select a candidate and explain why its chemistry could suit both contacts | Initial shortlist versus random selection |
| Interpret a failed candidate | Identify which calculated criterion failed and what this implies for the working hypothesis | Explanation refers to the actual returned measurements |
| Generalise cautiously to related candidates | Decide whether to explore a related composition or a different family | Subsequent selections improve under the fixed evaluator |
| Balance refinement and exploration | Choose between a near neighbour of a promising candidate and a chemically different option | Search reaches acceptable candidates efficiently |
| Reconsider assumptions | Revise a hypothesis or state that the feedback is inconclusive | True-feedback selection outperforms a matched no-feedback control |

Illustrative example, not a scientific result: a proposed oxide is compatible
with the cathode but reacts strongly with the electrolyte. A human might infer
that their original selection prioritised only one contact, inspect the reaction
products, and try a different anion chemistry. The LLM is asked to perform that
interpretation and choose the next test. It must not invent reaction energies,
transport properties or evidence that a whole family will behave identically.

The outer loop supplies the available tools and enforces the budget. The LLM
supplies the chemical proposals and revisions. The calculator supplies the
numbers. The evaluator supplies the fixed definition of success. The LLM cannot
modify that definition, declare its own candidate valid, or see unqueried results.

There is no need for an LLM to sort a completed table. Its proposed value is in
choosing what to evaluate before that table is known. Nor does a persuasive
explanation prove reasoning: the experiment tests whether feedback-conditioned
choices actually help. Familiar formulas allow prior knowledge and recall; the
controls below measure their contribution rather than claiming to remove them.

## 3. Chosen scope: design A, with MLIP follow-up

1. Construct approximately 50 candidates and freeze their identities.
2. Compute the inexpensive evaluator for the entire pool once.
3. Hide this result table behind a query interface. Charge one evaluation whenever
   an arm requests a new candidate, even though outcomes are cached.
4. Compare search strategies with matched query budgets and repeated trials.
5. Apply one common MLIP protocol to 3–5 selected candidates, including a baseline
   comparator, to assess whether favourable thermodynamic screening also gives
   plausible interfaces and adhesion.

This is a test of sample efficiency on an approximate evaluator with known
reference outcomes. It does not demonstrate actual wall-clock savings over an
exhaustive thermodynamic screen, nor prove transfer to expensive MLIP search.
MLIP follow-up is a separate validation stage, not a hidden change to the search
objective. Discovery is the headline; modelling-decision arms are supporting work.

## 4. Freeze the candidates and data provenance

Add `scripts/build_candidate_pool.py` and a versioned pool file under `data/pools/`.
Query Li-containing oxides, phosphates, borates, silicates, halides and other
polyanionic compounds. Use Xiao et al. as a source of candidate classes and
reference examples, not as the target ranking to reproduce.

Starting feasibility filters: ordered structures, energy above hull at most
25 meV/atom and primitive cells with at most 40 atoms. These are proposed practical
filters, not universal scientific requirements. Record any exception separately;
do not silently add a familiar coating that fails them. Use stratified sampling
by chemical family if there are too many candidates, with a recorded seed.

Each record must contain candidate ID, MP material ID, formula, structure,
chemical family, hull energy, band gap, retrieval date and relevant database/energy
provenance. Treat polymorphs explicitly: structure, gap and entry energy must refer
to the same material ID. The present formula-based gap lookup is insufficient.
Choose either one predeclared polymorph per formula or use IDs throughout search.
Store the pool hash and all filtering decisions. Fetch and cache calculations
before the experiment. Never adjust pool membership after viewing strategy results.

## 5. Evaluator v2 and a preregistered objective

Implement a structured result in `interphaise/discovery_evaluator.py` with:

- Cathode–coating reaction energy and products.
- Coating–electrolyte reaction energy and products.
- Coating self-decomposition penalty at the specified lithium chemical potential.
- Band gap for the pinned coating structure, with a separate missing-data status.
- Validity, provenance, units and diagnostic errors.

The current grand-potential mixing calculation excludes no-mixing decomposition
by default. Compute coating self-stability explicitly rather than confusing
mixing compatibility with stability against the lithium reservoir. Test on a case
where the coating decomposes without mixing. Check energy normalization carefully:
grand-potential energies and closed-system energies must be converted to a declared
common atom basis before comparing or combining them. Keep database and MLIP total
energies separate.

Use explicit language: reaction energies are non-positive; closer to zero means
less driving force for reaction. Self-decomposition penalties are non-negative;
smaller is better. Missing gaps or failed calculations are unknown/failed, not
positive evidence of compatibility.

Before strategy runs, freeze an `experiment.yaml` containing:

- The band-gap screening threshold and handling of missing data. A 2 eV gate is a
  starting proposal, not a calibrated conductivity criterion.
- Acceptability thresholds for both contacts and self-decomposition.
- The scalar penalty used for regret, its units and normalization. A simple
  candidate is the maximum of the three non-negative energy penalties after
  normalization. Report its components as well; do not obscure failure modes.
- Fixed energy bins (proposed width: 20 meV/atom), bin origin and boundary rules.
  Do not use pairwise “within tolerance” sorting, which can be non-transitive.
- Budgets, candidate pool hash, operating conditions, seeds and model settings.

For candidates passing the insulation/data gates, minimise the fixed penalty.
Use bins to define practically indistinguishable groups. Preserve genuine ties;
do not reward ever-larger band gaps or invent a secondary term merely to obtain a
unique winner. In a future expensive search, adhesion can distinguish candidates
within an energy bin. In design A, adhesion does not enter the search score.

Inspect the exhaustive distribution before any strategy runs: count valid and
acceptable candidates, tied groups and failures. If all candidates pass, all fail,
or the evaluator is constant, investigate whether this is a useful task. Document
any redesign and freeze a new version before running strategies. Never tune the
objective to make the LLM win.

## 6. Search strategies and information controls

Extend `interphaise/discovery.py` with a cached benchmark evaluator and these arms:

| Arm | Candidate choices | Feedback shown |
|---|---|---|
| Random | Uniform sampling without replacement | None |
| Upfront LLM | Ordered budget-sized shortlist in one call | None |
| Sequential LLM, no results | One choice per turn; previous choices visible | No outcomes |
| Iterative LLM | One choice per turn | True outcomes for queried candidates only |
| Shuffled-feedback LLM | Same interaction as iterative | Observed outcome bundles permuted among queried candidates |

Prioritise the first four if time is limited. The sequential no-results arm
controls for extra model interactions; iterative versus upfront alone does not
isolate feedback. Keep selected candidates, task instructions and remaining pool
visible consistently. Hide all evaluator data from no-results histories, including
accidental error/status/timing clues. Do not pass local artifact paths or the full
benchmark table to the proposer.

For shuffling, use a recorded seed and permute complete outcome bundles only from
already evaluated candidates. Do not reveal future outcomes. True scores remain
unchanged for evaluation. Log the displayed feedback separately. With one observed
candidate there is no nontrivial shuffle. Shuffled feedback tests sensitivity to
correct associations; a null effect alone does not prove the model ignores results.

Ask for candidate ID, a concise chemical hypothesis, the prior observation motivating
this choice, and whether this explores a new family or refines a previous idea.
These annotations support inspection, not an LLM-graded reasoning score. Keep
bounded retries, charge failed calculations to the budget and log invalid proposals.

Set and record temperature, provider, exact available model identifier, response
model metadata and sampling parameters. Fix the existing router path so requested
temperature is actually forwarded. Record provider limitations on reproducibility.
Use paired pool-order permutations across arms/repeats to reduce list-order bias.

## 7. Metrics, repeats and plots

Add `scripts/run_discovery_experiment.py` and
`scripts/analyse_discovery_experiment.py`. Start with 10 runs per LLM arm as a
practical minimum, not a guarantee of statistical power. Predeclare a budget
curve such as evaluations 1–10 for a pool around 50. If feasible, repeat on a
second, physically justified voltage/condition selected before examining results.
Keep claims conditional on this pool and these tasks.

Primary plot: probability of finding any acceptable candidate versus evaluations.
Secondary plots: best finite penalty/regret versus evaluations and probability of
reaching the best equivalence group. Explicitly show runs with no valid candidate;
do not silently omit them or assign an arbitrary finite regret. Display uncertainty
across repeats; do not interpret overlapping small differences as clear wins.

For N candidates, M acceptable ones and k uniform draws without replacement, the
exact random success probability is 1 − C(N−M,k)/C(N,k). Calculate tie-aware random
best-of-k distributions from the exhaustive table. Do not break ties by evaluation
order when claiming a unique winner. Record LLM tokens, calls, cost where available,
latency, evaluation count and calculation failures alongside scientific metrics.

The key contrast is iterative versus sequential without results; upfront measures
initial prior knowledge. No observed improvement is an informative outcome. Do not
infer general scientific reasoning from one successful material shortlist.

## 8. MLIP follow-up and integration fixes

Use a predeclared selection rule for 3–5 candidates: leading compatibility groups
with a fixed diversity/tie rule, plus a baseline-selected comparator. Avoid picking
only the most visually appealing successful structures. Use the same potential,
facet/termination search budget and relaxation settings for all. Report failed
builds, invalid structures, adhesion and sensitivity to selected geometries.

Record per-candidate deltas of relaxation and single-point counters, wall time,
potential version and actual structures. These counters describe the follow-up;
they do not retrospectively turn cached benchmark queries into expensive searches.

Tag screen outputs with `purpose: discovery_eval` and make both comparison/scoring
scripts exclude these outputs. Require matching system, voltage and candidate pool
when comparing standalone decision arms. Add schema/objective/pool versions to
results. Preserve old output compatibility explicitly rather than silently mixing
experiments. Align `REPORT.md` and README after this design is frozen. Update the
shared report only when its destination is identified.

## 9. Implementation order and checks

| Priority | Deliverable | Acceptance check |
|---|---|---|
| 1 | Pinned pool and provenance | IDs resolve; structure, gap and entry match; deterministic pool hash |
| 2 | Evaluator v2 and frozen objective | Self-decomposition, sign, normalization, missing-data and bin-boundary tests |
| 3 | Exhaustive cached benchmark | Every candidate has an outcome; optimum/ties and acceptance fraction known |
| 4 | Feedback controls and model settings | No hidden outcomes leak; shuffle uses past data only; temperature reaches provider |
| 5 | Repeated experiment runner and analysis | Equal budgets; exact random curve checked on a toy pool; failed runs retained |
| 6 | MLIP follow-up and isolation fixes | Counter deltas recorded; discovery outputs cannot enter decision-arm comparison |
| 7 | Reports and demo | One discovery narrative; limitations visible on slides |

Day 1: complete priorities 1–4 and an offline smoke experiment before paid LLM
runs. Day 2: repeated runs, plots and bounded MLIP follow-up. If setup takes longer,
reduce optional controls/second conditions rather than omit evaluator validation.
Existing code already supplies budgeted selection, upfront/random baselines,
checkpointing and adapters; this plan extends it rather than replacing the pipeline.

## 10. What we can claim

If supported: “On a frozen battery-coating compatibility benchmark, computational
feedback improved LLM candidate selection beyond its prior-only choices.” Report
the actual magnitude, uncertainty, model, pool and evaluation budget.

Do not claim a newly discovered material, experimentally superior coating, measured
ionic conductivity, or demonstrated savings in an expensive discovery campaign.
The reason for using an LLM remains concrete: it attempts to replace the scientist's
chemical intuition in deciding the next candidate to test, and the experiment
measures whether revising that intuition using results helps.

Sources informing evaluator design:
- Xiao et al., Joule (2019): https://ceder.berkeley.edu/publications/Joule2019_coating.pdf
- pymatgen interface-reaction documentation: https://pymatgen.org/pymatgen.analysis.html
