# Development log

This is the chronological record of completed work, evidence and remaining tasks.
Read the latest checkpoint first, then the linked handoff for implementation detail.
The scientific overview is in [REPORT.md](REPORT.md); the experimental design is
in [DISCOVERY_IMPLEMENTATION_PLAN.md](DISCOVERY_IMPLEMENTATION_PLAN.md).
Never treat a planned feature as implemented or a software test as scientific validation.

## 2026-10-21 — Draft evaluator and Materials Project pool

**Branch:** `davide`, based on merged `main`.
**Implementation commit:** `23a9ea4` — `Add draft pinned-entry evaluator and reproducible 50-material pool`.
This entry retrospectively records the immediately preceding development session.
The commit was made locally and was not pushed during that session.

### Purpose and decisions

Prepare Davide's computational side of the discovery experiment while keeping
Adem's search code separate. The original evaluator could overlook decomposition
of a coating by itself, accepted no explicit insulation gate, and used exact
energy ordering that left adhesion almost no opportunity to affect ranking.

The new evaluator uses pinned reactant energies and a single normalization,
eV per non-Li atom, at the imposed lithium chemical potential. Fixed bins preserve
transitive ties and allow adhesion to distinguish candidates within a bin. These
choices and numerical thresholds are still a draft requiring full-pool diagnostics.

### Changes

- Added `interphaise/discovery_evaluator.py`: coating self-decomposition, contact
  reactions including endpoint decomposition, explicit insulation checks, fixed
  energy bins, optional adhesion ranking and entry provenance. Unknown gaps cannot
  pass. Pure-Li endpoints and missing pinned entries are rejected explicitly.
- Added `scripts/build_candidate_pool.py`: Materials Project summary retrieval,
  cached offline replay, recorded filters, seeded family sampling and pool hashing.
- Created `data/pools/mp_candidates_v2.json`: 50 candidates, ten each from halides,
  other oxides, phosphates, borates and silicates. Of 3,770 downloaded unique
  records, 141 passed local filters. All 50 selected gaps are known; 48 meet the
  proposed 2 eV gate. Polymorphs remain separate material IDs.
- Added evaluator and pool tests. Updated `REPORT.md`,
  `DISCOVERY_IMPLEMENTATION_PLAN.md` and `WORK_DIVISION.md`.
- Wrote [EVALUATOR_HANDOFF.md](EVALUATOR_HANDOFF.md) with the callable interface,
  scientific assumptions, reproducibility instructions and integration tasks.

### Verification and external calls

- Full offline suite: **62 passed**, with existing ASE/spglib deprecation warnings.
  Command: `MPLCONFIGDIR=/private/tmp/interphaise-mpl .venv/bin/python -m pytest -q`.
- Analytic tests cover self-oxidation, an interior mixing reaction, a metastable
  pinned polymorph, formula-unit scaling, insulation, missing entries and bin ties.
- A real Materials Project retrieval succeeded using the ignored local credential.
  No live LLM call or new MLIP calculation was performed in this session.
- Offline pool replay reproduced the exact SHA-256:
  `e850b4f1d77e12e895d6d5446ab80f3210184842b6c91ecf88577158c34a8758`.
  The selected pool is tracked; raw retrieval data are local and ignored at
  `runs/mp_pool_snapshot.json`. A different machine needs that snapshot to repeat
  the exact sampling from the original retrieval, or must create a new pool version.
- `git diff --check` passed; `.env` remained ignored. Working tree was clean after
  the implementation commit.

### Unfinished work and scientific limitations

The legacy discovery CLI still uses the old evaluator. No complete v2 benchmark
or strategy comparison has been run. Summary hull values are only pool prefilters;
they are not a compatible set of thermodynamic entries for phase diagrams.

Electrode/electrolyte decomposition may impose a common penalty floor and obscure
coating differences. Some database candidates, such as LiO8, need inspection.
The pool and objective are not yet frozen for experiments. The shortlist says
nothing conclusive about Li transport, synthesis or experimental battery performance.

### Next steps

1. Pin the cathode and electrolyte IDs and retrieve consistent, corrected thermo
   entries for each candidate's combined chemical system, recording energy provenance.
2. Evaluate the entire pool; inspect failures, shared penalty floors and genuine
   ties before freezing the objective and candidate set.
3. Integrate the candidate-ID evaluator with Adem's runner, preserving the boundary
   that prevents the LLM from seeing unqueried results.
4. Run the agreed search controls only after integration; perform separate PET-MAD
   follow-up on the shortlist and a baseline comparator.

## 2026-10-21 — Persistent reporting requirement

**Branch:** `davide`.
**User request:** Always write a report so a human or another LLM can follow the work.

Added this log and a standing reporting requirement in `AGENTS.md`. Future substantive
sessions must append their purpose, changes, evidence, limitations and next steps.
Scientific/status changes must also update `REPORT.md`. Earlier entries should be
preserved, with corrections recorded explicitly.

Verification: documentation consistency review and `git diff --check`. No code or
scientific criteria changed, so the test suite was not rerun for this documentation
update. No external API, LLM or MLIP calls were made. Next implementation work remains
the thermo-data retrieval and validation described above.

## 2026-10-21 — Thermodynamic validation and frozen v3.0 handoff

**Branch:** `davide`; session started from `3cf9192`.
**Purpose:** retrieve compatible thermodynamic data, validate every candidate and
prepare a reproducible evaluator/query contract for Adem.

### Scientific finding and user decision

The original v2 absolute-contact objective produced 41 tied best candidates out of
50: electrolyte self-decomposition at 4 V set a common penalty floor of 1.439628
eV/non-Li atom. Random search would reach this best bin with 99.5714% probability
after three queries. We retained the full diagnostic instead of hiding the result.

We then tested an explicitly versioned alternative: additional reaction on mixing
separately equilibrated endpoints, plus the coating's own self-decomposition and
insulation gate. The user selected **“Use the additional-contact-reaction objective”**
in response to the scientific-choice question. That criterion is now frozen as
**v3.0**, before any LLM strategy runs. It measures coating compatibility, not
absolute stability of the stack. No thresholds or candidates were changed to
improve LLM results; no such results have been collected.

V3 has 24 occupied eligible bins, one best-bin candidate and two criterion passes.
The full population remains 50: 49 have calculated outcomes, one has a missing
GGA/GGA+U entry, and two of the calculated candidates fail insulation. Missing data
and gate failures remain in query-budget accounting. Full details and scientific
limitations are in [BENCHMARK_VALIDATION.md](BENCHMARK_VALIDATION.md).

### Implementation and artifacts

- Installed official mp-api 0.47.0 in the project virtual environment. Declared
  `mp-api>=0.47.0` in the MP extra and SciPy as a direct dependency.
- Added `interphaise/tools/thermo_dataset.py` and `scripts/fetch_thermo_dataset.py`:
  corrected GGA/GGA+U retrieval, subsystem deduplication, cached resumable batches,
  database/version provenance, typed-ID resolution, structure matching and hashes.
- Retrieved 4,887 entries across 949 chemical subsystems from MP database 2026.09.28.
  Pinned ordered LiCoO2 (`mp-22526`) and Li6PS5Cl (`mp-985592`) at 4 V.
- Added an exact linear-programming solver to `discovery_evaluator.py`, preserving
  the Qhull backend for independent checks. Added explicit pinned/equilibrated
  reference conventions and endpoint-instability diagnostics.
- Added exhaustive evaluation, independent solver-check, freeze and diagnostic-plot
  scripts. The freeze operation changes version/status metadata, not numerical outcomes.
- Tracked `data/thermo/mp_gga_v2.json.gz` (about 7.1 MB), complete frozen outcomes in
  `data/benchmarks/coating_v3.json`, rejected v2 diagnostic, solver cross-check,
  validation plot and a planned MLIP subset. These allow offline replay without keys.
- Added `interphaise/benchmark.py` with a budgeted `BenchmarkQueries` interface and
  `scripts/query_benchmark.py` for an offline integration smoke run. Public prompt
  metadata contain only task definition and candidate ID/formula/family; observed
  results are returned only when queried. This is an application information boundary,
  not an OS security sandbox. Copies prevent accidental mutation of cached results.
- Updated README, REPORT, implementation plan and work division. Replaced the earlier
  handoff with the current frozen-v3 contract. Adem's existing agent code was not edited.

### Errors encountered and corrected

The first bulk download failed because provider metadata used Element objects as
JSON dictionary keys. Serialization now normalizes metadata keys and IDs and checks
that corrected energies are unchanged. Completed downloads are cached for resumption.

The first attempted freeze detected a hash mismatch: integer histogram keys sort
differently before and after JSON serialization. Canonical hashing now normalizes
JSON keys first. Both diagnostic benchmarks were regenerated, and a regression test
checks round-trip integrity. Earlier ignored files named `benchmark_v*_draft.json`
are superseded by the canonical artifacts; they are not valid experiment inputs.

The alphabetical pool IDs are aliases of numeric MP IDs, not different materials.
Canonicalization uses the official emmet type. We did not replace polymorphs by formula.
LiMgCl3 (`mp-aaahikjt`, `mp-3346453`) lacks an entry in the selected energy scheme;
that outcome is explicitly retained as failed.

### Verification actually performed

- **82 tests passed**, including solver equivalence, energy-preserving serialization,
  ID aliases, hash round trips, freezing, exact tied-optimum random probabilities,
  query leakage checks, mutation protection and failed/repeated-query budget charging.
  Command: `MPLCONFIGDIR=/private/tmp/interphaise-mpl .venv/bin/python -m pytest -q`.
  Existing ASE/spglib deprecation warnings remain.
- Eight comparisons on real LiF/LiNbF6 contacts, both reference conventions and both
  endpoints: maximum LP/Qhull difference 1.78e-15 eV/non-Li atom.
- Recomputed the full alternative objective from the tracked compressed dataset:
  every candidate status and numerical outcome matched exactly.
- Completed a three-query random smoke run through the frozen query interface.
  This smoke run is not used as an empirical baseline; exact random curves are stored.
- Generated and visually inspected `data/benchmarks/validation.png`.
- Live Materials Project calls were made. **No live LLM call and no new MLIP run**
  occurred. Credentials remained local and ignored.

Frozen hashes (canonical JSON, excluding each artifact's own hash field):

- Pool: `e850b4f1d77e12e895d6d5446ab80f3210184842b6c91ecf88577158c34a8758`
- Thermodynamic dataset: `e9fa1add41e7a5a5b3f42522e59f1c8915c9ad6fd428d0289e80069918cb48e4`
- Objective v3.0: `a194076f6e3f671ed09e49baf3b65dccef436adcee4b9094d45577752cab6c0d`
- Benchmark: `d2718c20f0ca8c3cc25d2378011bc68736ad71a502d657312bfff1da15a4ecfa`

### Remaining work and next ownership

Adem should connect his candidate-ID agent to `BenchmarkQueries`, use the v3 prompt
and ranking convention, and run the agreed repeated controls with recorded sampling
settings. The old `scripts/run_discovery.py` still uses the old objective; it is not
a v3 experiment runner. Do not send exhaustive results or this report to the proposer.

Davide should implement/validate a common PET-MAD interface protocol and per-candidate
compute accounting. The planned three distinct leading formulas are LiNbF6, LiCaAlF6
and LiZr2(PO4)3. The uniform random comparator (seed 2026) happens to be LiCaAlF6;
retain that overlap rather than resampling to make the baseline worse. No adhesion
or convergence claim is available yet.

The low-level evaluator retains historical defaults; callers recomputing v3 must
explicitly use `Objective(version="v3.0", contact_reference="equilibrated")` or the
provided replay script. Search agents should use the frozen query interface.

Final pre-commit checks: staged diff whitespace check passed; a local scan of every
staged file (including decompressed thermodynamic data) found none of the configured
API key values. This checkpoint is committed locally on `davide`, not pushed.
