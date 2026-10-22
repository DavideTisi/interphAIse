# Final experiment slides, traces, integration and tests

21 October 2026. From Adem. Branch `work/agent-experiments`, which includes `davide` at `fa10a1a`
(merge `2bc7087`). No paid runs. The production archive `data/experiments/environment_v1/` is unchanged.

## Slides

`presentations/interphAIse_environment_experiment_2026-10-21.pptx`: 5 widescreen slides to insert
into the main deck, with speaker notes giving each slide's sources.

1. **Feedback beats no feedback; random wins on LLZO.** Success vs query budget in all three
   environments, plus the three per-environment results.
2. **Planned comparisons: 3 of 6 survive Holm.** Table of the six McNemar contrasts with raw and
   Holm p, next to your endpoint overview figure.
3. **What changed the next selection.** The two selected traces.
4. **LLZO: random exploration wins in 10 queries.** 24/30 vs 12/30, the pick-concentration table,
   late narrow adaptation, and the caveat from SYNC_ADEM_10 (5 of 17 flagged; 18 of random's 24
   successes also found an unflagged candidate; proxy limits; no evidence of deliberate
   avoidance). Your approved wording is in the notes.
5. **What the study supports, and what it does not**, including the optimum-finding and
   mechanism limits.

Checks: the pptx validator passes; programmatic checks show no off-slide shapes and correct text.
**Not visually checked:** LibreOffice/pdftoppm are unavailable here and image viewing was blocked,
so please look at it in PowerPoint before presenting. Fonts are Calibri (your deck uses Aptos).
The build script was run from a scratch folder and is not in the repo.

## Figures

- `figures/environment_success_vs_budget.png`, new, from `scripts/plot_environment_curves.py`
  (reads the archived per-environment `summary.json`): P(acceptable by query k), 5 arms × 3
  environments, 95% Wilson, exact random, post-hoc fluoride-first. Not viewed, for the same
  reason.
- `figures/trace_environment_pair.png`, new, from `scripts/plot_trace_pair.py`.
- `figures/environment_acceptance_review_20261021.png`: your endpoint overview, reused.

## Selected traces (rule fixed before reading rationales)

Lowest seed whose first acceptable hit is at the arm's typical query.

- **Sulfide, iterative seed 202** (`environment_v1/lpscl/iterative_r202.json`, median first hit 8).
  After Li₂O 1.815 and Li₃PO₄ / LiF / LiAlO₂ ≈ 0.3 fail, it keeps fluoride chemistry and adds Al³⁺:
  Li₃AlF₆ 0.160 (query 6), so it refines to LiMgAlF₆ 0.057 (query 7, just above the limit),
  then LiCaAlF₆ 0.048, acceptable at query 8. The observation it cites at each step matches the
  recorded result.
- **LLZO, iterative seed 207** (`environment_v1/llzo/iterative_r207.json`; 10 of 12 successes first
  hit at queries 8–10). After six failures it attributes them to La-bearing products (LaPO₄, LaF₃,
  LaBO₃). Li₄SiO₄ shows a low contact reaction but self-decomposition 0.346, so it proposes a less
  Li-rich Al/Si oxide: LiAlSiO₄ 0.033, acceptable at query 9. Query 10 re-tests a LiAlSiO₄
  polymorph (narrow).

The mechanisms in the rationales are Haiku's hypotheses; the penalties it cites are recorded values.

## Integration and tests

- Merged `fa10a1a`; the only conflict was the dev log, both entries kept.
- Targeted tests: 43 passed (discovery, experiment analysis, environment study, PET-MAD registry).
- Full suite in the `agents` conda env: **154 passed, 4 failed**. The failures are the
  pre-existing interface-pipeline tests (`test_orchestrator` ×2, `test_screen`, `test_tools`
  matcher), which also fail at `c92699a` in this env and pass in your `.venv`. Probable cause:
  pymatgen 2026.4.16 here; not confirmed.

## Remaining issues before merging to main

1. Visual check of the new slides and the curves figure.
2. The pymatgen/matcher failures in this environment (pin, or fix the matcher).
3. `SYNC_DAVIDE_6.md` ends with "Next on my side: slides"; that was written before we agreed
   that slides are mine for the experiment part and yours for the overall deck.
4. Joint review of the combined diff against `main`.
