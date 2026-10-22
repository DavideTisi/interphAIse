# DeepSeek repeat: validated results and LLZO audit

22 October 2026, 19:30 CEST. From Adem. Branch `work/agent-experiments`.
Protocol: [DEEPSEEK_PROTOCOL.md](DEEPSEEK_PROTOCOL.md).
Archive: [data/experiments/deepseek_v1/](data/experiments/deepseek_v1/README.md).

This **supersedes the interim figures sent earlier today**. Those covered only about 60% of the runs.

**Label:** a comparison of model configurations, not matched reasoning compute.

## Execution

- **Runs:** all 360 complete, 0 failed. 2,793 calls, including 3 charged format retries.
- **Configuration:** `deepseek/deepseek-v3.2`, pinned to SiliconFlow fp8 with no fallbacks. Reasoning cap 3,072, output cap 4,096; 0 cap or provider violations.
- **Spend:** USD 8.99 recorded by OpenRouter; the key's total spend was USD 9.19, including about USD 0.2 from a duplicate launch that was stopped after about 2 minutes and excluded. Limit USD 12.
- **Validation:** `analyse_environment_study.py --production --policy deepseek_v1` passed. That covers the settings, the per-call metadata, the workflow hashes, and a replay of every query.

## Acceptance within 10 queries (n = 30 per arm)

| Environment | Arm | Haiku 5.5 | DeepSeek V3.2 |
|---|---|---|---|
| Li₆PS₅Cl (random 8/30) | iterative | 20 | 12 |
| | sequential | 2 | 2 |
| | shuffled | 6 | 3 |
| | upfront | 0 | 2 |
| Li₃InCl₆ (random 29/30) | all four arms | 30 | 30 (ceiling) |
| LLZO (random 24/30) | iterative | 12 | 10 |
| | sequential | 0 | 4 |
| | shuffled | 4 | 12 |
| | upfront | **1** | **20** |

## Planned comparisons (paired, exact McNemar, Holm within each model's family of 6)

| Environment | Contrast | Haiku: difference (Holm p) | DeepSeek: difference (Holm p) |
|---|---|---|---|
| Li₆PS₅Cl | iterative − sequential | +0.60 (4.6e-5) **reject** | +0.33 (0.078) not rejected; raw p 0.013 |
| Li₆PS₅Cl | iterative − shuffled | +0.47 (0.0024) **reject** | +0.30 (0.11) not rejected; raw p 0.023 |
| Li₃InCl₆ | both contrasts | 0 (1), ceiling | 0 (1), ceiling |
| LLZO | iterative − sequential | +0.40 (0.0024) **reject** | +0.20 (0.44) |
| LLZO | iterative − shuffled | +0.27 (0.17) | −0.07 (1) |

For DeepSeek, none of the six tests survives Holm. The full tables are in [model_comparison.md](data/experiments/deepseek_v1/model_comparison.md).

## Answers to the three questions (descriptive)

1. **Does correct feedback help both models?**
   - **Sulfide:** the direction is the same for DeepSeek: iterative 12/30 against 2 and 3. But the effect is smaller and does not survive Holm correction.
   - **LLZO:** feedback gives DeepSeek no benefit; iterative is slightly below shuffled.
   - So the feedback benefit is clearest for Haiku, and only partly replicated.
2. **Is Haiku's LLZO failure specific to Haiku?**
   - Largely, yes. DeepSeek's upfront shortlist, which gets no feedback, succeeds in 20/30 runs, close to random (24/30); Haiku's succeeded in 1/30.
   - Iterative stays well below random for both models (Haiku 12, DeepSeek 10).
3. **Starting knowledge or use of feedback?**
   - DeepSeek's LLZO strength comes from its starting knowledge (upfront 20/30), and feedback lowers it (iterative 10/30).
   - Haiku's sulfide strength comes from using feedback (iterative 20/30 against upfront 0/30).

## LLZO exploratory audit (post-hoc; [llzo_audit.md](data/experiments/deepseek_v1/llzo_audit.md))

| Model, arm | Successful runs | Flagged-only runs | Flagged picks | Distinct formulas (30 runs) | Mean Jaccard |
|---|---|---|---|---|---|
| Haiku, upfront | 1 | 0 | 0 | 22 | 0.58 |
| Haiku, iterative | 12 | 0 | 0 | 33 | 0.51 |
| DeepSeek, upfront | 20 | 0 | 0 | 38 | 0.47 |
| DeepSeek, iterative | 10 | 1 | 5 | 45 | 0.32 |

- **Which formulas succeed:**
  - DeepSeek's upfront successes are all unflagged: LiAlSiO₄ ×18, LiMgPO₄ ×3, LiAl(SiO₃)₂ ×1.
  - LiAlSiO₄ is the same compound Haiku found only through feedback, with 26 iterative picks.
  - DeepSeek's iterative selections include 5 flagged picks (LiIO₃ ×3, LiClO₄, Li₅IO₆), and 1 run succeeded only through a flagged compound.
- **Diversity:**
  - DeepSeek's upfront shortlists are more varied than Haiku's: 38 distinct formulas and similarity 0.47, against 22 and 0.58.
  - Its iterative selections are the most varied of all (45 distinct, similarity 0.32).
  - So feedback spreads DeepSeek's picks around rather than focusing them.
  - Flagged = the explicit oxyhalogen review set (SYNC_ADEM_10). It is a narrow annotation, not a hazard classifier.

## Suggested slide wording

> Repeating the three-environment study with DeepSeek V3.2 (a comparison of model configurations): the feedback benefit in the sulfide keeps its direction but is smaller and not significant after Holm correction. Haiku's LLZO failure is largely Haiku-specific: DeepSeek's prior already proposes LiAlSiO₄ and reaches 20/30 without feedback. In LLZO, feedback does not help either model beat random search.

Figure: [deepseek_success_vs_budget.png](data/experiments/deepseek_v1/deepseek_success_vs_budget.png).
