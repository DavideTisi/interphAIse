# Environment production complete

21 October 2026. From Adem. Branch `work/agent-experiments`.

All 450 runs of the frozen study completed at execution commit `710d346` (workflow identical to smoke
`26beb73`), with usage checked after each environment, and no pause triggered. 2,800 calls (10 format
retries), 24.30M input / 2.40M output tokens, ≈ USD 3.63 at list price (estimate; projection 3.68).
All 4,500 queries replay exactly. Final analysis with `--production`: complete frozen study, Holm family 6.

Acceptable within 10 queries (n = 30/arm), iterative / sequential / shuffled / upfront / random (exact): Li6PS5Cl 20/2/6/0/8 (25.7%); Li3InCl6 30/30/30/30/29 (ceiling, declared in advance); LLZO 12/0/4/1/24 (73.6%). Paired exact McNemar, Holm over six: iterative > sequential in Li6PS5Cl (Holm p 4.6e-5) and LLZO (0.0024); iterative > shuffled in Li6PS5Cl (0.0024), not in LLZO (0.17). In LLZO random search beats every LLM arm.

Reading: correctly attributed feedback replicates the v3 effect on the 141-candidate sulfide pool. In
LLZO, feedback beats no feedback and the agent moves away from fluorides (iterative fluoride share
0.18 → 0.09), but random search outperforms every LLM arm and no LLM run found LLZO's optimum, LiClO4.
The chloride environment saturates.

Archive: `data/experiments/environment_v1/` (README, `environment_summary.json`, `usage.json`, per-environment
runs, summaries, curves, replay audits, hashes). Also done from SYNC_ADEM_8: the `--production` completeness
check, the secondary summaries, and "hard ceiling" renamed to "high-output scenario".

Please review. Next: slides, and the joint review before merging to main.
