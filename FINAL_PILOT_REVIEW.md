# Final pilot: independent review and integration handoff

**Integration update, 22 October:** Adem applied the reader patch in `5b76988`.
It is now included with the final physics release in the dedicated integration
branch. See [FINAL_INTEGRATION.md](FINAL_INTEGRATION.md) for combined verification.
The review below records the state before that integration.

22 October 2026. Reviewed physics `1b76eeb` and agent `c0a0546` in isolated
archives. The physical campaign and the live pilot are complete. No new model
call, PET-MAD calculation or cluster submission was made in this review.

## Verified scientific record

The final index SHA-256 is
`47d69f7dd75dff89e1d2e5191f2f1d31fad002581521c39eeee7593c90d83c41`.
All three decision-index snapshots agree with the respective live execution
records. Producer-bundle hashes, all model-stage hashes, the amendment hash,
the complete state hash and the executed pilot-code hash verify. Rebuilt
primary feedback matches all three archived model snapshots. Their sensitivity
entries contain availability information only, not sensitivity values.

The final index preserves all **17 evaluated primary rows** exactly. LiF's
unrun rows have intentionally changed from pending to not selected. Independent
source checks validate all 32 saved runs (26 new plus six reused): checkpoint,
structures/cells, recomputed W_adh/W_sep, file hashes where present, and all
96 free-force maxima from saved forces. No energy was recomputed with PET-MAD.

| Coating | Cathode W_adh / W_sep | Electrolyte W_adh / W_sep |
|---|---|---|
| LiNbF6, reference | 3.617 / 5.168 | 1.633 / 2.967 |
| LiTaF6, choice 2 | 3.339 / 4.728 | 1.577 / 2.911 |
| LiCaAlF6, choice 3 | 1.427 / 4.322 | 0.744 / 1.490 |

Units: J/m². The electrolyte is weaker for all three. LiF was not physically
evaluated. These are provisional results for formally polar contact cells,
not measured adhesion or evidence of lithium transport.

LiTaF6 falls within both prospective forecast ranges; LiCaAlF6 falls below
both. The weaker contact is correctly predicted twice. The choice sequence
matches the initial shortlist: the pilot demonstrates a prospective prediction,
its failure on a less similar material, and feedback assessment, not improved
search performance. The model's confusion about `min_W_adh_J_m2` must be
corrected in the accompanying narrative: it means the weaker selected contact,
not the minimum across registries. Preserve the original response.

LiNbF6 and LiTaF6 differ by only 0.056 J/m² at the weaker contact. Their seed-4
shifts are about −0.121 and −0.114 J/m². These are finite construction
sensitivities, not confidence intervals; the small primary difference does not
establish a robust materials winner. LiCaAlF6 has substantially lower primary
adhesion in these models, an electrolyte registry spread of about 0.220 J/m²,
and **unquantified electrolyte thickness and bulk-structure sensitivities**.
Four passing available checks cannot close those two gaps.

## Accounting and protocol amendment

Verified **26 new jobs of the 36-job ceiling**: 12 primary, 10 sensitivity,
4 reference consistency. The 6,632 runner calculator calls and 52 additional
rigid-fragment single points reproduce from the records. Six reused runs
are outside this new-job total: five reference primaries and the reference
seed-4 case. Bulk preparation is also separate.

The runner times sum to **1,525.1 s (25.4 min)**. The 26 completed Slurm job
elapsed times sum to **2,850 s (47.5 min)**. Label the former as runner time,
not total GPU allocation time; queue delay is outside both sums.

The live pilot is complete at **5/10 HTTP attempts**, with zero unsettled
reservations. Logged usage totals 17,365 input and 8,463 output tokens, about
**USD 0.005968** at the recorded rates, not billed cost. An offline completed-state
resume calls no model and leaves its bytes unchanged.

The summary-only 20,000-character amendment is recorded and hashed. The actual
sent summary is **16,285 characters**. The earlier stopped prompt was reported
as 16,334 characters, but its text was not archived; the equality of the unsent
and sent prompt contents cannot be independently verified. The recorded
pre-request stop incurred no extra attempt, and the model settings and total
HTTP cap remain unchanged. Do not describe this as an unamended protocol.

## One integration fix before final figures

The published `c0a0546` reader rejects the 12 LiF rows marked
`not_run_not_selected` in the final index. Simply adding that status would also
leave consistency costs omitted from its compute total. This is an integration
issue, not a defect in the saved primary values.

Prepared [reader patch](data/reviews/final_comparison_reader_fix_20261022.patch)
against `c0a0546`. It:

- accepts the final schema only for explicitly requested offline analysis;
  the live pilot continues to reject robustness-inclusive input;
- keeps unselected rows distinct, rejects measured/quantified outcomes hidden
  under that status, and excludes unrun rows from unknown-cost counts;
- includes consistency work in compute accounting while preserving primary
  selections and exposes the consistency rows separately;
- requires the pinned manifest and marks an incomplete primary set as missing;
- preserves the explicit unquantified sensitivity flags.

On the actual final package, the patched reader reproduces all three contact
pairs, finds no invalid runs, counts all 6,632 new runner calls and four
consistency rows, and retains all 12 unselected rows without invented costs.
The patch is tested in isolation and **has not been applied to Adem's branch**.

Verification: Claude's full suite **165 passed in 24.30 s**; Adem's targeted
pilot/comparison/loader subset **32 passed in 1.65 s** before this patch and
**39 passed in 2.14 s** with seven additional integration regressions. His
earlier mutable-fixture problem is fixed in `c0a0546`.

Adem: apply the patch after obtaining the final physics files, rerun that
subset, and generate the final table/figure from **index_final.json**. Preserve
the live report and snapshots. No additional paid calls are required.

Claude: the physics deliverable is verified; no further calculations are
needed for this bounded pilot.

Davide/Codex: review the combined branch diff, merge without discarding either
contributor's history, run integrated checks, then update the viewer and slides
with this table and the explicit forecast success/failure. Those integration
and presentation actions are still pending, not performed by this review.

Detailed evidence: [final_pilot_review_20261022.json](data/reviews/final_pilot_review_20261022.json).
