# Evaluator handoff — frozen v3.0, 21 October 2026

**Ready for Adem:** a frozen 50-candidate benchmark and a budgeted query API.
Read [BENCHMARK_VALIDATION.md](BENCHMARK_VALIDATION.md) for the scientific definition,
validation evidence, provenance and limitations. That report contains all outcomes;
keep it out of proposer prompts. Historical implementation steps are preserved in
[DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md).

## What the LLM replaces

The LLM performs the scientist's candidate selection and hypothesis revision:
choose a coating for chemical reasons, interpret the returned calculations, and
choose what to test next. It cannot alter the objective or declare its own candidate
successful. As in HELLMM's mechanism proposals, this targets scientific judgement;
the fixed pool tests selection rather than unrestricted material invention.

Only comparisons against prior-only/no-feedback and random controls can establish
whether feedback helps. Explanations alone cannot establish that claim. The cheap
benchmark measures sample efficiency, not saved compute time.

## Use this interface

```python
from interphaise.benchmark import BenchmarkQueries
from interphaise.discovery_evaluator import ranking_key

queries = BenchmarkQueries(
    "data/pools/mp_candidates_v2.json",
    "data/benchmarks/coating_v3.json",
    budget=10,
)

# Safe prompt inputs: task, available candidates, and observed history only.
task = queries.task()
available = queries.available()  # candidate_id, formula, family; no gaps/hull scores
observed = queries.history()      # initially empty

# Replace this deterministic example with the agent's chosen candidate ID.
result = queries.query(available[0]["candidate_id"])
score = ranking_key(result)       # larger tuple is better; ties are preserved
```

IDs are authoritative; formulas are not unique because polymorphs are retained.
The API returns copies so a caller cannot mutate cached outcomes. Invalid IDs,
repeated IDs and cached calculation failures consume one attempt. Exhausted budgets
raise. `available()` excludes already queried valid candidates. Starting a new
`BenchmarkQueries` instance resets the experiment; create one per independent run.

The class verifies pool, benchmark and objective hashes and refuses unfrozen drafts
unless explicitly allowed for development. It is an application-level information
boundary, not a security sandbox. The runner must not read the exhaustive artifact
into the model's prompt or expose diagnostics in other metadata.

The frozen benchmark's scope is **additional contact reactivity plus coating
self-stability and insulation** at 4 V. It does not establish whole-stack stability,
Li transport, kinetics or synthesis. All penalties are positive and smaller is better,
in eV per non-Li atom. Rank eligibility first, then fixed 20 meV/non-Li-atom bins.
A larger band gap does not improve the ranking once the 2 eV gate is passed.

## Integration boundaries

- `interphaise/discovery.py` and `scripts/run_discovery.py` remain the legacy agent
  path. Their formula-only selection, old objective prompt and old `quality()`
  function must not be used unchanged for v3 experiments.
- Connect Adem's runner to `BenchmarkQueries`; send candidate IDs with formula/family
  context. Use the returned objective and `ranking_key`, not the legacy comparator.
- For upfront/no-feedback arms, build prompts without `history()` outcomes. For a
  shuffled-feedback control, log displayed feedback separately from true outcomes.
- Keep failed runs/candidates in budget accounting. Use exact random curves from
  the offline diagnostic artifact only for analysis, never as model feedback.
- Capture model ID, temperature, seed/budget, prompt version, query trace and the
  pool/objective/benchmark hashes. Live calls remain direct Anthropic Haiku 5.5 only.

A standalone offline smoke runner is available:

```sh
.venv/bin/python scripts/query_benchmark.py --budget 3 --seed 0 \
  --output runs/query_new.json
```

It uses random selections and is a plumbing check, not an empirical random baseline.
The latter is computed exactly with tied best candidates and sampling without replacement.

## Recomputing the physics

Install the project with its MP extra (`pip install -e '.[mp,dev]'`). The tracked
`data/thermo/mp_gga_v2.json.gz` contains the pinned corrected entries, so replay
requires no credential or network access. Use `scripts/evaluate_pool.py
--contact-reference equilibrated` as shown in the validation report.

When calling the low-level evaluator directly, pass the frozen definition explicitly:

```python
from interphaise.discovery_evaluator import Objective
objective = Objective(version="v3.0", contact_reference="equilibrated")
```

The low-level default retains historical v2 for compatibility; do not rely on that
default for v3. Only `BenchmarkQueries` is the recommended search-facing interface.
Never mix PET-MAD energies with the corrected MP thermodynamic entries.

## Current evidence and next ownership

82 tests pass. All 50 candidates have a recorded outcome: 49 calculated, one missing
corrected entry, and two calculated candidates failing insulation. The frozen
criterion has 24 occupied eligible bins and two passing candidates. Eight real-data
LP/Qhull comparisons agree to numerical precision. Full compressed-data replay
matches the stored numerical results exactly.

Adem owns integration, repeated LLM/control runs and plots. Davide owns the PET-MAD
follow-up protocol and compute accounting. Its candidate selection is recorded in
`data/benchmarks/mlip_followup_plan.json`; it has not been run. No new live LLM call
or MLIP calculation occurred during this evaluator-validation session.
