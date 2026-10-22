# interphAIse — project report

**Final integration — 22 October 2026:** Both collaborators' completed branches
are combined in `work/final-integration-20261022`, including Adem's `5b76988`
final-index reader fix, his documentation-only `1f7bf11` fresh-environment test
record, and Claude's `1b76eeb` physics release. Adem reports 200 passing tests
on his branch; our integrated tree previously passed 227. The original
presentation data agree with the regenerated analyses. The viewer now selects
all six contacts for the three computed coatings and separates primary evidence
from later robustness; LiF remains uncomputed. [REPRODUCE.md](REPRODUCE.md)
provides one offline command, and [FINAL_INTEGRATION.md](FINAL_INTEGRATION.md)
records tests, provenance and remaining release steps. This supersedes the
integration-pending statements in the historical entries below. No new live
LLM, MLIP or cluster work was performed.

**Viewer launch correction — 22 October 2026:** Open the generated
`runs/structure_viewer.html`, not `scripts/viewer/template.html`. The source
template now displays build instructions instead of empty controls. All three
coating shortcuts load their archived contacts in the generated explorer;
[STRUCTURE_VIEWER.md](STRUCTURE_VIEWER.md) includes the local HTTP launch option
for the in-app browser. Scientific results and saved geometry are unchanged.

**Consolidated results and new presentation — 2026-10-22:** The
[results synthesis](RESULTS_SYNTHESIS_2026-10-22.md) now joins the 50-structure
benchmark, 450-run environment study and completed three-coating PET-MAD pilot.
The [new deck](presentations/results_2026-10-22/interphAIse_results_synthesis_2026-10-22_v2.pptx)
contains 18 main slides and six backups with source notes and editable evidence.
The LLM's role is scientific selection, feedback interpretation and prospective
prediction. Correct feedback helps on sulfide, but random wins on LLZO and
chloride is at ceiling (all LLM arms 30/30, sampled random **29/30**).
The physical pilot validates both Ta forecast ranges and contradicts both Ca–Al
ranges; candidate order stayed unchanged. We achieved a rigorous version of
the agreed cheap benchmark plus three-coating follow-up, not general expensive
search superiority or a validated materials winner. Branch integration, the
final-index reader patch and viewer synchronization remain separate pending
work. The older checkpoints below are historical. No new paid or physics run
was made for the synthesis.

**Pilot complete and independently reviewed — 2026-10-22:** Physics `1b76eeb`
and agent `c0a0546` preserve the decision snapshots and evaluated primary rows.
W_adh cathode/electrolyte is **3.617/1.633** for LiNbF6, **3.339/1.577** for
LiTaF6 and **1.427/0.744 J/m²** for LiCaAlF6. Both LiTaF6 forecasts held;
both LiCaAlF6 forecasts missed; weaker contact was correct twice. Candidate
order did not change with feedback. The summary misread the weaker-contact
field as a registry minimum; retain that response with an explanatory correction.
Nb/Ta seed sensitivities exceed their small primary difference; Ca's electrolyte
thickness and bulk sensitivity remain unquantified. All cells remain formally
polar. Verified 26 new jobs, 6,632 runner calls plus 52 separation points,
25.4 min runner time versus 47.5 min summed Slurm elapsed time; the pilot used
5 HTTP attempts, about USD 0.00597 at recorded rates. The summary-only prompt
limit amendment is archived. Reader compatibility with the final index needs
the tested patch in [FINAL_PILOT_REVIEW.md](FINAL_PILOT_REVIEW.md); branch
integration and final viewer updates remain pending; the consolidated deck above
now incorporates these results. No further physics
or paid LLM run is needed for this bounded pilot.

**First prospective forecast checked; third coating selected — 2026-10-22:**
Independently verified `9b59000`/`d5ab477`. LiTaF6 gives selected-primary W_adh
**3.339 J/m²** at the cathode and **1.577 J/m²** at the electrolyte: both fall
inside Haiku's recorded ranges, and the predicted weaker contact is correct.
This supports one analogy-based forecast. Choose-3 selected **LiCaAlF6**, already
next in the original shortlist and the only acceptable unevaluated candidate;
the sequence did not change with feedback. Its forecasts are cathode 3.0–3.8,
electrolyte 1.4–1.9 J/m², electrolyte weaker. Four of ten HTTP attempts are used,
about USD 0.00334 at the recorded rates. LiNbF6's 0.056 J/m² weaker-contact
advantage over LiTaF6 is below the numerical tolerance and known reference
sensitivity, so it does not establish a robust winner. Claude's six LiCaAlF6
jobs have completed in Slurm; their physical package awaits validation. A
test-fixture regression found in this review has a tested patch for Adem.
See [review and next steps](SYNC_ADEM_15.md) for evidence and limits.

**LiTaF6 primary jobs completed — 2026-10-22:** Claude already submitted the
six selected-coating runs as Niflheim jobs **11017049–11017054**, source
`207f879`. All six completed with exit code zero in 2:44–2:57 each on RTX
3090s; all 18 relaxations report convergence. A read-only check confirms the
frozen manifest and choice hashes, recorded registries, depths, atom/fixed
counts and checkpoint/device metadata. The runs report 1,502 calculator calls,
plus 12 rigid-separation single points. Claude assembles the package; Adem's
full manifest/source validation must pass before choose-3. This is completion
and metadata verification, not approval of the physical comparison. No duplicate
jobs or model calls were launched. Evidence:
[completion check](data/reviews/litaf6_primary_completion_20261022.json).

**First live choice archived — 2026-10-22:** Verified Adem's published
`1875726`: Haiku selected **LiTaF6** after the LiNbF6 feedback and predicted
W_adh ranges of **3.2–3.9 J/m²** (cathode) and **1.4–1.9 J/m²** (electrolyte),
with electrolyte the weaker contact. Three of ten HTTP attempts are charged;
logged usage gives about USD 0.00162 at the recorded list rates. State, record
and feedback hashes verify; an offline resume stops at pending physics without
calling a model. The shortlist is unchanged from the prior, so this is a
prospective forecast, not yet a demonstrated feedback-driven selection gain.
Six LiTaF6 primary jobs are the next dependency. Adem reports `d1ec1b0` and
77 passing tests for the remaining manifest checks, but that commit was not
yet available on the shared branch at review. See [live handoff](SYNC_ADEM_14.md)
and [audit](data/reviews/live_selection_review_20261022.json). No new live calls
or physical calculations were launched by Codex during this verification.

**Live pilot approved — 2026-10-22:** Davide explicitly approved Adem starting
the reviewed prior and first selection, with **ten HTTP attempts total** across
the pilot and a **USD 0.05 allowance** at the reported rates. Adem owns the live
execution and archives the selected ID, predictions and hashes before Claude's
six primary jobs. The normal physics pause and manifest/source validation
requirements before choose-3 remain. Approval is recorded; live execution and
its outcomes are not yet confirmed. See [approved handoff](SYNC_ADEM_14.md).
Codex has not launched a duplicate run.

**Initial live selection ready for approval — 2026-10-22:** Reviewed Adem's
`f8abbc0`; 188 tests pass and the completed 450-run analysis is unchanged.
The earlier cap/resume, invalid-value and prediction-history regressions pass.
With Claude's real campaign files, the mocked command makes prior and choose-2,
then exits at pending physics. An independent preflight checks the exact
manifest/index coverage, all prospective build identities and the reference
source hashes, physical fixed masks and free forces. Recommend starting only
the initial live selection on that package after approval, followed by the
planned physics pause. Generic manifest-derived coverage and source-identity
checks still need tightening before choose-3. The 10-attempt cap is enforced;
the quoted USD 0.030 is an estimate, not a proven dollar ceiling. See
[scoped readiness handoff](SYNC_ADEM_14.md) and
[audit](data/reviews/live_pilot_review_20261022.json). No live calls were made.

**Frozen physical menu reviewed — 2026-10-22:** Claude's `38e4872` supplies
LiNbF6 plus the three intended alternatives, frozen primary builds/registries
and index. Independent checks confirm the manifest hash, all six primary input
hashes and their atom/fixed-mask counts; 163 tests pass. Adem's unchanged
`2d2cac3` still needs the readiness fixes and support for both unavailable-job
statuses. A producer integrity mismatch is detected but still leaves a bundle
consumable; this must remain distinct from genuine failed calculations.
Four optional reference consistency jobs are recommended as separate,
lower-priority robustness work after primary scheduling; they are not launched
or approved by this review. Live-pilot approval is also pending. See
[Claude 11](SYNC_CLAUDE_11.md) and the
[saved audit](data/reviews/frozen_menu_review_20261022.json).

**Pilot readiness reviewed — 2026-10-22:** Adem's `2d2cac3` passes 183 offline
tests; independent production replay preserves all 450 runs and planned
comparisons. Three remaining pilot gaps were reproduced with temporary data
and mocked transport: the prompt bypasses source validation, the 10-HTTP cap
can be exceeded across errors/resumes, and later prompts omit earlier model
predictions. Missing successful-call metadata also passes the new F3 check.
These are implementation safeguards to finish, not evidence that the genuine
scientific results changed. The intended amended menu is still LiNbF6 plus
LiTaF6, LiF and LiCaAlF6, pending Claude's final manifest. The tiny API estimate
is conditional on token assumptions; live-pilot approval remains pending.
See [Adem's focused handoff](SYNC_ADEM_13.md) and
[saved review evidence](data/reviews/adem_pilot_review_20261022.json).
No live LLM/PET-MAD calculation, cluster action or code merge occurred here.

**Construction screen reviewed; cap amended — 2026-10-21:** Reviewed Claude's
`work/petmad-comparison:49daa72` and reproduced 157 passing tests. Independently
rebuilt LiCaAlF6(100) against both contacts without a potential: its 1,212-atom
electrolyte cell passes all geometry gates when the uniform cap becomes 1,250.
The original screen is retained; this pre-energy resource amendment is applied
to all candidates, with other rules and material/job budgets unchanged. Intended
menu: LiNbF6 reference plus LiTaF6, LiF and LiCaAlF6, pending final manifest.
The next LiCaAlF6 film-thickness increment is 1,302 atoms and remains unavailable,
not a passed sensitivity test. The real LiNbF6 feedback example's five registry
values and hash check out. Offline mutation tests exposed remaining assembler
gaps in coverage, comparable run identity and work arithmetic; failed-run cost
accounting also needs correction before live use. See
[decision and follow-up](SYNC_CLAUDE_10.md) and
[saved audit](data/reviews/claude_screen_review_20261021.json).
F1/F2 are implemented on Claude's branch; it has not been merged here. No new
interface energy, live LLM call or cluster action occurred in this review.
**LLM–PET-MAD pilot complete — 2026-10-22:** live, Haiku 5.5. It used 5 of 10 HTTP attempts, about USD 0.006 at list price (not billed).
- **Forecasts:** both LiTaF₆ W_adh ranges were supported; both LiCaAlF₆ ranges missed (cathode 1.43, electrolyte 0.74 J/m²). The weaker contact was correct for both.
- **Order:** the candidate order was unchanged by feedback.
- **Correction:** `min_W_adh_J_m2` is the weaker of the two selected contact values, not the minimum across registries. Haiku's suspicion arose from misreading that definition. The field rename is kept for a future protocol version.
- **Final ranking:** LiNbF₆ > LiTaF₆ > LiCaAlF₆ > LiF. This is the model's assessment: LiF was not physically evaluated, and the small LiNbF₆–LiTaF₆ difference does not establish a robust winner.
- **Record:** the summary prompt first stopped, uncharged, at the 16,000-character bound. A hashed summary-only 20,000 bound was recorded, and the original prompts, responses and state are preserved.
- **Links:** [interpretation](data/experiments/llm_petmad_pilot_v1/INTERPRETATION.md), [generated report](data/experiments/llm_petmad_pilot_v1/report_live/report.md), [slide](presentations/interphAIse_llm_petmad_pilot_2026-10-22.pptx). This supersedes the "no pilot implementation" status below.

**Deadline plan refined — 2026-10-21:** The pilot now uses validated primary
registry results for each decision; declared sensitivity checks can run in
parallel or afterwards and remain explicitly pending until complete. LiNbF6's
sensitivity is material-specific context, not a noise bound for new coatings.
Require pre-energy W_adh ranges for both contacts and a weak-contact prediction.
Disable/test the unsafe legacy F1 route for now; F2 remains mandatory. The
execution plan sets Thursday 10:00/12:00 progress/fallback checkpoints, a 20:00
slide/writeup freeze and Friday 00:30 submission target before the user-provided
23 October 02:00 CEST deadline. A completed reviewed pilot gets one slide;
otherwise report future work and only tests actually performed. See the updated
[pilot plan](LLM_PETMAD_PILOT_PLAN.md) and recipient handoffs. These are plan
changes, not implemented fixes, new calculations or scheduled automations.

**LLM–PET-MAD pilot plan amended — 2026-10-21:** Davide clarified that the
new coating exploration should exercise the LLM's hypothesis revision. The
active plan uses the existing LiNbF6 evidence and two new coatings selected
sequentially after validated physical feedback. Claude prepares a bounded
feasible menu and owns calculations; Adem owns the resumable loop, validation,
cost estimate and decision/comparison figures. Freeze thermodynamic/adhesion
trade-off definitions and the protocol before new energies; retain the initial
shortlist as a descriptive decision comparison. Three material slots cannot
establish search superiority, and uncomputed alternatives have no measured
counterfactual outcome. See [pilot plan](LLM_PETMAD_PILOT_PLAN.md),
[Adem 12](SYNC_ADEM_12.md) and [Claude 9](SYNC_CLAUDE_9.md). This supersedes
the fixed-cohort/no-new-LLM direction below. It is a planning amendment only:
no pilot implementation, new live calls or calculations have been performed
here. The completed 450-run experiment and scientific archives are unchanged.

**Three-coating campaign directed — 2026-10-21:** Davide confirmed the
three-coating comparison as the next deliverable. Start with LiNbF6, LiCaAlF6
and LiZr2(PO4)3 at both contacts, with a bounded geometry gate and a declared
LiF-then-LiTaF6 contingency before interface energies. Claude owns calculation
safeguards, construction and the full bounded campaign; Adem owns discovery
code safeguards plus the MLIP validator, table and figures; Davide/Codex owns
scope, independent review, integration and the viewer. See
[Claude's handoff](SYNC_CLAUDE_8.md), [Adem's handoff](SYNC_ADEM_11.md) and
[the updated plan](MLIP_COMPARISON_PLAN.md). This is physical assessment of a
shortlist, separate from the completed thermodynamic feedback experiment.
The handoffs are written; fixes and new calculations have not been performed
in this planning update. No external message was sent.

**Joint code/evidence review — 2026-10-21:** Reviewed `davide:8975d4b` and
Adem's freshly fetched `b8b1392`. Fresh replay matches all 450 runs, 4,500
charged outcomes and 2,800 recorded proposal attempts; primary results are
unchanged. Checked 37 PET-MAD result packages and 105 available final
relaxations, with no force/energy inconsistency found. The two compact smoke
packages omit their final structures. Offline suites pass 145 tests on davide,
158 on Adem's branch and 159 on the combined committed-tree preview; the
preview has one development-log conflict and is not an actual branch merge.
Four open safeguards concern legacy relaxation convergence, matching model
checkpoints, production-analysis integrity/settings, and HTTP retry accounting.
They do not invalidate the independently replayed archive. See
[review and assignments](JOINT_REVIEW_AND_HANDOFF.md) and
[WORK_DIVISION.md](WORK_DIVISION.md). No implementation fix or new production
calculation was made.

**MLIP comparison feasibility — 2026-10-21:** The proposed three-coating
follow-up is useful but not ready for an unchanged-protocol launch. Offline
geometry checks find a shared LiCaAlF6(100) orientation with exposed Al
coordination to review; LiZr2(PO4)3 has no electrolyte match in the tested
low-index set under the existing 300 Å² cap. The bounded plan budgets a
geometry gate first, then approximately 2–6 GPU-hours and 1–2 working days
for three coatings, conditional on suitable cells. See
[MLIP_COMPARISON_PLAN.md](MLIP_COMPARISON_PLAN.md) and its saved audit.
No new MLIP production, API call or cluster job has started.

**Goals versus results — 2026-10-21:** [GOALS_AND_RESULTS.md](GOALS_AND_RESULTS.md)
compares the 20 October plan with the completed evidence. Feedback improves
sulfide candidate selection, with environment-dependent limits; general search
superiority, best-material discovery and actual compute savings are not shown.
The 141-ID/three-environment benchmark exceeds the original scale, while the
planned 3–5-coating MLIP comparison remains incomplete: physical follow-up covers
one coating's two contacts. This synthesis changes no objective or result.

**Structure viewer current — 2026-10-21:** The shareable offline export now
opens the selected Niflheim cathode registry (1/3, 1/3) and GPU seed-0 electrolyte
reference. Four named evidence comparisons include the completed seed-4 result
with its combined construction-sensitivity caveat. Registry/device labels,
areas, fixed counts and updated protocol limits distinguish the saved runs.
Coverage is 339 geometries, 141 candidate IDs and 35 calculated interface runs.
All twelve viewer tests pass; browser filters/comparisons and the downloaded
cathode XYZ were checked. See [viewer update](VIEWER_UPDATE.md) and regenerate
with `python scripts/build_structure_viewer.py`. No new scientific calculation
was run. Earlier viewer-pending entries below are historical; presentation v4
and the joint branch integration still require their final updates/review.

**LLZO practical-chemistry caveat audited — 2026-10-21:** Five of the 17
acceptable IDs (three LiIO3 polymorphs, LiClO4 and Li5IO6) form an oxyhalogen
review set. Four have supplier oxidiser classifications; Li5IO6 is a periodate
family flag with compound-specific GHS status unverified. Six of random's
24 successful runs found only flagged compounds; 18 also found an unflagged
acceptable candidate, against iterative's 12. This is a descriptive post-hoc
partition, not a changed endpoint. The original 24/30 versus 12/30 result
stands. Iterative adapts late and concentrates on LiAlSiO4 polymorphs; the
traces do not establish deliberate hazard avoidance. The evaluator already
includes self-decomposition and O2 products, so “fully oxidised anions cannot
react” is not the explanation. Benchmark acceptance does not qualify practical
thermal, processing, safety or transport performance. See
[chemistry audit and slide wording](SYNC_ADEM_10.md). Frozen inputs, primary
analysis and slides are unchanged; no new live calculation was run.

**Environment production complete and reviewed — 2026-10-21:** Adem's
`06a4271` archives 450 completed runs executed at `710d346`. Independent
review reproduces all 4,500 charged query outcomes, 2,800 archived prompts,
full run states and shuffled source maps, and the six-test Holm analysis.
Twelve targeted analysis tests pass. Successes (iterative / sequential /
shuffled / upfront / random) are sulfide **20/2/6/0/8**, chloride
**30/30/30/30/29**, and LLZO **12/0/4/1/24**, each out of 30. Iterative beats
both planned controls in sulfide after Holm correction; in LLZO it beats
sequential, but not shuffled at the corrected threshold, and random search
has the higher observed success rate. This is environment-dependent benefit,
not universal search superiority. Usage recomputes to USD 3.6303784 at the
archived rates, not billed cost. See [review and slide handoff](SYNC_ADEM_9.md)
and [overview figure](figures/environment_acceptance_review_20261021.png).
No new live calls or branch merge occurred. Stop data collection and proceed
to presentation/demo updates and joint integration review. Earlier production
pending/approved-only entries below describe their historical checkpoints.

**Niflheim batch reviewed — 2026-10-21:** The bounded five-run batch at
`f1861ef` is complete: all 15 archived relaxations, physical fixed masks,
energy arithmetic, overlap gates and 1,216 calls plus ten separation points
check out. The lowest sampled cathode registry is now (1/3,1/3), at
W_adh / W_sep = **3.61705 / 5.16762 J/m²**. The GPU electrolyte reference is
**1.63339 / 2.96722**, while seed 4 gives **1.51201 / 2.80536**. The differences
(0.12138 / 0.16186) exceed the 0.1 tolerance and measure combined bulk-reference
and interface-construction sensitivity, not an isolated disorder effect or
statistical error bar. Both contacts remain formally polar and provisional.
Recommend publishing the three commits plus the reviewed formatting/docs
and stopping this batch; see [SYNC_CLAUDE_7.md](SYNC_CLAUDE_7.md).
The viewer's current-cathode pointer and presentation v4 still need updating.
No new MLIP/LLM run or push occurred in this review. Adem's environment
production remains approved and independent.

**Final-geometry review — 2026-10-21:** Reviewed Claude's `97cf4af` through
`dc62dfe`. Saved forces/energies and accounting support 30 converged
relaxations and final-geometry constraint spreads of 0.0133 J/m² (cathode)
and 0.0482 (electrolyte) in W_adh. The final 880-atom vacuum check passes.
The half-supercell cathode offsets were redundant: the earlier relaxed scan
sampled one physical registry. The electrolyte has two sampled registries,
with W_adh 1.631–1.633 but W_sep 2.967–3.065 J/m². Both contacts remain
formally polar and provisional. The 504-atom Niflheim smoke reproduces local
W_adh within 0.0002 J/m² on CPU and GPU. Recommend the bounded seed-4 and
distinct-cathode-registry batch with matching GPU references in
[SYNC_CLAUDE_6.md](SYNC_CLAUDE_6.md). Fixed a runner bug that would reject
explicit off-grid offsets; eight regression tests pass. No new MLIP/API run
or push occurred here. Earlier pending constraint/vacuum statements below
are historical checkpoints. Adem's environment production remains approved.

**Environment production results — 2026-10-21:** All 450 frozen runs completed (execution commit `710d346`, 2,800 calls, ≈ USD 3.63 at list price, estimate). Acceptable within 10 queries (n = 30/arm), iterative / sequential / shuffled / upfront / random (exact): Li6PS5Cl 20/2/6/0/8 (25.7%); Li3InCl6 30/30/30/30/29 (ceiling, declared in advance); LLZO 12/0/4/1/24 (73.6%). Paired exact McNemar, Holm over six: iterative > sequential in Li6PS5Cl (Holm p 4.6e-5) and LLZO (0.0024); iterative > shuffled in Li6PS5Cl (0.0024), not in LLZO (0.17). In LLZO random search beats every LLM arm. Feedback consistently beats no feedback, but where Haiku's chemical prior is wrong (LLZO) it stays below random within 10 queries. Archive and README: `data/experiments/environment_v1/`; note: `SYNC_DAVIDE_5.md`.

**Environment production approved — 2026-10-21:** Following the measured-cost
review, Davide explicitly said “i approve the production”. The approval covers
the unchanged frozen study: three environments, five arms, 30 repeats, budget
10, seeds 200–229, Haiku 5.5 via direct Anthropic, temperature 1.0 and 4096
output tokens. That is 450 runs and approximately 2,790 LLM calls before
retries. Adem owns execution and may use the commands on his branch in
SYNC_DAVIDE_4.md. The [protocol](ENVIRONMENT_PROTOCOL.md) and
[handoff](SYNC_ADEM_8.md) now record the sign-off. No production run was
launched here; approval does not establish that a run has started. Earlier
smoke-only/pending statements below describe their historical checkpoints.

**Environment production readiness — 2026-10-21:** Reviewed Adem's `0072f3d`
analysis at branch head `710d346` and the smoke archive from `26beb73`.
Eleven relevant analysis tests pass in an isolated snapshot. Recounted 31
smoke calls, one format retry and complete usage records: USD 0.03597 at
current public list rates, not provider-billed cost. The full frozen study
projects to USD 3.68 expected / 5.27 with contingency; USD 9.49 is a high-output
scenario, not an enforced ceiling. Scientific recommendation is to proceed
once Davide explicitly approves production; only smoke is currently approved.
Adem owns execution. See [cost and analysis review](SYNC_ADEM_8.md) for the
complete-study guard and secondary reporting details to finish before final
analysis. No live calls or branch merge occurred in this review.

**Viewer update complete — 2026-10-21:** The offline viewer now includes 278
geometries, with 141 candidate IDs, four battery endpoints, bulk references
and saved interface/slab states. Current contacts use the 696-atom cathode and
880-atom electrolyte. Search/filter and comparison controls retain exact
provenance and provisional labels. Eleven viewer tests and browser interaction
checks passed; no new calculation was performed. See [VIEWER_UPDATE.md](VIEWER_UPDATE.md)
and regenerate the local viewer with `python scripts/build_structure_viewer.py`.
The HTML is an ignored build output; the source and archived inputs are shared.

**Latest contact validation — 2026-10-21:** Reviewed Claude's `d0bd1f3`.
The working cathode remains 696 atoms at W_adh / W_sep = 3.60014 / 5.12754
J/m²; the electrolyte now has four substrate and four coating layers, 880
atoms, at 1.63294 / 2.96690 J/m². Its earlier 544-atom value below is a
thinner-coating comparison. Independent checks reproduce the four new
thickness-run energies, 12 converged relaxation records, physical fixed
masks and 1,054 calls plus eight separation single points. The 30 archived
vacuum points pass the numerical isolation check, at the cathode 2+4 and
electrolyte 4+2 geometries. The final electrolyte has a 15.731 Å empty gap but
no separately archived vacuum sweep. Final-geometry constraint brackets,
relaxed registry comparisons and the seed-4 comparison remain pending;
polarity remains unresolved. Recommend publishing the commit and the bounded
plan in [SYNC_CLAUDE_5.md](SYNC_CLAUDE_5.md). GitHub was at `84f1c76` when
checked; this audit ran no calculation and made no push. Presentation v4
still predates the new contact results. Earlier checkpoints below are history.

**Cathode coating-thickness review — 2026-10-21:** Claude's `84f1c76` selects
four coating layers (696 atoms): W_adh 3.6001 and W_sep 5.1275 J/m², with final
increments 0.0147 / 0.0185 J/m². Independent archive checks confirm all nine
recorded relaxations, energy arithmetic, the same physical 104 fixed substrate
atoms, and 426 calls plus six separation single points. GitHub still points to
`40b80fa` at this review; `84f1c76` remains local. Recommend publishing it and
performing bounded vacuum checks, while explicitly addressing the still
untested LiCoO2 substrate thickness and electrolyte-contact coating thickness
before claiming whole-contact thickness convergence. Both contacts remain
formally polar and provisional. See [current Claude handoff](SYNC_CLAUDE_4.md).
No new calculation or push occurred in this review. The v4 presentation below
predates this cathode result and needs that update in its next revision.

**Scientific presentation — 21 October 2026:** [Main ideas and results](presentations/interphAIse_main_ideas_and_results_2026-10-21_v4.pptx), 16 main slides plus five technical backup slides, focused exclusively on interphAIse, with editable charts and source notes. Reviewed against the archived results and updated with an explicit LLM decision role, published environment freeze and smoke-only approval, and the bounded cathode-thickness next step. Includes the shuffled control, expanded environment screen and provisional four-layer electrolyte result. This is a saved checkpoint; [presentation notes](presentations/README.md) list newer contact results that are not yet in the deck.

**Publication and smoke sign-off — 2026-10-21:** The frozen environment copies
preserve every original result row and scientific field. ENVIRONMENT_PROTOCOL.md
now records their exact hashes and Davide's smoke-only approval. Adem owns the
single live smoke batch; production remains on hold for its cost report. The
current local suite passes 127 tests, including Claude's new thickness code.
The publication also includes his committed `b51c14e`: four electrolyte layers
meet the declared final-two-thickness and tested constraint tolerances, while
vacuum/registry, seed sensitivity and polar-surface limitations remain open.
The presentation linked above uses this evidence checkpoint.

**Thickness review and next physics step — 2026-10-21:** Confirmed on GitHub
that `40b80fa` already includes Claude's `b51c14e`. Independent checks of five
unique archived runs verify 15 converged relaxations, adhesion arithmetic and
1,827 calculator calls plus ten separation single points. Recommend a bounded
cathode coating-thickness test at two/three/four layers: geometry-only checks
give 504/600/696 atoms in the same matching cell, with the same physical
104-atom substrate constraint. Use an 800-atom study cap and preserve the
surface cuts. No new MLIP run occurred. See [Claude handoff](SYNC_CLAUDE_3.md)
for the protocol and qualifications on constraint and registry sensitivity.

**Environment tables frozen; paid study pending — 2026-10-21:** Reviewed Adem's
`fc6a54c` protocol and froze separate copies of the three environment tables in
`data/benchmarks/environment_v1/`, preserving every scientific field and all 423
outcomes. Recommend seeds 200–229, Holm correction across six planned paired
contrasts, and shuffled in all three environments. Davide approved only the
approximately 30-call smoke batch; production requires a cost review and further
approval. Final protocol sign-off remains pending; no expanded live LLM run has
started here. A temporary
integration with Claude's contact work and the new freezer/analysis guard passes
136 tests. Both dependency files now pin the tested pymatgen/core versions.
See [ENVIRONMENT_FREEZE_REVIEW.md](ENVIRONMENT_FREEZE_REVIEW.md) and the short
[Adem handoff](SYNC_ADEM_7.md). Earlier “no freeze” entries are historical.

**Primary contacts built and reviewed — 2026-10-21:** Claude's `7249e7a` fixes
termination selection before truncation and maps equivalent, uncut Cl surfaces
across electrolyte seeds. The 504-atom cathode and two 440-atom electrolyte
inputs are built. All 18 constraint-study relaxations and 114 tests pass.
Cathode W_adh spans 3.471–3.488 J/m²; electrolyte seed 0 spans 1.288–1.411 J/m².
These remain provisional: cathode constraint insensitivity does not prove
cancellation of polar-surface energy errors, and the electrolyte is sensitive
across the tested bracket. Recommend publishing the commit and testing electrolyte
thickness at a fixed bottom depth of 3.257602 Å. Geometry-only checks give
492/544 atoms for three/four substrate layers; no thickness relaxations were run
in this review. See [SYNC_CLAUDE_2.md](SYNC_CLAUDE_2.md). The commit is still local
at this review checkpoint; the earlier contact-build status below is historical.

**Publication checkpoint — 2026-10-21:** Bulk calculations and audits are committed
as `57774d6`; the audited environment expansion is committed as `81e4625`, both
on `davide`. That publication checkpoint passed 113 tests. The user requested publication
to `origin/davide`; [SYNC_ADEM_6.md](SYNC_ADEM_6.md) is the short team handoff.
Earlier entries saying the work was uncommitted describe their review checkpoints.
The new agent-control commits remain on Adem's branch pending integration.

**Shuffled control completed and reviewed — 2026-10-21:** Adem's `6e74e88`
archives 30 matched shuffled runs: 6/30 acceptable versus iterative 19/30.
Independent replay verified all 300 outcomes and all 300 prompt/source maps;
the paired table gives exact McNemar p = 0.004425 (planned follow-up).
Correctly associated feedback helps candidate selection here, but this control
does not uniquely establish chemical reasoning. All 104 tests pass, including
in a temporary merge with committed `b210db0`; real branches remain unchanged.
Defer IDs-only and prepare the environment experiment. See
[SYNC_ADEM_5.md](SYNC_ADEM_5.md) for evidence, limitations and integration scope.

**Multistart and facet review — 2026-10-21:** Claude completed five additional
starts per distorted material (7,216 added calculator calls). Saved forces/stresses
confirm 6/6 converged Li6PS5Cl and 5/6 LiZr2(PO4)3 structures; seed 0 is lowest in
both sampled sets. These are model references, not established phases. Recommend
LiNbF6(001) for both primary contacts with LiCoO2(001), using existing unconstrained
bulk references. Geometry-only rematching confirms 504-/440-atom feasibility.
The electrolyte seed-0/seed-4 choices currently have different termination labels;
map equivalent cuts before interpreting a bulk-only sensitivity. Explicit
termination selection must also precede the scan's candidate cutoff. Polarity,
constraints and numerical convergence remain open; no new interface relaxation
has run here. See [SYNC_CLAUDE_1.md](SYNC_CLAUDE_1.md) for the concrete protocol,
and [BULK_RELAXATION.md](BULK_RELAXATION.md) for Claude's evidence. The earlier
[bulk review](BULK_REVIEW_AND_NEXT_STEPS.md) records the initial relaxation audit.

**Environment expansion evaluated — 2026-10-21:** The delegated study completed
all 423 combinations of 141 structures with LiCoO2 at 4 V and Li6PS5Cl, Li3InCl6
or ordered tetragonal LLZO. Compatible MP retrieval added 36 batched entry calls;
the final dataset has 7,420 entries. There are 414 computed outcomes and nine
explicit missing-entry failures. Acceptable counts are 4/55/17, respectively.
All sulfide acceptable structures contain fluorine; no LLZO acceptable structure
does. Chloride acceptance is easy even for random search. All 50 original results
reproduce exactly; 40 targeted tests and six independent solver checks pass.
These are computational landscapes, not expanded LLM results or validated coatings.
No new LLM experiment is frozen or launched. See
[EXPANSION_PROGRESS.md](EXPANSION_PROGRESS.md) for audited evidence and the
separate pre-run decisions, and [ENVIRONMENT_EXPANSION.md](ENVIRONMENT_EXPANSION.md)
for the original plan. The implementation and data are committed in `81e4625`.

**Integrated live experiment — 2026-10-21:** Merged Adem's agent branch into
`davide`, corrected invalid-ID accounting and ran 30 repeats per arm. At budget 10,
iterative succeeds 19/30 versus upfront 4/30, sequential 4/30 and random 10/30.
All 120 runs completed and all 1,200 evaluations matched an independent offline
replay. The post-hoc fluoride-first heuristic still succeeds earlier, and best-bin
performance is close to random. The full sanitized archive, figures, costs and
interpretation are in [INTEGRATED_DISCOVERY_RESULTS.md](INTEGRATED_DISCOVERY_RESULTS.md).
The older checkpoint entries below are retained as history.

**Next-work checkpoint — 2026-10-21:** The updated
[WORK_DIVISION.md](WORK_DIVISION.md) assigns Adem the matched shuffled-feedback
control, Davide the five-bulk and two-contact PET-MAD validation, and both the
presentation and final integration. Bulk-relaxation code is being developed
locally; this planning review has not validated it or launched new calculations.
The four-arm archive remains the completed baseline.

**Electrolyte-contact feasibility pilot — 2026-10-21:** Li6PS5Cl(111) | LiNbF6(101),
216 atoms, converged on free atoms; provisional constrained W_adh 0.4275 J/m². Under the
cathode pilot's 160 Å² matching cap no valid LiNbF6 | Li6PS5Cl interface was found among
the tested low-index facet pairs. Increasing the search cap to 300 Å² produced a
selected interface of about 183 Å²; rematch after bulk relaxation before freezing
a common two-contact area limit. Run before the
amendment's protocol validation; not comparable with the cathode value for ranking.
See the electrolyte section of [PETMAD_INTERFACE_PILOT.md](PETMAD_INTERFACE_PILOT.md).

**Structure viewer — 2026-10-21:** An offline interactive viewer now displays the
50 bulk candidates and eight saved pilot geometries from both contacts, including linked initial/relaxed
interface views, cell replication and coating/cathode or fixed-atom colouring.
Geometry exports preserve the saved coordinates and cell. See
[STRUCTURE_VIEWER.md](STRUCTURE_VIEWER.md) for build instructions and limitations.

**Pre-run review amendment — 2026-10-21:** The offline fluoride-first baseline
finds an acceptable coating on query 2. The pool contains 42 distinct formula
strings; removing fluorine leaves zero acceptable candidates. The revised plan
uses at least 30 runs per LLM arm and explicitly allows a prior-knowledge-only
conclusion if feedback adds no demonstrated benefit. PET-MAD bulk relaxation and
surface/convergence validation precede comparative adhesion rankings. See
[EXPERIMENT_AMENDMENT.md](EXPERIMENT_AMENDMENT.md) for the audit, integration
checklist and distinction between implemented checks and planned experiments.

**PET-MAD pilot completed — 2026-10-21:** LiCoO2(001) | LiNbF6(101), 224 atoms:
registry scan and joined/separated slab relaxations completed with movable-atom
forces below 0.05 eV/Å. The provisional constrained adhesion estimate is 2.1003 J/m²
(236 calculator executions; 98.9 s CPU calculation time). Polar slabs and large
reaction forces on fixed atoms prevent interpreting this as a validated adhesion
prediction. It is one contact, not a full coating score. See
[PETMAD_INTERFACE_PILOT.md](PETMAD_INTERFACE_PILOT.md). The suite now has 86 passing tests.

**Latest checkpoint — 2026-10-21:** The 50-candidate thermodynamic benchmark is now
computed and **objective v3.0 is frozen**, following the user's choice of additional
contact reactivity plus coating self-stability and insulation. V2 produced 41 tied
best candidates because electrolyte decomposition dominated. V3 has 24 occupied
eligible bins, one best-bin candidate and two criterion passes. It measures coating
compatibility, not whole-stack stability. A budgeted query API is ready for Adem;
82 tests and real-data LP/Qhull cross-checks pass. No LLM performance experiment
or new MLIP relaxation has been run. See [BENCHMARK_VALIDATION.md](BENCHMARK_VALIDATION.md)
and [EVALUATOR_HANDOFF.md](EVALUATOR_HANDOFF.md). The entries below describe earlier checkpoints.

**Discovery update — 2026-10-21:** Discovery is the headline experiment; the
original six-coating modelling screen below is supporting work. On `davide`, a
separate v2 draft evaluator now includes coating self-decomposition, an insulation
gate and fixed energy bins. A reproducible 50-candidate MP pool has been built.
The complete suite passes 62 tests. Neither the new evaluator nor the pool is
yet wired into the legacy discovery CLI; no v2 LLM benchmark has been run. See
[EVALUATOR_HANDOFF.md](EVALUATOR_HANDOFF.md) for the exact contract, assumptions
and remaining integration work.

**Runtime update — 2026-10-21:** PET-MAD S 1.6.0 (r²SCAN) is now the default for
both anode and cathode calculations, loaded through UPET 0.3.1. A real CPU smoke
test on displaced two-atom bcc lithium returned finite energy, forces and stress.
Five FIRE steps reduced energy from −3.931923 to −3.932929 eV and maximum force
from 0.06625 to 0.04152 eV/Å; it did not converge within that deliberately short
budget. All 38 offline tests passed in the new `.venv`. This supersedes the older
“no real MLIP run” status below; full interfaces remain unvalidated. Results and
dependency versions are in ignored `runs/petmad_smoke.json` and
`runs/petmad_environment.txt`. Public weights were cached under
`/private/tmp/interphaise-hf` (set `HF_HOME` to reuse this test cache).

> **Purpose of this file.** A self-contained brief for people and for LLM sessions that pick this
> project up later. It records what the project is, every design decision taken so far and why, what
> is built, what is verified and what is not. Read this before the code. Last updated 2026-10-20
> (rules arm added).

**Event:** OSI Hackathon (formerly LLM Hackathon for Materials & Chemistry), 21–22 October 2026.
Judging: impact, innovativeness, scalability, relevance to materials science and chemistry.
**Repo:** `OSI_Hackathon/interphAIse` (git), next to `OSI_Hackathon/hellmm`. Python package: `interphaise`.
**Shared version:** a Claude Docs report with the same content exists for the team.

---

## 1. One-paragraph summary

interphAIse answers a battery question: **which buffer coating makes a solid-state cathode interface
stable, and what atomistic model of each contact should be simulated?** The flagship case is
LiCoO₂ | coating | Li₆PS₅Cl at 4 V, screening six coatings against the uncoated cathode. An LLM makes
the modelling decisions an expert makes by judgement (which facets touch, whether a contact stays sharp
or grows a reaction layer, what that layer contains, whether it passivates, whether a relaxed structure
is physical). Thermodynamics, lattice matching and machine-learned interatomic potentials (MLIPs)
compute every number. The output is a ranked table of coatings, a verdict and structures per contact,
and a decision log.

## 2. The question and the output

For each candidate coating (plus "none"), two contacts are modelled: cathode | coating and
coating | electrolyte. For each coating the tool returns:

- **rank and tier**: 1 = both contacts stay sharp, 2 = a passivating (insulating, self-limiting) layer
  forms, 3 = a growing (electronically conducting) layer forms;
- **verdict per contact**: sharp or interphase, the layer phases in order, passivating or growing, with
  the reasoning;
- **simulation-ready structures** (`*_best.extxyz`) and the **work of adhesion** W_adh of each contact;
- **decision log** (`decision_log.json`): every LLM decision, its consensus agreement, every gate result
  and rejected candidate;
- `ranking.md` / `ranking.json` with the arm's ranking and a thermodynamics-only ranking side by side.

The same screen runs with three **decision arms** (§5): the LLM, deterministic rules, and a person.

Flagship candidate list (`config.py`): LiNbO₃, Li₃PO₄, Li₂ZrO₃, LiTaO₃, Li₃BO₃ (oxides used as
coatings in sulfide cells) and Li₃InCl₆ (halide). "Used in practice" is not yet backed by DOIs — see §10.

## 3. Prior art and positioning

| Work | What it does | What it leaves out |
|---|---|---|
| pymatgen ZSL / CoherentInterfaceBuilder, MPInterfaces, Ogre | Lattice matching, slab and interface generation | Which interface to build; no chemistry judgement |
| InterOptimus (J. Energy Chem. 106, 631, 2025) | Termination scan + ranking with universal MLIPs, battery interfaces (Li₂S\|Ni₃S₂, LiF\|NCM, Li₃PS₄\|Li) | Interphase decision; no LLM |
| AGAPI-Agents (arXiv 2512.11935) | LLM agent with a Zur-matching heterostructure tool | Battery chemistry, reactivity; demo is GaN/AlN |
| Paimon (arXiv 2606.09422) | Multi-agent MD workflows incl. Li diffusion in Li₆PS₅Cl | Interface construction |
| Lang2MLIP (arXiv 2605.14527) | Agents build SEI structures for MLIP training | Liquid electrolytes, not coherent solid–solid interfaces |
| **Xiao, Miara, Wang, Ceder, Joule 3, 1252 (2019)** | **Deterministic computational screen of cathode coatings for solid-state batteries**: phase stability, (electro)chemical stability, ionic conductivity. Top: polyanionic oxides LiH₂PO₄, LiTi₂(PO₄)₃, LiPO₃; some borates | No atomistic interface models, no adhesion, no kinetic/experimental judgement |

**Consequence of Xiao et al. 2019:** a coating screen by itself is not new. interphAIse must be pitched
on (a) the expert-judgement layer and its measured value over deterministic rules, (b) atomistic
interface structures with adhesion, (c) LLM orchestration. Use Xiao et al. as the deterministic
reference and as a source of expected answers; consider adding LiH₂PO₄, LiTi₂(PO₄)₃, LiPO₃ to the
screen. Check what that paper reports for LiNbO₃ (widely used in practice) before claiming anything.

## 4. The decisions the LLM makes instead of a human

There are three LLM decisions per contact. Each is sampled `N_RUNS` (default 3) times; the majority
answer and its agreement fraction are logged.

### Decision 1 — does a reaction layer form, and what is it? (`reasoners/interphase_reasoner.py`)

- **Today:** a modeller reads the convex-hull reactivity analysis, weighs it against what experiments
  report, and decides what structure to build.
- **LLM input:** the two materials, voltage, temperature, a one-line setting, and the hull analysis:
  reaction energy (eV/atom) per mixing ratio and the products.
- **LLM output:** (i) **sharp or interphase**; (ii) the **layer stack**, electrode side to electrolyte
  side; (iii) **passivating or growing**; plus rationale and kinetic argument.
- **Why it is judgement:** the hull gives the driving force, not what happens. Li | LLZO is slightly
  unstable on paper but kinetically stable → model it sharp. Li | Li₆PS₅Cl reacts to Li₂S, Li₃P, LiCl,
  all insulating → passivating. Li | Li₁₀GeP₂S₁₂ forms an electron-conducting Li–Ge alloy → growing. The
  hull alone cannot separate the last two.
- **Checks:** phases must be hull products of the pair; every adjacent pair in the stack must be
  mutually stable (`tools/reactivity.check_stack`), otherwise the LLM gets the reason and retries.
- **Weight:** passivating vs growing sets the coating's tier, so this is the decision that most
  changes the ranking.

### Decision 2 — which facets are in contact? (`reasoners/facet_reasoner.py`)

- **Today:** chosen from knowledge of the real material: particle morphology, microscopy, texture
  (e.g. LiCoO₂ particles mainly expose (104) and (003)).
- **LLM input:** both phases, space groups, lattice parameters, context.
- **LLM output:** up to three facet pairs ranked by experimental relevance, each with a reason.
- **Deliberately not given:** lattice mismatch, strain, energies (they are computed for every pair it
  proposes). HELLMM lesson: an LLM asked to guess stability discards exactly the cases that matter.
- **Check:** lattice matching must find a cell within strain and atom limits; failed pairs are fed
  back and the LLM proposes again.

### Decision 3 — is the relaxed structure physical? (`reasoners/judge.py`)

- **Today:** the modeller opens the structure in a viewer (OVITO) before trusting the numbers.
- **LLM input:** descriptors before/after relaxation (displacements, gap change, atoms crossing the
  interface, coordination numbers, shortest distance), validation warnings (polar slab,
  non-stoichiometric termination), W_adh.
- **LLM output:** accept / accept with caveat / reject, and for reject one action: thicker slabs, next
  termination, different facets, or larger cell.
- **Check:** none directly — it is the check. Its action drives the next step.

### Orchestration

The LLM does not write code or call tools freely. Its answers choose branches of a fixed state machine
(`orchestrator.py`):

| LLM answer | Next step |
|---|---|
| "interphase, 3 layers" | Build and compute each adjacent pair instead of one interface |
| stack fails the check | Back to decision 1 with the reason |
| facets with no valid match | Back to decision 2 with the reason |
| "reject: thicker slabs" etc. | Rebuild accordingly and recompute |

### Not decided by the LLM

All numbers (reaction energies, strain, energies, W_adh); the ranking rules; the candidate coatings
(chosen by a person in `config.py` — LLM-proposed candidates would be a natural extension, not built).

### Principles carried over from HELLMM

Generation separated from verification; gates not critics (hard, logged rejections); information
barrier (prompts never contain downstream-computed quantities or benchmark answers); never ask the LLM
what is computed; self-consistency by repeated sampling.

## 5. Can the decisions be made deterministically? — the rules arm

Largely yes, and since 2026-10-20 the rules are **implemented as a third arm** (`RulesPolicy` in
`interphaise/policies.py`). They are the baseline the LLM must beat; the older "thermodynamics-only"
ablation (every reactive contact = growing) is too weak to be the comparison.

| Decision | Deterministic rule | What the rule misses | LLM likely adds value? |
|---|---|---|---|
| Sharp or interphase | Threshold on reaction energy (sharp if > −X meV/atom) | Kinetic stabilisation (Li \| LLZO); arbitrary threshold | **Yes** — kinetics and experimental knowledge |
| Layer phases and order | Decomposition products of the electrolyte as μ_Li sweeps from the electrode value to the electrolyte (grand-potential phase diagrams; "chemical potential profile" approach) | Nucleation order, amorphous products | **Probably not** — the rule is well founded |
| Passivating or growing | Band gap of each product from Materials Project; any metallic product → growing (mixed conducting interphase) | PBE gap underestimation, small-gap phases, insulating but Li-blocking layers | **Marginal** — edge cases only |
| Facets | BFDH (larger d_hkl first, zero cost); Wulff shape from MLIP surface energies; or exhaustive low-index pairs (`run_bruteforce.py`) | Synthesis morphology, texture, which facet touches the electrolyte | **Possibly**, but hard to separate from recall of papers |
| Physicality | Thresholds on descriptors + fixed mapping to actions | Multi-signal trade-offs, explanation | **Weakest case** — rules probably as good and more reproducible |
| Orchestration | Already a fixed state machine; with rule answers the pipeline is fully deterministic | — | No |

### What is implemented (2026-10-20)

**Policy layer.** The orchestrator never calls an LLM directly; it asks a *policy* for each decision
(`decide_interface_type`, `propose_facets`, `judge`). Same pipeline, gates and numbers for every arm.

| Arm | `--policy` | Class | Decisions by |
|---|---|---|---|
| LLM | `llm` (default) | `LLMPolicy(make_llm(model))` | LLM reasoners, majority over `N_RUNS` samples |
| Rules | `rules` | `RulesPolicy(RuleSettings())` | Deterministic rules below; agreement always 1 |
| Human | `human` | `LLMPolicy(HumanLLM())` | A person answering the same prompts |

A bare `llm(system, user)` callable passed to `Orchestrator` or `run_screen` is still accepted and
wrapped in `LLMPolicy` (backwards compatible). Every decision event in `decision_log.json` now has
kind `"decision"` and `inputs.policy`; `ranking.json` carries `policy` and `policy_settings`
(all rule thresholds).

**The rules as implemented** (`RuleSettings` defaults):

| Decision | Rule | Default |
|---|---|---|
| Sharp or interphase | Sharp if the min reaction energy (hull) > threshold | `sharp_threshold = -0.05` eV/atom |
| Layer phases | Dominant products of the most favourable reaction, by atoms in the balanced equation | `max_intermediate = 3` |
| Layer order | First permutation whose adjacent pairs all pass `check_stack`; ties by Li fraction (Li-rich phases on the Li-richer side) | — |
| Passivating or growing | Growing if any layer phase has MP band gap < threshold; metal-only composition when the gap is unknown | `metallic_gap = 0.1` eV |
| Facets | BFDH: rank symmetry-distinct facets by effective d_hkl (d / smallest n with non-zero Z-weighted structure factor of n·hkl, so extinctions are handled); pair the top ones by rank sum; retries skip tried pairs | `facet_max_index = 2`, `facets_per_phase = 3` |
| Physicality | min distance < 1.0 Å or gap opened > 1.5 Å or W_adh ≤ 0 → reject, next termination; > 5 % of atoms crossed the interface → reject, different facets; mean interface displacement > 1.0 Å or coordination change > 30 % → reject, thicker slabs; validation warnings → accept with caveat; else accept | see `RuleSettings` |

Band gaps come from Materials Project (`tools/materials.get_band_gap`, needs `mp-api`; cached in
`data/band_gaps.json`).

**Layer-order caveat found while building the rule:** when all products are mutually stable (e.g.
Li₂S, Li₃P, LiCl against Li), thermodynamics does not fix their order; the rule falls back to Li
fraction. The order is therefore weakly determined by either arm, and scoring of decision 1-order
should be given less weight than sharp/interphase and passivating/growing.

**Comparison.** `scripts/compare_arms.py runs/` takes the latest screen of each arm and prints (and
with `--out` writes) the rankings side by side with the thermodynamics-only ablation, every contact
where the arms disagree, the number of contacts where the LLM overrides the rules, and each arm's
score against `benchmark/literature_cases.yaml`.

**Tests:** 21 offline tests pass, 9 of them for the rules arm (each rule, BFDH extinctions, retry
skipping, judge thresholds, full pipeline with `RulesPolicy`, screen + `compare_arms`).

### Still to do

1. **Hybrid mode (likely strongest).** Give the LLM the rule outputs as inputs (ordered products,
   their band gaps, the BFDH facet ranking). It decides where they conflict with known chemistry.
   Report the **override rate** and **override accuracy** against the literature.
2. **Threshold sensitivity.** The rule thresholds are judgement calls themselves; sweep
   `sharp_threshold` (e.g. −0.01 to −0.2 eV/atom) and report how the rules ranking changes.
3. **Better rules if time allows:** layer order from the chemical-potential profile (electrolyte
   decomposition as μ_Li sweeps from electrode to electrolyte); Wulff facets from MLIP surface energies.
4. Framing: decision 1 sharp/interphase and decision 2 are where the LLM is expected to win; layer
   order and the physicality check are explanation and exception handling.

## 6. Architecture and code map

One state machine per contact; the screen runs it twice per coating; the ranker orders coatings.

```
REACTIVITY ─▶ INTERFACE_TYPE ─▶ STACK_CHECK ─┐      reactive neighbours → feedback → INTERFACE_TYPE
   [det]         [LLM, dec. 1]      [det]    ▼
for each adjacent pair in the stack:
   FACETS ─▶ MATCH+VALIDATE ─▶ ENERGETICS ─▶ JUDGE ─▶ next pair / DONE
 [LLM, dec. 2]    [det]           [det]    [LLM, dec. 3]
     ▲             │ no valid match              │ reject + action
     └─────────────┴──────── feedback ◀──────────┘
screen.py: all contacts × coatings → ranker.py → ranking.md / ranking.json
```

| Path | Role |
|---|---|
| `interphaise/context.py` | Dataclasses passed between stages (all JSON-loggable) |
| `interphaise/orchestrator.py` | State machine for one contact; asks a policy for every decision; `build_structures=False` stops after decision 1 |
| `interphaise/policies.py` | `LLMPolicy` (LLM, human), `RulesPolicy` + `RuleSettings` + `bfdh_ranking`, `make_policy` |
| `interphaise/screen.py` | Coating screen: contacts per coating + uncoated baseline |
| `interphaise/ranker.py` | Tiered ranking; `mode="decisions"` (the arm's calls) and `mode="thermo"` |
| `interphaise/reasoners/` | `interphase_reasoner`, `facet_reasoner`, `judge`, `consensus`, all prompts in `prompts.py` |
| `interphaise/tools/materials.py` | MP bulk structures, entries and band gaps, cached under `data/` |
| `interphaise/tools/reactivity.py` | Interfacial reactivity (closed system for Li metal, grand potential with Li open otherwise); `check_stack` |
| `interphaise/tools/matcher.py` | ZSL matching over all terminations, symmetry-duplicate removal |
| `interphaise/tools/validation.py` | Gates: atom budget, strain, overlapping atoms, charged slabs (reject); polar, non-stoichiometric (warn) |
| `interphaise/tools/energetics.py` | Registry scan (in-plane offset × gap), FIRE relaxation, W_adh, evaluation counters |
| `interphaise/tools/descriptors.py` | Structural descriptors for the judge |
| `interphaise/tools/mlip.py` | `pet-mad`, `metatomic:<path>`, MACE-MP / UMA via HELLMM, `lj` toy |
| `interphaise/llm.py` | `make_llm` (litellm or HELLMM router), `HumanLLM` (person answers the prompts), `ScriptedLLM` (tests) |
| `benchmark/literature_cases.yaml` | Expected expert decisions and `coating_screens` expectations (all `verified: false`) |
| `benchmark/score_agreement.py` | Scores decision logs and rankings against the yaml |
| `scripts/run_screen.py` | Flagship: `--decision-only`, `--dry-run`, full |
| `scripts/run_cases.py`, `scripts/run_bruteforce.py` | Single contacts; exhaustive no-LLM baseline |
| `scripts/compare_arms.py` | Arms side by side, disagreements, LLM overrides of the rules, scores |
| `config.py` | LLM model, MLIPs, cases, `COATING_SCREEN` |

**Ranking rule** (worst contact decides): tier → worst reaction energy (closer to 0 better) → weakest
W_adh (higher better) → consensus agreement.

**Potential convention:** both contacts of a cathode coating are evaluated with Li open at the cathode
potential. Conservative for the coating | electrolyte side; state it when reporting.

**MLIP choice (updated 2026-10-21):** both defaults now use the public PET-MAD S 1.6.0
r²SCAN checkpoint via `upet:pet-mad-s@1.6.0`. This replaces the earlier legacy
PBEsol PET-MAD / MACE default selection. Model suitability for each interface still
requires validation. Keep MLIP energy differences separate from MP thermodynamics.

## 7. How to run

```bash
pip install -e ".[dev,llm,upet]"     # selected PET-MAD backend
pip install -e ../hellmm              # optional: reuse HELLMM's LLM router and MLIP loader
cp .env.example .env                  # MY_MP_API_KEY, MY_OPENROUTER_API_KEY, MY_ANTHROPIC_KEY
pytest                                # offline: toy Li–S chemistry, scripted LLM, LJ calculator
python scripts/run_screen.py --decision-only                  # LLM arm
python scripts/run_screen.py --decision-only --policy rules   # rules arm
python scripts/run_screen.py --decision-only --policy human   # human arm (interactive)
python scripts/compare_arms.py runs/ --out runs/compare.md
python scripts/run_screen.py --policy rules                   # full pipeline, any arm
python benchmark/score_agreement.py runs/
```

`LLM_MODEL = "deepseek-v3.2"` is a HELLMM alias; without HELLMM installed use
`openrouter/deepseek/deepseek-v3.2`.

## 8. Compute cost

No long simulations: every number is a single point or a relaxation of at most a few hundred steps.
Only the stretch goals (MD anneal, Li transport across the interface) need nanoseconds of MD.

| Mode | What runs | Estimated time, 13 contacts |
|---|---|---|
| `--decision-only` | Hull reactivity + ~3–10 LLM calls per contact | 5–15 min, < $1 LLM |
| `--dry-run` | + facets and lattice matching | 15–30 min, CPU |
| full, `--no-relax` | + registry scan, single points | < 1 h, one GPU |
| full | + 3 relaxations per candidate | 1–3 h on one GPU; ~a day on laptop CPU |

These are estimates from typical MLIP speeds, not measurements. Contacts are independent: one per GPU
brings the full screen under an hour. First pass: `registry_n_xy=2`, two gaps, `top_k_candidates=1`.

## 9. Evaluation plan

Target headline: *known-good coatings outrank the bare cathode, and the LLM's calls beat the
deterministic rules in the cases where kinetics or experiment matter.* All arms run through the same
pipeline; `compare_arms.py` produces items 1, 3 and 4.

1. **Ranking vs experiment**: known-good coatings above the uncoated cathode, for LLM, rules and
   thermodynamics-only rankings.
2. **Decisions vs published studies**: 7–15 systems in `literature_cases.yaml`; sharp/interphase,
   phases and order, facets. Only DOI-verified entries count.
3. **Rules vs LLM vs human, blind**: `--policy rules | llm | human`, same pipeline.
4. **Override metric**: how often the LLM overrides the rules (`compare_arms.py`, available now), and how
   often it is right (check each override against the literature). Hybrid mode will sharpen this.
5. **Efficiency**: relaxations to the best interface, LLM-guided vs `run_bruteforce.py`.
6. **Reproducibility**: repeat runs, second LLM vendor; per-decision agreement.

## 10. Status (2026-10-20)

**Built and committed:** scaffold, coating screen, ranker, benchmark scorer, renaming to interphAIse,
**rules arm** (policy layer, `RulesPolicy`, `--policy` flag, `compare_arms.py`).
**Tested:** 21 offline tests pass (toy Li–S chemistry, scripted LLM, Lennard-Jones calculator).
**Not yet run:** anything against Materials Project, a real LLM or a real MLIP.
**Unverified:** every entry in `benchmark/literature_cases.yaml`, including which coatings work in
practice — all `verified: false`, need DOIs.
**Not implemented:** hybrid mode and the threshold sweep (§5); merged multilayer interphase cells (stacks
are built as pairwise interfaces); interface energy γ_int (only W_adh); MD anneal and Li transport.

## 11. Risks

- The rules may match the LLM on most decisions; the pitch then rests on the few cases where they
  differ (measure, don't assume).
- LLM recall vs reasoning on well-studied systems; separate with the blind human baseline and
  less-studied coatings.
- Cell size: garnet and argyrodite interfaces can exceed the 600-atom budget.
- Disorder: argyrodites and garnets use MP ordered approximants; record the MP id.
- MLIP domain for magnetic cathodes (see §6).

## 12. Two-day plan

First milestone, Wednesday noon: `run_screen.py --decision-only` end to end on real MP data and a real
LLM (no MLIP needed). Pre-fetch all MP data Wednesday morning and commit `data/`.

| Work package | People | Wed 21 Oct | Thu 22 Oct |
|---|---|---|---|
| A. Benchmark | 2 | Verify `literature_cases.yaml` and `coating_screens` with DOIs | Human blind baseline; scoring |
| B. Reasoners, rules, prompts | 1–2 | Decision-only screen with the LLM and rules arms; prompt iteration; rule thresholds | Hybrid mode, override accuracy, threshold sweep, repeat runs |
| C. MLIP and energetics | 1–2 | PET-MAD / MACE-MP; Li \| LLZO adhesion sanity check | Full screen; brute-force baseline counts |
| D. Demo | 1 | Structure and decision-log viewer | Slides and video |

## 13. Project history (decisions taken in brainstorming)

- Ideas considered: agent benchmark for atomistic simulations (crowded: ASE-Bench, MDGym, MDArena);
  transport agent with statistical error bars (partly done by Paimon); MLIP fit-for-purpose checker;
  reproducibility auditor; MLIP dataset health check; trajectory-analysis notebooks; derivation checker.
- Chosen: extend HELLMM's design (LLM proposes, deterministic stages compute) to solid–solid battery
  interfaces, because the team owns a working pipeline and an MLIP stack, and interface modelling has a
  clear human-judgement step.
- Reframed from "build an interface model" (a modelling tool) to a **coating screen** (a battery result
  checkable against experiment), with LiCoO₂ | Li₆PS₅Cl as flagship.
- Hackathon requirement adopted: a clear component where human reasoning is replaced by an LLM, in
  addition to LLM orchestration (§4).
- Name: **interphAIse**; Python package `interphaise`.
- Asked whether the decisions could be deterministic: largely yes. Found Xiao et al. 2019 (deterministic
  coating screen). Decided to make deterministic rules a full third arm (built 2026-10-20) so the LLM is
  measured against expert rules, not against the crude thermodynamics-only ablation.

## Sources

- Xiao, Miara, Wang, Ceder, *Computational Screening of Cathode Coatings for Solid-State Batteries*,
  Joule 3, 1252 (2019): https://escholarship.org/uc/item/3mb3d98h
- InterOptimus, J. Energy Chem. 106, 631 (2025):
  https://cityudg.globalimpact.cn/en/publications/interoptimus-an-ai-assisted-robust-workflow-for-screening-ground-/
- AGAPI-Agents: https://arxiv.org/html/2512.11935v2
- Paimon: https://arxiv.org/pdf/2606.09422
- Lang2MLIP: https://arxiv.org/pdf/2605.14527
- MPInterfaces: https://ar5iv.labs.arxiv.org/html/1602.07784 · Ogre: https://arxiv.org/pdf/2103.13947
- OSI Hackathon: https://llmhackathon.github.io/
