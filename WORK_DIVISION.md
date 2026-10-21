# interphAIse — work division for Davide and Adem

OSI Hackathon, 21–22 October 2026. All scheduling below uses Copenhagen time.

## Shared objective

Test whether computed feedback improves an LLM's selection of compatible battery
coatings beyond its initial chemical knowledge. The LLM replaces the scientist's
intuition in proposing candidates, interpreting failures and choosing what to test
next. Deterministic tools calculate properties and apply a fixed objective.

Use the frozen-pool benchmark for controlled evaluation; a small composition
proposal-and-revision demonstration can show the broader design idea. Keep those
claims separate. MLIP follow-up evaluates selected structures, not the accuracy
of the whole search benchmark.

## Ownership

| Owner | Owns | Deliverable |
|---|---|---|
| **Davide** | Materials data, physical criteria, computational evaluator, PET-MAD follow-up | A validated evaluator that accepts a candidate and returns numerical outcomes with provenance |
| **Adem** | Haiku hypotheses, feedback loop, search controls, repeated experiments and plots | An agent that chooses the next candidate and an experiment measuring the value of feedback |
| **Together** | Objective and result schema, scientific interpretation, integration and presentation | One end-to-end demonstration and a defensible conclusion |

Detailed scientific design: [DISCOVERY_IMPLEMENTATION_PLAN.md](DISCOVERY_IMPLEMENTATION_PLAN.md).

## First joint session — approximately 30 minutes

Before working independently, agree on:

1. Cathode, electrolyte and operating conditions for the main experiment.
2. Candidate identity: use pinned material IDs, not ambiguous formula-only lookups.
3. Evaluator result schema, energy signs, atom normalization and missing-data rules.
4. Acceptability criteria, ranking/tie convention and query budget.
5. Which files each person owns and the shared integration checkpoint.

Freeze the objective before strategy results are inspected. If the exhaustive pool
has no meaningful variation, document a redesigned task before starting LLM runs.

## Davide — materials and evaluator

### Wednesday 21 October

- Fix coating self-stability at the chosen lithium chemical potential.
- Fetch band gaps and structures for the same pinned MP material IDs.
- Implement validity gates, explicit units/normalization and fixed energy bins.
- Build and freeze approximately 50 chemically diverse, ordered candidates with
  recorded filtering criteria and a pool hash.
- Evaluate the inexpensive objective over the pool once; inspect failures,
  acceptable-candidate fraction and tied groups.
- Prepare a representative structure for the first PET-MAD interface calculation.

**Handoff to Adem:** versioned candidate metadata, the frozen objective and an
access-controlled evaluator/query function. The benchmark runner may load the
complete results, but must not reveal unqueried outcomes to the LLM.

### Thursday 22 October

- Sanity-check leading candidates and failure cases.
- Run the same PET-MAD protocol on a small shortlist, including a baseline-selected
  comparator; record relaxation/single-point counts and wall time.
- Inspect resulting structures and clearly distinguish incomplete relaxation from
  valid converged results.
- Prepare structure images and the explanation of what the evaluator measures.

**Main files:** `interphaise/tools/`, proposed
`interphaise/discovery_evaluator.py`, `scripts/build_candidate_pool.py`,
`data/pools/`, objective configuration and evaluator tests.

## Adem — agent and experiments

### Wednesday 21 October

- Implement chemical proposals with a concise hypothesis and explicit reference
  to the observation motivating a revision.
- Develop against a synthetic evaluator while the real evaluator is being built.
- Implement upfront LLM, sequential LLM without results and iterative LLM with
  true feedback; retain uniform random selection as the baseline.
- Ensure histories do not leak unqueried outcomes or result metadata into the
  no-feedback arm. Log failures and charge the agreed evaluation budget.
- Add repeated-run orchestration, model/sampling metadata and plotting support.
- If implementing free formula proposals, resolve them to known structures;
  report unresolved proposals explicitly and evaluate this demo separately.

**Handoff to Davide:** the runner, synthetic end-to-end demonstration and exact
input/output expectations. Do not modify evaluator criteria to improve agent scores.

### Thursday 22 October

- Run repeated experiments on the frozen benchmark (target: at least 10 runs per
  LLM arm, subject to the agreed token budget).
- Calculate the exact random success curve, respecting ties and sampling without
  replacement.
- Plot success probability and best objective versus evaluations, with uncertainty
  across repeats and failed runs retained.
- Select one trace showing a hypothesis, contradictory feedback and the resulting
  next proposal. A compelling explanation alone is not evidence of better search.

**Main files:** `interphaise/discovery.py`, proposer prompts,
`scripts/run_discovery.py`, proposed `scripts/run_discovery_experiment.py` and
`scripts/analyse_discovery_experiment.py`, search/control tests.

## Shared evaluator contract

Illustrative request (values and field names to freeze together):

```json
{
  "candidate_id": "candidate-017",
  "hypothesis": "The chemical reason for testing this coating"
}
```

Illustrative response — numbers below are synthetic, not material predictions:

```json
{
  "candidate_id": "candidate-017",
  "status": "ok",
  "contact_reaction_energies": [-0.03, -0.12],
  "self_decomposition_penalty": 0.08,
  "band_gap_eV": 3.2,
  "reaction_products": [],
  "warnings": [],
  "objective_version": "v2"
}
```

The final schema must declare the energy units and normalization basis explicitly.
Missing values must be null/unknown, not zero. The evaluator supplies the score
and diagnostic components. The LLM cannot change the objective or self-certify a
candidate. Preserve separate records for real outcomes and displayed feedback.

## Integration milestones

| When | Joint acceptance criterion |
|---|---|
| Wednesday, after the initial setup | Both sides agree on the schema and run against the same synthetic fixture |
| Wednesday afternoon | One real coating is evaluated; Haiku receives the outcome and selects the next candidate |
| Thursday, before large runs | Pool/objective frozen; information-barrier and budget tests pass |
| Thursday, before the presentation | Repeated comparison plot, one intelligible agent trace, and inspected MLIP follow-up where available |

Keep a short joint check-in after the first real evaluation. If the integration
fails, fix it before adding more candidates or more agent features.

## Git and collaboration

Integration base: `main` (updated 21 October after the discovery work was merged).

Create personal work branches from the same latest integration commit:

- Davide: `davide` (created from `main`, active evaluator development)
- Adem: `work/agent-experiments`

Adem’s branch name is a suggestion; Davide’s branch already exists.
Keep changes within the owned files where practical. Agree before changing shared
configuration or the evaluator contract. Use small commits and merge at the
milestones; avoid simultaneous edits of the same file. Do not merge to `main`
until the integrated tests pass and both people have reviewed the scientific scope.

## Fixed runtime and credential rules

- Live LLM: **Claude Haiku 5.5 only**, exact ID `claude-haiku-5-5`, through direct
  Anthropic access. No other model/provider or fallback is authorised.
- MLIP: **PET-MAD S 1.6.0, r²SCAN**, selected as `upet:pet-mad-s@1.6.0`.
- Each person configures credentials locally in ignored `.env`. Never commit or
  send keys through reports, GitHub issues or logs. `.env.example` stays empty.
- Use credentials only for this workflow and minimal connection tests.
- API connectivity and a small PET-MAD CPU smoke test have passed. These are
  software checks, not scientific validation of the battery-interface evaluator.

## Scope and pitch

Minimum successful submission:

1. A verified, frozen computational evaluator.
2. One complete proposal–calculation–revision loop.
3. A controlled comparison against prior-only/no-feedback and random selection.

Stretch work: shuffled feedback, a second operating condition, more MLIP interfaces,
and broader composition proposals. Keep the original modelling-decision arms as
supporting material only if the main experiment is complete.

The main claim, if supported, is that calculated feedback improves candidate
selection beyond the model's prior chemical knowledge. The cheap benchmark measures
sample efficiency, not real compute savings. The shortlist does not establish Li-ion
transport, synthesis feasibility or experimental battery performance; state these
limits on the slides. A negative feedback result is still worth reporting honestly.
