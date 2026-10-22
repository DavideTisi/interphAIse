# LLZO exploratory audit (post-hoc, descriptive)

Flagged = explicit oxyhalogen review set (LiIO3, LiClO4, Li5IO6), a narrow annotation, not a hazard classifier. Diversity: formulas per run (of 10 queries), distinct formulas over 30 runs, and mean pairwise Jaccard similarity of run formula sets (1 = identical shortlists).

| Model | Arm | Successful runs | Unflagged-hit runs | Flagged-only runs | Flagged picks | Formulas/run | Distinct (30 runs) | Mean Jaccard |
|---|---|---|---|---|---|---|---|---|
| Haiku 5.5 | upfront | 1/30 | 1 | 0 | 0 | 9.4 | 22 | 0.58 |
| Haiku 5.5 | iterative | 12/30 | 12 | 0 | 0 | 9.0 | 33 | 0.51 |
| Haiku 5.5 | sequential | 0/30 | 0 | 0 | 0 | 6.9 | 19 | 0.44 |
| Haiku 5.5 | shuffled | 4/30 | 4 | 0 | 0 | 9.8 | 44 | 0.38 |
| DeepSeek V3.2 | upfront | 20/30 | 20 | 0 | 0 | 10.0 | 38 | 0.47 |
| DeepSeek V3.2 | iterative | 10/30 | 9 | 1 | 5 | 8.7 | 45 | 0.32 |
| DeepSeek V3.2 | sequential | 4/30 | 4 | 0 | 0 | 5.7 | 28 | 0.35 |
| DeepSeek V3.2 | shuffled | 12/30 | 12 | 0 | 0 | 8.8 | 42 | 0.32 |

## Acceptable formulas found (acceptable picks over 30 runs); anion classes of distinct formulas per run, summed

- **Haiku 5.5, upfront**: LiMgPO4 ×1.
  Anion classes: O only 248, F 35.
- **Haiku 5.5, iterative**: LiAlSiO4 ×26, LiAl(SiO3)2 ×1, LiAl(Si2O5)2 ×1, LiMgPO4 ×1.
  Anion classes: O only 230, F 40.
- **DeepSeek V3.2, upfront**: LiAlSiO4 ×18, LiMgPO4 ×3, LiAl(SiO3)2 ×1.
  Anion classes: O only 255, F 37, Cl 7, F+O 1.
- **DeepSeek V3.2, iterative**: LiAlSiO4 ×21, LiAl(SiO3)2 ×6, LiMgPO4 ×3, LiIO3 (flagged) ×3, LiAl(Si2O5)2 ×1, LiClO4 (flagged) ×1, Li5IO6 (flagged) ×1.
  Anion classes: O only 224, F 31, oxyhalogen (flagged) 3, F+O 1, Cl 1, I+O 1.
