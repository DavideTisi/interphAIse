# Reply to Adem — evaluator and experiment sync

21 October 2026. Prepared for Davide to share; not sent automatically.
Responds to Adem's `SYNC_DAVIDE.md`. His branch and live-run results are reported
in that note; they have not yet been independently inspected in this session.

Your two evaluator concerns match our exhaustive checks. The absolute-decomposition
objective gave 41 tied best candidates because electrolyte oxidation dominated.
Davide has now selected the additional-contact-reaction alternative, frozen as
**v3.0** before the main strategy experiments. The benchmark is ready locally in
commit `946c1ed` on `davide`; that commit has not been pushed by this agent.

## 1. Potential convention

Both contacts use Li open at 4 V versus Li/Li+, with the same elemental-Li reference.
This is an imposed-potential thermodynamic proxy, not a resolved potential profile
across a real insulating coating.

V3 separates **additional reaction on mixing** from endpoint oxidation: it measures
the contact reaction relative to separately equilibrated endpoint assemblages at
that potential. It separately penalizes the coating's own decomposition. The
absolute contact energies and electrode/electrolyte self-decomposition are retained
as diagnostics. Passing v3 does not imply a stable whole stack or a pristine interface.

A zero mixing energy with decomposition products listed does not by itself quantify
coating self-instability. The explicit self-decomposition penalty supplies that check.

## 2. Objective and units

All benchmark energy penalties are **eV per non-Li atom**. They must not be directly
compared with the old CLI's eV/atom output without checking that normalization.

For each contact, with h denoting the grand-potential hull energy, minimize:

`h((1-x)c1 + x*c2) - [(1-x)h(c1) + x*h(c2)]`.

The final positive penalty is:

`max(coating_self_decomposition, -contact_1_minimum, -contact_2_minimum, 0)`.

Smaller is better. Eligible candidates rank by ascending fixed 0.020 eV/non-Li-atom
penalty bins; candidates within a bin tie. Use `ranking_key(result)` from
`interphaise.discovery_evaluator`, where larger tuples are better. Do not use the
legacy raw-energy comparator or break ties by evaluation order.

## 3. Acceptance

- Known band gap >= 2.0 eV.
- Final penalty <= 0.050 eV/non-Li atom. Because it is a maximum, all three component
  penalties must meet this limit.
- Failed or unknown outcomes never pass. They still consume query budget.

Use the returned `acceptable` boolean. Do not run the old analyser's `--accept -0.05`
unchanged: the new score is positive, includes self-decomposition and has an insulation gate.
The frozen pool contains 50 IDs, 49 calculated outcomes, one missing corrected entry,
and two calculated candidates that fail insulation. There are two acceptable candidates.

## 4. Candidate identity and what the LLM sees

Use `candidate_id` plus formula and family. The candidate ID is already the pinned
MP ID; a duplicate MP-ID column is optional. Formulas are not unique: polymorphs are
separate candidates. Alphabetical and numeric MP IDs can be aliases, and the evaluator
handles their correspondence through the official emmet type.

`BenchmarkQueries.available()` supplies only candidate ID, formula and family.
Do not give the proposer hull energy, gap, full-pool results or diagnostic reports.
Task conditions and the fixed objective are public. Only queried outcomes should
be added to feedback histories; your no-feedback arm must suppress those outcomes.

## 5. Output schema and integration ownership

Please adapt the agent-side mapping on your branch. Keep the complete v3 result
in `details` if retaining the old `Evaluation` container, but migrate acceptance,
ranking and prompts explicitly. Do not put a bin index into a field labelled physical
reaction energy, and do not assume `worst_reaction_energy` captures the self/gap gates.

Recommended interface:

```python
from interphaise.benchmark import BenchmarkQueries
from interphaise.discovery_evaluator import ranking_key

q = BenchmarkQueries(
    'data/pools/mp_candidates_v2.json',
    'data/benchmarks/coating_v3.json',
    budget=10,
)
# Prompt uses q.task(), q.available(), and observed q.history() only.
r = q.query(chosen_candidate_id)
accepted = r.get('acceptable', False)
rank = ranking_key(r)
```

Successful results include `candidate_id`, `status`, `insulating`, `band_gap_eV`,
`self_decomposition_penalty`, `contact_reaction_energies`, `contacts` with products,
`penalty`, `penalty_bin`, `acceptable`, objective version, units and provenance.
Failed results contain status/error information and must be handled before accessing
numerical fields. Returned results are copies. Failed, repeated and invalid-ID queries
consume attempts; one instance represents one independent run.

The existing `scripts/run_discovery.py` on Davide's branch remains legacy code.
Use [EVALUATOR_HANDOFF.md](EVALUATOR_HANDOFF.md) as the current integration contract.

## 6. Frozen answer table and exact random curves

The complete answer table is `data/benchmarks/coating_v3.json`, under `results`.
The pool is `data/pools/mp_candidates_v2.json`. The benchmark pins that exact pool
snapshot; the pool's historical draft-status label has been retained without modifying
its hash. The compressed thermodynamic source is tracked for offline replay.

Distinguish these analysis targets:

| Target | Number of successes M in N=50 | Random success by k=10 |
|---|---:|---:|
| Find a criterion-acceptable candidate | 2 | 36.3265% |
| Find the best eligible score bin | 1 | 20% |

Both use `1 - C(N-M,k)/C(N,k)`, without replacement. The benchmark's stored
`random_best_bin_success` curve is the second target, **not** the acceptance curve.
For your P(acceptable found) plot, derive M from the stored `acceptable` flags.
Keep the missing-data candidate and gate failures in N. Do not filter them away
before sampling or computing the baseline. Preserve ties in best-of-k analysis.

Benchmark hash:
`d2718c20f0ca8c3cc25d2378011bc68736ad71a502d657312bfff1da15a4ecfa`.
Record pool, objective and benchmark hashes in every run.

## 7. Budget, repeats and readiness

50 candidates, budget 10, and 10 repeats per LLM arm is a reasonable main-run plan
subject to recording the actual token/cost budget. Upfront uses 10 calls if each call
returns a whole shortlist; sequential-no-results and iterative each use 100 calls.
That is **210 proposal calls before retries**, plus 100 if shuffled feedback is added.
A low call count alone is not a cost estimate: history length and output limits matter.

Freeze prompt versions, temperature, model ID and seeds before the repeats. Use only
configured direct Anthropic Haiku 5.5. First run an integration test with the real
frozen query interface, then a tiny live run, before launching all repeats.

The local evaluator has 82 passing tests, an offline three-query smoke run, full
compressed-data replay, and eight real LP/Qhull checks agreeing to numerical precision.
Your reported legacy two-query run is useful evidence of plumbing and a feedback
trace, but not a v3 benchmark result or proof that feedback improves selection.

## Next coordination

1. Publish/share Davide's branch so Adem can access commit `946c1ed` and its artifacts.
2. Integrate the v3 query, acceptance, ranking and prompt changes on the agent branch.
3. Test the combined no-feedback information boundary and failed-query accounting.
4. Run the tiny live integration check, then the repeated controls.

Davide can continue the PET-MAD protocol in parallel. No merge, push, message to Adem
or new live model run was performed merely by reviewing this note.
