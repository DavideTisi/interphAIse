# Experiment amendment after the pre-run review

21 October 2026, branch `davide`. This supersedes the ten-repeat recommendation
in the earlier sync. The frozen v3 pool and objective are unchanged. The audit
below is implemented; the revised LLM protocol and bulk-relaxation work remain
to be integrated and run. Adem's incoming code has not been inspected or merged.

## What the offline audit establishes

Reproduce with `.venv/bin/python scripts/audit_chemical_prior.py`.
The saved output is `data/benchmarks/chemical_prior_audit.json`; it records the
pool/objective/benchmark hashes and the complete deterministic trajectory.
Keep this file and all full-answer reports out of agent prompts.

- The pool has 50 IDs and **42 distinct formula strings**, not 43. Seven formulas
  repeat: LiAlSiO4, LiTi2(PO4)3, LiIO3, LiBr, Li6Ti2O7 and LiO8 twice each,
  and LiZr2(PO4)3 three times.
- Six formulas contain fluorine; both acceptable candidates are in this group.
  A deterministic order of fluorine-containing candidates first, with ascending
  candidate ID within each group, reaches an acceptable candidate at evaluation 2.
  The ordering does not read outcomes. However, the choice of this heuristic was
  motivated by reviewing the full results: disclose that provenance.
- Random ordering within the six fluorinated candidates succeeds by evaluation 3
  with probability `1 - C(4,3)/C(6,3) = 0.8`. This is a separate diagnostic,
  not a probability assigned to the single deterministic order.
- Removing fluorine leaves 44 candidates and **zero acceptable candidates**.
  Do not add this as a confirmatory acceptance experiment. A relative-best search
  could be an explicitly exploratory analysis, with its endpoint fixed before
  running it. Do not change thresholds after seeing agent performance.
- The two LiO8 records have gaps 0.1521 and 0 eV and fail the 2 eV insulation
  gate. Their presence is a materials-plausibility concern, not a winning loophole.
  Formula and near-hull status alone do not establish a usable coating. Detailed
  structural/provenance review remains open; retain both IDs in the frozen pool.

## Protocol for Adem's integration

1. Retain budget 10 and use at least 30 independent runs per LLM arm: upfront,
   iterative, sequential without results, and shuffled feedback if implemented.
   Thirty is a practical starting allocation, not a power guarantee. Freeze the
   run count before production; do not stop when a preferred conclusion appears.
2. Primary endpoint: probability of finding an acceptable candidate by query 10.
   Primary feedback contrast: iterative versus sequential without results.
   Upfront measures prior-informed selection; iterative versus upfront also mixes
   feedback with differences in interaction and call count. Report both.
3. Show the full best-bin and acceptance curves over queries 1–10, and the
   distribution of the first successful query. Treat these as secondary diagnostics,
   especially if budget-10 success saturates. Preserve bin ties. Include bin regret
   against the exhaustive optimum; separately report runs with no eligible result.
4. Include exact uniform-random curves over all 50 IDs and the deterministic
   fluoride-first trace. Do not count repeats of the same deterministic trace as
   independent observations. Report run-level uncertainty and confidence intervals
   on the primary difference; freeze the analysis procedure before production.
5. If upfront and the heuristic already saturate, conclude that this task supports
   prior-guided screening but does not establish a feedback advantage. An uncertain
   difference is inconclusive, not proof of equivalence. Do not replace the endpoint
   after observing saturation. Improvements at early queries remain secondary.
6. Tell every arm: "Each candidate ID denotes a separate structure. Some formulas
   repeat because the pool contains polymorphs. Querying another polymorph costs
   another evaluation; failed, invalid and repeated-ID queries also consume budget."
   Use the same candidate information across arms; do not reveal target identities.
7. Freeze model ID, temperature, prompts, seeds, shuffled-feedback mapping/procedure,
   token limits and retry policy. Shuffle complete feedback records consistently
   rather than independent fields; prevent accidental true-result leakage. The
   scoring evaluator always uses real outcomes. A shuffle control probes dependence
   on feedback but does not by itself establish chemically valid reasoning.
8. Record tokens, calls, retries and wall time. At 30 runs and budget 10, upfront
   uses 30 proposal calls, iterative 300 and sequential 300: 630 before retries;
   shuffled feedback adds 300. Call counts alone are not monetary cost estimates.
   Use only the authorized direct Anthropic Haiku 5.5 configuration.

## What the LLM substitutes for

The human task is to choose the next material, explain an observed failure and
revise a chemical hypothesis. The LLM should do that selection and revision;
the deterministic evaluator supplies physical evidence and checks the criterion.
For example, after observing that an insulating fluoride still reacts with the
electrolyte, the agent should reconsider the relevant chemistry rather than assume
all fluorides pass. This is an illustrative reasoning task, not an instruction to
put benchmark-specific answers into prompts.

A plausible written explanation is not evidence that feedback helped. The evidence
is improved selection under the same evaluation budget compared with no-feedback
controls, supported by traces showing how specific observations changed choices.
If prior knowledge alone wins, that is useful automation of human screening but a
weaker claim than replacing iterative scientific intuition. This small, inexpensive
cached benchmark cannot demonstrate real compute savings or new material validation.

## Next PET-MAD work — Davide

The 2.1003 J/m² pilot is an execution check, not a comparative adhesion prediction.
Large forces on fixed atoms can reflect imposed constraints and surface/interface
physics as well as bulk-model mismatch; they do not uniquely diagnose bulk strain.

1. Relax the two bulk structures with the same conservative PET-MAD checkpoint,
   allowing lattice and atomic positions to respond. Save starting/final cells,
   energies, forces, stress, settings, convergence, model hash and calculator calls.
2. Rebuild and rematch slabs from those bulk references. Report the residual
   coherent mismatch; bulk relaxation does not remove epitaxial strain or polarity.
3. Test termination/polarity and fixed-layer choices before interpreting thickness
   and vacuum convergence. Use identical strained cells and consistent constraints
   for joined and separated references. Record both free-atom and fixed-atom forces.
4. Vary slab thickness and vacuum separately, then registry sampling. Predeclare
   a practical adhesion-change tolerance (proposed 0.1 J/m² across the last two
   settings) and report failures rather than labelling a single run converged.
   That tolerance is a numerical check, not an accuracy guarantee for PET-MAD.
5. Only after a usable protocol is established, compute the electrolyte contact
   and the shortlist consistently. Li transport remains outside this criterion.
   (A LiNbF6 electrolyte-contact feasibility pilot was already run in parallel with
   this amendment; see PETMAD_INTERFACE_PILOT.md. It shows that step 2's matching
   cap must exceed ~185 Å² for that contact. Recompute it under the final protocol.)

Use local CPU for initial small tests. The 99-second pilot excludes preparation
and does not guarantee similar timing for thicker cells or bulk optimization.
Use authorized Niflheim Slurm resources if the tested workloads warrant it.

## Integration boundary

Adem owns agent/runner/analysis integration and the run manifest. Davide owns this
offline audit, evaluator and PET-MAD validation. Inspect Adem's incoming diff before
merging, check v3 query accounting and prompt isolation offline, then run a small
authorized live integration test before the production batch. No paid LLM run,
new MP request or PET-MAD calculation was made for this amendment.
