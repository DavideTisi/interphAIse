# Final-geometry review and bounded Niflheim follow-up

21 October 2026, `davide`, reviewed at `dc62dfe`.

**Recommendation: publish `97cf4af`, `ea02e86` and `dc62dfe`, then run the
seed-4 comparison and two distinct cathode registries on Niflheim.** Include
the small runner fix in this review before attempting off-grid registries.
The remote was still at `e5c745e` when checked. This review did not push,
submit jobs or message Claude directly; this is Davide's handoff to relay.

## What the archive supports

The ten new runs contain 30 converged relaxation records. Independently read
saved final forces and energies, checked free-force targets and recorded
absence of overlaps, recomputed W_adh and W_sep, and reconciled 2,826 calculator
calls plus 20 rigid-fragment single points. Both constraint brackets pass at
the working geometries:

| Contact | Atoms | W_adh spread | W_sep spread |
|---|---:|---:|---:|
| Cathode | 696 | 0.01326 | 0.00048 |
| Electrolyte | 880 | 0.04818 | 0.02289 |

Works are in J/m². This supports insensitivity within the tested brackets.
The final 880-atom vacuum record has identical energies at 15 and 25 Å and
passes the relaxed free-force targets. It remains an isolation check within
the finite-range model, with no remedy for polar electrostatics.

**The earlier half-supercell grid recommendation in SYNC_CLAUDE_5.md was
inadequate.** I recommended it without checking translational redundancy.
The cathode relaxed comparisons therefore tested one physical registry;
those repeats do not establish registry convergence. The 36-point unrelaxed
diagnostic spans 0.00819 J/m², which motivates a small relaxed follow-up,
not a claim that all relaxed registries coincide.

For the electrolyte, the four archived runs give W_adh 1.63133–1.63307 and
W_sep 2.96690–3.06471 J/m². Keep (0,0) as the working representative of the
lower reported joined-energy class. The very small joined-energy difference
does not establish a uniquely resolved physical minimum. Report the W_sep
registry range alongside its reference value. A factual correction to the
protocol: repeated A energies differ by 0.000977 eV and repeated B energies
by 0.002930 eV, not less than 0.001 eV in both cases.

The archived Niflheim 504-atom smoke agrees with the local W_adh to
0.000154 J/m² (GPU) and 0.0000661 J/m² (CPU), with identical steps and calls.
That validates this smoke workflow. There is no archived GPU W_sep smoke,
and its runtime is not a promise for an 880-atom relaxation.

## Necessary runner fix

`run_petmad_interface.py --registry` previously selected from the fixed
2×2×3 scan only. Asking for (1/3,1/3) or (1/6,0) would raise `StopIteration`.
It now adds the requested point once, evaluates its overlap/energy, and
explicitly selects it even if another unrelaxed point is lower. Invalid or
rejected requested points fail without falling back. The historical scan
is unchanged for existing inputs; an off-grid request adds one accounted
single point. Eight offline regression tests pass.

`fixed_geometry_separation.py` now accepts `--device`, defaulting to CPU,
and records both its device and the joined run's device. Use `--device cuda`
for the GPU follow-up so the rigid fragments use the same device as the
joined and relaxed references. Device plumbing is checked offline; no new
GPU calculation has been run in this review.

## Proposed batch: five runs at most

Use one pinned source snapshot containing the runner fix and the same
checkpoint hash `3f52e97c459b2a28a94fc49b8a2f9a92551231a0ea4f5b5db2396f12d8ffa1e9`.
Use the validated RTX 3090 partition, Slurm allocations and isolated env.
Specify the immutable `CODE=.../code_<commit>` path per job rather than
relying on a symlink that could change while queued. Keep API credentials local.

1. **Cathode reference on GPU:** original 696-atom 2+4-layer build at (0,0).
2. **Cathode distinct registry:** same build at (1/3,1/3).
3. **Cathode distinct registry:** same build at (1/6,0).
4. **Electrolyte seed-0 reference on GPU:** original 880-atom 4+4-layer build
   at (0,0).
5. **Electrolyte seed 4:** build 4+4 layers with the already mapped, uncut
   Cl framework cut, same coating facet and fractional registry (0,0).

The two reference runs make each comparison use the same device and settings.
Reuse one only if an equivalent completed GPU run already exists; no duplicate
submission. Predeclare these inputs and outputs before starting. Claude owns
this batch; this review has not launched it.

Shared settings: 15 Å vacuum, initial gap 2 Å, fixed in-plane cells, existing
FIRE force target 0.05 eV/Å and 400-step limit, existing three-stage relaxation
and two rigid-fragment single points. Keep the cathode's physical 104-atom
bottom mask (0.34 fraction of its unchanged substrate); electrolyte frozen
depth 3.257602 Å. Record seed 4's actual fixed count rather than requiring
it to equal 38. Verify labels, masks, stoichiometry, intact PS4 units and
absence of overlaps before computing. Record seed 0 vs seed 4 cell, area,
strain, physical mask and termination correspondence. Do not equate a
matching pymatgen termination label with an equivalent cut.

Pass decimal coordinates to argparse, for example:

```text
--registry 0.3333333333333333 0.3333333333333333 2
--registry 0.16666666666666666 0 2
```

For cathode registry selection, compare relaxed joined energies only within
the identical cell/composition/mask; retain each run's own consistently
relaxed references and report their differences. Preserve failures. For
seed sensitivity, compare both works at the same fractional registry, report
all geometry differences, and do not rank different seeds by raw interface
total energy. Use 0.1 J/m² as the existing reporting tolerance, not a reason
to add further settings after seeing the outcomes.

Record source/checkpoint, device, package versions, job IDs/resources,
convergence, calculator calls including requested off-grid single points,
wall times, and both works. If a case exhausts its limit, report that before
extending the study. This is a bounded sensitivity check, not a global
registry search or proof of physical accuracy.

## Claims and project scope

Working reference values remain cathode **3.60 / 5.13** and electrolyte
**1.63 / 2.97 J/m²** (W_adh / W_sep), with electrolyte registry variation
reported explicitly. Both contacts remain formally polar, model-dependent
and provisional. A seed-4 agreement would support robustness to these two
sampled bulk references; it would not establish an ensemble or experimental
phase. Keep the LLM feedback study as the main result and the interface work
as supporting feasibility and sensitivity evidence.

Adem's frozen environment production is already approved and independent;
Adem owns that execution. No extra LLM calls, candidate ranking, coating
campaign or changes to the frozen scientific tables are part of this batch.

Evidence: [audit JSON](data/reviews/final_checks_review_20261021.json),
[CONTACT_PROTOCOL.md](CONTACT_PROTOCOL.md), [NIFLHEIM.md](NIFLHEIM.md).
