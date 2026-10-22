# Bulk-results review and next PET-MAD protocol

21 October 2026, `davide`. Prepared for Davide to share with Claude; not sent to
another session. The multistart and interface work below is recommended, not run.

## Verification

The saved ten relaxations reconcile to **2,944 calculator calls**, **548.84 s**.
Energy differences recomputed from stored energies/atom counts agree with the
report. Structural inspection replayed exactly in a temporary copy. All six
`tests/test_relaxation.py` tests pass, with dependency deprecation warnings.

Symmetric runs converge on **symmetry-projected** forces/stress: raw maximum
forces remain 0.0116–0.0208 eV/Å, and LiCoO2's raw maximum stress is 0.110 GPa.
The unconstrained checks meet the limits on unprojected values. One small-rattle
check is not a full dynamical-stability test.

UPET documents approximate rotational equivariance
([official documentation](https://lab-cosmo.github.io/upet/latest/usage/ase.html#rotational-averaging)).
We rotated the saved structures and cells together and checked identity plus three
random orientations (seed 20261021), using the verified checkpoint, CPU/two threads.

| Material | Distorted minus symmetric energy over four orientations | Largest orientation range for one structure |
|---|---:|---:|
| Li6PS5Cl | −64.20 to −63.58 meV/atom | 0.663 meV/atom |
| LiZr2(PO4)3 | −7.75 to −7.57 meV/atom | 0.557 meV/atom |

Both energy decreases persist across these orientations. This supports investigating
lower minima within PET-MAD; it does not validate physical phases or bound every
orientation error. No geometry was relaxed in this check.

Code: `scripts/check_bulk_rotations.py`. Results and checkpoint/input/script hashes:
`data/petmad/bulk_rotation_review_v1.json`. The initial interactive check used 16
single points; executing the saved script used another 16 and reproduced the
energies exactly. Total added here: **32 single-point evaluations**, separate from
Claude's 2,944 calls. No API calls or cluster jobs.

```bash
MPLCONFIGDIR=/private/tmp/interphaise-mpl HF_HUB_OFFLINE=1 .venv/bin/python \
  scripts/check_bulk_rotations.py --output runs/bulk_rotation_replay.json
```

Choose a fresh output path. This diagnostic does not change the production model.

## Recommended decisions for Claude

1. **Option (c), starting with a fixed small multistart batch.** For Li6PS5Cl and
   LiZr2(PO4)3, add seeds 1–5 at sigma 0.02 Å from each saved symmetric relaxed cell,
   retain seed 0, and relax positions/cell without symmetry. Keep the checkpoint,
   zero external pressure, force/stress targets and initial 1,000-step budget fixed.
   Save failures and costs; identify any longer continuation explicitly. Inspect
   short contacts, volume and framework coordination, and compare final structures
   as well as energies. Choose a valid low-energy unconstrained minimum as a model
   reference and retain a distinct low-energy alternative, if found, for sensitivity.
   This probes nearby basins, not every Li occupation or S/Cl disorder configuration.
   If starts agree, an MD anneal is optional. If they disagree materially, define a
   broader sampling/annealing protocol separately; a short anneal does not establish
   equilibrium disorder. Start locally; use Niflheim Slurm if measured cost warrants it.
2. **Initial common cap of 512 atoms, primary LiCoO2(001).** Keep the 128-atom (101)
   cathode option as a separately labelled orientation sensitivity. The 440-/456-atom
   matches used symmetric bulk cells: rematch the selected references before assuming
   those sizes or a 512-atom limit suffice. Keep the parent basis or record basis
   transformations; do not restore cubic symmetry merely for matching convenience.
   The other three materials have saved unconstrained checks meeting raw limits.

The cap is a resource limit, not convergence evidence. Thickness tests may need
larger cells. The 300 Å² search cap is also provisional; the earlier ~185 Å²
observation is superseded. Enumeration stops at 60 candidates per facet pair, so
report truncation and describe minima as those among returned candidates.

The leading matches remain polar (formal dipole/area reaches about 2.06 e/Å on the
cathode-(001) substrate). Apply the existing termination, constraint, thickness,
vacuum and registry checks. Use consistent strain, stoichiometry and constraints
for joined/separated references, and inspect whether they reconstruct into different
basins. If reporting both, distinguish fixed-geometry cleavage from independently
relaxed adhesion. The new match also changes the coating facet: a difference from
the old pilot cannot be attributed solely to bulk relaxation.

## Interpretation and project boundary

- Say **PET-MAD finds lower-energy distorted structures**. DFT literature reports
  Li6PS5Cl symmetry breaking ([D'Amore et al., 2022](https://pubs.rsc.org/en/Content/ArticleLanding/2022/CP/D2CP03599E)),
  which supports plausibility but does not validate this Pc minimum.
- The input is a fully occupied ordered MP approximant. The calculations alone
  do not establish that its coordinates are an experimental disorder average.
- Bulk rearrangement may affect the electrolyte pilot, but contributions can partly
  cancel between joined and separated references. The bulk energy drop alone gives
  neither the size nor direction of the adhesion error. Retain 0.43 and 2.10 J/m²
  as historical feasibility values until consistent recalculation.
- Contraction was measured here. Generic claims about r²SCAN contraction or agreement
  with experiment need phase-specific source checks; the approximate experimental
  lattice constants in the original bulk report were not verified here.
- These PET-MAD findings do not change the frozen MP-based discovery result or the
  prepared 423-combination expansion.

Claude owns bulk multistart/interface implementation; the other Davide workstream
owns expanded thermodynamic data; Adem owns feedback controls. Shared reports now
record the bulk milestone. Claude's code and original evidence remain intact.
Commit bulk work separately from the expansion and stage explicit files in the
shared checkout. No commit, push or cross-session message was made in this review.
