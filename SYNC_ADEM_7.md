# Environment study handoff to Adem

**Publication update:** ENVIRONMENT_PROTOCOL.md now contains the exact frozen
hashes and the Davide-side sign-off for the approved smoke batch. All result rows
are unchanged; status, freeze provenance and hashes change. Retrieve the frozen
copies from `data/benchmarks/environment_v1/`, not the preserved exploratory
source directory. The latest local suite passes 127 tests including Claude's
thickness implementation. Production approval remains explicitly unchecked.

21 October 2026. Reviewed `fc6a54c`; scientific settings below are recommended.
Davide explicitly approved the approximately 30-call smoke batch only in this
chat. Production is on hold until measured cost is reviewed. No paid calls were
made here; Adem owns the live smoke batch to avoid duplicate launches.

**What we want to test, and why.** We want to know whether calculation feedback
helps the LLM revise a chemical hypothesis and choose a better next coating,
beyond what it can propose from prior knowledge alone. This is where it replaces
human scientific intuition: interpreting a disappointing calculation, deciding
which assumption may be wrong, and choosing the next experiment. Deterministic
tools still calculate all properties. Our first benchmark favors fluorides;
the expanded sulfide model also favors them, whereas none of the acceptable LLZO
coatings contains fluorine. Changing the electrolyte therefore challenges that
shortcut. Chloride stays in the study as a declared easy condition. Each run
starts fresh: we test feedback-driven revision within an environment, not
transfer of learned experience between environments.

The intended production design is the five arms (random, upfront, sequential,
iterative and shuffled), 30 repeats per arm in each of the three environments,
budget 10. Use Haiku 5.5 through direct Anthropic, temperature 1.0 and max_tokens
4096. The main outcome is finding an acceptable coating within ten queries;
early-query and best-bin/regret curves remain important for the easy chloride
case. This full design is scientifically recommended, but its spending is not
yet approved.

**The three tables are frozen.** Use `data/benchmarks/environment_v1/lco_*.json`
and the unchanged `data/exploration/environment_expansion_v1/pool.json`.
[manifest.json](data/benchmarks/environment_v1/manifest.json) records all hashes.
Every scientific field and all 423 outcomes match the original exploratory
tables, which remain untouched. The new frozen tables load without an override.

Answers to section 7:

1. Seeds **200–229**, unchanged across arms/environments; fresh run histories.
2. **Holm over the six contrasts**, keeping LLZO prominent in the interpretation.
3. **Shuffled in all three environments**; chloride stays in the study with its
   near-ceiling expectation and early-query/bin-regret results.
4. **The 30-call smoke batch is approved**. Report measured input/output tokens,
   retries and projected full-run cost before asking Davide to approve production.
   This handoff does not authorize production spending.

Small smoke amendment: per environment, run upfront at **budget 10** and the
other three LLM arms at **budget 3**, seed 999. Still 30 calls before retries,
but this tests the full upfront shortlist at the actual output cap. Both batches
are excluded from results. Longer production histories still need a conservative
token estimate.

**Please check how expensive the full study would actually be before starting
it.** Verify the model identifier returned by the API and the rates that apply
to this collaborator account; do not infer a dollar price from the model name.
Using the approved smoke batch, send back:

1. Actual calls, input/output tokens, malformed-output retries, truncation and
   wall time, broken down by arm and environment. Include billed failed attempts
   and any cache-read/cache-write tokens separately.
2. The applicable input/output/cache prices, their source/date and currency,
   plus the smoke batch's measured or estimated monetary cost. Distinguish
   provider-billed cost from an estimate if billing data are unavailable.
3. Expected full-study cost and a conservative higher-cost estimate, by arm and
   environment and in total. The planning estimate is **2,790 production calls,
   about 25M input and 2.4M output tokens before retries**. Validate that against
   measured usage, allow for longer ten-turn histories, and state assumptions
   about retry rates and caching. Show smoke and production costs separately.
4. If the estimate is too high, recommend a cheaper declared design and its
   scientific trade-off before changing settings or dropping any arm/environment.

Keep the smoke batch separate from results. If it encounters repeated technical
failures, stop and report them rather than expanding the retry work. After the
smoke batch, **stop and send the cost report to Davide; wait for explicit
production approval**. The smoke approval does not authorize the 2,790-call run.

The temporary integration of your branch and Claude's contact commit passes
124 tests. With the data-freezing utility and the analysis guard added here,
**136 tests pass**. I found that analysis did not yet reject draft runs; the
guard now rejects draft metadata and unfrozen benchmark contents, with three
regression tests. Preserve your best-bin panel when bringing this change in.

I pinned `pymatgen==2026.9.24` and `pymatgen-core==2026.10.16` in both dependency
files, matching the passing environment. No local packages were changed; please
rerun in a fresh environment before the release. This does not diagnose the
older-version mismatch or change matcher tolerances.

Please update your protocol with the frozen hashes and these decisions, verify
the frozen runner, and record the eventual production code commit. Include all
five arms explicitly; the runner default still omits shuffled. Keep the cohorts
separate and retain every declared environment and run. This package is being
published on `davide`; no real branch merge has been performed here.

Claude's primary contacts and constraint bracket are complete; electrolyte
thickness is next. The physics work does not block this environment study.
Details and scientific caveats: [ENVIRONMENT_FREEZE_REVIEW.md](ENVIRONMENT_FREEZE_REVIEW.md).
