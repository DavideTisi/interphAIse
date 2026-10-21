# Shuffled-control review and next work

21 October 2026. Reviewed `work/agent-experiments` at `6e74e88`; its live shuffled
run used source `ea0326d`. Local working branch remains `davide` at `b210db0`,
with separate, uncommitted expansion and bulk work. This is a saved handoff,
not a message sent to Adem and not a record of a production merge.

## Result verified

At budget 10, iterative succeeds in **19/30** runs and shuffled feedback in
**6/30**. The seed-matched table is 3 both, 16 iterative only, 3 shuffled only,
8 neither. Exact two-sided McNemar p = **0.004425048828125**; observed difference
is 43.3 percentage points. This is a planned follow-up after the original result,
not a blind original preregistration or a multiplicity-adjusted primary test.
Matching seeds blocks on candidate display order; it does not make the provider's
generations deterministic.

The defensible claim is: **correctly associated calculation feedback improves
this LLM's candidate selection under the frozen coating criterion**. Together
with sequential 4/30, the result supports useful feedback-driven decisions.
It does not uniquely establish chemical reasoning: contradictory earlier
rationales can hurt the shuffled arm, products can reveal identities, and some
outcomes remain correctly associated. The original post-hoc fluoride-first rule
still succeeds sooner; iterative best-bin success is 7/30 versus random 6/30.

The LLM substitutes the human step of revising a chemical hypothesis and choosing
the next candidate after a calculation. It does not replace the energy evaluator,
validate the hypothesis by writing it down, or demonstrate a new battery material.
The cheap benchmark measures selection efficiency, not saved expensive computation.

## Independent checks

- The complete `6e74e88` suite passes **104 tests**. The sparse/all-ineligible
  exact-random-median fallback and its tests are present.
- All **300 query outcomes** replay exactly. All 30 runs completed; no malformed
  retries occurred. There are **12 charged failed queries**: 10 missing pinned
  entries and 2 unknown IDs. These are retained in the denominator.
- Reconstructed all **300 displayed-source maps** from the declared shuffle seed
  and all **300 saved prompt histories** from the true outcomes. They match.
  All four workflow hashes match source `ea0326d`; every archive file hash matches.
- Recomputed the paired table directly from run histories and reproduced the
  five-arm curves. Visually inspected the combined figure and selected r111/r114
  example figure. These are explicitly selected examples, not representative proof.
- Metadata consistently records direct Haiku 5.5, temperature 1.0 and 4096 output
  tokens. Saved usage totals **1,594,978 input / 259,023 output tokens**, 300 calls.
  This review made no new paid calls.
- Per-turn displacement agrees with the archive table. The map after query 10
  is logged but is not consumed by another proposal at budget 10. About one fixed
  point is expected per displayed permutation, not one correct observation over
  the entire run.

Compact independent evidence is saved in
`data/reviews/shuffled_v3_20261021.json`. Standard reproduction after integration:

```bash
python -m pytest -q
python scripts/audit_discovery_batch.py data/experiments/shuffled_v3_20261021_s100 \
  --output runs/shuffled_replay_review.json
python scripts/analyse_discovery_experiment.py \
  data/experiments/integrated_v3_20261021_s100 \
  data/experiments/shuffled_v3_20261021_s100 \
  --plot runs/five_arm_review.png --summary runs/five_arm_review.json
```

## Decision: environment study before IDs-only

Defer the roughly 300-call IDs-only diagnostic. It would test the effect of
retaining rationales within sequential search; it would not by itself isolate
chemical reasoning. The completed control already supplies a useful feedback
sensitivity result. The next question is whether feedback helps the model adapt
when the chemical environment changes.

The expansion subagent has completed all 423 combinations: 141 pinned structures
against three electrolytes, with LiCoO2 at 4 V and the unchanged objective.
See [EXPANSION_PROGRESS.md](EXPANSION_PROGRESS.md).

| Electrolyte | Acceptable /141 | Exact random acceptance by 10 | Fluoride-first first success |
|---|---:|---:|---:|
| Li6PS5Cl | 4 | 25.74% | 3 |
| Li3InCl6 | 55 | 99.43% | 1 |
| Ordered tetragonal LLZO | 17 | 73.57% | 40 |

All sulfide acceptable structures contain fluorine; no LLZO acceptable structure
does. This changes the previously useful shortcut. It establishes an informative
test landscape, not LLM adaptation. Chloride acceptance saturates, so keep all
three declared environments and show early-query and bin-regret curves. Do not
tighten thresholds or remove environments after seeing these scores. LLZO's
unique model optimum is LiClO4; it is not a validated coating recommendation.

**Adem's next useful deliverable:** prepare the runner/query integration and a
separate pre-run protocol for these hashed environment tables, preserving the
query boundary, invalid-query charging and true/displayed feedback distinction.
Freeze arms, seeds, budgets, metrics and aggregation before production calls.
Use the same controls where comparisons are claimed; keep these runs separate
from original v3. No expanded LLM batch has been launched or frozen here.

**Davide/Codex:** reviewed expansion byte/semantic hashes, row counts, acceptance,
fluorine split and exact-random calculations independently. The subagent's 40
tests, exact 50-row original replay and six independent solver checks are recorded
in its report. Continue protocol review and keep original results immutable.

**Claude:** continue bulk-reference selection and physically consistent two-contact
validation. PET-MAD energies stay separate from the MP thermodynamic benchmark.

## Integration readiness

A temporary local clone was used to merge **committed `b210db0` + `6e74e88`**,
without committing or changing either real branch. It merges without conflicts,
preserves Claude's pilot preparation/inspection code and documentation, and the
combined tree passes **104 tests** with a clean whitespace check. No merge blocker
was found in these committed changes. This excludes active uncommitted bulk and
expansion work and is not a test of a prospective merge with a changed `main`.

Review the completed discovery release now; it need not wait for an expanded LLM
study. Before the actual merge, preserve current work in scoped commits, reconcile
the latest status reports, inspect the resulting diff against current `main`, and
confirm its tests/replay. Keep the original archive and source provenance intact.
Do not replace `davide` with Adem's branch: `b210db0` must remain included.
No actual merge, commit or push was performed by this review.
