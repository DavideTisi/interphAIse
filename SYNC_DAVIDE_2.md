# Agent results on frozen v3, and questions for Davide

21 October 2026, afternoon. From Adem. Follows `SYNC_ADEM.md`.

## What we have done since the first note

All on `work/agent-experiments` (pushed, head `11aa655`), in order:

1. **`d380de0` Sequential control and synthetic fixture.** Added the sequential arm (one
   choice per turn, sees its own earlier choices, no outcomes) and a synthetic pool. Also
   removed leftover lines in `llm.py` that made every live Haiku call fail; you repaired the
   same thing on `main` in `247e0dc`.
2. **`072c941` Experiment runner and analysis.** Proposals now carry `motivation` and
   `mode` (explore/refine); LLM model and token usage are logged per attempt. Added
   `scripts/run_discovery_experiment.py` (repeats with the same candidate order across arms,
   failed runs kept) and `scripts/analyse_discovery_experiment.py` (success curves against the
   exact random baseline).
3. **`c66c5ea` Merged your frozen v3 benchmark** (`946c1ed` onwards) into the branch.
4. **`c312010` Integration with `BenchmarkQueries`**, following `EVALUATOR_HANDOFF.md`:
   - A fresh `BenchmarkQueries` per run, so failed, repeated and invalid queries cost budget
     as you defined.
   - The proposer sees `candidate_id`, formula and family, plus the public task and objective.
     The iterative arm sees only the scientific fields of queried results (no provenance,
     timing or diagnostics); the sequential control sees only its own earlier choices.
   - Scoring uses `ranking_key` and `acceptable`; the legacy `quality()` comparator and the
     live `CoatingEvaluator` are removed, and so is `scripts/run_discovery.py`.
   - Every run records the pool, objective and benchmark hashes and the prompt version.
   - The synthetic fixture now writes pool and benchmark files that go through your real
     `BenchmarkQueries` (with `allow_draft`).
   - Tests on the real frozen data check the information boundary, budget accounting for a
     failed candidate, bounded retries and that seeds give the same candidate order across arms.
5. **Checks before paid runs.** 200 offline random runs match the exact curves; the exact
   values match yours (36.33% and 20% at k = 10). A small live run (3 LLM arms, budget 3) ran
   cleanly. It showed Haiku sometimes returning several candidates when asked for one and
   miscopying IDs, so the prompt was tightened (`v3-2026-10-21b`) and retry messages now name
   the bad ID.
6. **Main experiment:** 4 arms × 10 repeats (results below).
7. **`44fedf6` Merged your PET-MAD pilot** (`8f97726`). No file overlap.
8. **`11aa655` Fixes after the main run.** The runner's output cap defaults to 4096 tokens and
   is recorded, after upfront truncation at 2048. The analysis uses 95% Wilson intervals and
   can combine experiment folders, so a rerun arm replaces the original.

## Main experiment

Settings: `claude-haiku-5-5` (direct Anthropic), temperature 1.0, prompt `v3-2026-10-21b`,
budget 10, seeds 0–9 (same candidate order across arms within a repeat), 10 runs per arm.
Output cap 2048 tokens for random, sequential and iterative; upfront was rerun at 4096 (see
below). About 240 Haiku calls including the rerun, ~1.0M input and ~0.23M output tokens.

| Arm | Acceptable found by k = 10 | Best bin (LiNbF₆) found by k = 10 |
|---|---|---|
| Iterative (sees queried results) | **7/10** | **3/10** |
| Upfront (one shortlist, rerun) | 2/10 | 0/10 |
| Random | 2/10 | 1/10 |
| Sequential (no results) | 1/10 | 0/10 |
| Exact random | 36.3% | 20% |

- **Key contrast**, iterative against sequential: 7/10 against 1/10, two-sided Fisher exact
  p = 0.02. The iterative curve rises only after about 5 evaluations; the gain comes from
  revising after the first, prior-driven choices fail.
- **Upfront rerun:** with the 2048 cap, a 10-candidate shortlist (~2000 output tokens) was
  truncated twice and one run failed. Rerun at 4096 with the same seeds and prompt: no failures.
  The original upfront runs are kept in `runs/`, not deleted.
- **Example trace for the slides,** iterative repeat 7: Li₃PO₄ and LiF score badly (bins
  16, 15) → Haiku cites the products, switches to chlorides (Li₂MgCl₄, bin 9) → bromide, borate
  and silicate do worse; it notes no chlorides remain → hard-to-reduce mixed fluoride LiCaAlF₆
  (bin 2, acceptable) → refines to Li₂SiF₆ (bin 4). The explanations are Haiku's own
  interpretation; nobody has checked whether its chemistry is right.

## Something you should look at: acceptance cuts through bin 2

Bin 2 is [0.040, 0.060) eV per non-Li atom. LiCaAlF₆ (0.048) is acceptable; the three
LiZr₂(PO₄)₃ polymorphs (0.056, self-decomposition 0.009–0.019) are not. They tie in
`ranking_key` but differ in `acceptable`. LiZr₂(PO₄)₃ is Haiku's main prior pick: it was the
best result in 8 of the 10 upfront runs.

**This sensitivity check was chosen after seeing the results, and I'm not proposing to change
the frozen objective.** With "reached bin ≤ 2" as the target (M = 5, exact random by k = 10:
68.9%):

| Arm | Reached bin ≤ 2 |
|---|---|
| Upfront | 10/10 |
| Iterative | 8/10 |
| Random | 5/10 |
| Sequential | 1/10 |

So under the frozen criterion the model's prior looks weak. Under a looser one, the prior
alone does very well, because it already knows LiZr₂(PO₄)₃ is a good coating. Iterative against
sequential still holds either way. Sequential choosing one candidate per turn without results
avoids LiZr₂(PO₄)₃, unlike upfront, which is odd and worth looking into.

## Questions

1. **Threshold within a bin:** was it intended that 0.050 falls inside bin 2? I'd keep 0.050
   as the primary, frozen criterion and report bin ≤ 2 only as a labelled sensitivity check.
   Do you agree, or does the evaluator side want to say something about it?
2. **Run data:** `runs/` is git-ignored. Should I commit the two experiment folders (~4 MB,
   including prompts and responses) under something like `data/experiments/`, so you can inspect
   and reproduce the figures?
3. **Shuffled-feedback control** (about 100 more calls): run it now? It tests whether the
   iterative gain depends on the right result being tied to the right candidate, or only on
   seeing some results at all.
4. **MLIP follow-up:** your predeclared selection should stay as it is. Does it already cover
   LiNbF₆, LiCaAlF₆ and a LiZr₂(PO₄)₃ polymorph? If not, I'm only noting it; it shouldn't be
   changed to fit these results.
5. **Merging to `main`:** when do we both review the scientific scope? From my side, the
   integrated tests pass.
