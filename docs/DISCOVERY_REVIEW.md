# Review of the iterative coating discovery branch

> Review of commit `e1b50e7` on branch `codex/iterative-coating-discovery`
> (`interphaise/discovery.py`, `scripts/run_discovery.py`, `tests/test_discovery.py`,
> `DISCOVERY_REPORT.md`). Written 2026-10-20 for the team and for any LLM session that continues
> the work. Read together with `DISCOVERY_REPORT.md` (scope) and `REPORT.md` (project).

## Verdict

**The direction is right and should become the headline of the project.** It turns "the LLM makes
modelling calls" into a measurable experiment: does an LLM that sees computed feedback find good
coatings in fewer evaluations than an upfront shortlist or random search, under a fixed evaluator it
cannot influence? The software is careful (failures charged to the budget, bounded proposal retries,
no silent fallback, checkpointing) and all 31 offline tests pass.

**As built, it cannot yet support a claim.** Three problems would make any result unconvincing: the
pool is too small to separate strategies, the objective has a large tie at the top and ignores two
properties a coating must have, and the expensive MLIP stage almost never changes the ranking. All
are fixable before the first real run, mostly in a few hours.

## What to keep

- Proposer and evaluator separated; no LLM label, confidence or agreement enters the score. This also
  removes the circularity of the screen, where a coating's tier comes from the deciding arm's own call.
- Matched budgets, failures consume budget, invalid proposals logged separately.
- The upfront arm. It separates the LLM's prior knowledge from its use of feedback.
- `DISCOVERY_REPORT.md`'s explicit limits (approximate evaluator, no experimental claim).

## Objections, most serious first

### O1 — The pool is too small to measure anything

Six coatings with a budget of three: random search contains any given coating with probability 1/2,
and the best one is found by chance half the time. No strategy can be distinguished from random.
`DISCOVERY_REPORT.md` notes this; it is the first thing to fix, not a later improvement.

**Fix.** Build a pool of 40–100 candidates *before* any LLM run and freeze it (file with MP ids and a
hash, committed). Source: Materials Project Li-containing compounds in the classes coatings come from
(oxides, phosphates, borates, silicates, halides, polyanion compounds), filtered to ordered structures
within ~25 meV/atom of the hull and ≤ ~40 atoms per primitive cell. Add the six current coatings and
the Xiao et al. (Joule 2019) top picks. Store the pool as data, not in `config.py`.

### O2 — The objective has a large tie at the top

With `use_hull_energy=True`, any pair that does not react returns a minimum reaction energy of
exactly 0. Every coating stable against both contacts ties for first place, and in thermodynamic mode
adhesion is absent, so the tie is broken by evaluation order. "Best so far" then only records whether
*any* non-reactive coating has been found.

**Fix.** Add a continuous secondary term that ranks the non-reactive coatings (O3 gives two natural
ones), and fix a tolerance for "equally reactive" (e.g. 10–20 meV/atom) before running.

### O3 — The objective ignores two things a buffer coating must do

1. **The coating's own stability at the cathode potential.** `GrandPotentialInterfacialReactivity`
   is used with the default `include_no_mixing_energy=False`, so the energy of a reactant decomposing
   on its own in the open-Li ensemble is not counted. A coating that oxidises by itself at 4 V can
   still score 0. **Fix:** add the coating's decomposition energy in the grand-potential phase diagram
   at μ_Li(4 V), or its electrochemical stability window margin, as an explicit term (Xiao et al.
   screen on exactly this).
2. **Electronic insulation.** A buffer only works if it blocks electrons; a metallic or narrow-gap
   coating passes the current objective. **Fix:** a validity gate on the coating's MP band gap
   (e.g. > 2 eV; `get_band_gap` already exists).

Li-ion transport stays out of scope (`DISCOVERY_REPORT.md`), but with these two terms the winner can
no longer simply be the most inert compound in the pool. State the remaining gap on the slides.

### O4 — In full mode the expensive part does not change the ranking

The order is exact lexicographic: adhesion decides only when two reaction energies are equal to the
last digit, which almost never happens. Full mode therefore ranks like thermodynamic mode and adds
only failure cases, at a cost of minutes of GPU per candidate. Conversely, thermodynamic mode costs
seconds for the whole pool, so search is unnecessary there.

**Fix — pick one design and write it down before running:**

- **A (recommended for two days).** Run the search experiment on the improved thermodynamic objective
  (O2, O3). The whole pool is cheap, so the true optimum is known and every strategy can be scored by
  regret and by evaluations-to-top-k. Then run full mode only on the top 3–5 candidates to give each
  an atomistic interface and adhesion. Claim: "the LLM reaches the optimum in fewer evaluations on a
  benchmark with known ground truth"; the cost argument transfers to expensive evaluators.
- **B.** Make the objective genuinely expensive: bin reaction energies (O2) so adhesion decides within
  a bin, and search in full mode. Honest, but few repeats fit in two days.

### O5 — Prior knowledge vs reasoning

The LLM sees formulas it knows, and coating screens with nearly this objective are in the literature
(Xiao et al. 2019). Good iterative performance may be recall. **Fix:**

- keep the upfront arm (prior only) and report iterative minus upfront as the value of feedback;
- add a **shuffled-feedback** control: the LLM sees real formulas but outcomes permuted across
  evaluated candidates. If performance does not drop, it is not using the results;
- if time allows, repeat on a less-studied system (another cathode or voltage) where recall helps less.

### O6 — Baselines and statistics

- **Random:** with a known pool (design A), compute the expected best-of-k curve exactly
  (order statistics) or average ≥ 1000 seeds; one seed per run is not a baseline.
- **Fixed:** the order in `config.py` was written by us knowing the literature (LiNbO₃ first). Either
  drop it or have an expert write an order before seeing any results, and log who and when.
- **LLM arms:** ≥ 10 runs each, temperature and exact model version recorded (`make_llm` currently
  leaves temperature unset). Report median and interquartile range of the best-so-far curves.

### O7 — Objective wording in the prompt is ambiguous

`OBJECTIVE = "... maximise worst-contact reaction energy ..."`. Reaction energies are ≤ 0, so
"maximise" means "closer to zero". A model can easily read it as "most negative". **Fix:** state
signs and units explicitly in the prompt ("reaction energies are ≤ 0 eV/atom; values closer to 0 are
better"), and test that the LLM's stated hypotheses use the right direction.

### O8 — Discovery evaluations contaminate the arm comparison

In full mode `CoatingEvaluator` calls `run_screen(..., RulesPolicy())` for one coating at a time,
writing `ranking.json` files under `runs/<...>/evaluations/`. `scripts/compare_arms.py` and
`benchmark/score_agreement.py` scan `runs/` recursively and take the latest `rules` ranking, which can
be a one-coating discovery evaluation. **Fix:** mark these rankings (e.g. `"purpose": "discovery_eval"`)
and skip them, or write discovery evaluations outside `runs/`.

### O9 — Compute accounting

`elapsed_seconds` is recorded, but not relaxations or single points per candidate (the energy
counters are process-global). **Fix:** record the counter deltas per evaluation in `history`, so a
compute-saving claim (design B) has numbers behind it.

### O10 — Two stories in one repository

The screen with three decision arms and the discovery loop answer different questions, and
`REPORT.md`, the shared report and the README ("new branch") do not yet describe how they relate.
For a two-day pitch, one headline is stronger.

**Suggestion.** Headline = discovery (best objective vs evaluations; iterative vs upfront vs
shuffled vs random). Supporting = the evaluator: how each candidate is modelled, and where the LLM's
modelling calls differ from the rules (the arm comparison), as one slide.

## Suggested order of work (Wednesday morning first)

| # | Change | Effort | Addresses |
|---|---|---|---|
| 1 | Freeze a 40–100 candidate pool from MP (with ids and hash) | 1–2 h | O1 |
| 2 | Objective v2: coating self-stability at μ_Li(V), band-gap gate, tolerance bins, written down in `DISCOVERY_REPORT.md` before any run | 1–2 h | O2, O3, O4 |
| 3 | Unambiguous objective text in the prompt | 15 min | O7 |
| 4 | Exhaustive thermodynamic evaluation of the pool → ground truth, exact random baseline | 30 min | O4, O6 |
| 5 | Shuffled-feedback strategy; temperature and model version recorded | 1 h | O5, O6 |
| 6 | ≥ 10 runs per LLM arm; regret and evaluations-to-top-k plots | runs + 1 h | O6 |
| 7 | Full mode on the top 3–5 candidates only | GPU hours | O4 |
| 8 | Mark discovery rankings; skip them in `compare_arms.py` and `score_agreement.py`; per-evaluation counters | 30 min | O8, O9 |
| 9 | Merge the branch; update `REPORT.md`, README and the shared report with one headline | 1 h | O10 |

## Open questions for the team

- Design A or B (O4)?
- Who, if anyone, writes the expert order for the fixed baseline before results are seen?
- Which second system (if any) for the recall check (O5)?
