# LLM-guided PET-MAD pilot — MOCK (no live model)

Status: **running**. Mode `mock`, settings `{"model": "claude-haiku-5-5", "temperature": 1.0, "max_tokens": 4096}`. HTTP attempts used 2 of 10 (reservations unsettled: 0). Menu `0a83d472ab56`, table `f70342c9aae0`, manifest `99ef2dc199b7`.

## Decision timeline

| # | Stage | Attempt | Selected | Shortlist | Hypothesis | Forecast W_adh cathode / electrolyte (J/m²) | Weaker (pred.) | Change trigger | Prior-prediction assessment | Feedback seen | HTTP | Record |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | prior | 0 | — | LiTaF6, LiCaAlF6, LiF | mock hypothesis | — | — |  |  | — | 1 | c08975a91eb4 |
| 2 | choose_2 | 0 | LiTaF6 | LiTaF6, LiCaAlF6, LiF | mock hypothesis | [2, 4] / [1, 2] | electrolyte | mock trigger | mock assessment | db7306f2 | 1 | b9c0b2aefed7 |

## Prediction checks (observed = selected primary registry)

| Decision | Coating | Contact | Forecast | Width | Observed | In range | Miss | Weaker pred./obs. | Agrees |
|---|---|---|---|---|---|---|---|---|---|
| choose_2 | LiTaF6 | — | — | — | not yet revealed | | | | |

## Decision comparison

Not available until both choices are made.

## Limitations

- Forecast ranges are model statements, not calibrated confidence intervals.
- Two new coatings cannot establish search superiority or statistical significance.
- The unchosen coating in the decision comparison has no measured outcome.
- Contact models are formally polar; Li transport is not tested; sensitivity checks are reported separately.
