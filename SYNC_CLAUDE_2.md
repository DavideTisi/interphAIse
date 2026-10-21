# Contact review and electrolyte thickness handoff

2026-10-21, `davide`. Reviewed implementation: `7249e7a`.

**Recommendation: publish `7249e7a` and proceed with a bounded electrolyte
thickness study.** Both termination issues are addressed. This review makes no
new MLIP calculations and does not publish the commit itself.

## What was checked

The full suite passes **114 tests**. Independently read all 18 saved relaxations:
free-atom convergence, stored energies, corresponding fixed indices in the joined
and separated substrate, and the adhesion arithmetic agree. All three contact
builds reproduce their input hashes, atom counts and uncut-polyhedra records;
the seed-0/seed-4 framework signatures agree for the selected cuts. The archive
accounts for **1,208 calculator calls plus 12 separation single points**.

The 99 committed paths contain no configured credential values; `.env` remains
ignored and untracked. Code, documentation and other data pass the whitespace
check. Two ASE-generated electrolyte `initial.extxyz` files contain 880 trailing
spaces in total; this is formatting, not a numerical discrepancy. Raw artifacts
were preserved.

## Interpretation to retain

- Cathode adhesion varies by only **0.0175 J/m² across the tested constraints**.
  Fixed-atom force vectors in joined/separated structures differ by at most
  0.075 eV/Å, supporting a similar residual force pattern. Similar forces do
  **not prove exact cancellation of polar-surface energy errors**. Say
  “insensitive within this constraint bracket”; polarity remains unresolved.
- Electrolyte adhesion varies by **0.1235 J/m²** across the bracket. The
  +0.0920 J/m² contribution is the change in **fixed-geometry separation energy**,
  a difference involving the joined structure and both rigid fragments. It is
  not a unique attribution to the joined-interface total energy alone.
- The separation/adhesion difference compares rigid fragments with independently
  relaxed references. Its algebra is exact; it does not establish the relaxation
  path or uniquely identify which minimum an isolated fragment would reach.
- The earlier 2.10/0.43 J/m² pilots are not comparable with this protocol.

## Next calculation: vary substrate thickness only

Keep seed 0, the Cl cut, LiNbF6(001), the existing in-plane transformations and
strain, two coating layers, vacuum, checkpoint and optimizer settings. Keep the
current initial registry (0,0), gap 2 Å for this controlled thickness comparison;
save any registry scan separately and flag a changed optimum. Do not change the
surface or matching cell to fit an atom cap.

Geometry-only reconstruction at the same **170.7083 Å²** area gives:

| Substrate layers | Substrate z span | Total atoms | Fixed atoms at bottom depth 3.257602 Å |
|---|---:|---:|---:|
| 2 | 9.58 Å | 440 | 38 |
| 3 | 15.43 Å | 492 | 38 |
| 4 | 21.28 Å | 544 | 38 |

Use a **600-atom cap for this study**. These are feasible input geometries, not
converged thickness results. The constant-depth two-layer mask matches the
archived 0.34-fraction mask; geometry matches up to periodic wrapping. Reuse that
baseline only after the production script verifies the full settings and mask.

Expose substrate/film layer counts and a fixed-depth option in the scripts.
Keep the existing fraction default for reproducibility, make fraction/depth
mutually exclusive, and record the chosen depth, actual indices, slab spans,
transformations and hashes. Apply precisely corresponding fixed masks to joined
and separated substrate references. Verify that increasing slab thickness does
not silently increase the frozen depth.

First run the 3- and 4-layer cases and report **both W_adh and W_sep**, free/fixed
forces, structural rearrangement and calculator costs. Use the proposed
0.1 J/m² final-two-setting tolerance for each energy observable. If they fail,
report the failure and define the next bounded extension before running it.
Then repeat the constraint check at the chosen thickness; passing thickness
alone does not establish constraint independence. Define the fixed depths for
that check in advance.

Afterward: cathode coating thickness, vacuum/registry checks, then seed 4 with
the chosen protocol and equivalent cut. Record any seed-dependent fixed count;
do not force equal counts by changing the physical rule. Keep the polar cathode
provisional even if numerical convergence improves.

This work supports the materials demonstration. It does not change the frozen
LLM experiment or delay Adem's separate environment-study protocol. The expanded
thermodynamic tables are already evaluated; expanded LLM runs remain unlaunched.

Machine-readable review: [contact_constraint_review_20261021.json](data/reviews/contact_constraint_review_20261021.json).
Primary evidence and build details: [CONTACT_PROTOCOL.md](CONTACT_PROTOCOL.md).
