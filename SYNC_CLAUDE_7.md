# Niflheim batch 1 review: publish and close the bounded study

21 October 2026. Reviewed `72353cd`, `279e2b1` and `f1861ef` on `davide`.
The remote was verified at `dc62dfe`; these three commits are not yet published.

**Recommendation: publish the three commits with the formatting correction
below, and stop this calculation batch.** Keep seed 0 as the electrolyte
reference and report seed 4 as a failed sensitivity tolerance. Do not add
runs to obtain a passing result. The next project priority is Adem's approved
environment experiment, final integration, and presentation/demo updates.

## Independently checked

All five runs' saved geometries, energies and force arrays were inspected.
All 15 relaxations meet their free-force targets; independently rerun overlap
checks pass. Cells, species order and physical fixed-atom positions are
preserved within each relaxation, and the substrate reference masks match
the joined masks. Both works recompute from the archived energies. Accounting
is 1,216 calculator calls plus ten rigid-fragment single points; the two new
registry offsets each add exactly one scan point. Both stages record CUDA and
the same checkpoint. Job logs record source `279e2b1`; scheduler records show
all five jobs completed. No fresh energy evaluation or cluster access was
needed for this review.

| Contact / setting | W_adh | W_sep |
|---|---:|---:|
| Cathode (0,0), GPU reference | 3.60036 | 5.12772 |
| Cathode (1/6,0) | 3.59696 | 5.09080 |
| Cathode (1/3,1/3), selected | **3.61705** | **5.16762** |
| Electrolyte seed 0, GPU reference | 1.63339 | 2.96722 |
| Electrolyte seed 4 | 1.51201 | 2.80536 |

Units: J/m². CPU–GPU differences in W_adh / W_sep are cathode
+0.000220 / +0.000176 and electrolyte +0.000458 / +0.000315 J/m².
This batch therefore checks both observables at the working atom counts.

## Scientific interpretation and stopping point

The cathode selection follows the declared lowest-relaxed-joined-energy rule:
(1/3,1/3) is 0.0927 eV below (0,0) in the same cell/composition/mask. Its
unrelaxed ordering would have selected the wrong member of this three-registry
set. That is useful evidence for relaxing candidate registries; this selection
was a deterministic rule, not an additional demonstration of LLM reasoning.
Three of nine classes were relaxed, so call this the lowest **sampled** registry.

The earlier constraint and thickness brackets were measured at (0,0), not
at the newly selected registry. Present them as checks on the reference
protocol plus a separate finite registry comparison. We do not need to
restart every convergence sweep for this hackathon, but must not claim that
the new registry itself has passed all those brackets.

Seed 4 changes W_adh by -0.121382 and W_sep by -0.161856 J/m² relative to
seed 0 on the same device. Both exceed the reporting tolerance. This is a
**combined bulk-reference and interface-construction sensitivity**: disorder,
area, strain, matching basis, constraints and possibly physical alignment
change together. It is neither an isolated disorder effect nor an uncertainty
interval from a sampled ensemble. Say “largest quantified sensitivity tested
so far”, rather than “largest uncertainty”: polar-model error is unquantified.
Keep the two-seed ranges (1.512–1.633 and 2.805–2.967) separate from the
seed-0 registry range (W_sep 2.967–3.065); do not combine them into an error bar.

**Defer seed 4 at (0,0.5).** Its unrelaxed preference is a reason to test it in
future, not evidence that it will remain preferred after relaxation—the
cathode example shows why. An additional run would answer a within-seed-4
registry question, but would not remove the between-seed confounders. If this
later becomes a priority, declare a new sensitivity study and its selection
rule first, retaining the completed batch unchanged. No new run is requested
by this handoff. Both formally polar contacts remain provisional; the study
has established feasibility and documented sensitivities, not validated
coating adhesion or transport.

## Publication and handoff

A configured credential-value scan of all 81 changed paths across the three
commits is clean; `.env` is ignored and untracked. No credential was printed.
One residual formatting issue remained in
`data/petmad/niflheim_batch1/cathode_reg_third_third/initial.extxyz`: 696 lines
had trailing whitespace. Removed only trailing spaces and verified all ASE
arrays, cell, PBC and metadata are identical before and after. The audit
records both hashes. The combined diff now passes whitespace checks and the
Slurm script passes shell syntax validation. Add this correction in a small
new commit; no need to rewrite the scientific commits.

Update the presentation and viewer's current cathode selection to the selected
Niflheim run, and include the seed-4 comparison. Those artifact updates remain
pending: the viewer currently pins the old cathode reference, and presentation
v4 predates these results. The presentation README now lists the current
numbers and caveats. Adem's frozen LLM study and production authorization are
unchanged; the interface results must not alter the frozen benchmark rows.

The prior Codex review/docs remain uncommitted alongside this review. Publish
them in a separate explicit documentation commit, preserving both authors'
log entries. This review itself did not commit, push, launch jobs or send an
external message.

Evidence: [audit JSON](data/reviews/niflheim_batch1_review_20261021.json),
[CONTACT_PROTOCOL.md](CONTACT_PROTOCOL.md), and `data/petmad/niflheim_batch1/`.
