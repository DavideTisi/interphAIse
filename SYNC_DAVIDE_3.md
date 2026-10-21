# Agent update after SYNC_ADEM_3: integration, reproduction and controls

21 October 2026. From Adem. Replies to `SYNC_ADEM_2.md` and `SYNC_ADEM_3.md`.

## Integrated

Branch `work/agent-experiments`, head `e3bab25`, merges `davide` at `6097831`.

- **Your accounting and analysis are kept.** Invalid and repeated IDs are charged, batches are
  validated strictly, paths are portable, duplicates need explicit replacement, and the
  summaries and fluoride-first baseline are unchanged. The merge keeps your prompt version
  `v3-2026-10-21c-charged-ids`. The prompt text is untouched, so new arms remain comparable with
  your archived iterative cohort.
- **Best-bin panel re-added on top of your analysis.** It shows the median best penalty bin found
  so far per arm. The band is the interquartile range (spread, not a confidence interval) from
  order statistics v[(n-1)//4], v[(n-1)//2] and v[ceil(3(n-1)/4)]. It also shows the exact random
  median and the fluoride-first trajectory. Runs with no valid candidate yet count as worse than
  every bin. The median quartiles are added to `--summary`. The reference lines now look the same
  in every panel, with one shared legend.
- **`scripts/__init__.py` added.** The `agents` conda environment has an installed top-level
  `scripts` package that shadowed ours, so `test_batch_audit.py` and `test_experiment_analysis.py`
  could not import there. An empty `__init__.py` fixes it and changes nothing for `.venv`.
- **Tests:** 41 pass (discovery, analysis, batch audit, benchmark, client restrictions, viewer).

## Your 30-run batch, reproduced

The analysis and audit commands in `INTEGRATED_DISCOVERY_RESULTS.md` reproduce your numbers exactly
from `data/experiments/integrated_v3_20261021_s100`: acceptable found 19, 10, 4 and 4 of 30 for
iterative, random, upfront and sequential; best bin 7, 6, 1 and 0. You're right that sequential
picks LiZr₂(PO₄)₃ in 10/30 runs there. My "never" applied only to my first batch, and I withdraw
it. I also agree that escaping a self-reinforcing hypothesis can be how feedback helps, not a flaw
in the control.

**Bin ≤ 2, chosen after seeing results** (M = 5, exact random 68.9% by k = 10):

| Arm | Bin ≤ 2 by 10 | LiZr₂(PO₄)₃ picked |
|---|---|---|
| Upfront | 26/30 | 25/30 runs |
| Iterative | 22/30 | 4/30 |
| Random | 18/30 | 14/30 |
| Sequential | 13/30 | 10/30 |

**Median best bin so far:**

| k | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Random (exact median) | 15 | 8 | 5 | 3 | 3 | 3 | 2 | 2 | 2 | 2 |
| Random | 16 | 9 | 8 | 3 | 3 | 3 | 2 | 2 | 2 | 2 |
| Upfront | 16 | 15 | 15 | 10 | 9 | 2 | 2 | 2 | 2 | 2 |
| Iterative | 16 | 15 | 15 | 9 | 9 | 9 | 9 | 2 | 2 | 2 |
| Sequential | 16 | 15 | 15 | 10 | 10 | 10 | 10 | 10 | 10 | 8 |
| Fluorides first (post-hoc) | 15 | 2 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |

This supports your headline. The feedback benefit shows up late, iterative is no better than
random at finding the optimum, and the post-hoc fluoride-first heuristic beats every arm.

Figure: `python scripts/analyse_discovery_experiment.py data/experiments/integrated_v3_20261021_s100
--plot <path>`. I didn't overwrite the `curves.png` in your archive.

## Example runs for slides (iterative, your batch)

19 of 30 succeed, almost all along the same path: Li₃PO₄ (bin 16) → LiF (15) → chlorides
Li₂MgCl₄ / Li₂ZnCl₄ (9) → LiCaAlF₆ (2, acceptable) → more fluorides. The 11 failures split three ways:
3 near misses reaching LiZr₂(PO₄)₃ at bin 2 (r108, r113, r122); 5 that stall at the chlorides
(bin 9) and never try a mixed fluoride (r100, r101, r121, r124, r125); and 3 that never try a
halide after LiF and stay in oxides, silicates and borates (r104, r114, r117; r122 also never
returns to halides).

- **Success, r111** (acceptable at step 6, best bin LiNbF₆ at step 10). After Li₃PO₄ fails, it
  tries Li₂MgCl₄ at step 2 (0.189, bin 9), so the later poor LiF (0.310) reads as an exception
  within a promising halide direction. It then turns to mixed fluorides with hard-to-reduce
  cations: LiCaAlF₆ (0.048) → Li₂SiF₆ (0.081) → Li₂TiF₆ (0.076) → LiNbF₆ (bin 1). Every number
  it cites matches the queried results.
- **Failure, r114.** Li₃PO₄ then LiF both fail, and it concludes that "phosphate or fluoride
  chemistry" performs worse. That writes off a whole family from one example, which the plan
  warns against. It then chases an oxide local minimum (LiAlSiO₄ 0.204 → LiSiBO₄ 0.177) and never
  returns to halides. Claims such as "Al-containing products drove the higher penalties" are
  Haiku's interpretation; nobody has checked them against the products.

Chemical claims in both: the cited penalties and bins are correct. The mechanisms it gives (anion
exchange, hard-to-reduce cations, Li content) are hypotheses the evaluator doesn't test, and the
slides should present them that way. Point for discussion: whether a fluoride gets a second
chance seems to depend on the order of the early results.

## Controls: implemented and tested, not run

**Shuffled (`--arms shuffled`).**
- **How it works:** only first queries of pool candidates are permuted, by an inside-out
  Fisher–Yates shuffle with a recorded seed. Each turn, the newest outcome swaps with a random
  earlier real outcome, so at most one earlier displayed outcome changes per turn. Each displayed
  outcome is relabelled with the candidate it sits next to.
- **Invalid IDs:** charged invalid or repeated IDs are never permuted and keep their own error at
  their slot. ID handling is type-safe, so non-string IDs are fine.
- **Logging:** true results are kept unchanged for scoring, and `displayed_sources` logs the true
  source of every displayed slot after each turn.
- **Tests:** permutation of queried outcomes only, relabelling, true-score preservation,
  reproducibility, and unknown, `None`, list and repeated IDs.
- **Limitations,** also in the code:
  - A moved outcome can contradict a rationale written when it was shown elsewhere.
  - Reaction products can hint at the true source; a chloride's products next to a fluoride,
    for example.
  - The first real outcome cannot be shuffled.

  So it measures sensitivity to corrupted feedback, not clean proof of chemical reasoning. A
  history that never changes earlier displays is not possible online without repeating
  outcomes, which is why at most one earlier display changes per turn.

**IDs-only sequential (`--arms sequential_ids`).** Same prompt and request as sequential, but the
history shows only earlier `candidate_id`s, with no hypotheses, motivations or outcomes. Compared
with sequential it tests dependence on rationale history. As you note, iterative against IDs-only
changes two things at once, so it isn't a matched feedback ablation.

## Proposal and questions

1. **Run shuffled, 30 runs** with your settings: seeds 100–129, budget 10, Haiku 5.5, temperature
   1.0, `--max-tokens 4096`, prompt `v3-2026-10-21c-charged-ids`. That's about 300 proposal calls
   before retries:
   `python scripts/run_discovery_experiment.py --arms shuffled --repeats 30 --start-seed 100 --temperature 1.0`
   Agreed? It would be analysed against your archived iterative cohort, since the prompt and
   settings match.
2. **IDs-only, 30 runs** (another ~300 calls): now, or only if time and budget allow?
3. **Slides:** shall I prepare the three-panel figure and the r111 / r114 pair?
