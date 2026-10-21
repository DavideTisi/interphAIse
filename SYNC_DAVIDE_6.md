# Clarifications after SYNC_ADEM_9

21 October 2026. From Adem. Branch `work/agent-experiments`, which now includes `davide` at `ad6b471`
(combined tests: 43 passed across discovery, analysis, environment study and PET-MAD registry).
The production archive `data/experiments/environment_v1/` is unchanged.

1. **Analysis provenance.** The primary endpoint, contrasts, Holm family and secondary definitions
   were fixed in `scripts/analyse_environment_study.py` at `0072f3d`, before production ran. The
   final analyser used for the archived `environment_summary.json` additionally contains, from
   `abab0a2`: the `--production` completeness check, best-bin Wilson intervals, first-hit
   quartiles and counts, per-run fluoride records (all requested in SYNC_ADEM_8), and a
   serialisation fix (a numpy p-value made the Holm flag non-JSON-serialisable; no values
   changed). It is not byte-identical to the `0072f3d` version. The archive README's sentence
   "Analysis code fixed at `0072f3d` before the runs" should be read this way; the archive is left
   unchanged.
2. **Chloride wording.** My earlier "every arm succeeds" for Li₃InCl₆ should read: every LLM arm
   30/30, sampled random 29/30 (exact 99.4%). It is the declared ceiling case.
3. **LLZO evaluator question** (sent on Slack, recorded here). The LLM arms concentrate on about
   20–33 textbook coatings (Li₃PO₄, LiNbO₃, LiAlO₂, Li₂ZrO₃, Li₃BO₃, LiF), none acceptable for LLZO.
   Random spreads over 95 formulas, and 11% of its picks are acceptable. The acceptable LLZO set
   includes LiIO₃, Li₅IO₆ and LiClO₄ (strong oxidisers that a chemist would not propose as
   coatings) alongside aluminosilicates and Mg/Ti oxides. I suggest stating this as a caveat for
   LLZO (the prior partly disagrees with the 0 K, fixed-Li-potential criterion), without changing
   the frozen criterion or adding a primary claim. Do you agree?

Next on my side: slides following your suggested story, using
`figures/environment_acceptance_review_20261021.png`.
