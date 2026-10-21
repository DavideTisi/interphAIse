# Short team update for Adem — 21 October 2026

The original discovery result is now supported by the shuffled control. Our next
priority is testing adaptation across battery environments, while Claude develops
the interface-validation part independently.

**Codex — review and integration.** Independently verified your `6e74e88` archive:
all 300 true outcomes, saved feedback permutations and prompt histories match.
Iterative succeeds 19/30 versus shuffled 6/30; exact paired p = 0.004425.
The defensible claim is that correctly associated feedback improves candidate
selection here. History contradictions and identity leakage still limit the
reasoning claim; the original fluoride-first heuristic remains faster.
A temporary merge of committed `b210db0` and `6e74e88` was conflict-free and passed
104 tests, preserving Claude's pilot code. No actual branch merge occurred.

**Expansion subagent — data and exhaustive evaluation.** Expanded the unchanged
pool filters to 141 structures and evaluated three electrolyte environments,
keeping LiCoO2, 4 V and the v3 objective: **423 combinations**. Retrieved compatible
MP data, giving 7,420 corrected entries; 414 outcomes computed and nine retain
explicit missing-entry failures. All 50 original scores reproduce exactly;
40 targeted tests and six independent solver checks pass.

| Electrolyte | Acceptable /141 | Exact random success by 10 | Fluoride-first first success |
|---|---:|---:|---:|
| Li6PS5Cl | 4 | 25.74% | Query 3 |
| Li3InCl6 | 55 | 99.43% | Query 1 |
| Ordered tetragonal LLZO | 17 | 73.57% | Query 40 |

All acceptable sulfide structures contain fluorine; none of the LLZO ones does.
This gives us a useful test of revising chemical intuition. Chloride is easy even
for random search, so retain all environments and report early-query and bin-regret
curves. **No expanded LLM experiment has been frozen or run.**

**Claude — PET-MAD bulk references.** Completed five bulk relaxations, their
unconstrained checks, and five additional starts for each distorted material.
Li6PS5Cl has six converged arrangements; LiZr2(PO4)3 has five, with one failed seed
excluded. Seed 0 remains the reference for both; alternative seeds are 4 and 1.
These are model structures, not established phases. The proposed primary contacts
share LiNbF6(001), with LiCoO2(001), at about 504/440 atoms. Codex found differing
electrolyte terminations and a candidate-cutoff issue to resolve before comparison.
Rebuilt interface relaxations and polarity/convergence validation remain pending;
the old adhesion values remain feasibility results.

**Next for you:** defer IDs-only; prepare the environment runner and a separate
pre-run protocol with matched controls, fixed settings and per-environment metrics.
The LLM replaces the scientist deciding which hypothesis to revise and candidate
to test after feedback. We have prepared the landscape to test that ability;
adaptation across environments is still an open result. Review the completed
discovery release now, keeping expansion and bulk changes in separate commits.
The changes are now committed on `davide`: **`57774d6`** contains the bulk work
and audits; **`81e4625`** contains the expansion code and data. This handoff and
the shared reports form a separate documentation commit. The full current suite
passes **113 tests**. The publication targets `origin/davide`; integration into
your agent branch and `main` remains a separate step.

Details: [discovery review](SYNC_ADEM_5.md),
[expansion results and reproduction](EXPANSION_PROGRESS.md),
[interface handoff](SYNC_CLAUDE_1.md). The development log records the full sequence.
