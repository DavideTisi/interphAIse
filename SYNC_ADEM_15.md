# Adem: choose-3 verified, LiCaAlF6 batch complete in Slurm

22 October 2026. Reviewed agent archive `9b59000`, manifest-validation changes
`d1ec1b0`, and the LiTaF6 physics package `d5ab477` in isolated copies.
This supersedes the pending-publication and pending-validation statuses in
[SYNC_ADEM_14.md](SYNC_ADEM_14.md).

## Confirmed result and next decision

The state-file checksum, every stage record and feedback snapshot verify.
Eleven primary records pass the consumer's manifest/source checks; rebuilt
feedback matches both archived snapshots exactly. For all six new LiTaF6
runs, Codex additionally reconstructed the physical fixed mask from the initial
structure and frozen depth, and recomputed all 18 free-force maxima from the
saved final structures. These match the recorded masks/forces and force target.
No new energy calculation was needed.

| LiTaF6 forecast | Observed selected-primary result | Check |
|---|---|---|
| Cathode W_adh 3.2–3.9 J/m² | 3.338748 J/m², R1 | Inside range |
| Electrolyte W_adh 1.4–1.9 J/m² | 1.577359 J/m², R2 | Inside range |
| Weaker contact: electrolyte | Electrolyte | Agrees |

Choose-3 selects **LiCaAlF6 (`mp-aaaaajby`)**, record hash
`66ff7ea1abab1ac18f014da8b82b68119c79e402e934c4161a22df6ac58f0282`.
Its prospective ranges are cathode **3.0–3.8**, electrolyte **1.4–1.9 J/m²**,
with electrolyte weaker. Four HTTP attempts are charged, six remain; the
9,404 input and 4,808 output tokens imply **USD 0.0033444** at the previously
recorded rates, not billed cost. Offline resume with a sentinel callable stops
at pending LiCaAlF6 physics without invoking the callable or changing state.

Claude's existing LiCaAlF6 primary jobs **11017178–11017183** were all
`COMPLETED`, exit `0:0`, at 10:12 CEST. Runtime was 1:07–1:21 per job.
This is scheduler completion only; no LiCaAlF6 energies or convergence were
inspected in this review. Claude should publish all six source packages;
Adem validates them and then resumes the final assessment under the existing
approval, same state and total attempt cap. Do not repeat the selections or
submit a duplicate batch. Sensitivities remain outside decision feedback.

## What the pilot does and does not show

The analogy-based LiTaF6 forecast is supported for this one prospective case.
The intervals are broad, uncalibrated ranges; this is not a statistical test of
prediction accuracy or search superiority. LiCaAlF6 was already next in the
initial shortlist and is the only acceptable unevaluated option. The candidate
sequence therefore did not change with feedback.

The response now compares evaluated coatings using adhesion and reports an
"implicit preference" for LiTaF6 over LiNbF6 as revised. The original shortlist
ranked only unevaluated candidates, so it never explicitly ranked LiTaF6 over
the reference. Describe this as a stated reassessment after feedback, not a
documented reversal of an earlier numerical ranking.

LiNbF6's weaker-contact value exceeds LiTaF6's by **0.056 J/m²**. That is below
our 0.1 J/m² numerical tolerance and the approximately 0.12 J/m² bulk-structure
sensitivity demonstrated for the reference. Do not claim a robust materials
winner from that gap. Both models remain formally polar. Keep frozen
thermodynamic labels unchanged despite the model's recurring speculative
trigger about future changes to acceptance/bin.

## Test fixture fix to apply

On published `9b59000`, the pilot/comparison/loader subset gives **29 passes,
2 failures**. The test fixture copies the evolving campaign index. Now that
LiTaF6 has real results, the simulated pause test no longer starts pending, and
the synthetic report test inherits real result hashes. This does not invalidate
the reviewed live package, whose independent checks pass.

Prepared [test-only patch](data/reviews/pilot_fixture_fix_20261022.patch): retain
genuine reference evidence but reset prospective test rows to pending and clear
their outcome fields; give each synthetic result its own hash. The same subset
then gives **31 passes in 1.60 s** in the pinned environment. Existing manifest
coverage, wrong-identity and wrong-species regressions pass. This is not a claim
that all 77 previously reported tests were rerun.

Apply the patch on the agent branch and run:

```sh
git apply /path/to/davide/data/reviews/pilot_fixture_fix_20261022.patch
python -m pytest -q tests/test_pilot.py tests/test_mlip_comparison.py tests/test_mlip_loader.py
```

The patch changes tests only and has been exercised in an isolated archive;
it is not yet applied to your branch. No live state, production result or
runtime validation rule was changed. Review evidence:
[choose3_review_20261022.json](data/reviews/choose3_review_20261022.json).
