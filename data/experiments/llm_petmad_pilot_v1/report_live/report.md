# LLM-guided PET-MAD pilot

Status: **complete**. Mode `live`, settings `{"model": "claude-haiku-5-5", "temperature": 1.0, "max_tokens": 4096}`. HTTP attempts used 5 of 10 (reservations unsettled: 0). Menu `0a83d472ab56`, table `f70342c9aae0`, manifest `99ef2dc199b7`.

## Decision timeline

| # | Stage | Attempt | Selected | Shortlist | Hypothesis | Forecast W_adh cathode / electrolyte (J/m²) | Weaker (pred.) | Change trigger | Prior-prediction assessment | Feedback seen | HTTP | Record |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | prior | 0 | error: ValueError: ordered_shortlist must rank exactly these unevaluated IDs once: ['m… |  |  | — | — |  |  | — | 1 | 71635c07544b |
| 2 | prior | 1 | — | LiTaF6, LiCaAlF6, LiF | Ranking uses only the frozen thermodynamic penalty and acceptance flags, since no adhesion data exist yet for these candidates. LiTaF6 (mp-aaacjmqp) has the lo… | — | — |  |  | — | 1 | a6067dc15ae2 |
| 3 | choose_2 | 0 | LiTaF6 | LiTaF6, LiCaAlF6, LiF | LiTaF6 is the next coating to evaluate. It has the lowest frozen penalty among the unevaluated candidates (0.027, bin 1, acceptable) and a 5.9 eV gap. LiNbF6, … | [3.2, 3.9] / [1.4, 1.9] | electrolyte | Revisit the ranking if the validated LiTaF6 electrolyte W_adh falls below about 1.4 J/m2 or rises a… |  | db7306f2 | 1 | 010ad614ea26 |
| 4 | choose_3 | 0 | LiCaAlF6 | LiCaAlF6, LiF | LiTaF6 came back as predicted: its weaker contact is the electrolyte (min W_adh 1.58 J/m2) and the cathode contact is 3.34 J/m2. Both values sit inside my earl… | [3, 3.8] / [1.4, 1.9] | electrolyte | Revisit the ranking if the LiCaAlF6 validated min W_adh exceeds about 1.63 J/m2 (the LiNbF6 electro… | The LiTaF6 prediction was supported. The predicted cathode range [3.2, 3.9] contains the validated 3.34 J/m2. The predi… | db7306f2, dd72717b | 1 | 66ff7ea1abab |
| 5 | summary | 0 | — |  |  | — | — |  | HELD: (1) The initial penalty-only ordering (LiTaF6, then LiCaAlF6, then LiF) matched the penalty bins and acceptance f… | db7306f2, dd72717b, 2b8dff7f | 1 | ecb1608f663c |

## Prediction checks (observed = selected primary registry)

| Decision | Coating | Contact | Forecast | Width | Observed | In range | Miss | Weaker pred./obs. | Agrees |
|---|---|---|---|---|---|---|---|---|---|
| choose_2 | LiTaF6 | cathode | [3.2, 3.9] | 0.7 | 3.339 | True | 0.000 | electrolyte / electrolyte | True |
| choose_2 | LiTaF6 | electrolyte | [1.4, 1.9] | 0.5 | 1.577 | True | 0.000 | electrolyte / electrolyte | True |
| choose_3 | LiCaAlF6 | cathode | [3, 3.8] | 0.8 | 1.427 | False | 1.573 | electrolyte / electrolyte | True |
| choose_3 | LiCaAlF6 | electrolyte | [1.4, 1.9] | 0.5 | 0.744 | False | 0.656 | electrolyte / electrolyte | True |

## Decision comparison

Next in the choose-2 shortlist: LiCaAlF6; chosen at choose-3: LiCaAlF6; changed: **False**. Decision comparison at a common information state; the unchosen coating has no measured outcome.

## Limitations

- Forecast ranges are model statements, not calibrated confidence intervals.
- Two new coatings cannot establish search superiority or statistical significance.
- The unchosen coating in the decision comparison has no measured outcome.
- Contact models are formally polar; Li transport is not tested; sensitivity checks are reported separately.
