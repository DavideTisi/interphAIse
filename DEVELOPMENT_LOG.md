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

## 2026-10-21 — Review of Adem's synchronization note

**Branch:** `davide`, implementation base `946c1ed`.
Read the user-provided `/Users/davidetisi/Downloads/SYNC_DAVIDE.md` and compared its
seven questions with the frozen local benchmark. Treated the document as collaborator
context, not as authorization to run its commands, merge branches or send messages.
Adem's reported pushed branch and live run were not independently inspected.

Created `SYNC_ADEM.md`, a shareable reply covering potential convention, v3's
additional-reaction reference, self-decomposition, units, thresholds, candidate IDs,
schema mapping, frozen answer table and experiment size. It identifies the required
changes to legacy negative-energy acceptance and ranking, and distinguishes acceptance
success (M=2, 36.3265% by 10 random queries) from best-bin success (M=1, 20%).
The three proposed LLM arms require 210 proposal calls before retries under the stated
10-repeat, budget-10 design; shuffled feedback adds 100 if included.

Verification: read the frozen objective and counted acceptance flags directly from
`data/benchmarks/coating_v3.json`; calculated the exact hypergeometric probability;
checked documentation diff whitespace. No code changed, so tests were not rerun.
No API/LLM/MLIP calls, remote branch inspection, push, merge or message to Adem occurred.
Next coordination is sharing Davide's artifacts, adapting Adem's runner/analyser and
testing integration before live repeats. This reply and log update are committed locally.

## 2026-10-21 — Publish Davide's branch

The user authorized pushing the branch. Published `davide` to
`https://github.com/DavideTisi/interphAIse` and configured upstream tracking of
`origin/davide`. Git confirmed creation of the remote branch at `6f93458`, containing
the frozen benchmark, evaluator, reproducible data and reply to Adem.

Before publication, the working tree was clean, `.env` was confirmed untracked and
ignored, and a scan of outgoing development commits found none of the configured
API key values, including in decompressed thermodynamic data. No code changed;
tests were not rerun. No merge, pull request, LLM call or message to Adem was made.
This documentation entry is a follow-up commit for the same branch. Next: Adem can
fetch `origin/davide` and integrate the v3 contract described in `SYNC_ADEM.md`.

## 2026-10-21 — End-to-end PET-MAD interface pilot

**Branch:** `davide`, starting from published `a2880b5`.
**User request:** perform one end-to-end PET-MAD interface calculation.

### Completed calculation

Selected LiNbF6 from the frozen benchmark's best bin, without consulting an MLIP
result. Constructed a sharp LiCoO2(001) | LiNbF6(101) interface from pinned MP
structures. The selected model has 224 atoms, 55.9942 Å² contact area and 0.03071
von Mises matching strain. There are 192 cathode atoms and 32 coating atoms; 64
bottom-substrate atoms are fixed. Both slabs are formally neutral but polar.

Scanned 12 registry/gap combinations, then relaxed the joined interface and both
separated references in the same cell and strain state. PET-MAD S 1.6.0 (r²SCAN)
ran on CPU with two Torch threads, using the already cached checkpoint directly.
All three relaxations converged below 0.05 eV/Å on movable atoms:

- Interface: 126 steps, final free force maximum 0.04723 eV/Å.
- Coating reference: 57 steps, 0.04628 eV/Å.
- Cathode reference: 35 steps, 0.04506 eV/Å.

The provisional constrained work of adhesion is **2.100316 J/m²**. Calculation time
was 98.9 seconds, excluding lattice enumeration. There were 236 actual ASE calculator
executions: 12 registry executions and 224 across the three relaxations; property
cache hits are excluded. The count reconciles exactly with per-stage records.

### Interpretation and limits

This is one contact, not a complete coating score. The simulation is neutral and
fixed-stoichiometry, with no explicit voltage or electron reservoir; its energies
were not mixed into MP thermodynamics. The frozen v3 benchmark is unchanged.

Numerical convergence applies only to free atoms. Forces on constrained atoms remain
about 2.465 eV/Å. Formal polar-slab warnings and those large constraint forces make
this a provisional constrained estimate, not validated experimental adhesion. The
MP-derived bulk lattice was not reoptimized with PET-MAD. Slab thickness, vacuum,
constraints, termination choice and registry sampling have not been convergence-tested.

Structural inspection found no overlap violations in any final structure. Atom
counts, cell and element ordering are preserved. The minimum cross-contact distance
changes from 2.481 to 2.049 Å; maximum displacement is 1.624 Å and RMS displacement
0.390 Å. Rendered and visually inspected the geometry and force histories.

### Implementation, encountered issues and evidence

- Fixed `tools/matcher.py`: newer pymatgen raises for no ZSL matches; the wrapper
  now returns the empty list promised by its contract.
- The initial 200-atom cap rejected all neutral valid matches. Increased it to 256
  before model evaluation; four of 38 enumerated interfaces then passed the gates.
  Among small equal-strain options, chose the lower formal-dipole termination.
- Fixed interface serialization of numpy arrays using MontyEncoder.
- UPET's named model loader tried repository-file discovery in offline mode despite
  cached weights. Added a direct `--checkpoint` route; the successful run needed no
  download, credentials or external service. Failed initialization directories are
  retained under ignored runs; they contain no claimed calculation result.
- Added `tools/relaxation.py`: convergence records, raw versus constrained force
  maxima and actual calculator-call accounting. Exhausted relaxations are explicit.
- Added preparation, run and inspection scripts. An unconverged/invalid calculation
  produces a null validated adhesion field, retaining its raw energy difference
  separately for diagnosis.
- Added four tests covering no-match handling, cache-aware execution counting,
  step-budget exhaustion and constrained-force convergence. **86 tests pass**;
  existing dependency deprecation warnings remain.
- Saved compact, replayable evidence under `data/petmad/linbf6_cathode_pilot_v1/`,
  including initial/final structures, optimizer logs as text, registry scan, provenance,
  metrics and figure. Full trajectories remain ignored under `runs/`.
- Re-ran the inspection using only tracked artifacts, including archived optimizer
  logs, and verified that its accounting and geometry checks reproduce.
- Updated REPORT, README, evaluator handoff and the follow-up manifest. Wrote
  [PETMAD_INTERFACE_PILOT.md](PETMAD_INTERFACE_PILOT.md) with full interpretation,
  energies, commands and next steps. No live LLM or Materials Project call was made.

Checkpoint hash:
`3f52e97c459b2a28a94fc49b8a2f9a92551231a0ea4f5b5db2396f12d8ffa1e9`.

### What remains

Before comparative adhesion ranking, validate bulk preparation, polarity and
constraint sensitivity, then thickness/vacuum/registry settings. Calculate the
coating–electrolyte contact and apply an identical protocol to the shortlist.
The weakest-contact adhesion is not yet available. Adem's v3 experiment integration
can proceed independently. This checkpoint is committed locally, not pushed.

## 2026-10-21 — Niflheim access authorized and checked

The user authorized heavier calculations through `ssh fjorm`, using
`/home/scratch12/davti/OSI_Hackathon`. Read-only SSH checks succeeded: the expected
hostname and scratch directory were found, Slurm tools and rsync are available,
and CPU/GPU partitions are advertised. Default Python is 3.9.25, below the project's
>=3.11 requirement. GPU account eligibility and a compatible runtime remain unverified.

Added `NIFLHEIM.md` with the verified status and setup steps, and persistent cluster
instructions in `AGENTS.md`. The current pilot runner fixes CPU/two threads and will
need configurable device/thread arguments for a GPU job. No files were transferred,
packages installed or jobs submitted; unrelated running jobs were not modified.
Documentation consistency and whitespace checks were performed; no code changed,
so the test suite was not rerun. No LLM/Materials Project calls were made.
Next cluster work is runtime/resource setup and an allocated PET-MAD smoke test
before heavy production calculations. Documentation is committed locally, not pushed.

## 2026-10-21 — Publish pilot and cluster-access updates

At the user's request, pushed `3922869` (completed PET-MAD interface pilot) and
`35be6ef` (authorized Niflheim access documentation) to `origin/davide`.
Git confirmed the remote advance from `a2880b5` to `35be6ef`. The working tree was
clean before publication; `.env` remains untracked and ignored. No code changes,
tests, calculations, cluster submissions or merges were performed in this step.
This follow-up log entry accompanies the publication on the same branch.

## 2026-10-21 — Audit review concerns and amend the pre-run plan

On `davide`, checked the supplied review against the frozen v3 artifacts. Added
`scripts/audit_chemical_prior.py` and its replayable output
`data/benchmarks/chemical_prior_audit.json`. It validates the frozen inputs through
BenchmarkQueries, orders candidates using only fluorine membership and candidate
ID, and records the full offline trajectory and input hashes. The heuristic itself
was motivated by inspection of outcomes; the report discloses this rather than
claiming blind preregistration.

Results: 50 IDs, **42** distinct formula strings (correcting the review's 43), six
fluorinated candidates, both acceptable candidates fluorinated. The deterministic
order first succeeds at query 2. Random ordering within the six succeeds by query 3
with probability 0.8. Removing fluorine leaves zero acceptable candidates. Both
LiO8 entries fail insulation (gaps 0.1521 and 0 eV); physical plausibility remains
unvalidated. The frozen pool/objective were not modified.

Added `EXPERIMENT_AMENDMENT.md`, linked it from REPORT and SYNC_ADEM, and superseded
the earlier ten-repeat recommendation with at least 30. The plan specifies the
feedback contrast, saturation interpretation, polymorph identity, controls and
integration responsibilities. It keeps the 2.1003 J/m² pilot outside comparative
rankings and prioritizes bulk relaxation followed by surface/constraint/convergence
checks. These experiments remain planned, not executed.

Verification: ran the audit against the actual frozen benchmark; independently
enumerated all three-element subsets of the fluoride group to check the 0.8
probability; checked deterministic replay and whitespace. No paid LLM, MP API,
MLIP or cluster run occurred. No incoming Adem branch was inspected or merged.
Changes are local and not pushed. Next: integrate Adem's runner against this
protocol and implement/validate PET-MAD bulk relaxation before rebuilding slabs.

## 2026-10-21 — Offline interactive structure viewer

On `davide`, added `scripts/build_structure_viewer.py` and
`scripts/viewer/template.html`. The generator reads the 50 saved pool structures
and four pilot geometries into a self-contained HTML file, with no external web
assets, credentials or API calls. The generated local deliverable is
`runs/structure_viewer.html` (ignored, approximately 420 KB). A browser preview is
running at http://127.0.0.1:8876/structure_viewer.html; opening the HTML directly
also works without a server.

Implemented linked orthographic views, initial/relaxed selection, drag rotation,
zoom and orientation presets, a/b cell replication, element/layer/constraint
colouring, layer filtering, atom hover details and PNG/extended-XYZ exports.
Custom ASE-readable inputs can be appended with repeated `--structure` arguments.
No interpolation, bond assignment, energy ranking or new calculation is performed.
Cells and coordinates remain unwrapped; panels centre their geometry independently.
The initial file lacks the later relaxation constraints, which the UI states.

Verification: generated 54 entries and round-tripped all geometry downloads through
ASE, matching species, coordinates, cells and PBC. Confirmed 64 fixed atoms and
32 film atoms in the relaxed interface. Added a scientific data-preservation test:
`.venv/bin/python -m pytest tests/test_structure_viewer.py -q` passed (1 test;
4 existing ASE/NumPy deprecation warnings). Browser checks verified comparison at
desktop width, narrow layout, bulk selection, layer filtering (128 coating atoms
for 2x2), cell replication (896 interface atoms for 2x2), and orientation controls.
No browser JavaScript errors were observed. Saved a visual preview to
`runs/structure_viewer_preview.png`. Whitespace checks passed.

Updated README and REPORT and wrote STRUCTURE_VIEWER.md with usage, extension
instructions and scientific limitations. Earlier review amendments remain local.
An independent edit to scripts/prepare_interface_pilot.py appeared during this
session; it was not changed or included in viewer verification. No LLM/MP calls,
MLIP runs, cluster jobs, commits or pushes were made for this viewer task.
Next: rebuild the viewer as bulk-relaxed and converged interface geometries become
available; the viewer itself does not resolve those outstanding scientific checks.

## 2026-10-21 — Show both coating contacts in the viewer

The electrolyte pilot artifacts were already present from independent work when
this request began. Inspected selected.json/result.json and the saved geometries;
no new calculation was needed or launched here. Removed the viewer's single-folder
limitation: its default now discovers data/petmad/*/selected.json, and --pilot can
be repeated. Each geometry carries its material pair, source directory and state.
The rebuilt offline HTML contains 58 structures: 50 bulk and eight pilot geometries
from LiCoO2 | LiNbF6 (224 interface atoms) and Li6PS5Cl | LiNbF6 (216).

Added a Contact selector for initial/relaxed comparisons and Compare contacts for
both relaxed interfaces. Corrected cathode-specific substrate labels. Added optional
in-plane periodic wrapping (on by default) to display the electrolyte slab inside
its cell; original coordinates remain in exports. No z wrapping or geometry
optimization occurs. Updated STRUCTURE_VIEWER.md and REPORT.md.

Verification: two viewer tests passed, including both contact identities and all
four electrolyte geometry exports against their original files. Browser checks
confirmed contact switching, the 224/216-atom comparison, and wrapped rendering;
no JavaScript errors were observed before the wrapping addition. Saved the updated
comparison preview under runs/structure_viewer_preview.png. Changes remain local,
not committed or pushed. Other ongoing pilot-code/data changes were left intact.

## 2026-10-21 — Prepare viewer publication

At the user's request, preparing a commit on davide containing the offline viewer,
its tests/documentation, the saved electrolyte pilot data required for the second
contact, and the pending review amendment/audit referenced by REPORT and SYNC_ADEM.
The two viewer tests and interactive checks passed in the preceding session; no
implementation changes required repeating them. Publication checks include staged
whitespace, explicit file inventory and credential exclusion. Generated HTML stays
ignored under runs and can be rebuilt with scripts/build_structure_viewer.py.
Independent modifications to scripts/prepare_interface_pilot.py and
scripts/inspect_interface_pilot.py remain unstaged and are not part of this commit.
No API or calculation runs were performed. Push outcome is reported in the chat.

## 2026-10-21 — Review Adem's second sync note

Read origin/work/agent-experiments at 40e79c3 and inspected discovery.py plus the
experiment/analysis runners. Wrote SYNC_ADEM_2.md as a local reply for Davide to
share, with responses to all five questions and concrete integration issues.
The reported 7/10 versus 1/10 outcome remains unverified without the ignored run
archive. Retain frozen acceptance and label bin<=2 as post-hoc sensitivity.
Confirmed all three proposed MLIP shortlist materials in the saved manifest.

Found by inspection: invalid/repeated-ID proposals are retried before the budgeted
query API, contradicting the stated accounting; analysis uses nonportable absolute
benchmark paths, does not validate missing repeat files, and replaces whole arms
rather than appending follow-up repeats. It also checks hashes/budget but not all
experimental settings across batches. No claim is made that these findings alter
the reported counts without inspecting raw runs.

Verification: read-only source comparison and whitespace check. No branch switch,
merge, test execution, paid calls, calculations, message to Adem, commit or push.
Existing local preparation/inspection edits preserved. Next: obtain a sanitized
run archive and settle accounting/analysis policy before integrating into main.

## 2026-10-21 — Merge agent work and prepare integrated follow-up

At the user's request to merge and try real discovery, committed the review reply
as 8c82a10 and merged origin/work/agent-experiments at 40e79c3 into davide cleanly.
Main was not changed. Preserved local preparation/inspection script edits.

Corrected proposal accounting: once schema-valid proposals contain candidate IDs,
invalid and repeated IDs reach BenchmarkQueries and consume evaluations. Malformed
messages retain bounded retries. Versioned the prompt to v3-2026-10-21c-charged-ids.
Prevented stale usage metadata from being attributed to subsequent failed calls.
The experiment runner now supports independent clients, bounded concurrency, explicit
seed ranges, portable in-repo paths and source/file hashes. Analysis now validates
expected repeat files, statuses and settings, requires explicit duplicate replacement,
combines disjoint seeds, verifies the analysis benchmark, and includes the chemical
heuristic plus a machine-readable report. No frozen data/objective was modified.

Verification: full suite passed 92 tests; four new analysis tests passed separately.
An offline 30-run random batch completed with all expected files, seeds 100–129.
The live pilot is recorded separately under runs/integration_smoke. Wrote
INTEGRATED_DISCOVERY_PROTOCOL.md before production, fixing the 30-repeat follow-up,
settings, exclusion policy, interpretation and relation to Adem's earlier results.
No new MLIP or Materials Project calculation/request occurred.

## 2026-10-21 — Integrated production completed and independently replayed

Production used commit 6c81809 and the frozen follow-up protocol, seeds 100–129,
budget 10, three independent runs in flight, direct Haiku 5.5 at temperature 1.0
and 4096 output tokens. The separate seed-90 live pilot completed all three arms
with seven calls and is excluded. No provider/model fallback was used.

All 120 production runs completed (30 per arm), with 1,200 evaluations. Independent
query replay matched every saved result. Acceptance counts: iterative 19/30,
upfront 4/30, sequential 4/30, random 10/30; best-bin counts 7, 1, 0 and 6 respectively.
The fixed, review-motivated fluoride-first heuristic succeeds at query 2 and finds
the best bin at query 4. The observed iterative/sequential acceptance difference
is +50 percentage points, with 17 versus 2 discordant pairs (supplementary exact
McNemar p=0.000729). No runs were excluded/replaced or stopped based on significance.

Production used 631 proposal calls, with 2,773,563 recorded input and 576,415 output
tokens; every proposal attempt has usage. There was one schema-repair attempt.
Failed queries (retained and charged): iterative 26, sequential 5, upfront 5,
random 1. These include missing evaluator data and invalid/repeated IDs; none is a
run-level failure. The diagnostic bin<=2 sensitivity is upfront 26/30, iterative
22/30, random 18/30, sequential 13/30; it remains secondary, not a changed objective.

Added scripts/audit_discovery_batch.py and a passing paired-analysis unit test.
The earlier 92-test suite, four analysis tests and this one test all passed (97
across those runs). Inspected the generated plot and moved its legend outside the
data region, then regenerated it. Wrote INTEGRATED_DISCOVERY_RESULTS.md and updated
README, REPORT and the sync reply to identify current versus historical status.

Archived 120 full JSON traces, manifest, original-file hashes, summary, audit and
plot under data/experiments/integrated_v3_20261021_s100 (about 10 MB). Checked all
raw JSON files against configured credential values before copying; none occurred.
All paths needed for ordinary archive analysis are repository-relative. Reproduction
commands are in the report. No new MP requests, MLIP runs or cluster jobs occurred.
Main remains unchanged, and independent preparation/inspection script edits remain
local. The tested integration and archive are being committed/pushed on davide;
publication outcome is reported in chat. Shuffled feedback and physically validated
bulk/slab/transport work remain future scientific controls, not completed claims.

## 2026-10-21 — Review Adem's 0889d0e and assign next work

Fetched origin/work/agent-experiments through 0889d0e and inspected the diff from
40e79c3. New work is an unrun shuffled-feedback arm, best-bin trajectory analysis
and expanded sync interpretation. Wrote SYNC_ADEM_3.md with a shareable handoff:
Adem owns merging the controls/analysis onto 703f4d9 and validating them; Davide
keeps materials/MLIP validation. At the integrated 30-repeat setting each new
sequential control costs roughly 300 calls, not the old estimate of 100.

Noted source-inspection concerns: shuffled history changes prior assignments while
retaining older rationales; products/errors may reveal source identities; a lookup
on malformed IDs needs adaptation to our charged-query policy. These are review
findings, not results from a new control run. Clarified that escaping anchoring may
be a mechanism of feedback, and upfront also changes interaction/call structure.

Checked the archived new batch's LiZr2(PO4)3 selections: sequential chooses it in
10/30 runs (12 selections), upfront 25/30 (25), iterative 4/30 (7). This limits
how broadly to present the earlier ten-run 'never chooses it' diagnosis; cohorts
have different protocols and remain separate. Whitespace check performed. No
merge, paid call, calculation, message to Adem, commit or push in this review.

## 2026-10-21 — Publish the third sync handoff

At the user's request, committing SYNC_ADEM_3.md and the corresponding review log
on davide for publication to origin/davide. Scope is documentation only; existing
preparation/inspection script edits remain local. Staged file and whitespace checks
performed; no tests or paid calls needed. Push outcome is reported in chat.

## 2026-10-21 — Electrolyte-contact feasibility pilot (provenance for 05757ee data)

**Branch:** `davide`. This records the origin of `data/petmad/linbf6_electrolyte_pilot_v1/`.
That data was produced in a separate session running in parallel with the amendment,
viewer and integration work above. The parallel session then committed it in `05757ee`
for the viewer. The scripts that generated it were left uncommitted until this checkpoint.

**Order relative to the amendment.** EXPERIMENT_AMENDMENT.md puts the electrolyte contact
after bulk relaxation and slab-protocol validation. This run happened before that order
was visible to the session. It is a construction/execution feasibility check, not a
comparative adhesion value. The amendment's step 5 now notes this.

**Protocol finding.** With the cathode pilot's matching settings (160 Å², ZSL 5 %/3 %,
≤256 atoms, 6 % strain gate), LiNbF6 has no lattice match with Li6PS5Cl on any of the
3 × 5 facet pairs. A 6 % length tolerance gives only 6.2 % strain. Raising only the area
cap to 300 Å² yields 8 valid of 38 enumerated interfaces. A common two-contact protocol
needs a cap of at least ~185 Å².

**Result.** Li6PS5Cl(111) | LiNbF6(101), `F2_C2/m_1` / `Li3Cl_R3m_4`, 216 atoms (36 fixed),
183.022 Å², strain 0.01898. Same runner and settings as the cathode pilot; checkpoint
SHA-256 verified. Free-atom convergence in all three relaxations: interface 133 steps
(0.0461 eV/Å), LiNbF6 70 (0.0487), Li6PS5Cl 103 (0.0475). Maximum force on fixed atoms
was 0.805 (interface) and 1.188 eV/Å (substrate). Provisional constrained
**W_adh = 0.4275 J/m²**. 324 calculator executions, reconciled; 120.6 s wall time.
No overlap violations. Full table, limits and reproduction commands are in
PETMAD_INTERFACE_PILOT.md. Do not rank on 0.43 vs 2.10 J/m²: the two contacts used
different area caps and facet searches, and neither is protocol-validated.

**Code (this commit).**
- `scripts/prepare_interface_pilot.py`: `--contact {cathode,electrolyte}`, `--film-id`,
  `--substrate-miller`, `--all-substrate-facets`, `--max-area`. `contact` is recorded in
  outputs. Defaults reproduce the tracked cathode `selected.json` and `interface.json`
  exactly (checked).
- `scripts/inspect_interface_pilot.py`: the title comes from the selected pair and facets
  (it was hardcoded to LiCoO2). Plotting uses wrapped copies so non-orthogonal cells are
  not cropped. Numerical output is unchanged: the cathode `inspection.json` replays
  identically. The committed electrolyte `inspection.png` already used this version.

**Other.** The PET-MAD checkpoint was copied out of volatile `/private/tmp/interphaise-hf/…`
to `~/.cache/interphaise/pet-mad-s-v1.6.0.ckpt`, and its SHA-256 re-verified. Docs updated:
PETMAD_INTERFACE_PILOT.md (new section), REPORT.md (status line), EXPERIMENT_AMENDMENT.md
(step 5 note). No LLM, MP API or cluster calls were made in this work.

**Next.** Follow the amendment: PET-MAD bulk relaxation of LiCoO2, Li6PS5Cl and the
shortlist coatings, then rebuild both contacts under one matching setting with a cap
of at least ~185 Å². Then do the constraint, thickness, vacuum and registry checks.
