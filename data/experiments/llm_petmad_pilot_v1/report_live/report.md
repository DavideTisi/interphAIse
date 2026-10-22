# LLM-guided PET-MAD pilot

Status: **running**. Mode `live`, settings `{"model": "claude-haiku-5-5", "temperature": 1.0, "max_tokens": 4096}`. HTTP attempts used 3 of 10 (reservations unsettled: 0). Menu `0a83d472ab56`, table `f70342c9aae0`, manifest `99ef2dc199b7`.

## Decision timeline

| # | Stage | Attempt | Selected | Shortlist | Hypothesis | Forecast W_adh cathode / electrolyte (J/m²) | Weaker (pred.) | Change trigger | Prior-prediction assessment | Feedback seen | HTTP | Record |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | prior | 0 | error: ValueError: ordered_shortlist must rank exactly these unevaluated IDs once: ['m… |  |  | — | — |  |  | — | 1 | 71635c07544b |
| 2 | prior | 1 | — | LiTaF6, LiCaAlF6, LiF | Ranking uses only the frozen thermodynamic penalty and acceptance flags, since no adhesion data exist yet for these candidates. LiTaF6 (mp-aaacjmqp) has the lo… | — | — |  |  | — | 1 | a6067dc15ae2 |
| 3 | choose_2 | 0 | LiTaF6 | LiTaF6, LiCaAlF6, LiF | LiTaF6 is the next coating to evaluate. It has the lowest frozen penalty among the unevaluated candidates (0.027, bin 1, acceptable) and a 5.9 eV gap. LiNbF6, … | [3.2, 3.9] / [1.4, 1.9] | electrolyte | Revisit the ranking if the validated LiTaF6 electrolyte W_adh falls below about 1.4 J/m2 or rises a… |  | db7306f2 | 1 | 010ad614ea26 |

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
