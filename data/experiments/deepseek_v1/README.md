# DeepSeek V3.2 repeat of the three-environment study, production

22 October 2026, executed by Adem and approved by Davide. Protocol and pre-registration: [DEEPSEEK_PROTOCOL.md](../../../DEEPSEEK_PROTOCOL.md).

**Label:** a comparison of **model configurations**, not matched reasoning compute.

## Configuration and execution

- **Model and settings:** `deepseek/deepseek-v3.2` via OpenRouter, pinned to `siliconflow/fp8` with fallbacks disabled; reasoning cap 3,072, total output cap 4,096, temperature 1.0.
- **Frozen inputs:** prompt `v3-2026-10-21c-charged-ids`, the frozen tables in `data/benchmarks/environment_v1/`, and the pool `data/exploration/environment_expansion_v1/pool.json`.
- **Execution:** commit `70e1901`, 14:20–17:21 UTC.
- **Runs:** 360 (4 LLM arms × 30 seeds, 200–229, × 3 environments), all complete, none failed.
- **Random baseline:** reused from the Haiku archive (`../environment_v1/`).

## Usage and spending

- **Calls:** 2,793, including 3 charged format retries. 2 failed attempts have no usage record.
- **Tokens:** 16.07M input (5.03M served from the provider's cache), 6.78M output, of which 6.43M reasoning.
- **Cost:** USD 8.99 recorded per call by OpenRouter. The key's total spend was USD 9.19; it also includes about USD 0.2 from a duplicate launch that was stopped after about 2 minutes and excluded from this archive.
- **Limits:** the spending limit was USD 12. `monitor.jsonl` records every check: 0 cap or provider violations, and every call served by SiliconFlow.

## Validation

`environment_summary.json` comes from `analyse_environment_study.py --production --policy deepseek_v1`, and its production check passed. That covers the manifest and per-call settings, the workflow hashes, and a replay of every charged query against `BenchmarkQueries`.

## Results

Acceptable coating found within 10 queries, n = 30 per arm. Paired exact McNemar tests, Holm-corrected within DeepSeek's own family of 6.

| Environment | Iterative | Sequential | Shuffled | Upfront | Random (Haiku archive) | Iter vs seq (Holm p) | Iter vs shuffled (Holm p) |
|---|---|---|---|---|---|---|---|
| Li₆PS₅Cl | 12 | 2 | 3 | 2 | 8 | +0.33 (0.078) | +0.30 (0.11) |
| Li₃InCl₆ | 30 | 30 | 30 | 30 | 29 | 0 (1, ceiling) | 0 (1) |
| LLZO | 10 | 4 | 12 | 20 | 24 | +0.20 (0.44) | −0.07 (1) |

## Files

- [model_comparison.md](model_comparison.md): cross-model tables (Haiku against DeepSeek, descriptive).
- [llzo_audit.md](llzo_audit.md): Davide's exploratory LLZO audit.
- [deepseek_success_vs_budget.png](deepseek_success_vs_budget.png): success-curve figure.
- `usage.json`: usage data.
- Per-environment `summary.json` and `curves.png`.
- The smoke batches in `smoke/` are excluded from these results.
