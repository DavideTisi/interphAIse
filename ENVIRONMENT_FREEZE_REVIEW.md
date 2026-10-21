# Environment data freeze and experiment review

21 October 2026, `davide`. Reviewed Adem's `fc6a54c` and the protocol on
`work/agent-experiments`. **Data are frozen; Davide approved only the approximately
30-call smoke batch in this chat. Production remains on hold pending cost review.**
This review does not sign for either human collaborator or launch an experiment.

## Answers to the four protocol decisions

1. **Seeds 200–229.** Use the same set across arms and environments, with a fresh
   history for every run. These seeds control candidate order and local shuffling,
   not deterministic Anthropic sampling. Do not imply pairing with the original
   100–129 cohort.
2. **Holm correction over all six predeclared contrasts.** Keep iterative versus
   sequential and iterative versus shuffled in each environment, with exact
   two-sided paired McNemar tests and family-wise alpha 0.05. Report paired counts,
   effect direction, success-rate differences and raw/adjusted p-values. A
   significant loss is not evidence of improvement. Keep LLZO scientifically
   prominent without promoting it to the only primary test after reviewing the
   landscapes. No pooled significance test across environments.
3. **Shuffled in all three environments.** Preserve one experimental design and
   the existing control definition/limitations. Chloride remains a declared
   near-ceiling condition. Keep upfront and exact random comparisons, the
   post-hoc fluoride-first baseline and the deferred IDs-only decision.
4. **Davide approved the smoke batch only**, explicitly selecting “Smoke batch
   only; review measured cost before production” in this chat on 21 October.
   The proposed production is
   2,790 calls before retries, estimated 25M input and 2.4M output tokens. This
   is not a price quote or a hard cap. Recommend approving the approximately
   30-call smoke batch first, measuring usage/retries, then confirming production
   spending. Adem owns those live calls; no paid call was made in this review.

Keep the unchanged v3 objective, 30 repeats per arm/environment, budget 10,
Haiku 5.5 on direct Anthropic, temperature 1.0 and 4096 output tokens. All planned
runs stay in the denominator; technical reruns require recorded reasons. Keep
the original cohort separate. Thirty runs may miss modest effects; failure to
reject is not equivalence, especially near the chloride ceiling.

Retain the primary outcome: acceptable found by query 10. Secondary plots should
include first-success curves, best-bin success and **bin regret** relative to
each environment's own best bin. Runs without an eligible candidate have no
finite regret; do not invent one. The first-success index capped at 11 for
failures is a restricted summary, not an estimate of eventual discovery time.
Fluoride-pick trajectories describe behavior; rationales alone do not establish
chemical reasoning. This study tests within-environment feedback use, not
cross-environment transfer of learned experience.

## Immutable data snapshot

New copies are under `data/benchmarks/environment_v1/`. The original exploratory
tables and manifest remain untouched. Every scientific field, including all
423 rows, failure cases, diagnostics, endpoints and objective version, is equal
to its source. Only freeze metadata, status and the table hash change.

| Environment | Frozen semantic SHA-256 |
|---|---|
| Li6PS5Cl | `f70342c9aae0bd0e95f588bfb8c2f956815b3cf336c24e866119f7ab7f45f510` |
| Li3InCl6 | `a95dc6fb78a0f295784ca004f77fc02a04005fe106f7fa35296cc51a424117e2` |
| Ordered tetragonal LLZO | `9bdef5811bafc0b24f6ae55140f74f0be592a0f4367ca253310e0544ebb8e060` |

The [freeze manifest](data/benchmarks/environment_v1/manifest.json) records original
semantic/file hashes, new file hashes, pool/objective/dataset hashes, timestamp
and freezer source hash. The pool remains the same 141 pinned structures in
`data/exploration/environment_expansion_v1/pool.json`.

`scripts/freeze_environment_tables.py` validates all three tables together and
refuses missing/duplicate candidate rows, mixed objectives or datasets, hash
mismatches, partial environment sets and output overwrite. It never changes the
source tables or the scientific objective. Nine focused tests cover real-data
preservation and refusal cases. The frozen copies load without `--allow-draft`.

## Integration and reproducibility

The unmodified agent branch plus Claude's committed contact changes passes
124 tests in an isolated checkout using the existing `.venv`. With this review's
freezer and analysis guard it passes **136 tests**. This is a temporary integration
check; neither real branch was merged into the other or into `main`.

One protocol promise was not yet enforced: draft runs could enter
`analyse_discovery_experiment.py`. It now rejects non-synthetic runs marked
`allow_draft`, unfrozen manifest status, or an actually unfrozen benchmark even
if the manifest flag is missing. Historical manifests still work when their
hash-verified table is frozen. Three regression tests cover the gap. Merge this
small change while preserving Adem's best-bin panel and existing analysis tests.

Both dependency files now pin **pymatgen 2026.9.24 and pymatgen-core 2026.10.16**,
the versions used for the current passing suite and frozen evaluator. No package
was installed or changed in the shared environment. Adem should use a fresh
environment and rerun the suite before release. His reported 2026.4.16 failures
were not reproduced here; the pin establishes a supported setup, not an upstream
root-cause diagnosis. Preserve matcher behavior and archived geometry rather
than changing tolerances merely to make old-version tests pass.

An independent offline replay of 100 random runs per environment (seeds 0–99)
reproduces Adem's 25/98/72 successes and fluoride-first first successes at
queries 3/1/40. Four scripted arms per environment exercise full ten-query runs:
93 generated prompts contain none of the checked internal diagnostic fields
and show the correct electrolyte. These are workflow checks, not LLM results.
The numerical record and tested code hashes are in
[environment_freeze_review_20261021.json](data/reviews/environment_freeze_review_20261021.json).
Concurrent later Claude thickness edits are outside this tested snapshot.

## Smoke test and remaining steps

Under the smoke-only spending approval, preserve about 30 calls while exercising the complete
upfront shortlist: **per environment, one upfront run at budget 10, and one run
of each sequential/iterative/shuffled arm at budget 3**, all at seed 999. This
costs 1 + 3×3 = 10 calls per environment before retries. Keep both smoke batches
outside every scientific result. Measure input/output usage, malformed retries,
truncation and endpoint visibility; three-turn histories do not measure the
largest ten-turn prompt, so extrapolate conservatively.

All smoke/production invocations must name the pool and frozen table explicitly,
and omit `--allow-draft`. Production must explicitly include all five arms:
`--arms random upfront sequential iterative shuffled --repeats 30 --start-seed 200
--budget 10 --temperature 1.0 --max-tokens 4096 --workers 3`.

Adem should update ENVIRONMENT_PROTOCOL.md with these paths/hashes, settings and
smoke amendment, verify the merged runner against the frozen copies, and record
the exact production code commit. Any prompt/code change prompted by smoke
findings must be recorded and the protocol finalized before production. Obtain
the collaborators' protocol sign-off and review actual smoke usage before asking
Davide to authorize production; the data freeze and smoke approval do not permit
the full production batch. Continue Claude's PET-MAD thickness work
independently.
