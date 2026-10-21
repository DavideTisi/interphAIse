# Environment smoke batch: measured usage and production cost estimate

21 October 2026. From Adem. Replies to the smoke approval in `ENVIRONMENT_PROTOCOL.md`.
**Smoke only. Production has not been started and waits for your approval.**

## What was run

- **Execution commit:** `26beb73` on `work/agent-experiments` (merge of `origin/davide`
  `40b80fa`), recorded as `source_commit` in every manifest.
- **Tables:** the frozen copies in `data/benchmarks/environment_v1/`, status `frozen`, with
  hashes matching the protocol exactly. `allow_draft` was false. Every result row is identical to
  the exploratory originals; only status, freeze metadata and hash differ.
- **Runner check first (offline):** 3 random-arm runs per frozen table, no `--allow-draft`;
  hashes verified and your analysis accepts them.
- **Settings:** `claude-haiku-5-5` direct, temperature 1.0, max output 4096, prompt
  `v3-2026-10-21c-charged-ids`, seed 999, pool `environment_expansion_v1` (141).
- **Layout, per environment:** 1 upfront run at budget 10, and 1 run each of sequential,
  iterative and shuffled at budget 3.
- **Archive:** `data/experiments/environment_smoke_v1/`, with `usage.json` from
  `scripts/usage_report.py`. Excluded from all results.

## Measured usage

| Environment | Arm | Calls | Format retries | Input | Output (incl. thinking) | Thinking | USD (list estimate) |
|---|---|---|---|---|---|---|---|
| Li₆PS₅Cl | upfront | 1 | 0 | 6,869 | 1,793 | 727 | 0.0016 |
| Li₆PS₅Cl | sequential | 3 | 0 | 20,962 | 1,972 | 1,436 | 0.0031 |
| Li₆PS₅Cl | iterative | 3 | 0 | 22,000 | 2,226 | 1,413 | 0.0033 |
| Li₆PS₅Cl | shuffled | 3 | 0 | 22,023 | 2,071 | 1,252 | 0.0032 |
| Li₃InCl₆ | upfront | 1 | 0 | 6,867 | 1,784 | 650 | 0.0016 |
| Li₃InCl₆ | sequential | 3 | 0 | 21,202 | 2,597 | 1,815 | 0.0034 |
| Li₃InCl₆ | iterative | 3 | 0 | 22,004 | 2,249 | 1,462 | 0.0033 |
| Li₃InCl₆ | shuffled | 3 | 0 | 21,913 | 2,524 | 1,829 | 0.0035 |
| LLZO | upfront | 2 | 1 | 13,764 | 3,615 | 1,163 | 0.0032 |
| LLZO | sequential | 3 | 0 | 20,983 | 2,092 | 1,530 | 0.0031 |
| LLZO | iterative | 3 | 0 | 22,055 | 2,183 | 1,319 | 0.0033 |
| LLZO | shuffled | 3 | 0 | 22,026 | 2,310 | 1,484 | 0.0034 |
| **Total** | | **31** | **1** | **222,668** | **27,416** | **16,080** | **0.036** |

- 30 planned calls, plus 1 format retry: the LLZO upfront call returned 11 proposals instead of
  10. Retries are free of query budget but are billed, and they are counted above.
- No missing usage records. No charged failed queries (no invalid or repeated IDs, no missing
  entries hit).
- Cache writes and cache reads are both 0; caching is not used.
- Thinking tokens are already inside output and are not added again.
- Largest single output: 1,906 tokens, below the 4,096 cap, so nothing was truncated.
- Largest prompt: about 7,800 tokens, far below the 100k price step.

## Prices used (estimates, not billed)

Anthropic public list prices for Haiku 5.5, prompts ≤ 100k tokens, global routing, no batch
discount: USD 0.10 per million input, 0.50 per million output (thinking included), 0.01 per
million cache read, 0.125/0.20 per million for 5-minute/1-hour cache writes. Source:
https://platform.claude.com/docs/en/about-claude/pricing, checked 21 October 2026, matching your
cross-check. **Billed cost and any contract pricing are unverified. The account owner must
confirm them in the Anthropic Console.** Every USD figure here is usage × list price.

## Production projection (2,790 calls before retries)

The smoke batch measures the base prompt for the 141-candidate pool. Budget 3 doesn't show
10-turn histories, so the growth per turn comes from the archived 10-turn v3 runs. The smoke
batch's first turns match that growth: iterative +440 and +532 tokens, against v3's +426 and
+535.

| Arm (per run) | Calls | Mean prompt per call | Output per call |
|---|---|---|---|
| iterative | 10 | 9,260 (v3 5,250 + 4,007 for the larger pool) | 852 (v3) |
| shuffled | 10 | 9,320 (v3 5,317 + 4,007) | 863 (v3) |
| sequential | 10 | 7,700 (v3 3,692 + 4,007) | 881 (v3) |
| upfront | 1 | 6,870 (measured) | 1,852 (v3) |

The 4,007 is the measured difference between smoke and v3 call-1 prompts (6,869 against 2,862).
Output per call uses v3's values, which are higher than the smoke batch's (~750).

| Scenario | Input tokens | Output tokens | USD (list estimate) |
|---|---|---|---|
| **Expected** | 24.3M | 2.50M | **≈ 3.70** |
| **Conservative:** input +20% (longer rationales in the history), +10% calls for retries, output +50% | 32.0M | 4.13M | **≈ 5.30** |
| **Hard ceiling:** conservative input, and every call (+10% retries) hitting the 4,096-token output cap | 32.0M | 12.6M | **≈ 9.50** |

Other numbers:
- **Retry rates:** 1 in 931 calls (0.1%) in the v3 production batches, 1 in 31 in this smoke.
  The 10% allowance covers both comfortably.
- **Wall time:** about 2 hours with `--workers 3`.
- **No cheaper design is needed.** The conservative total is about USD 5. Prompt caching or the
  Batch API would save at most a few dollars, would change the request path, and would need the
  protocol re-frozen. I don't recommend them.

## Requests

1. **Approve production** as frozen: 3 environments × 5 arms × 30 runs, seeds 200–229, budget 10,
   execution commit `26beb73` (or a later commit if anything changes; it would be recorded).
   About 2,790 calls before retries.
2. **Account owner:** confirm billed cost and contract pricing (for example, the cost of this
   smoke batch in the Console against the USD 0.036 estimate).
3. **Sign-off:** I'll tick my box in `ENVIRONMENT_PROTOCOL.md` (runner verified on the frozen
   copies, execution commit recorded) in the same commit as this report.

## Ready once approved: production and analysis commands

The workflow code (`run_discovery_experiment.py`, `discovery.py`, `llm.py`, `benchmark.py`) is
byte-identical to the smoke execution commit `26beb73`. Later commits only add analysis and
docs. Each manifest records the actual `source_commit` and these file hashes.

```bash
for env in lpscl lic llzo; do
  python scripts/run_discovery_experiment.py \
    --arms random upfront sequential iterative shuffled --repeats 30 --start-seed 200 \
    --budget 10 --temperature 1.0 --max-tokens 4096 --workers 3 \
    --pool data/exploration/environment_expansion_v1/pool.json \
    --benchmark data/benchmarks/environment_v1/lco_${env}_4v.json \
    --out runs/environment_v1/${env}
done
```

Analysis (written and tested before any production results; definitions in its docstring):

```bash
python scripts/analyse_environment_study.py runs/environment_v1/*/*_experiment --json environment_summary.json
for d in runs/environment_v1/*/*_experiment; do                    # per-environment curves
  python scripts/analyse_discovery_experiment.py "$d" --plot "$d/curves.png" --summary "$d/summary.json"
done
python scripts/usage_report.py runs/environment_v1/*/*_experiment --json environment_usage.json
```

`analyse_environment_study.py` gives the primary endpoint per environment, the exact paired
McNemar contrasts (iterative against sequential, iterative against shuffled), Holm across all six,
first-acceptable query index (none counts as 11), best-bin rate, fluoride fraction in queries
1–5 against 6–10, and the equal-weight mean difference across environments. The fluoride
fraction is how "moves away from fluorides in LLZO" is measured; it is fixed now, before results.
