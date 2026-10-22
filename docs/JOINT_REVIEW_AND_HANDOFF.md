# Code, evidence and work-division review

**Current assignment amendment:** [LLM_PETMAD_PILOT_PLAN.md](LLM_PETMAD_PILOT_PLAN.md)
and notes [Adem 12](https://github.com/DavideTisi/interphAIse/blob/786029128ad234e34aaa880d2bff5250c79277ed/SYNC_ADEM_12.md) / [Claude 9](https://github.com/DavideTisi/interphAIse/blob/786029128ad234e34aaa880d2bff5250c79277ed/SYNC_CLAUDE_9.md) now govern
selection for the three-coating follow-up. F1–F4 and the evidence checks below
remain unchanged. The LLM will select two new coatings sequentially after the
known reference, rather than evaluate a fully predetermined cohort.

21 October 2026. Davide requested a review of Adem's branch and Claude's
PET-MAD work before dividing the next tasks. Reviewed `davide:8975d4b` and
the freshly fetched `work/agent-experiments:b8b1392`. No implementation fix,
actual branch merge, live API call or new MLIP calculation was made here.

**The archived headline results survive this review.** The main actionable
findings are missing safeguards around future calculations and analysis,
rather than an observed numerical error in the completed production data.
Fix them before using these entry points for a new comparison. The review is
bounded to the discovery runner, analysis/provenance path, interface/bulk
workflow and relevant tests; it is not an exhaustive audit of every module.

## Findings, ordered by priority

### F1 — P1: the older interface pipeline ignores relaxation failure

Location: `interphaise/tools/energetics.py:57–64,117–135`, reached through
`interphaise/orchestrator.py:stage_pair`. This is shared legacy code, not the
new converged-run implementation used for Claude's archived pilots.

`relax()` discards the return value of `FIRE.run`, returns an energy even when
the step limit is exhausted, and propagates it into W_adh. The rules judge
checks geometry and adhesion but has no force/convergence field to reject.
Thus an unconverged candidate can receive an apparently usable ranking.

**Reproduced offline:** a one-atom harmonic calculator with zero optimization
steps returns energy 0.5 eV and force 1 eV/Å despite a target of 0.01. The newer
`relax_record` correctly returns `converged=False` for the same example.
The numerical values are test fixtures, not PET-MAD results.

**Action — Claude:** use one convergence-aware implementation across entry
points, or explicitly disable the legacy quantitative path. Propagate finite
energy/force, free-force, step-exhaustion and post-relaxation geometry gates to
the caller. A failed candidate must have no validated adhesion/rank and must
remain in failure accounting. Add an integration regression covering an
exhausted relaxation reaching the orchestrator. Do not simply teach an LLM
judge to recognise an error that should be a deterministic gate.

**Impact on existing results:** none found. The current archived interface
study uses `run_petmad_interface.py` and `relax_record`, which already gate
the reported W_adh. The frozen discovery experiment uses thermodynamic tables.

### F2 — P2: separation and multistart can mix checkpoint energy references

Locations: `scripts/fixed_geometry_separation.py:27–40`,
`scripts/multistart_bulk.py:53–59`; review `scripts/vacuum_check.py` with them.

The separation script hashes its supplied model but never compares that hash
with the joined run. It can subtract an old joined energy from new fragment
energies produced by another checkpoint. The multistart script similarly
compares newly computed energies against saved symmetric/seed-0 energies
without enforcing a matching checkpoint. Matching a filename is insufficient.

**Reproduced offline:** a copied cathode archive, a deliberately different
checkpoint byte string and a fake calculator were accepted; two fragment
calls occurred and a separation JSON was written despite the hash mismatch.
No model was loaded and the real archive was untouched.

**Action — Claude:** validate the supplied hash against each reference before
calculator construction or output writes. Require valid/converged inputs for
derived observables, or produce a distinctly labelled diagnostic without a
validated work. Validate label counts/order, cell/area and finite values too.
Use a common checkpoint-validation helper, and add wrong-hash and invalid-run
tests. Keep device differences explicit; they are not a substitute for model
identity checks.

**Impact on existing results:** all 37 checked interface result packages have
the same recorded checkpoint, and every checked rigid-separation hash matches
its joined run. Both multistart archives use that hash as well. No mixed-model
result was found.

### F3 — P2: `--production` is not yet a complete evidence-validation gate

Locations on Adem's branch:
[`analyse_discovery_experiment.py:84–110`](https://github.com/DavideTisi/interphAIse/blob/b8b139212430751857f09a05be6e22ae5766b832/scripts/analyse_discovery_experiment.py#L84)
and
[`analyse_environment_study.py:69–86`](https://github.com/DavideTisi/interphAIse/blob/b8b139212430751857f09a05be6e22ae5766b832/scripts/analyse_environment_study.py#L69).

The loader checks run identity, declared hashes, lengths and frozen table
integrity, but trusts the stored history outcomes. The production check fixes
environments, seeds, arms, budget and the Holm family, but does not enforce
the approved model, temperature, output limit or prompt/workflow version.
Settings are compared between manifests within an environment, rather than
against a full frozen production specification and per-call metadata.

**Reproduced on temporary copies:** set manifest temperatures to 0.0 instead
of 1.0 and change one sulfide upfront history result to `acceptable=True`,
leaving declared hashes unchanged. The production check still returns no
problems and reports upfront 1/30 instead of 0/30. Real files were untouched.
The two omissions should have separate regression cases when fixed.

**Action — Adem:** replay each charged query through `BenchmarkQueries` before
analysis, check proposal/result correspondence and derived traces, and enforce
the complete frozen settings against manifests and recorded call metadata.
Make the archived-workflow/hash boundary explicit. The existing independent
replay supplies a model for this check. Continue allowing failed runs in the
denominator according to the protocol; validation must not silently remove
them or relax the production requirements.

**Impact on existing results:** none found. Fresh replay of every real run
matches its full saved state and prompt history. This finding concerns what
the standalone production analyser currently accepts, not a corrupted cohort.

### F4 — P2: HTTP retries are absent from the reported call accounting

Location: `interphaise/llm.py:57–78`, consumed by Adem's `usage_report.py`.
This is shared client code. The retry loop handles HTTP 429/5xx but saves only
the successful response metadata. One proposal attempt can therefore contain
multiple transport attempts while the report counts it as one call.

**Reproduced with mocked HTTP:** 429 followed by success makes two transport
attempts, one logical call and no retry count in metadata. No network call
was made. Separately, two malformed production responses were not retained
as raw text, so replay correctly uses their recorded exceptions.

**Action — Adem:** distinguish proposal attempts, HTTP attempts, format
retries and transport retries; record response/request IDs and final errors
without credentials or headers. Report unknown historical HTTP retry counts
as unknown. Retain malformed response text in a deliberate, bounded logging
field if full future parsing replay is required. Do not fabricate missing
historical response bodies or re-query the model to replace them.

**Impact on existing results:** the 2,800 recorded proposal attempts and usage
totals reproduce. They are not an independently verified count of all HTTP
requests. The approximately $3.63 remains an estimate from recorded usage,
not an invoice; the logs cannot resolve unrecorded transport behaviour.

## Scientific interpretation and smaller improvements

- **Preserve the environment-specific outcome.** Sulfide supports the feedback
  claim; chloride is near ceiling; LLZO favours random over every LLM arm by
  observed acceptance. LLZO iterative versus shuffled is not significant
  after Holm correction. Acceptability is not discovery of the best material.
- **Update Adem's new note using SYNC_ADEM_10.md.** The broad oxyhalogen review
  set is five IDs; four have directly checked supplier oxidiser classifications.
  Li5IO6 is an orthoperiodate family flag. Avoid claiming that all five are
  established unusable coatings or that the model deliberately avoided hazards.
  Random has 18 successful runs with an unflagged acceptable hit versus
  iterative's 12, so the flagged compounds do not explain the whole difference.
  This remains descriptive and post hoc; keep the frozen primary outcome.
- **Keep physical sensitivities separate.** Both contact models are formally
  polar; vacuum isolation does not validate electrostatics. The 0.12/0.16 J/m²
  seed difference mixes bulk arrangement and construction changes. The selected
  cathode registry did not itself receive every earlier convergence bracket.
- **Clarify the separated-slab energy difference.** The runner relaxes the
  separated slabs from the original built geometry, while rigid W_sep splits
  the relaxed joined contact. Their energy difference is exactly a difference
  between these reference states; no relaxation trajectory from each rigid
  fragment to the saved free slab was computed. Use that precise description
  rather than implying the observed dynamics follow that release path.
- **Archive completeness:** two compact Niflheim smoke packages retain records
  but omit their six final structure files. This limits independent force
  verification of those smoke jobs. The five later batch-1 jobs have full
  structures, and their quantitative conclusions do not depend on this gap.
  Retrieving the missing smoke files is optional archival housekeeping.
- **Avoid equal layer counts across coatings.** The new comparison needs common
  physical construction rules and a bounded geometry gate; see
  [MLIP_COMPARISON_PLAN.md](MLIP_COMPARISON_PLAN.md). Current LiCaAlF6 and
  phosphate matching findings are not permission to silently change the
  shortlist, constraints or scientific objective.

## Checks completed

Machine-readable evidence: `data/reviews/joint_code_review_20261021.json`.

- Full offline tests: **145 passed** on `davide`, **158 passed** on Adem's
  latest committed branch, **159 passed** in an isolated combined-tree export.
  All used the local pinned environment. Existing ASE/NumPy and spglib
  deprecation warnings remain; there was no second-environment test here.
- Fresh replay: **450 runs, 4,500 charged outcomes, 2,800 proposal attempts**.
  Prompts, parsed-response/exception handling, traces and shuffled mappings
  reproduce the complete saved states. This is deterministic archive replay,
  not new stochastic inference or a reconstruction of HTTP retries.
- The current production analysis reproduces all primary counts and six Holm
  contrasts. The scientific archive and core experiment/analysis code are
  unchanged between `06a4271` and `b8b1392`.
- Checked **37 interface result packages**: adhesion arithmetic agrees.
  **35 have complete structures**, supplying **105 final relaxations** whose
  saved raw forces, fixed masks and energies agree with their convergence
  records. Rigid-separation arithmetic and matching checkpoint hashes pass
  wherever those outputs are present. No fresh PET-MAD energy was evaluated.
- Git merge preview of the two committed heads has **one conflict, in
  DEVELOPMENT_LOG.md**. Code merges cleanly and the combined tests pass;
  the conflicting documentation still needs both histories retained. The
  preview excluded the current uncommitted planning/review documents and did
  not move a branch, edit the checkout or merge to main.

## Work division from this checkpoint

**Scope update, 21 October:** Davide confirmed that the three-coating
comparison is the next deliverable. The recipient-specific instructions in
[SYNC_CLAUDE_8.md](https://github.com/DavideTisi/interphAIse/blob/786029128ad234e34aaa880d2bff5250c79277ed/SYNC_CLAUDE_8.md) and [SYNC_ADEM_11.md](https://github.com/DavideTisi/interphAIse/blob/786029128ad234e34aaa880d2bff5250c79277ed/SYNC_ADEM_11.md)
carry this review into implementation and the bounded campaign.

| Owner | Owns next | Deliverable / acceptance evidence |
|---|---|---|
| **Adem** | F3 analysis validation, F4 client/accounting, new MLIP campaign validator and comparison figures, slides | Offline failure tests; unchanged production results; validated three-coating table/figure generated from the manifest; slides retain LLZO and exact-random context |
| **Claude** | F1 convergence integration, F2 checkpoint/reference validation, construction and full bounded three-coating campaign | Focused safeguards pass; frozen build manifest before interface energies; two documented contact outcomes per selected coating, planned sensitivity checks and complete archives |
| **Davide, with Codex** | Scientific scope and comparability decisions, independent review, integration/release, overall narrative and viewer | Apply the declared surface/bounds/fallback rules, review fixes and results, preserve archives/logs and run combined checks; own the release snapshot |

Adem should continue in `work/agent-experiments`. Give Claude a dedicated
physics branch/worktree (for example `work/petmad-comparison`) for the new
work; this review has not created it. Davide uses `davide` for review and
integration. Assign one owner per changed implementation file. In particular,
Adem owns shared `llm.py`; Claude owns `energetics.py`, relaxation and PET-MAD
scripts. Davide consolidates REPORT.md, WORK_DIVISION.md and the release log.
Each contributor should keep a scoped handoff/log entry for integration,
rather than both editing the same status paragraph concurrently.

**Order:** safeguards, geometry preparation and comparison-analysis development
proceed in parallel. Review safeguards and freeze the three-coating manifest
before interface energies, then complete the bounded campaign and its analysis.
The original shortlist remains the first choice; the updated plan fixes a
LiF-then-LiTaF6 fallback for pre-energy construction failures. Retain failed
members and label any amended cohort. Five final coatings and more LLM cohorts
are outside this assignment. Figures/slides and release preparation proceed
alongside the active materials comparison.

No rerun of the completed 450-run production study is recommended. The
findings above are open assignments, not implemented fixes. These notes are
for Davide to share; no external message was sent to Adem or Claude.
