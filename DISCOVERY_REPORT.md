# interphAIse: iterative coating discovery

**Updated experimental plan:** [DISCOVERY_IMPLEMENTATION_PLAN.md](DISCOVERY_IMPLEMENTATION_PLAN.md) supersedes the design below where they differ. It specifies design A, the LLM’s role in replacing human candidate-selection intuition, evaluator fixes, controls and implementation milestones.

Agreement and implementation brief — 20 October 2026.

## Scientific objective

Given a cathode, electrolyte, operating voltage and a calculation budget, use an
LLM to propose coatings, interpret computed outcomes and revise its next choice.
The LLM substitutes part of a scientist's hypothesis generation and experimental
design. Calling tools alone is not the scientific contribution.

HELLMM is already published and is not the submission. This is a distinct
battery-interface project; existing utilities are infrastructure only.

## Two-day scope

Start with a bounded, predefined pool of coatings with retrievable structures.
The model knows the formulas, but not unevaluated outcomes. This tests adaptive
selection, not discovery of previously unknown compounds. Universal MLIPs and
phase-diagram tools are acceptable approximate evaluators. Success means better
search within that evaluator, not demonstrated experimental battery performance.

Compare iterative LLM selection, one upfront LLM shortlist, seeded random search,
and a declared fixed order. The fixed order is only an expert baseline if an expert
actually supplies it before seeing outcomes. Use the same pool, objective,
evaluator settings and evaluation budget. Repeat seeds/model runs before making
an acceleration claim. The six existing coatings are a smoke-test pool; a larger
pool is necessary for a convincing search experiment.

## Fixed objective and information barrier

All valid candidates outrank failed candidates. Among valid candidates, minimise
reaction driving force at the worse of the two original contacts, then maximise
adhesion at the weakest modelled contact. No policy-generated stability tier,
LLM confidence or agreement enters the discovery score. The first implementation
uses exact lexicographic ordering; adhesion only breaks equal reaction energies.
A tolerance/binning rule for comparable reactivities must be fixed before any
future experiment, not tuned to favour an arm.

Thermodynamic mode measures reaction energies only and checks bulk retrieval.
Full mode uses the same fixed RulesPolicy for every candidate to construct and
validate interfaces and obtain MLIP adhesion. This evaluator remains an
approximation with modelling assumptions; its rule verdicts are not experimental
truth. Missing or failed required computations invalidate the candidate. Failures
consume budget and remain in the record. Database and MLIP energy scales are not
mixed in a single energy difference.

The proposer receives only the task, remaining formulas and previously evaluated
outcomes. It must give a chemical hypothesis and explain how feedback informed
its choice. Explanations are logged, but performance measures reasoning's utility.
Repeated or out-of-pool proposals are rejected with bounded retries; no silent
random fallback. Invalid proposal attempts are logged separately from calculation
budget. All strategies are charged one evaluation per selected candidate, including
failed calculations. Candidate counts are not equal GPU time: real costs and
relaxation counts need recording before claiming compute savings.

## First implementation

- `interphaise/discovery.py`: strategy loop, fixed objective, history, best-so-far
  trace, bounded proposal validation, live evaluator and injectable test evaluator.
- `scripts/run_discovery.py`: CLI for random, fixed, upfront and iterative strategies;
  thermodynamic mode or full fixed-policy MLIP evaluation.
- `tests/test_discovery.py`: offline checks for feedback isolation, budgets,
  invalid proposals, failed calculations and ranking.

Each run has a unique output directory. `discovery.json` is checkpointed after
proposals/evaluations and includes configuration, strategy, seed, objective,
evaluator metadata, timing, errors and trace. The pre-existing screen is retained
for comparing interface decisions; it answers a different evaluation question.

## Remaining work

Run a small real Materials Project case; sanity-check full MLIP calculations on
reference structures; curate a larger candidate pool; run matched-budget arms and
repeat trials; plot best objective versus evaluations. Validate top structures and
look for evaluator exploitation. Lithium transport, synthesis and experimental
performance remain outside the initial objective. Free composition generation,
new structure prediction, full multilayer cells and MD are stretch goals.

## Validation of this first implementation

31 offline tests passed (21 existing, 10 new), using an isolated ARM Python test
environment; CLI `--help` and `git diff --check` also passed. New tests cover
feedback isolation, upfront selection, failed-calculation budget accounting,
bounded malformed/repeated proposal handling, objective ordering, reproducible
random selection, the thermodynamic adapter on toy chemistry and rejection of
incomplete full evaluations. No real MP, LLM or MLIP runs were performed in this
implementation session. These checks establish software behaviour, not scientific
accuracy or a search advantage.
