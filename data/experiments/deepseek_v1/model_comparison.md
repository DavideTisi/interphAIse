# Haiku 5.5 vs DeepSeek V3.2: three-environment study

A comparison of **model configurations**, not matched reasoning compute. Random is reused from the Haiku archive. Entries: acceptable runs / 30, with 95% Wilson interval. Descriptive across models.

## Acceptance within 10 queries

| Environment | Arm | Haiku 5.5 | DeepSeek V3.2 |
|---|---|---|---|
| Li6PS5Cl | random | 8/30 (0.14–0.44) | reused (Haiku archive) |
| Li6PS5Cl | upfront | 0/30 (0.00–0.11) | 2/30 (0.02–0.21) |
| Li6PS5Cl | sequential | 2/30 (0.02–0.21) | 2/30 (0.02–0.21) |
| Li6PS5Cl | iterative | 20/30 (0.49–0.81) | 12/30 (0.25–0.58) |
| Li6PS5Cl | shuffled | 6/30 (0.10–0.37) | 3/30 (0.03–0.26) |
| Li3InCl6 | random | 29/30 (0.83–0.99) | reused (Haiku archive) |
| Li3InCl6 | upfront | 30/30 (0.89–1.00) | 30/30 (0.89–1.00) |
| Li3InCl6 | sequential | 30/30 (0.89–1.00) | 30/30 (0.89–1.00) |
| Li3InCl6 | iterative | 30/30 (0.89–1.00) | 30/30 (0.89–1.00) |
| Li3InCl6 | shuffled | 30/30 (0.89–1.00) | 30/30 (0.89–1.00) |
| Li7La3Zr2O12 | random | 24/30 (0.63–0.90) | reused (Haiku archive) |
| Li7La3Zr2O12 | upfront | 1/30 (0.01–0.17) | 20/30 (0.49–0.81) |
| Li7La3Zr2O12 | sequential | 0/30 (0.00–0.11) | 4/30 (0.05–0.30) |
| Li7La3Zr2O12 | iterative | 12/30 (0.25–0.58) | 10/30 (0.19–0.51) |
| Li7La3Zr2O12 | shuffled | 4/30 (0.05–0.30) | 12/30 (0.25–0.58) |

## Planned comparisons (paired by seed, exact McNemar, Holm within each model's family of 6)

| Environment | Contrast | Model | iterative-only / other-only | Difference | p | p (Holm) | Holm 0.05 |
|---|---|---|---|---|---|---|---|
| Li6PS5Cl | iterative-sequential | Haiku 5.5 | 18 / 0 | +0.60 | 7.63e-06 | 4.58e-05 | reject |
| Li6PS5Cl | iterative-sequential | DeepSeek V3.2 | 12 / 2 | +0.33 | 0.0129 | 0.0776 | not rejected |
| Li6PS5Cl | iterative-shuffled | Haiku 5.5 | 15 / 1 | +0.47 | 0.000519 | 0.00244 | reject |
| Li6PS5Cl | iterative-shuffled | DeepSeek V3.2 | 11 / 2 | +0.30 | 0.0225 | 0.112 | not rejected |
| Li3InCl6 | iterative-sequential | Haiku 5.5 | 0 / 0 | +0.00 | 1 | 1 | not rejected |
| Li3InCl6 | iterative-sequential | DeepSeek V3.2 | 0 / 0 | +0.00 | 1 | 1 | not rejected |
| Li3InCl6 | iterative-shuffled | Haiku 5.5 | 0 / 0 | +0.00 | 1 | 1 | not rejected |
| Li3InCl6 | iterative-shuffled | DeepSeek V3.2 | 0 / 0 | +0.00 | 1 | 1 | not rejected |
| Li7La3Zr2O12 | iterative-sequential | Haiku 5.5 | 12 / 0 | +0.40 | 0.000488 | 0.00244 | reject |
| Li7La3Zr2O12 | iterative-sequential | DeepSeek V3.2 | 8 / 2 | +0.20 | 0.109 | 0.438 | not rejected |
| Li7La3Zr2O12 | iterative-shuffled | Haiku 5.5 | 11 / 3 | +0.27 | 0.0574 | 0.172 | not rejected |
| Li7La3Zr2O12 | iterative-shuffled | DeepSeek V3.2 | 6 / 8 | -0.07 | 0.791 | 1 | not rejected |

## LLZO against the reused random baseline

Random (Haiku archive): 24/30 (0.63–0.90).

| Model | Arm | Acceptable | Difference vs random |
|---|---|---|---|
| Haiku 5.5 | iterative | 12/30 (0.25–0.58) | -0.40 |
| Haiku 5.5 | upfront | 1/30 (0.01–0.17) | -0.77 |
| DeepSeek V3.2 | iterative | 10/30 (0.19–0.51) | -0.47 |
| DeepSeek V3.2 | upfront | 20/30 (0.49–0.81) | -0.13 |

LLZO interpretation keeps the chemistry-audit caveat (SYNC_ADEM_10): the acceptable set includes flagged oxyhalogen candidates with different evidence levels.

## Usage (LLM arms, three environments)

| Model | Calls | Input tokens | Output tokens (incl. reasoning) | Reasoning | Cost (USD) | Cost basis |
|---|---|---|---|---|---|---|
| Haiku 5.5 | 2800 | 24,304,759 | 2,399,805 | 1,518,160 | 3.63 | list-price estimate |
| DeepSeek V3.2 | 2793 | 16,074,042 | 6,782,984 | 6,433,030 | 8.99 | OpenRouter-reported charge |
