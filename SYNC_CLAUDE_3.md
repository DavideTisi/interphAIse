# Electrolyte thickness review and cathode thickness handoff

21 October 2026, `davide`, reviewed at `40b80fa`.

**`b51c14e` is already published.** Codex's push of `40b80fa` included it.
A fresh GitHub branch-tip check confirms `origin/davide` is at
`40b80fa3f1f65b330a372878c2589ea17c80e7f2`. No additional push of that commit
is needed. Preserve the concurrent presentation/report edits.

## Review

The electrolyte result meets the declared numerical criterion. The final
thickness increments are 0.0674 J/m² for relaxed adhesion and 0.0527 J/m² for
fixed-geometry separation. At four layers, the constraint spreads are
0.0481 and 0.0240 J/m², respectively. Retain four layers and the reference
frozen depth of 3.257602 Å for the subsequent electrolyte checks.

Independently read the five unique archived runs: all 15 relaxations meet
their recorded free-force targets, are finite and have no recorded overlap
violations. Adhesion recomputed from the saved total energies and area agrees.
The archive accounts for 1,827 calculator calls plus ten rigid-separation
single points. The reference four-layer run belongs to both study tables;
do not count it twice. No new energy calculation ran in this review.

Keep the following distinctions in the write-up:

- Say **insensitive within the tested constraint bracket at 0.1 J/m²
  tolerance**, rather than independent of the constraint. A small trend remains.
- Four layers meets the final-two-setting tolerance. A plateau has not been
  demonstrated, and both contacts remain formally polar.
- The 0.018 J/m² registry difference at three layers comes from an unrelaxed
  scan. It supports holding registry fixed for this controlled thickness test,
  but does not establish that competing registries relax to equivalent energies.
- The separated-surface Li rearrangement persists from two to four layers.
  That supports a surface contribution; it does not prove all remaining
  finite-thickness effects are absent.

## Proceed with a bounded cathode coating-thickness test

Vary only the number of LiNbF6 coating layers at the existing cathode contact.
Keep LiCoO2(001), LiNbF6(001), explicit termination
`F2_P-6_3` / `Li_P6/mmm_1`, two cathode substrate layers, the same bulk inputs,
in-plane transformations, strain, 15 Å vacuum, model/checkpoint, optimizer and
free-force target. Hold the initial registry at (0,0), gap 2 Å and save the
scan separately. Compare relaxed adhesion and fixed-geometry separation.

Geometry-only reconstruction verifies:

| Coating layers | Total atoms | Substrate atoms | Fixed substrate atoms |
|---|---:|---:|---:|
| 2 | 504 | 312 | 104 |
| 3 | 600 | 312 | 104 |
| 4 | 696 | 312 | 104 |

Use an **800-atom cap for this bounded study**. The verified area remains
88.800 Å² and strain 1.952%. Transformations, cuts, substrate geometry and the
physical fixed mask match the baseline, with no cut CoO6 or NbF6 polyhedra.
The coating's formal polarity grows from 0.613 to 0.920 to 1.226 e/Å, so report
it at each thickness. These are feasible inputs, not relaxed-energy results.

The unchanged substrate allows reuse of the baseline 0.34-fraction constraint.
Verify that it selects the same physical 104 atoms, and use the corresponding
mask in the separated substrate. **Global atom indices change when coating
atoms are added** because the combined structure's ordering changes. Compare
masks through substrate-relative ordering/site correspondence, not by copying
the old joined-system indices. If switching to a fixed-depth parameter, first
verify it reproduces the same mask exactly.

Reuse the archived two-layer baseline only after verifying the full settings,
initial geometry, registry and constraint correspondence. Run three and four
layers, then apply the same 0.1 J/m² final-two-setting criterion to both energy
observables. Report the trend, separate film/substrate relaxation contributions,
free/fixed forces, rearrangement, polarity and actual compute cost. If it fails,
report the failure and propose a bounded extension before launching it.

Reproduction of the geometry check uses `scripts/build_contact.py` with the
existing bulk stability-check files, `--names LiCoO2 LiNbF6`,
`--substrate-miller 0 0 1 --film-miller 0 0 1`, the explicit termination above,
`--substrate-layers 2`, `--film-layers 2`, `3` or `4`, and `--max-atoms 800`.
Use a fresh output directory for every build and assert agreement with the
baseline transformation, strain and cut records before starting relaxation.

## Following this test

Next are vacuum and denser registry checks for both contacts, followed by seed 4
at the selected electrolyte protocol and equivalent Cl cut. For registry
sensitivity, relax a small declared set of promising competing registries;
single-point ranking alone is insufficient. Numerical checks cannot by
themselves resolve the polar-surface/model limitations.

This work remains supporting atomistic validation. It does not modify the
frozen thermodynamic objective or block Adem's approved environment smoke batch.
Expanded LLM production still requires its separate cost review and approval.

Evidence: [review JSON](data/reviews/electrolyte_thickness_review_20261021.json)
and [CONTACT_PROTOCOL.md](CONTACT_PROTOCOL.md). This handoff is a saved
recommendation for Davide to relay; no external message or new MLIP run was sent.
