# Environment study: pre-run protocol (DRAFT, not frozen)

21 October 2026. Drafted by Adem for joint review with Davide. Nothing here is frozen until
both sign off below. **No production LLM calls before then.** Builds on `ENVIRONMENT_EXPANSION.md`,
`EXPANSION_PROGRESS.md` and `SYNC_ADEM_5.md`.

## 1. Question

Does correctly attributed calculation feedback help Haiku choose compatible coatings when the
electrolyte changes, including where the shortcut that worked before (fluorides, for the sulfide)
fails? The LLM replaces the scientist deciding which chemical assumption to revise after a contact
calculation, and which candidate to test next. This is an exploratory study informed by v3, not a
blind replication. The sulfide environment contains all 50 original candidates and both original
winners.

**Not tested here:** transfer of experience between environments. Each run starts with a fresh
history in a single environment. "Adaptation" means revising the model's prior within a run,
given the stated environment and the results it queries.

## 2. Frozen inputs (to be confirmed at freeze)

| Item | Value |
|---|---|
| Pool (141 structures, 100 formulas) | `data/exploration/environment_expansion_v1/pool.json`, sha256 `833d5a68…e71d` |
| Objective (unchanged v3) | sha256 `a194076f…6c0d`: 2 eV gap gate, 0.020 bins, 0.050 acceptance |
| Cathode / voltage | LiCoO₂ (mp-22526), 4.0 V, imposed Li potential |
| Li₆PS₅Cl table | `…/evaluation/lco_lpscl_4v.json`, sha256 `65f5991a…e0a2` |
| Li₃InCl₆ table | `…/evaluation/lco_lic_4v.json`, sha256 `a5d4eb20…4464` |
| LLZO (ordered tetragonal) table | `…/evaluation/lco_llzo_4v.json`, sha256 `d6ce854b…0d54` |

The tables are currently `exploratory-exhaustive-not-frozen`. **Davide freezes them** (status
`frozen`, hashes recorded here) before production. `BenchmarkQueries` refuses unfrozen tables
unless `--allow-draft` is passed. The runner records `allow_draft` and `benchmark_status` in
`experiment.json`, and runs on drafts are excluded from every result. Endpoints, pool, objective
and thresholds do not change after freeze. Changing any of them makes a separately labelled
study.

## 3. Arms and settings

| Setting | Value |
|---|---|
| Arms | random, upfront, sequential, iterative, shuffled (IDs-only deferred) |
| Model | `claude-haiku-5-5`, direct Anthropic only |
| Temperature / output cap | 1.0 / 4096 tokens |
| Prompt | `v3-2026-10-21c-charged-ids`, unchanged. The environment reaches the model only through the public task: endpoints, voltage, objective and instructions. |
| Budget | 10 queries per run; invalid, repeated and failed queries are charged |
| Repeats | 30 per arm per environment |
| Seeds | 200–229, the same set in every environment and arm. They pair candidate order across arms within an environment and are disjoint from v3's 100–129. |
| Shuffled definition | As archived in `data/experiments/shuffled_v3_20261021_s100/README.md` (inside-out Fisher–Yates over real first queries; charged invalid IDs stay in place), with the same disclosed limitations |
| Runs | One `run_discovery_experiment.py` invocation per environment, `--workers 3`, fresh history per run |

All declared runs are executed and reported regardless of outcome. Failed runs stay in the
denominators. There is no early stopping, no extension and no rerun of an arm because of its
results. Any replacement of a crashed run needs a recorded technical reason and
`--replace-duplicates`, listed in the report.

## 4. Endpoints and analysis

**Primary endpoint** (per environment, as in v3): acceptable candidate found within 10 queries.

**Primary contrasts** (per environment, paired by seed, exact two-sided McNemar):
1. iterative against sequential (feedback against no feedback, same interaction);
2. iterative against shuffled (correctly attributed against corrupted feedback).

That gives 3 environments × 2 contrasts = 6 tests, with a **Holm correction at family-wise
α = 0.05**. Unadjusted p-values and effect sizes (difference in success rate with paired counts)
are reported alongside.

**Expected ceiling:** in Li₃InCl₆, random already reaches 99.4% acceptance by query 10 (55/141
acceptable), so a null primary contrast there is uninformative, not evidence against feedback.
This is declared now so it can't be argued after the results.

**Secondary endpoints** (per environment, descriptive, with 95% Wilson or interquartile
intervals):
- P(best bin found) by query 10;
- query index of the first acceptable candidate (runs with none count as 11; mean and median
  per arm). This stays informative near the ceiling;
- median best bin found so far, k = 1..10, against the exact random median;
- fluorine fraction of each arm's picks per environment, and per run whether it moves away from
  fluorides in LLZO. This describes whether the prior is being revised.

**Aggregate:** no pooled significance test across environments. One descriptive number only:
the equal-weight mean across the three environments of the per-environment difference in
acceptance rate (iterative minus sequential, and iterative minus shuffled).

**References on every plot:** the exact random curves and the post-hoc fluoride-first rule. The
fluoride-first rule is labelled as chosen after seeing v3.

**Must not be done:** pool runs with the v3 cohort; drop or reweight an environment after
seeing results; change thresholds; break best-bin ties by raw energy; report a draft-table run
as a result.

## 5. Sequence

1. **Freeze** (Davide): set the three tables to `frozen`, record the hashes above, and both sign
   this file.
2. **Smoke batch** (excluded from results): 1 repeat × 4 LLM arms × 3 environments, budget 3,
   seed 999, on the frozen tables. It checks prompt length, retries and the output cap with
   141 candidates. About 3 × (1 + 3 × 3) = 30 calls. If the prompt or code must change after
   the smoke batch, re-version the prompt and re-freeze this protocol before production.
3. **Production:** 3 environments × 5 arms × 30 runs. LLM calls before retries:
   3 × (30 upfront + 3 × 300) = **2,790**.
4. **Archive** each environment like the v3 batches: runs, manifest, summary, replay audit,
   file hashes, figures and README. Then analyse as section 4.

## 6. Resource estimate (not a price quote)

v3 iterative calls averaged 5,250 input and 852 output tokens. The 141-candidate list adds
about 7,200 characters per prompt, roughly 3,900 tokens at the observed 1.86 characters per
token, so about 9,000 input tokens per call. For 2,790 calls that's roughly **25M input and
2.4M output tokens**. Measure the real figures in the smoke batch before committing. With
`--workers 3`, v3 ran 300 calls in about 12 minutes, so production is roughly 2 hours of wall
time.

## 7. Open decisions for the freeze

1. Seeds 200–229, or reuse 100–129 for continuity? (Disjoint seeds are proposed to avoid
   implying a pairing with v3.)
2. Holm over 6 tests, or name LLZO iterative against sequential as the single primary test, the
   environment where the shortcut fails, with the rest secondary?
3. Include shuffled in all three environments (2,790 calls), or only LLZO and the sulfide
   (2,490)?
4. Is ~25M input tokens within the agreed budget?

## Sign-off

- [ ] Davide: tables frozen, hashes confirmed, protocol approved
- [ ] Adem: protocol approved, runner verified on frozen tables

## Already verified (offline, no LLM calls)

- The runner and query interface load all three environment tables, and the hashes verify.
  Unfrozen tables are refused without `--allow-draft`.
- Tests on all three real tables check that no internal-only field (`bin_regret`,
  `component_analysis`, endpoint-decomposition penalties, entries, timing) ever reaches a prompt,
  and that the electrolyte does.
- 100 offline random runs per environment match the exact curves within noise (acceptance by
  10: sulfide 25% against 25.7% exact, chloride 98% against 99.4%, LLZO 72% against 73.6%). The
  fluoride-first trajectories match `EXPANSION_PROGRESS.md`.
