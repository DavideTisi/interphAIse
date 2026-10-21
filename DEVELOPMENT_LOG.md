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
