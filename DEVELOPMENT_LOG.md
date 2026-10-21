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

## 2026-10-21 — Verify Claude's electrolyte provenance commit

Reviewed local commit b210db0 (six files), one commit ahead of origin/davide at
6097831. Checked the archived electrolyte energies directly: joined
-1190.93994140625 eV, film -723.2285766601562 eV, substrate -462.8282165527344 eV;
reported W_adh is 0.42747021237517197 J/m2, area 183.02248179483956 A2.
All three saved movable-atom convergence flags are true. These match the new
energy table and feasibility interpretation. The 97-test pass is reported by
Claude; no test rerun or new calculation was performed in this read-only review.

Recommended publishing the provenance commit and then relaxing the five pinned
bulk inputs (LiCoO2, Li6PS5Cl, LiNbF6, LiCaAlF6, LiZr2(PO4)3), keeping the same
checkpoint and saving cell/position/stress/convergence provenance. The matching
statement should refer to the tested low-index facets, not every possible facet;
the suggested ~185 A2 cap belongs to the present unrelaxed lattices and must be
reassessed after bulk relaxation. A 300 A2 cap was the demonstrated successful
search setting. No push, message to Claude or new job was issued in this review.

## 2026-10-21 — Refresh the remaining work and ownership

Branch `davide`. Reviewed the current repository and handoffs to answer what moves
the project forward. Local HEAD and the origin/davide tracking reference now both
point to b210db0; this corrects the earlier checkpoint's then-current ahead-by-one
status. Observed independent unfinished bulk-relaxation edits in relaxation.py,
test_relaxation.py and a new scripts/relax_bulk.py. Left those files untouched;
no saved bulk results were found during this review and no implementation test
or calculation was run here.

Updated WORK_DIVISION.md with the completed 30-repeat baseline, current ownership,
prioritized next work and completion evidence. Adem's next control is 30 matched
shuffled-feedback runs after integration and offline validation; IDs-only remains
optional. Davide's physics path is five pinned bulk relaxations, validation of
both LiNbF6 contacts, then conditional shortlist expansion. Presentation work can
proceed alongside these tasks. The existing four-arm archive and frozen criterion
remain unchanged. This is a work recommendation, not a newly launched paid batch
or a message sent to either collaborator.

Added the plan link to REPORT.md and corrected its overbroad matching statement:
the 160 Å² failure concerned tested low-index facets on unrelaxed lattices, while
300 Å² yielded the archived ~183 Å² interface. Matching limits must be reassessed
after bulk relaxation. Earlier log entries are preserved as historical records.

Verification: checked plan figures/settings against INTEGRATED_DISCOVERY_RESULTS.md
and SYNC_ADEM_3.md and performed a documentation diff/whitespace check. No new LLM,
MP API, MLIP or cluster run, git commit or push was performed in this planning work.
Next: complete the two evidence checks while preparing the reproducible demo,
then review the integrated code and scientific claims before a main-branch merge.

## 2026-10-21 — Prepare a broader coating/environment exploration

Branch `davide`. The user asked to explore more combinations and selected more
coatings across battery environments. Audited the local summary snapshot and
corrected-energy dataset without API calls. The unchanged coating filters admit
141 structures (100 formula strings), not the initially considered 200; retained
all 141, including every original candidate, without using new scores. The saved
pool includes 61 other oxides, 29 halides, 23 silicates, 16 phosphates and 12 borates.

Added all-eligible selection to scripts/build_candidate_pool.py while preserving
its fixed-size default. Added scripts/prepare_environment_expansion.py to prepare
hashed pool/plan/coverage records under data/exploration/environment_expansion_v1.
Kept the original LiCoO2 endpoint and 4 V, and prepared Li6PS5Cl, Li3InCl6 and LLZO
electrolyte environments: 423 combinations. The new endpoint models are the
lowest-summary-hull ordered cached records, explicitly pending phase review.
The LLZO model is tetragonal I4_1/acd, not a disordered cubic conductor. The script
checks hashes and original-pool inclusion, refuses output overwrites, and makes
no energy or search calls. Existing benchmark files and archives were untouched.

The audit finds 117/141 coating IDs in the existing energy dataset. Full ID and
subsystem-query coverage exists for 104 sulfide combinations; neither new endpoint
has a cached corrected entry. Additional queried systems needed are 496 (sulfide),
536 (chloride) and 724 (oxide), with a deduplicated union of 1,430. These are chemical
systems, not material or request counts. Coverage is not structure validation; no
partial phase diagram was scored. This avoids optimistic scores from missing
competing phases.

Added ENVIRONMENT_EXPANSION.md with the scientific question, sources supporting
the electrolyte-family choices, numerical audit, next implementation steps, owner
assignments and estimated proposal-call counts for future matched experiments.
Updated REPORT.md and WORK_DIVISION.md to distinguish this user-selected extension
from the completed experiment. The LLM role is adapting material choices and
chemical hypotheses to feedback in each environment; success is not assumed.

Validation: 12 targeted tests passed (candidate pool, environment expansion and
thermodynamic dataset helpers). A fractional-occupancy test initially failed
because reduced_composition does not normalize all fractional occupancies to
integer formulas; endpoint comparison was corrected to fractional_composition.
Verified the three generated artifact hashes and their pool links, and reproduced
the original 50-candidate selection with exactly its original hash. Whitespace
check passed.
No MP request, paid LLM call, PET-MAD run, cluster job, git commit or push occurred.
Independent bulk-relaxation edits remain untouched. Next: review endpoint phases,
extend the fetcher for the plan, obtain complete compatible energies, exhaustively
audit all environments, then freeze a new experiment before LLM production.

## 2026-10-21 — Review completed bulk relaxation and recommend next protocol

Branch `davide`. Read Claude's bulk report, code and archived evidence. Verified
the ten convergence records against their declared projected/unprojected criteria,
recomputed energy drops, and reconciled 2,944 calls with the saved total. Inspection
replayed exactly in a temporary copy. All six relaxation tests passed, with ASE/
NumPy deprecation warnings. Original code and bulk evidence were left unchanged.

The 440-atom electrolyte and 456-atom cathode-(001) matches use symmetric bulk cells;
they must be recomputed after unconstrained reference selection. The 128-atom cathode
alternative changes the surface. Wrote BULK_REVIEW_AND_NEXT_STEPS.md recommending
five additional fixed rattle seeds for each distorted material, then an initial
512-atom construction cap and primary LiCoO2(001), subject to rematching and slab
validation. No multistart, MD or interface relaxation was launched in this review.

Performed a focused rotation-sensitivity diagnostic with the verified PET-MAD S
1.6.0 checkpoint: identity plus three random orientations for symmetric/distorted
Li6PS5Cl and LiZr2(PO4)3. The drops persist at 63.58–64.20 and 7.57–7.75 meV/atom;
largest single-structure orientation ranges are 0.663 and 0.557 meV/atom. This checks
one numerical explanation, not model accuracy or experimental phase identity.
Saved reproducible scripts/check_bulk_rotations.py and
data/petmad/bulk_rotation_review_v1.json with checkpoint, input and script hashes.
An initial interactive check used 16 single points; testing the saved script used
another 16 and gave identical energies (32 calls total, separate from Claude's run).

Updated REPORT.md and WORK_DIVISION.md with the completed milestone. Documented
the distinction between projected convergence and raw convergence, ordered models
and experimental disorder, and possible cancellation of bulk reconstruction in an
adhesion energy difference. Checked relevant primary literature and UPET guidance;
sources are linked in the review. The frozen discovery result and expansion remain
unchanged. Whitespace check performed. No MP or LLM API calls, cluster jobs, git
commit/push or messages to other sessions. Next: Claude's bounded multistart check,
new matching, and consistent two-contact validation; expanded MP data and feedback
controls remain separate workstreams.

## 2026-10-21 — Review Adem's ea0326d and prioritize the controls

Branch `davide`. Fetched origin/work/agent-experiments from 0889d0e to ea0326d,
read SYNC_DAVIDE_3.md and inspected discovery/analysis/test changes. Created an
isolated git-archive checkout under /private/tmp for testing; no branch merge or
shared code edit occurred. The new control handles charged malformed/repeated IDs
and preserves true outcomes. Online reshuffling/history contradictions and chemical
identity hints remain disclosed limitations, not implementation claims of blinding.

All 41 relevant tests passed after correcting an initial test-command filename.
Re-ran the archived production analysis and visually checked the new three-panel
plot. It reproduces acceptance 19/10/4/4 and best-bin 7/6/0/1 in iterative/random/
sequential/upfront order. An offline deterministic comparison to b210db0 showed
identical prompt payloads, histories and traces for the original four strategies.
The first smoke fixture used a wrong payload key; correcting the fixture to count
resolved it, with no product-code change or live call.

Confirmed one future-pool plotting edge case: next(...) for the exact random median
raises StopIteration if no eligible-bin cumulative probability reaches 0.5. This
does not affect current v3 (47/50 eligible), but needs a no-eligible-result fallback
and sparse/all-ineligible tests before broader use.

Wrote SYNC_ADEM_4.md recommending 30 matched shuffled repeats now, deferring IDs-only,
and preparing the figure and r111/r114 examples. Included explicit settings, immutable
archive handling, a request to report actual source displacement, limitations and
interpretation of either outcome. Updated REPORT.md and WORK_DIVISION.md. Whitespace
check performed. No paid API calls, MP requests, MLIP runs, messages to Adem, commit
or push occurred. Bulk and expansion changes in the shared checkout were preserved.

## 2026-10-21 — Delegate environment data and exhaustive evaluation

The user explicitly authorized a subagent so the parent can remain available for
Claude's and Adem's reports. Started `/root/environment_expansion` in the shared
checkout to review the new endpoint models, implement resumable compatible MP data
retrieval, evaluate all 423 prepared coating/environment combinations, and produce
audited exploratory results. MP retrieval is within the authorized project scope;
no paid LLM experiment, automatic benchmark freeze, PET-MAD run or cluster job is
part of this delegation. The original frozen benchmark and archives stay intact.

The subagent owns new expansion scripts/tests/data and EXPANSION_PROGRESS.md.
It will coordinate a final append to this development log; the parent retains
REPORT.md, WORK_DIVISION.md and collaborator handoffs. Claude's bulk/interface work
and Adem's agent/control files are excluded from its edits. No branch switch,
commit, push or additional agent delegation was requested. The parent will review
the implementation and evidence when available; delegation is underway, not a
claim that the expanded evaluation has completed.

## 2026-10-21 — Complete delegated environment expansion and exhaustive audit

Branch `davide`; implementation not committed. The authorized expansion subagent
completed all 141 coatings × 3 environments without paid LLM runs or an automatic
benchmark freeze. Retained the preselected ordered Li3InCl6 (C2, 60 primitive sites)
and tetragonal LLZO (I4_1/acd, 96) as explicit 0 K computational models; inspected
composition, occupancy, geometry, provenance and exact corrected-entry structure
matches before scoring. No outcome-driven endpoint replacement or PET-MAD energy
mixing occurred. Parent-owned reports and collaborator implementation files were
left unchanged; detailed conclusions are in EXPANSION_PROGRESS.md.

Added scripts/fetch_environment_dataset.py, scripts/evaluate_environment_expansion.py,
scripts/plot_environment_expansion.py and tests/test_environment_evaluation.py.
The resumable fetcher checks source vintage/correction scheme, conflicting duplicate
entries, per-batch hashes and complete subsystem coverage. MP remains 2026.09.28:
36 new batched get_entries calls filled 1,430 missing subsystems, giving 7,420
corrected GGA/GGA+U entries and 2,379 covered systems. API exception/header strings
and credentials are not recorded. Inspection caught that the deprecated client
version getter only returns a cached attribute; corrected it to fetch a fresh
public heartbeat, then replayed all cached batches with no new entry queries.
The first and verified snapshots have exactly identical entries and batches.

Saved sanitized compressed data and all 423 outcomes in
data/exploration/environment_expansion_v2/ (dataset ~9.8 MB). Each environment has
138 computed candidates, 120 eligible and 3 explicit missing pinned-entry failures.
Sulfide/chloride/LLZO respectively have 4/55/17 acceptable candidates; exact random
acceptance by 10 queries is 25.74%/99.43%/73.57%. The unchanged fluoride-first rule
first succeeds at queries 3/1/40. All four sulfide acceptable structures contain F;
none of the 17 LLZO acceptable structures does. Best bins are 1/0/0, with 3/38/1
structures tied. LLZO's unique model optimum is LiClO4, a computational criterion
result rather than a validated coating recommendation. All environments remain;
chloride saturation and the limitations of the objective are explicit in the report.

All 50 original sulfide results reproduce, with maximum numerical difference 0.0
and identical status/insulation/bin/acceptability/pinned entries. Six independent
Qhull LiF contact checks agree with linear programming within 8.88e-16 eV/non-Li
atom. All 423 IDs and result hashes, source-code hashes, original benchmark identity,
and dataset/query provenance validate. 40 targeted tests pass (new evaluation,
expansion preparation, thermodynamic helpers, candidate selection and evaluator).
The final exhaustive pass took 66.87 s; an earlier pass took 69.17 s and is preserved
in ignored runs after the fresh-version-check correction. MP retrieval took 31.69 s
plus 3.20 s cached replay. HTTP pagination counts were not instrumented. No LLM,
MLIP or cluster calls, git commit/push, branch switch or further delegation.

Pool SHA-256 833d5a687d4413cab1ab7cdd9007b56b924e3b2d2802ae26170d9f6a7f82e71d;
new dataset fe7a0e815fd31d325095707b483f4a30be26e13f8c40e12eeef4d7f747d0a5ea;
audit 2fe5770d5687306ac4451dd36cde28348a9b8d1d894ab349b885f8e6ced1ee62.
The report records exact reproduction commands and remaining experimental choices.
A scan of new source/report/decompressed data found no configured credential values;
.env remains ignored/untracked. Whitespace check passes. The figure was visually
inspected, and artifact_manifest.json records byte hashes and validation accounting.

Next: parent reviews the outputs and aligns REPORT.md/WORK_DIVISION.md. Jointly
freeze separate prompts, budgets, per-environment metrics and controls before any
expanded paid LLM study. Keep the existing v3 cohort separate and retain all three
environments. Claude's validated-interface work and Adem's completed original
shuffled control remain independent workstreams.


## 2026-10-21 — Verify completed shuffled control and review integration

Branch `davide`, HEAD b210db0. Fetched origin/work/agent-experiments to 6e74e88
and reviewed the new archived shuffled run (source ea0326d), median fix and figures
in an isolated git-archive checkout. All 104 tests pass. Replayed all 300 true
query outcomes and independently reconstructed all 300 source permutations and
saved prompt histories. All source/archive hashes match. No malformed retries;
12 failed queries remain charged (10 missing-entry, 2 unknown ID). The 300 calls
record 1,594,978 input and 259,023 output tokens. No live LLM calls in this review.

Acceptance is shuffled 6/30 against iterative 19/30. The directly reconstructed
paired table is both 3, iterative only 16, shuffled only 3, neither 8; exact
two-sided McNemar p = 0.004425048828125. Reproduced the five-arm analysis and
visually inspected its plot and the selected r111/r114 figure. Treat the contrast
as a planned follow-up supporting useful correctly associated feedback, with
history contradictions and partial identity leakage, not proof of chemical
reasoning. Existing heuristic and best-bin limitations remain explicit.

Created an isolated temporary clone and merged committed b210db0 with 6e74e88
without committing. No conflicts; Claude's pilot code/docs remain included.
The resulting combined tree passes all 104 tests and whitespace checks. This is
an integration rehearsal, excludes uncommitted work, and is not a merge to main.
Real working branches were untouched. Standard ASE/spglib deprecation warnings
remain. Saved compact evidence in data/reviews/shuffled_v3_20261021.json.

The environment subagent completed its work and appended the preceding checkpoint.
Parent reviewed its scripts/report/figure and independently verified all eight
artifact byte hashes, present semantic hashes, complete row sets, acceptance counts,
fluorine split and exact-random probabilities. It reports 40 passing tests, exact
50-row replay and six independent solver checks. All 423 combinations remain;
414 compute and nine fail explicitly. Sulfide/chloride/LLZO acceptance is 4/55/17;
fluoride-first first successes are queries 3/1/40. No LLM adaptation result exists
yet. Chloride is easy and must remain in the declared study. Original scores are
unchanged; no PET-MAD energies entered the thermodynamic expansion.

Wrote SYNC_ADEM_5.md and aligned REPORT.md/WORK_DIVISION.md: defer IDs-only, have
Adem prepare the environment runner and a separate pre-run protocol, retain
Claude's independent interface validation, and review the completed discovery
release now. The subagent's expansion remains uncommitted. No messages were sent
to external collaborators, no actual merge/commit/push occurred, and no additional
MP/MLIP/cluster calls were made by this parent review. The expansion subagent's
36 MP entry calls are accounted separately in its checkpoint. Documentation and
whitespace checks performed; next is scoped integration and experiment freeze.


## 2026-10-21 — Review multistart references and choose primary coating orientation

Branch davide at b210db0, shared uncommitted work preserved. Read Claude's completed
multistart report/code/evidence. Re-read all twelve final structures with archived
single-point results: energies, force/stress criteria and convergence flags agree.
Li6PS5Cl 6/6 and LiZr2(PO4)3 5/6 converge; the latter's seed 5 force is 0.011387 eV/Å
and remains excluded. Seed 0 has the lowest saved energy among valid starts in both
materials. Additional batch cost is 7,216 calls and 1,567.47 summed seconds, not
elapsed batch wall time because the materials ran concurrently. No new MLIP call
was needed for this audit. All six targeted relaxation tests pass; the reported
113-test full-suite result was not independently rerun here.

Recommend LiNbF6(001) on both primary contacts, retain LiCoO2(001), and keep the
200-atom alternative as a separate orientation comparison. A common facet controls
orientation but does not establish a continuous coherent film. The selected seed-0
and seed-4 electrolyte matches have different saved termination identifiers
(P_C2/m_2 versus Cl2_P-1_2), so equivalent framework cuts and surface chemistry need
mapping before claiming a bulk-only sensitivity. P-labelled alternatives exist at
440 atoms in both archived scans; their actual equivalence remains to be inspected.

Performed geometry-only rematching with existing unconstrained LiCoO2/LiNbF6
stability-check cells and Li6PS5Cl seeds 0/4. Same-facet 504-/440-atom matches remain
feasible. Found that the 60-candidate global cap can omit F-terminated cathode
matches: the builder has 113 ZSL matches and four termination pairs. Explicitly
enumerating F2_P-6_3 / Li_P6/mmm_1 recovers the valid 504-atom match (1.9520% strain,
88.800 Å²). Requested termination selection before truncation and a regression
check in Claude's implementation. Exact geometries were enumerated transiently;
no production interface was exported or relaxed. Saved audit/input/code hashes in
data/reviews/multistart_facet_review_20261021.json.

Corrected interpretation in the new handoff: archived cathode polarity values
include 2.06 and 6.17 e/Å, rather than 2.06 for every termination; this is a formal
oxidation-state diagnostic. Read official pymatgen and UPET guidance. The small
LiZr2(PO4)3 seed gap does not demonstrate robust energetic ordering against the
earlier rotation diagnostic; neither check establishes a physical phase.

Wrote SYNC_CLAUDE_1.md with facet/termination/reference choices, validation order,
explicit interpretation limits and separate-commit guidance. Updated REPORT.md
and WORK_DIVISION.md; Claude's report/code/evidence were not edited. Shared log is
available for Claude to append its own provenance. Documentation/whitespace checks
passed. No MP/LLM API calls, MLIP evaluations, cluster jobs, external messages,
commit, push or actual branch merge. Next: Claude builds the pinned contacts and
mapped alternative, then checks polarity/constraints before convergence and ranking.
The discovery result and environment study remain unchanged.


## 2026-10-21 — Short team handoff for Adem

Branch davide. At the user's request, wrote SYNC_ADEM_6.md summarizing Codex's
shuffled-control and integration review, the subagent's completed 423-combination
expansion, and Claude's bulk/multistart work plus the remaining interface checks.
Included the three-environment baseline table, the LLM's hypothesis-revision role,
Adem's proposed next work and explicit uncommitted/not-yet-on-GitHub status.
Detailed source reports are linked rather than duplicating the technical reviews.
Checked consistency against REPORT.md, WORK_DIVISION.md and the latest log entries;
all local document links resolve and whitespace checks pass. Documentation only:
no new calculations, API calls, tests, collaborator messages, commit or push.

## 2026-10-21 — PET-MAD bulk relaxation, multistart references and rematch (provenance)

**Branch:** `davide`. The code and evidence for this work were committed in `57774d6`
together with the parallel review files. This entry records how they were produced.
Full results and interpretation: [BULK_RELAXATION.md](BULK_RELAXATION.md). Reviews:
BULK_REVIEW_AND_NEXT_STEPS.md and SYNC_CLAUDE_1.md.

**Bulk relaxation (EXPERIMENT_AMENDMENT step 1).** `scripts/relax_bulk.py` relaxes the
pymatgen conventional cells of the five pinned entries (LiCoO2 `mp-aaaabhik`, Li6PS5Cl
`mp-aaacebzk`, LiNbF6 `mp-aaacjjwh`, LiCaAlF6 `mp-aaaaajby`, LiZr2(PO4)3 `mp-aaabevhd`).
It uses PET-MAD S 1.6.0, CPU, offline checkpoint SHA-256 `3f52e97c…ffa1e9`. Each cell gets
a symmetric relaxation (FixSymmetry + FrechetCellFilter, FIRE), then a stability check:
rattle σ = 0.02 Å, seed 0, relax without symmetry. Converged means force ≤ 0.01 eV/Å and
|stress| ≤ 0.05 GPa, evaluated explicitly on the final structure.
- The first attempt stopped LiCoO2 at 0.198 GPa: FrechetCellFilter scales stress by atom
  count, so FIRE's own exit is loose. The run was stopped. `relax_cell_record` now restarts
  FIRE with a halved fmax until both criteria hold, and uses symmetry-projected
  forces/stress in symmetric mode (raw values recorded). The aborted output is kept in
  ignored `runs/bulk_relaxation_aborted_v0/` and is not used.
- Production: all 10 relaxations converged; 2,944 calculator calls, 548.8 s. Stable under
  the check: LiCoO2, LiNbF6, LiCaAlF6 (|ΔE| ≤ 0.05 meV/atom). Lower-energy distorted
  minima: Li6PS5Cl −63.81 meV/atom (Pc), LiZr2(PO4)3 −7.57 meV/atom (P1). Frameworks are
  intact; Li (and Cl) rearrange.

**Multistart (option c).** `scripts/multistart_bulk.py`, seeds 1–5, same settings and
1,000-step budget, four threads, the two materials run concurrently. Li6PS5Cl: 6/6
converged, six distinct minima from −57.73 to −63.81 meV/atom; 2,299 calls, 342 s.
LiZr2(PO4)3: 5/6 converged; seed 5 exhausted at 0.0114 eV/Å and is excluded; five
distinct minima from −6.07 to −7.57 meV/atom; 4,917 calls, 1,225 s. Selected model
references: seed 0 for both; alternatives Li6PS5Cl seed 4 and LiZr2(PO4)3 seed 1. The
LiZr2(PO4)3 seed 0/1 gap (0.3 meV/atom) is below the rotation-diagnostic spread, so that
ordering is not robust.

**Matching.** `scripts/scan_interface_matches.py` (matching only, no MLIP). The pilot
matches (224/216 atoms) no longer exist with relaxed lattices. Decision (SYNC_CLAUDE_1):
LiNbF6(001) on both primary contacts, LiCoO2(001) kept. Cathode 504 atoms; electrolyte
(111) 440 atoms for seeds 0 and 4. The 200-atom Li6PS5Cl(011)|LiNbF6(100) contact is an
optional secondary comparison. Open issues from the review: the 60-candidate cutoff hides
the F-terminated cathode match, and the seed 0/4 electrolyte matches differ in termination
(P vs Cl labels). Both are addressed next.

**Verification.** Two new relaxation tests (EMT Cu: lattice recovery and symmetry
retention; explicit exhaustion/stress gate). The full suite passed 104, then 113, tests on
the shared tree. The inspection replays identically from the archived evidence. No LLM,
MP API or cluster calls were made. The checkpoint was also copied to
`~/.cache/interphaise/` (hash verified).


## 2026-10-21 — Commit the reviewed work for publication on davide

The user explicitly requested committing and pushing so Adem can access the work.
Fetched origin: davide was still at b210db0 with no divergence; the agent branch
advanced to 1ef2c8a (merge of the electrolyte pilot), which was not merged here.
Reviewed and grouped all 118 changed/new files into explicit publication scopes.
No files were left outside those groups at the initial inventory.

Created 57774d6 for PET-MAD bulk relaxation, multistart data, reference/rotation/
facet audits and associated tests/reports (88 files). Created 81e4625 for the
141-coating, three-environment implementation, dataset, audits and figure
(22 files). The remaining handoffs and shared reports form a separate documentation
commit. Updated the short Adem handoff and current status reports to identify the
implementation commits and supersede earlier uncommitted-status checkpoints.

During preparation Claude added its separate provenance-only commit 408a37f.
Inspected that 47-line log addition and preserved it; it is included in the push
alongside the two implementation commits and the final handoff/report commit.

Validation: the full current suite passes 113 tests (existing ASE/spglib
warnings). Checked all expansion artifact hashes and recorded source hashes,
plus the rotation-review source hash. Whitespace checks pass. Scanned every
publication file for configured credential values, including decompressed
thermodynamic JSON: no matches. .env remains ignored and untracked; explicit
staging excludes runtime caches, environments, checkpoints and trajectories.
The bulk/expansion commits use a reviewed content snapshot to detect concurrent
changes before staging. No new LLM/MP API calls, MLIP calculations or cluster jobs.

Publication target is origin/davide using a normal push, with remote-head and
working-tree verification after the final documentation commit. No main merge,
force push or collaborator message is part of this request. The new agent-control
code/results are still on Adem's branch; both frozen result cohorts and exploratory
status of the expansion are preserved. Interface construction/validation and the
separate expanded LLM protocol remain next work.

## 2026-10-21 — Explicit terminations, primary contact builds and constraint check

**Branch:** `davide`. Follows SYNC_CLAUDE_1.md. Details: [CONTACT_PROTOCOL.md](CONTACT_PROTOCOL.md).

**Termination selection.** `enumerate_interfaces` gains `terminations`, applied before the
60-candidate cap, and a `report` that records the available terminations, the ZSL match
count and truncation. An unknown label raises. New regression test. This recovers the
F-terminated cathode match that the cap had hidden.

**Equivalent electrolyte cuts.** Termination labels differ between Li6PS5Cl seeds because
their symmetries differ. Cuts were matched by framework groups (species, parent (111) height
u = (x+y+z) mod 1, with Li ignored) ranked by mean z on each face. Both seeds descend from the
same symmetric parent in the same atom order. Atom-index sets and fixed distance windows were
tried first and were unreliable. Rule, fixed before any interface energy: no cut PS4, an
equivalent cut in both seeds, then the lowest formal substrate polarity. It selects the Cl
cut (seed 0 `Li6Cl_P1_7` ≡ seed 4 `Cl2_P-1_2`, identical framework signatures on both faces).
The old seed-0 pick `P_C2/m_2` cut four PS4 units.

**Builds** (`scripts/build_contact.py`; deterministic, and rebuilding reproduces `build.json`).
Cathode LiCoO2(001) | LiNbF6(001): 504 atoms, 88.800 Å², 1.952 %, `F2_P-6_3`/`Li_P6/mmm_1`,
formal |p|/A 2.058 / 0.613. Electrolyte Li6PS5Cl(111) | LiNbF6(001): 440 atoms, seed 0
170.708 Å², 3.006 %, |p|/A 0.174 / 0.558; seed 4 172.926 Å², 2.864 %, 0.129 / 0.551.
All slabs are formally neutral and stoichiometric; no polyhedra are cut. The fixed-fraction
rule fixes 38 vs 36 atoms in seeds 0 and 4. Saved under `data/petmad/contact_v1_*`, which
the viewer discovers (61 structures after a rebuild).

**Constraint check** (MLIP; PET-MAD S 1.6.0, checkpoint `3f52e97c…`, CPU, 2 threads × 6
concurrent). `run_petmad_interface.py` gains `--fixed-fraction`/`--threads`; the defaults keep
the pilot behaviour. Fractions 0.17 / 0.34 / 0.50, all 18 relaxations converged. Cathode W_adh
3.488 / 3.479 / 3.471 J/m² (insensitive). Electrolyte 1.288 / 1.329 / 1.411 J/m² (monotonic,
0.123 spread, above the 0.1 tolerance). Fixed-geometry separation
(`scripts/fixed_geometry_separation.py`, 12 single points): cathode 5.04–5.06 J/m², with the
separated LiNbF6 slab relaxing by 1.49 J/m²; electrolyte 2.47–2.56 J/m², with the separated
Li6PS5Cl slab rearranging (Li RMS 0.55–0.65 Å vs the joined interface, about 0.6 J/m²). Cost:
1,208 calls plus 12 single points, 236–309 s per run. Evidence:
`data/petmad/constraint_test_v1/`; the inspection replays identically.

**Correction (chat only).** I first attributed the electrolyte sensitivity "almost entirely"
to the separated slab, from total energies that include different fixed regions. The
decomposition shows +0.092 J/m² from the fixed-geometry separation, +0.049 from substrate
relaxation and −0.018 from the film.

**Verification.** The full suite passes (114 tests) with the matcher and runner changes.
No LLM, MP API or cluster calls. **Next:** electrolyte substrate thickness with a
fixed-thickness constraint rule, then the cathode film thickness, vacuum, registry, and the
seed-4 sensitivity. See CONTACT_PROTOCOL.md.

## 2026-10-21 — Independent contact audit and bounded thickness recommendation

**Branch:** `davide`, reviewing Claude's local `7249e7a` on top of published
`08747a0`. The user relayed the completed contact/constraint study and asked
whether publication and electrolyte thickness should proceed. Recommendation:
yes, publish that implementation and run a controlled thickness study. This
review does not itself push or launch new MLIP calculations.

Read the implementation, CONTACT_PROTOCOL.md, build records and saved outputs.
Recomputed adhesion and the fixed-geometry separation/relaxation identity from
archived energies; verified all 18 saved free-force convergence results and
matching fixed-index maps between joined and separated references. Inspected
fixed-atom force-vector differences: maxima are 0.033–0.075 eV/Å for the cathode,
versus 0.418–0.948 eV/Å for the electrolyte. Similar cathode residual forces
support insensitivity within this bracket, not proof that polar energy errors
cancel exactly. The +0.092 J/m² electrolyte term is a separation-energy
difference, not a unique decomposition of the joined-interface energy alone.

Geometry-only reconstructions preserve the seed-0 Cl cut, coating (001), both
in-plane transformations and the 170.7083 Å² area. Two/three/four substrate layers
give 440/492/544 atoms and z spans 9.58/15.43/21.28 Å. A fixed bottom depth of
3.2576018324 Å gives 38 fixed atoms throughout. The two-layer mask equals the
archived 0.34-fraction mask; coordinates agree modulo periodic wrapping.
No PS4 tetrahedra are cut. Recommend a 600-atom cap for this bounded test, with
fixed physical depth, consistent reference masks, and both W_adh/W_sep reported.
These are input-geometry checks, not thickness-convergence results.

Saved SYNC_CLAUDE_2.md with the calculation protocol, interpretation qualifiers,
and next-step sequence. Saved numerical review and source/input hashes in
data/reviews/contact_constraint_review_20261021.json. Updated REPORT.md and
WORK_DIVISION.md to distinguish completed contact construction/constraint tests
from pending thickness, vacuum, registry, seed-4 and polarity work. Adem's
environment-study protocol remains independent; no expanded LLM run is frozen.

Verification: `MPLCONFIGDIR=/private/tmp/interphaise-mpl .venv/bin/python -m
pytest -q` passes **114 tests** (existing ASE/spglib warnings). The archive
accounts for 1,208 calculator calls plus 12 separation single points. Scanned
the 99 committed paths against local configured credential values: no matches;
.env is ignored and untracked. Full commit whitespace check reports 880 trailing
spaces in two ASE-generated electrolyte initial.extxyz files; excluding EXTXYZ,
the check passes. Raw scientific artifacts were left byte-for-byte intact.
The first scratch geometry export hit NumPy JSON serialization; later scratch
checks also needed periodic wrapping and the actual archive filename layout
accounted for. Those diagnostic attempts produced no scientific calculation or
production data; the completed review export is the one linked above.

No new LLM calls, MP API requests, MLIP evaluations or cluster jobs occurred.
All review changes are local; Claude retains implementation ownership of the
thickness study. The original discovery cohort and exploratory expansion tables
are unchanged. Next: publish the implementation, implement fixed-depth/layer
options with provenance, run three/four-layer electrolyte cases, then repeat the
constraint check and remaining numerical/seed sensitivity tests.

## 2026-10-21 — Freeze environment tables and review Adem's experiment protocol

**Branch:** `davide`; reviewed fetched `origin/work/agent-experiments` at
`fc6a54c`. The user relayed Adem's runner/protocol update and requested the next
decisions. Read the draft protocol and changed runner/prompt-boundary tests.
Recommend seeds 200–229, six paired exact McNemar contrasts with Holm correction,
and shuffled feedback in all three environments. Keep the original v3 objective,
all 141 candidates per environment, near-ceiling chloride, and the cohorts
separate. Final protocol sign-off belongs to the collaborators.

Added scripts/freeze_environment_tables.py and nine tests. Froze separate copies
under data/benchmarks/environment_v1/; every scientific field and all 423 outcomes
remain exactly equal to their exploratory sources. Original files/manifests are
unchanged. The new manifest records original/frozen semantic and byte hashes,
timestamp, scientific decision, and freezer hash. The objective version/hash is
unchanged. The utility validates the full three-environment set, pool/result
identity, hashes and scientific consistency and refuses overwrites. Frozen tables
load through BenchmarkQueries without a draft override.

Found a real integration gap: analysis accepted draft runs although the protocol
excluded them. Added rejection of draft metadata or unfrozen table contents to
scripts/analyse_discovery_experiment.py, with three regression tests; existing
frozen historical archives remain supported. Pinned pymatgen==2026.9.24 and
pymatgen-core==2026.10.16 in pyproject.toml and requirements.txt, and documented
the tested setup in README.md. No packages were installed or changed. Adem's
2026.4.16 mismatch was not independently reproduced, so no upstream root-cause
claim or matcher-tolerance change is made.

Validation used an isolated archive of fc6a54c with Claude's committed 7249e7a
changes overlaid: 124 tests passed before this review's code additions, and
**136 passed after** the freezer/analysis changes. Existing ASE/spglib warnings
remain. No actual branch merge or branch switch occurred. An initial test-patch
application encountered Adem's extra analysis tests; applied only the guard and
appended the new tests, retaining his best-bin code/tests. Reviewed snapshot
source hashes are saved in data/reviews/environment_freeze_review_20261021.json.
Later concurrent Claude thickness edits in the shared tree are outside that test
snapshot and were not overwritten.

Independently reran 100 offline random searches per environment (seeds 0–99):
25/98/72 successes, matching Adem. Exact probabilities are 25.7369/99.4265/73.5723%.
Fluoride-first first succeeds at queries 3/1/40. Scripted full ten-query runs of
upfront/sequential/iterative/shuffled generated 93 inspected prompts across the
three frozen environments; none contained the checked internal diagnostic fields
and every task showed the correct electrolyte. These are offline workflow checks,
not live LLM results. Verified the original expansion artifact manifest, the new
freeze manifest, all table hashes and unchanged scientific fields.

**Human resource decision:** Davide explicitly chose “Smoke batch only; review
measured cost before production” in the asynchronous question. Record approval
for approximately 30 smoke calls only; production is NOT authorized. Recommend
one upfront run at budget 10 and three sequential-arm runs at budget 3 per
environment, seed 999: still 30 calls before retries, now testing the full
shortlist output cap. Adem owns execution to prevent duplicate live batches.
He must report actual usage, retries and projected production cost before the
roughly 2,790-call production decision. Keep smoke runs outside all results.

Wrote ENVIRONMENT_FREEZE_REVIEW.md and SYNC_ADEM_7.md and aligned REPORT.md and
WORK_DIVISION.md. No new paid/API/MLIP or cluster calls occurred in this review.
These new changes remain local and uncommitted; Claude separately published
7249e7a during the session (local origin/davide now matches it). Next: publish
this scoped package, finalize the protocol with frozen hashes, verify the merged
runner, execute the approved smoke batch once, then seek production approval
using measured cost. PET-MAD thickness work continues independently.

## 2026-10-21 — Clarify Adem's scientific brief and cost request

**Branch:** `davide`. The user asked for a clear explanation to Adem of what we
want to do, why, and how to assess expense. Expanded SYNC_ADEM_7.md with the
scientific question: whether feedback helps the LLM revise chemical hypotheses
and select the next coating beyond prior knowledge, using the differing sulfide
and LLZO chemistry as a test. Restated all five arms, three environments, fixed
settings and primary/secondary measures; distinguished within-run revision from
cross-environment transfer.

Added a concrete cost-report checklist: verify the returned model/account rates,
measure input/output/cache usage and retries, report actual versus estimated
smoke cost, and project expected/conservative production cost by arm/environment
and total. The 2,790 calls and 25M/2.4M token counts remain planning estimates,
not dollar quotes or spending caps. Davide's approval remains smoke only; Adem
must stop afterward and request production approval using the measured costs.
No external message was sent: the note is saved locally and the chat response
provides a copyable message for the user to forward.

Documentation-only change; checked the diff and consistency with the existing
protocol/resource decision. No tests rerun, API/LLM calls, MLIP calculations,
package changes, commit or push. Concurrent physics changes were left untouched.

## 2026-10-21 — Electrolyte substrate thickness and constraint check at four layers

**Branch:** `davide`. Follows SYNC_CLAUDE_2.md; `7249e7a` was pushed first. Details:
[CONTACT_PROTOCOL.md](CONTACT_PROTOCOL.md).

**Code.** `bottom_fixed_indices` gains `depth`. `run_petmad_interface.py` gains
`--fixed-depth` (mutually exclusive with `--fixed-fraction`, whose default stays 0.34) and
`--registry X Y GAP`, which holds the registry while still saving the scan and records the
scan optimum. It also records fixed indices and slab spans. `build_contact.py` gains
`--substrate-layers`/`--film-layers`. New test: a constant depth does not grow with slab
thickness. 115 tests pass.

**Thickness** (seed 0 Cl cut, LiNbF6(001), same transformations, strain and 170.708 Å² area;
fixed depth 3.257602 Å = 38 atoms throughout; registry (0,0,2 Å); PET-MAD S 1.6.0, checkpoint
`3f52e97c…`, CPU, 4 threads, 3 concurrent):
- 2 layers (440 atoms): W_adh 1.3291, W_sep 2.5190 J/m². This reproduces the archived
  0.34-fraction run, with an identical mask.
- 3 layers (492): 1.4644 / 2.8052. The unrelaxed scan optimum moved to (0,0.5), but by only
  0.0177 J/m².
- 4 layers (544): 1.5317 / 2.8579.

From 3 to 4 layers the changes are +0.067 and +0.053 J/m², below the 0.1 tolerance, so
**four layers is chosen**. W_adh is still rising. Formal substrate polarity grows with
thickness (0.174 / 0.260 / 0.347 e/Å) because the Cl cut's two faces are inequivalent.

**Constraint at four layers** (depths declared before running: 1.628801 / 3.257602 /
6.515204 Å = 26 / 38 / 68 atoms): W_adh 1.5069 / 1.5317 / 1.5549, W_sep 2.8448 / 2.8579 /
2.8688 J/m². Spreads 0.048 and 0.024 J/m²; criterion met. The separated-slab Li/Cl
rearrangement (Li RMS about 0.6 Å) persists at every thickness and depth.

**Cost:** 1,827 calculator calls in the five MLIP runs plus 10 separation single points.
Evidence: `data/petmad/thickness_v1/` (builds and runs); the inspection replays identically.
No LLM, MP or cluster calls. **Next:** cathode coating thickness, then vacuum/registry for
both contacts, then the seed-4 sensitivity.

## 2026-10-21 — Publish frozen inputs and smoke-only protocol sign-off

The user relayed Adem's request to publish the frozen inputs and clarify approval,
while the requested progress presentation remains active. Fetched his 76c493b
usage-report commit and reviewed the pricing arithmetic. The official Anthropic
pricing page agrees with USD 0.10/M input and 0.50/M output for Haiku 5.5 prompts
up to 100k tokens; cache reads/writes have separate rates. The existing planning
estimate implies about USD 3.70 before retries/account-specific adjustments.
No Console access or contract terms were verified; no billed-cost claim is made.

Created ENVIRONMENT_PROTOCOL.md from Adem's draft, recording all three exact
frozen hashes, preserving the agreed scientific design and marking Davide-side
review/smoke authorization as recorded by Codex. Production approval remains
unchecked. The protocol incorporates the ten-candidate upfront smoke test,
three-query sequential arms, and the requirement to report measured cost before
any production launch. Rechecked every source scientific field and all 423 rows:
no changes. Only frozen status, provenance metadata and table hashes differ.

The complete current suite passes 127 tests with existing ASE/spglib warnings.
Claude independently committed b51c14e during prior coordination; that committed
thickness work is preserved and accompanies the normal branch push. This package
publishes the previously reviewed freezer, snapshots, analysis guard, dependency
pins and handoff/report files. No LLM/MP/MLIP or cluster calls were launched here.
Credential scans and explicit staging precede the push; .env remains ignored.
Next: Adem verifies the frozen runner and performs the single approved smoke
batch; Codex continues the progress deck with the original feedback results,
expanded landscape and current interface evidence separated clearly.

## 2026-10-21 — Cathode coating thickness

**Branch:** `davide`. Follows SYNC_CLAUDE_3.md. Details: [CONTACT_PROTOCOL.md](CONTACT_PROTOCOL.md).
LiCoO2(001) | LiNbF6(001) with 2, 3 and 4 coating layers (504 / 600 / 696 atoms, cap 800).
Everything else is unchanged: termination, substrate (2 layers, 312 atoms), transformations,
strain, area, vacuum, PET-MAD S 1.6.0 (checkpoint `3f52e97c…`), FIRE 0.05 eV/Å. Registry held
at (0,0,2 Å), scan saved. The 0.34-fraction constraint was verified to select the same
104 substrate sites by substrate-relative correspondence, because global indices change with
coating thickness. The substrate is identical up to a rigid z shift (0.75 / 1.29 Å).

Results: W_adh 3.4794 / 3.5855 / 3.6001 J/m²; W_sep 5.0551 / 5.1090 / 5.1275 J/m². From 3 to
4 layers the changes are +0.015 / +0.019 (< 0.1), so **four coating layers is chosen**. The
2-layer run reproduces the archived run (≤ 2.4×10⁻⁴ eV). The separated LiNbF6 relaxes by
1.44–1.49 J/m² at every thickness. Fixed-atom forces stay at 2.446 eV/Å. The coating's formal
polarity grows 0.613 / 0.920 / 1.226 e/Å. All 9 relaxations converged, with no overlaps.
426 calls plus 6 single points. Evidence: `data/petmad/cathode_thickness_v1/`; the inspection
replays identically.

Also reworded the electrolyte conclusions per the review: "insensitive within the tested
constraint bracket at 0.1 J/m²"; the unrelaxed registry scan does not establish relaxed
equivalence; the persistent surface rearrangement does not rule out other finite-thickness
effects. No code changes; no LLM, MP or cluster calls. **Next:** vacuum and relaxed registry
checks for both contacts, then seed 4. The cathode substrate thickness is still untested.

## 2026-10-21 — Vacuum check and remaining thickness directions

**Branch:** `davide`; `84f1c76` was pushed first. Follows SYNC_CLAUDE_4.md. Details:
[CONTACT_PROTOCOL.md](CONTACT_PROTOCOL.md).

**Vacuum** (`scripts/vacuum_check.py`, new). Working geometries: cathode 2 + 4 layers,
electrolyte 4 + 2 layers. Cell z lengthened to 15 / 20 / 25 Å vacuum without scaling
coordinates; single points on the relaxed interface, the relaxed references and the rigid
fragments (30 total). W_adh and W_sep change by ≤ 4.4×10⁻⁵ J/m², and the free forces are
unchanged and within target, so no relaxation was needed. Empty gaps are 15.5–25.7 Å. This is
expected: PET-MAD's 8.0 Å neighbour list means no edge crosses the vacuum (interaction range
24 Å via message passing). It is an image-isolation check only, not a treatment of polar
electrostatics.

**Cathode substrate thickness** (coating 4 layers; LiCoO2 2 / 3 / 4 layers = 696 / 852 /
1,008 atoms; frozen depth 9.10044154 Å = the same 104 physical atoms; cap 1,200): W_adh
3.6001 / 3.6011 / 3.6009, W_sep 5.1275 / 5.1278 / 5.1275 J/m². Flat; two LiCoO2 layers kept.

**Electrolyte coating thickness** (argyrodite 4 layers; LiNbF6 2 / 3 / 4 = 544 / 712 / 880
atoms; depth 3.257602 Å = 38 atoms): W_adh 1.5317 / 1.6198 / 1.6329, W_sep 2.8579 / 2.9525 /
2.9669 J/m². Final changes +0.013 / +0.014, so **four coating layers is chosen**.

Working values: cathode 3.60 / 5.13 J/m² (696 atoms); electrolyte 1.63 / 2.97 J/m² (880
atoms). The constraint brackets were measured at two coating layers only. Both contacts are
formally polar and provisional. All 12 new relaxations converged, with no overlaps; 1,054
calls plus 8 single points (PET-MAD S 1.6.0, checkpoint `3f52e97c…`, CPU). Evidence:
`data/petmad/vacuum_v1/`, `data/petmad/thickness_gaps_v1/`; inspections replay identically.
No LLM, MP or cluster calls. **Next:** relaxed checks of a declared set of competing
registries, then the seed-4 electrolyte comparison.
