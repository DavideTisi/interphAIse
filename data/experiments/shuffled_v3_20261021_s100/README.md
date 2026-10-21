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
