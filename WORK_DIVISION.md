# interphAIse — work division for Davide, Adem and Claude

OSI Hackathon, 21–22 October 2026. All scheduling below uses Copenhagen time.

## Current assignments: LLM-guided three-coating pilot — 22 October

**Approved to start:** Davide approved Adem's initial live prior/choose-2 on
22 October, under one total ten-HTTP-attempt cap and a USD 0.05 allowance.
Adem's `f8abbc0` passes 188 tests and the initial package has an independent
preflight. Adem archives the selection, then pauses for physics. See
[SYNC_ADEM_14.md](SYNC_ADEM_14.md). Adem finishes manifest-derived source checks
before choose-3; Claude evaluates only the archived selection; Davide reviews
the resulting package. The earlier pending-fix status below is historical.

**Latest handoff:** Claude has frozen the four-member feasible menu and primary
inputs in `38e4872`; hashes/counts and 163 offline tests reproduce. Read
[SYNC_CLAUDE_11.md](SYNC_CLAUDE_11.md) for the final contract integration,
integrity-versus-calculation-failure distinction and recommended lower-priority
reference checks. Adem remains at `2d2cac3`; [note 13](SYNC_ADEM_13.md) is pending.
No new calculation or live-call approval is implied by this status update.

Davide clarified that the LLM should choose new coatings using PET-MAD feedback.
Use LiNbF6 as the known reference, then let the LLM select two new coatings
sequentially from a frozen feasible menu. The current scope and scientific
brief are in [LLM_PETMAD_PILOT_PLAN.md](LLM_PETMAD_PILOT_PLAN.md). Code polishing
supports this loop. The physical rules in MLIP_COMPARISON_PLAN.md remain;
the previous fixed cohort and automatic fallback order are superseded.

The construction review of Claude's `49daa72` supports a uniform 1,250-atom
cap, with LiCaAlF6, LiTaF6 and LiF as intended alternatives after final menu
validation. F1/F2 changes pass 157 tests on Claude's branch; retain the completed
F1 fix. Remaining producer/consumer gates concern feedback completeness,
comparable builds and recomputed work values; see [SYNC_CLAUDE_10.md](SYNC_CLAUDE_10.md).
The 1,302-atom LiCaAlF6 thickness increment stays unavailable under this cap.
The main checkout has not merged Claude's code.

Deadline execution: Thursday 22 October 10:00 progress check, 12:00
adaptive/fixed-comparison decision, 20:00 slide/writeup freeze; target submission
Friday 23 October 00:30, before the 02:00 CEST deadline supplied by Davide.
Primary registry feedback advances the loop; declared sensitivities can follow
or run in parallel, with their absence explicit. Require numeric W_adh forecasts
and preserve each decision-time feedback snapshot. LiNbF6 sensitivity is context
only. See the pilot plan for the exact fallback and validation rules.

The review of `davide:8975d4b` and Adem's latest `b8b1392` reproduces the
completed results and identifies four code safeguards to add. See
[JOINT_REVIEW_AND_HANDOFF.md](JOINT_REVIEW_AND_HANDOFF.md) for reproductions,
scope and acceptance criteria. F1/F2 were subsequently implemented on Claude's
branch as reviewed above. Adem's subsequent `2d2cac3` passes 183 tests and
replays production unchanged. F3/F4 are substantially implemented, with missing
successful-call metadata and exceptional/resumed HTTP accounting still to fix.
The new pilot also needs source validation before prompting and the previous
structured predictions in later prompts. See [SYNC_ADEM_13.md](SYNC_ADEM_13.md).
No new interface calculation was made in these reviews.

| Owner | Next work | Done when |
|---|---|---|
| **Adem** | Approved: run prior/choose-2 on the pinned package and archive the selection; finish manifest-derived coverage and real source-identity checks before choose-3. | First choice precedes its energies; the next package passes independent validation; all stages retain one state and total 10-attempt cap, within the USD 0.05 allowance. See [SYNC_ADEM_14.md](SYNC_ADEM_14.md). |
| **Claude** | Keep the frozen menu/builds; finish the producer/consumer contract with Adem and block corrupt evidence; calculate six primary jobs for each archived approved selection. | Complete validated primary feedback; costs and failure types explicit; optional reference work separately approved and reported. See [SYNC_CLAUDE_11.md](SYNC_CLAUDE_11.md). |
| **Davide, with Codex** | Own scientific comparability choices, independently review code/results, resolve integration/log history, maintain report, viewer and presentation narrative. | The comparison follows the frozen rules; combined tests/replay pass; structures and evidence are inspectable; both contributors' history is preserved in the release. |

Adem keeps `work/agent-experiments`; give Claude an isolated physics
branch/worktree for new work; Davide integrates on `davide`. This is a proposed
ownership arrangement, not a branch creation or a message sent to either
contributor. Adem owns `llm.py` and analysis; Claude owns energetics/relaxation
and PET-MAD scripts. Davide consolidates the shared status files. Keep scoped
handoff entries to avoid simultaneous edits to the same log paragraphs.

Safeguards, geometry preparation and mocked loop/analysis development proceed
in parallel. Freeze the feasible menu, objective and evaluation protocol first,
then archive each new selection before its interface energies. Adem supplies
the bounded API cost estimate before live pilot execution. No repeat of the
450-run LLM study is needed. Three coating slots demonstrate the physical
feedback loop; they do not establish statistically superior search. Complete
slides and release preparation alongside this work.

## Previous production handoff — 21 October

The following section records the earlier handoff; the assignments above
supersede its next-work table and pending-task descriptions.

**Production is complete and reviewed:** Adem's `06a4271` has all 450 runs;
independent replay and the six planned comparisons pass. The current work is
slides, joint branch review and a reproducible release. The viewer now opens
the selected cathode registry and includes the completed seed-4 comparison;
see [VIEWER_UPDATE.md](VIEWER_UPDATE.md).
See [SYNC_ADEM_9.md](SYNC_ADEM_9.md). No additional runs are requested.
The production approval below records the prior authorization, not pending work.

The expansion data are frozen in `data/benchmarks/environment_v1/`. The smoke
batch, cost review and analysis review are complete. Davide explicitly approved
**production** on 21 October 2026. **Adem owns execution** of the three-environment,
five-arm, 30-repeat study at budget 10, seeds 200–229, with six Holm-corrected
contrasts and shuffled in every environment. Use the unchanged Haiku 5.5 settings
and record the actual execution commit. See [SYNC_ADEM_8.md](SYNC_ADEM_8.md) and
[ENVIRONMENT_PROTOCOL.md](ENVIRONMENT_PROTOCOL.md). No duplicate batch has been
launched from Davide's checkout; start/completion must be recorded by the runner.

The following paragraphs record earlier integration and physics checkpoints;
the current next-work table below supersedes their pending-task descriptions.

The integrated four-arm experiment is complete: 30 runs per arm, budget 10,
seeds 100–129, frozen v3, direct Anthropic Haiku 5.5. Iterative finds an acceptable
candidate in 19/30 runs, upfront and sequential each in 4/30, and sampled random
in 10/30. All 1,200 queries replay exactly. The post-hoc fluoride-first heuristic
succeeds at query 2; best-bin performance is close to random. See
[INTEGRATED_DISCOVERY_RESULTS.md](INTEGRATED_DISCOVERY_RESULTS.md).

The publication batch on `davide` builds on `b210db0`, which includes the
electrolyte-pilot preparation code and provenance. Bulk implementation/evidence
and audits are committed as `57774d6`; the environment expansion as `81e4625`.
That publication checkpoint passed 113 tests. See [SYNC_ADEM_6.md](SYNC_ADEM_6.md) for
the short handoff. Multistart is now complete: seed 0
is retained for both distorted materials, with alternative seeds 4 and 1.
Claude's subsequent `7249e7a` builds the common LiNbF6(001) contacts, fixes
termination selection and maps equivalent electrolyte cuts. All 18 constraint
relaxations and the current 114 tests pass. The next physics step is electrolyte
thickness at a constant fixed depth, followed by cathode coating thickness and
remaining convergence checks; see [SYNC_CLAUDE_2.md](SYNC_CLAUDE_2.md).
Adem's `6e74e88` adds the completed shuffled control: 6/30 versus iterative 19/30,
with exact paired p = 0.004425. All 300 outcomes and prompt/source maps validate.
A temporary merge of both committed branches passes 104 tests and preserves
Claude's pilot provenance. No actual branch merge has occurred. Defer IDs-only;
prioritize the environment experiment and release review. See
[SYNC_ADEM_5.md](SYNC_ADEM_5.md).

**Next work, in priority order:**

| Owner | Action | Completion evidence |
|---|---|---|
| Adem | Present the completed environment study with its positive and negative results | Production reviewed at 06a4271; overview and six primary contrasts in SYNC_ADEM_9.md; retain LLZO random advantage |
| Davide + Claude | Use the published bounded Niflheim batch and reviewed viewer in the demo | Selected cathode and seed-4 comparison are available with their limitations; see SYNC_CLAUDE_7.md and VIEWER_UPDATE.md; no additional simulations requested |
| Adem + Davide | Prepare the presentation and reproducible demonstration alongside the calculations | Acceptance and best-bin curves with baselines, one successful and one failed trace, offline two-contact viewer, explicit scientific limits |
| Together | Review the combined branch and publish a reproducible release | Tests and archive replay pass, reports match the results, both people review scope before merging to `main` |

### 1. Preserve the completed feedback evidence

Follow [SYNC_ADEM_5.md](SYNC_ADEM_5.md). The 30 matched shuffled repeats are
complete and independently verified; the sparse exact-median plotting bug is
fixed. Use the five-arm figure and selected success/failure traces for the
presentation. Describe the control as feedback corruption with partial identity
leakage and possible history contradictions. The result supports useful feedback,
but does not alone prove sound chemical reasoning.

Keep both archives immutable and label the shuffled comparison as a planned
follow-up after the original result. Defer the optional roughly 300-call IDs-only
diagnostic. Prepare the expanded environment study before further paid runs;
freeze its protocol separately and do not pool it with the original cohort.

### 2. Establish a usable interface protocol

Bulk inputs are LiCoO2, Li6PS5Cl, LiNbF6 (`mp-aaacjjwh`), LiCaAlF6
(`mp-aaaaajby`) and LiZr2(PO4)3 (`mp-aaabevhd`). Endpoint IDs come from the
frozen dataset. Use the same conservative PET-MAD S 1.6.0 checkpoint. The initial
positions/cell relaxations and bounded multistart check are complete. Seed 0 is
the reference for both distorted materials; alternatives are Li6PS5Cl seed 4 and
LiZr2(PO4)3 seed 1. Completing an optimizer does not establish a physical phase.
Use the existing unconstrained LiCoO2/LiNbF6 references for construction and
follow [SYNC_CLAUDE_1.md](SYNC_CLAUDE_1.md): common coating (001) orientation,
explicit surface selection before truncation, and mapped electrolyte cuts for
the bulk-configuration comparison. The 200-atom option remains secondary.

LiNbF6 against both endpoints is built and the first constraint bracket is
complete. Follow [SYNC_CLAUDE_2.md](SYNC_CLAUDE_2.md) for electrolyte thickness
with a fixed 3.257602 Å bottom depth and unchanged in-plane matching cell.
Then vary cathode film thickness, vacuum and registry and test the mapped seed 4.
Use consistent strained cells and reference constraints in adhesion differences.
Freeze the numerical convergence criterion before comparing candidates; the
amendment proposes a change of at most 0.1 J/m² across the final two settings,
which is not an accuracy guarantee. Expand to the other two pinned coatings only
if this protocol is usable. Start locally and use Niflheim Slurm if measured
workload warrants it.

The earlier 2.10 and 0.43 J/m² values remain feasibility results and cannot be
compared with the new protocol's 3.47–3.49 and 1.29–1.41 J/m² ranges. The electrolyte
matching limitation was observed for the tested low-index facet pairs and
unrelaxed lattices; reassess area limits after bulk relaxation. Do not convert the
present ~185 Å² observation into a universal matching bound. See
[EXPERIMENT_AMENDMENT.md](EXPERIMENT_AMENDMENT.md) and
[PETMAD_INTERFACE_PILOT.md](PETMAD_INTERFACE_PILOT.md).

### 3. Prepare the submission now

The central demonstration should show the LLM replacing the human decision:
"Given the measured failure of this coating, what chemical hypothesis should I
revise, and which candidate should I test next?" The LLM selects and revises;
deterministic tools supply outcomes. Connect the selected trace to observed
feedback and check its chemistry rather than presenting its prose as proof.

Use a short narrative: scientific question and division of roles; frozen benchmark
and controls; quantitative results; one proposal–feedback–revision trace; both
interfaces and limitations. Include the exact random curve, the post-hoc heuristic,
threshold sensitivity and the failed trace in the main or supporting material.
The viewer can be shared as generated HTML, independent of a localhost server.

For the hackathon, prioritize a reproducible feedback experiment and an honest
materials feasibility demonstration. If physical convergence fails, report that
failure and retain the interfaces as feasibility illustrations. Do not delay the
submission or claim validated adhesion because the numerical protocol remains open.
Li transport, synthesis and real battery performance remain outside the evidence.

Keep the frozen pool, threshold and existing run count unchanged. Additional
conditions, larger pools, composition generation and new agent features are
follow-up studies, not requirements for finishing this submission.

The sections below retain the original ownership and startup plan for context.
This current handoff supersedes their preliminary schedules and ten-run target.

### User-selected extension: more coatings and environments

The delegated expansion has completed endpoint review, compatible retrieval and
all 423 outcomes. [EXPANSION_PROGRESS.md](EXPANSION_PROGRESS.md) records the
141-coating, three-environment results and audits. The original 50 scores replay
exactly. Davide/Codex owns data/evaluator review; Adem owns adapting the matched
search experiments and preparing a separate pre-run protocol. Retain all three
environments, including the easy chloride condition, and report early-query and
bin-regret curves. These are additional exploratory tasks, not revisions of v3.
The data tables are now frozen, with smoke-only spending approved and final
protocol/production sign-off pending; no expanded live LLM batch was launched here.
Interface validation continues independently.
See [ENVIRONMENT_FREEZE_REVIEW.md](ENVIRONMENT_FREEZE_REVIEW.md). The original plan remains in
[ENVIRONMENT_EXPANSION.md](ENVIRONMENT_EXPANSION.md).

## Shared objective

Test whether computed feedback improves an LLM's selection of compatible battery
coatings beyond its initial chemical knowledge. The LLM replaces the scientist's
intuition in proposing candidates, interpreting failures and choosing what to test
next. Deterministic tools calculate properties and apply a fixed objective.

Use the frozen-pool benchmark for controlled evaluation; a small composition
proposal-and-revision demonstration can show the broader design idea. Keep those
claims separate. MLIP follow-up evaluates selected structures, not the accuracy
of the whole search benchmark.

## Ownership

| Owner | Owns | Deliverable |
|---|---|---|
| **Davide** | Materials data, physical criteria, computational evaluator, PET-MAD follow-up | A validated evaluator that accepts a candidate and returns numerical outcomes with provenance |
| **Adem** | Haiku hypotheses, feedback loop, search controls, repeated experiments and plots | An agent that chooses the next candidate and an experiment measuring the value of feedback |
| **Together** | Objective and result schema, scientific interpretation, integration and presentation | One end-to-end demonstration and a defensible conclusion |

Detailed scientific design: [DISCOVERY_IMPLEMENTATION_PLAN.md](DISCOVERY_IMPLEMENTATION_PLAN.md).

## First joint session — approximately 30 minutes

Before working independently, agree on:

1. Cathode, electrolyte and operating conditions for the main experiment.
2. Candidate identity: use pinned material IDs, not ambiguous formula-only lookups.
3. Evaluator result schema, energy signs, atom normalization and missing-data rules.
4. Acceptability criteria, ranking/tie convention and query budget.
5. Which files each person owns and the shared integration checkpoint.

Freeze the objective before strategy results are inspected. If the exhaustive pool
has no meaningful variation, document a redesigned task before starting LLM runs.

## Davide — materials and evaluator

### Wednesday 21 October

- Fix coating self-stability at the chosen lithium chemical potential.
- Fetch band gaps and structures for the same pinned MP material IDs.
- Implement validity gates, explicit units/normalization and fixed energy bins.
- Build and freeze approximately 50 chemically diverse, ordered candidates with
  recorded filtering criteria and a pool hash.
- Evaluate the inexpensive objective over the pool once; inspect failures,
  acceptable-candidate fraction and tied groups.
- Prepare a representative structure for the first PET-MAD interface calculation.

**Handoff to Adem:** versioned candidate metadata, the frozen objective and an
access-controlled evaluator/query function. The benchmark runner may load the
complete results, but must not reveal unqueried outcomes to the LLM.

### Thursday 22 October

- Sanity-check leading candidates and failure cases.
- Run the same PET-MAD protocol on a small shortlist, including a baseline-selected
  comparator; record relaxation/single-point counts and wall time.
- Inspect resulting structures and clearly distinguish incomplete relaxation from
  valid converged results.
- Prepare structure images and the explanation of what the evaluator measures.

**Main files:** `interphaise/tools/`, proposed
`interphaise/discovery_evaluator.py`, `scripts/build_candidate_pool.py`,
`data/pools/`, objective configuration and evaluator tests.

## Adem — agent and experiments

### Wednesday 21 October

- Implement chemical proposals with a concise hypothesis and explicit reference
  to the observation motivating a revision.
- Develop against a synthetic evaluator while the real evaluator is being built.
- Implement upfront LLM, sequential LLM without results and iterative LLM with
  true feedback; retain uniform random selection as the baseline.
- Ensure histories do not leak unqueried outcomes or result metadata into the
  no-feedback arm. Log failures and charge the agreed evaluation budget.
- Add repeated-run orchestration, model/sampling metadata and plotting support.
- If implementing free formula proposals, resolve them to known structures;
  report unresolved proposals explicitly and evaluate this demo separately.

**Handoff to Davide:** the runner, synthetic end-to-end demonstration and exact
input/output expectations. Do not modify evaluator criteria to improve agent scores.

### Thursday 22 October

- Run repeated experiments on the frozen benchmark (target: at least 10 runs per
  LLM arm, subject to the agreed token budget).
- Calculate the exact random success curve, respecting ties and sampling without
  replacement.
- Plot success probability and best objective versus evaluations, with uncertainty
  across repeats and failed runs retained.
- Select one trace showing a hypothesis, contradictory feedback and the resulting
  next proposal. A compelling explanation alone is not evidence of better search.

**Main files:** `interphaise/discovery.py`, proposer prompts,
`scripts/run_discovery.py`, proposed `scripts/run_discovery_experiment.py` and
`scripts/analyse_discovery_experiment.py`, search/control tests.

## Shared evaluator contract

Illustrative request (values and field names to freeze together):

```json
{
  "candidate_id": "candidate-017",
  "hypothesis": "The chemical reason for testing this coating"
}
```

Illustrative response — numbers below are synthetic, not material predictions:

```json
{
  "candidate_id": "candidate-017",
  "status": "ok",
  "contact_reaction_energies": [-0.03, -0.12],
  "self_decomposition_penalty": 0.08,
  "band_gap_eV": 3.2,
  "reaction_products": [],
  "warnings": [],
  "objective_version": "v2"
}
```

The final schema must declare the energy units and normalization basis explicitly.
Missing values must be null/unknown, not zero. The evaluator supplies the score
and diagnostic components. The LLM cannot change the objective or self-certify a
candidate. Preserve separate records for real outcomes and displayed feedback.

## Integration milestones

| When | Joint acceptance criterion |
|---|---|
| Wednesday, after the initial setup | Both sides agree on the schema and run against the same synthetic fixture |
| Wednesday afternoon | One real coating is evaluated; Haiku receives the outcome and selects the next candidate |
| Thursday, before large runs | Pool/objective frozen; information-barrier and budget tests pass |
| Thursday, before the presentation | Repeated comparison plot, one intelligible agent trace, and inspected MLIP follow-up where available |

Keep a short joint check-in after the first real evaluation. If the integration
fails, fix it before adding more candidates or more agent features.

## Git and collaboration

Integration base: `main` (updated 21 October after the discovery work was merged).

Create personal work branches from the same latest integration commit:

- Davide: `davide` (created from `main`, active evaluator development)
- Adem: `work/agent-experiments`

Both personal branches now exist; integrated development is currently on `davide`.
Keep changes within the owned files where practical. Agree before changing shared
configuration or the evaluator contract. Use small commits and merge at the
milestones; avoid simultaneous edits of the same file. Do not merge to `main`
until the integrated tests pass and both people have reviewed the scientific scope.

## Fixed runtime and credential rules

- Live LLM: **Claude Haiku 5.5 only**, exact ID `claude-haiku-5-5`, through direct
  Anthropic access. No other model/provider or fallback is authorised.
- MLIP: **PET-MAD S 1.6.0, r²SCAN**, selected as `upet:pet-mad-s@1.6.0`.
- Each person configures credentials locally in ignored `.env`. Never commit or
  send keys through reports, GitHub issues or logs. `.env.example` stays empty.
- Use credentials only for this workflow and minimal connection tests.
- API connectivity and a small PET-MAD CPU smoke test have passed. These are
  software checks, not scientific validation of the battery-interface evaluator.

## Scope and pitch

Minimum successful submission:

1. A verified, frozen computational evaluator.
2. One complete proposal–calculation–revision loop.
3. A controlled comparison against prior-only/no-feedback and random selection.

Current priority beyond the completed experiment is shuffled feedback, as specified
above. Stretch work: a second operating condition, additional MLIP interfaces and
broader composition proposals. Keep the original modelling-decision arms as
supporting material only if the main experiment is complete.

The main claim, if supported, is that calculated feedback improves candidate
selection beyond the model's prior chemical knowledge. The cheap benchmark measures
sample efficiency, not real compute savings. The shortlist does not establish Li-ion
transport, synthesis feasibility or experimental battery performance; state these
limits on the slides. A negative feedback result is still worth reporting honestly.
