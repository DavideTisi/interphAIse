# Environment study: frozen inputs and smoke-approved protocol

21 October 2026. Drafted by Adem and reviewed on Davide’s side through Codex.
The data and scientific design are frozen. Davide approved the smoke batch only.
**Production requires a separate approval after the measured-cost report.** Builds on `ENVIRONMENT_EXPANSION.md`,
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

## 2. Frozen inputs

| Item | Value |
|---|---|
| Pool (141 structures, 100 formulas) | `data/exploration/environment_expansion_v1/pool.json`, sha256 `833d5a68…e71d` |
| Objective (unchanged v3) | sha256 `a194076f…6c0d`: 2 eV gap gate, 0.020 bins, 0.050 acceptance |
| Cathode / voltage | LiCoO₂ (mp-22526), 4.0 V, imposed Li potential |
| Li₆PS₅Cl table | `data/benchmarks/environment_v1/lco_lpscl_4v.json`, sha256 `f70342c9aae0bd0e95f588bfb8c2f956815b3cf336c24e866119f7ab7f45f510` |
| Li₃InCl₆ table | `data/benchmarks/environment_v1/lco_lic_4v.json`, sha256 `a95dc6fb78a0f295784ca004f77fc02a04005fe106f7fa35296cc51a424117e2` |
| LLZO (ordered tetragonal) table | `data/benchmarks/environment_v1/lco_llzo_4v.json`, sha256 `9bdef5811bafc0b24f6ae55140f74f0be592a0f4367ca253310e0544ebb8e060` |

The new copies have status `frozen`; the exploratory originals remain unchanged.
Every result row and scientific field is identical to its source. Only status, freeze
metadata and table hash differ. The manifest in `data/benchmarks/environment_v1/`
records both original and frozen hashes. Use the new copies for smoke and production. `BenchmarkQueries` refuses unfrozen tables
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

1. **Freeze complete** (Davide/Codex): inputs and hashes above are verified. Adem confirms
   the runner on these copies and records the code commit before smoke.
2. **Smoke batch approved** (excluded from results): per environment, one upfront run at
   budget 10 and one sequential, iterative and shuffled run each at budget 3, seed 999.
   Use the frozen tables and omit `--allow-draft`. It checks prompt length, retries and the output cap with
   141 candidates. About 3 × (1 + 3 × 3) = 30 calls. If the prompt or code must change after
   the smoke batch, re-version the prompt and re-freeze this protocol before production.
3. **Production on hold:** after smoke, report measured usage and expected/conservative
   costs to Davide and wait for explicit approval. Planned scope: 3 environments × 5 arms × 30 runs. LLM calls before retries:
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

## 7. Recorded decisions

1. Seeds 200–229, disjoint from the original cohort.
2. Holm over all six planned comparisons.
3. Shuffled in all three environments.
4. Davide explicitly approved only the approximately 30-call smoke batch in this chat.
   Production remains on hold until its measured-cost review and further approval.

## Sign-off

- [x] Davide side, recorded by Codex on 21 October 2026: data hashes and scientific
  protocol reviewed; smoke spending approved by Davide’s explicit chat answer.
- [x] Adem, 21 October 2026: runner verified offline on the frozen copies (hashes match, no
  `--allow-draft`); smoke executed at commit `26beb73` as approved; measured usage and cost
  in `SYNC_DAVIDE_4.md`.
- [ ] Davide: approve production after the measured smoke cost report.

## Public-price cross-check and account billing

Anthropic’s public pricing page, checked on 21 October 2026, agrees with Adem’s
rates for Haiku 5.5 prompts up to 100k tokens: USD 0.10/M input, 0.50/M output,
0.01/M cache reads, 0.125/M five-minute writes and 0.20/M one-hour writes.
Thus 25M uncached input plus 2.4M output implies about USD 3.70 before retries,
additional features or account-specific adjustments. This is arithmetic on a
planning estimate, not a quote or billed cost. Source:
https://platform.claude.com/docs/en/about-claude/pricing

The API credential does not establish Console access or the account’s contract
terms. Billed cost and negotiated pricing remain unverified; the account owner
must confirm them. The smoke report should label usage-based list estimates
accordingly, include missing usage/retry records, and avoid double-counting
thinking tokens already included in output tokens. No production approval is
implied by the public-price check.

## Already verified (offline, no LLM calls)

- The runner and query interface load all three environment tables, and the hashes verify.
  Unfrozen tables are refused without `--allow-draft`.
- Tests on all three real tables check that no internal-only field (`bin_regret`,
  `component_analysis`, endpoint-decomposition penalties, entries, timing) ever reaches a prompt,
  and that the electrolyte does.
- 100 offline random runs per environment match the exact curves within noise (acceptance by
  10: sulfide 25% against 25.7% exact, chloride 98% against 99.4%, LLZO 72% against 73.6%). The
  fluoride-first trajectories match `EXPANSION_PROGRESS.md`.
