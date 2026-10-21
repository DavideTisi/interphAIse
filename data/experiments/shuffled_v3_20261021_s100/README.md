# Shuffled-feedback control, frozen v3, seeds 100–129

Prospective follow-up to `../integrated_v3_20261021_s100`, approved by Davide on 21 October
2026, after the four-arm batch. Settings match that batch: Haiku 5.5 (`claude-haiku-5-5`, direct
Anthropic), temperature 1.0, 4096 output tokens, prompt `v3-2026-10-21c-charged-ids`, budget 10,
3 workers, same pool, objective and benchmark hashes. Source commit `ea0326d`.

**Arm.** Proposes like iterative. Outcomes of real first queries are permuted among
already-queried candidates (inside-out Fisher–Yates, seed `shuffle-<seed>`) and relabelled with
the candidate they are shown next to. Charged invalid or repeated IDs stay in place. True
outcomes are kept for scoring; `displayed_sources` logs the true source of each displayed slot
after every turn.

**Result** (primary: acceptable found by query 10):

| Arm | Acceptable | Bin ≤ 2 (sensitivity check chosen after seeing results) | Median best bin at 10 |
|---|---|---|---|
| Iterative (integrated batch) | 19/30 | 22/30 | 2 |
| Shuffled (this batch) | 6/30 | 10/30 | 9 |

Paired by seed against iterative: iterative-only 16, shuffled-only 3, both 3; exact two-sided
McNemar p = 0.004. 300 proposal calls with no malformed retries and 2 charged invalid IDs; all
300 query results replay exactly (`replay_audit.json`).

**Chronology.** The primary endpoint (acceptable found by query 10) and the four original arms
were set before any results. Iterative against sequential was observed first. This
iterative-against-shuffled comparison is a planned follow-up decided after that result. It was
not part of a blind original preregistration. The 30 runs were declared before launch and all
are reported.

**How much was actually shuffled** (from `displayed_sources`; turn t = the history shown after t
queries, i.e. to proposal t + 1; real slots exclude charged invalid/repeated IDs):

| After query | Real slots shown | Displaced (mean) | Runs with ≥ 1 displaced | Earlier slots changed vs previous turn (mean) |
|---|---|---|---|---|
| 1 | 1.00 | 0.00 | 0/30 | 0.00 |
| 2 | 2.00 | 0.93 | 14/30 | 0.47 |
| 3 | 3.00 | 1.83 | 25/30 | 0.53 |
| 4 | 3.97 | 2.83 | 30/30 | 0.70 |
| 5 | 4.97 | 3.93 | 30/30 | 0.83 |
| 6 | 5.93 | 5.00 | 30/30 | 0.90 |
| 7 | 6.93 | 6.07 | 30/30 | 0.87 |
| 8 | 7.93 | 7.03 | 30/30 | 0.87 |
| 9 | 8.93 | 8.10 | 30/30 | 0.90 |
| 10 | 9.93 | 9.23 | 30/30 | 0.93 |

On average about one real slot keeps its own outcome (a uniform permutation has one expected
fixed point), so some correct information remains. The control does not blind all chemical
information.

**Reading.** The benefit of feedback depends on outcomes being attached to the right candidates,
not just on seeing plausible numbers. Limits: a moved outcome can contradict an earlier rationale,
and reaction products can hint at their true source. This is sensitivity to corrupted feedback,
not clean proof of chemical reasoning.

Reproduce:

```bash
python scripts/analyse_discovery_experiment.py data/experiments/integrated_v3_20261021_s100 \
  data/experiments/shuffled_v3_20261021_s100 --plot curves_with_integrated.png
python scripts/audit_discovery_batch.py data/experiments/shuffled_v3_20261021_s100 --output replay_audit.json
```
