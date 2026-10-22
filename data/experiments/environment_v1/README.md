# Environment study, production (frozen protocol), seeds 200–229

21 October 2026, executed by Adem as approved by Davide (`ENVIRONMENT_PROTOCOL.md`, `e5c745e`).
Execution commit `710d346` (workflow identical to smoke `26beb73`); Haiku 5.5 direct, temperature 1.0,
max output 4096, prompt `v3-2026-10-21c-charged-ids`, frozen tables in `data/benchmarks/environment_v1/`.
450 runs (5 arms × 30 × 3 environments), all complete; 2,800 calls (10 format retries);
24.30M input / 2.40M output tokens; ≈ USD 3.63 at public list prices (estimate, not billed).
All 4,500 queries replay exactly (`*/replay_audit.json`). Analysis code fixed at `0072f3d` before the runs.

Acceptable found within 10 queries (n = 30 per arm); paired exact McNemar, Holm across six:

| Environment | Iterative | Sequential | Shuffled | Upfront | Random (exact) | Iter vs seq (Holm p) | Iter vs shuffled (Holm p) |
|---|---|---|---|---|---|---|---|
| Li₆PS₅Cl | 20 | 2 | 6 | 0 | 8 (25.7%) | +0.60 (4.6e-5) | +0.47 (0.0024) |
| Li₃InCl₆ | 30 | 30 | 30 | 30 | 29 (99.4%) | 0 (1, ceiling) | 0 (1) |
| LLZO | 12 | 0 | 4 | 1 | 24 (73.6%) | +0.40 (0.0024) | +0.27 (0.17, n.s.) |

In LLZO random search beats every LLM arm. Details: `environment_summary.json` (final analysis,
production check passed), `usage.json`, per-environment `summary.json` and `curves.png`.
The smoke batch (`../environment_smoke_v1/`) is excluded.
