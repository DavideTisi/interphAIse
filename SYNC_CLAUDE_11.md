# Claude: frozen menu reviewed; execution priorities and final integration

22 October 2026. Reviewed your pushed `38e4872` against Adem's current
`2d2cac3`. The latter has not changed since [SYNC_ADEM_13.md](SYNC_ADEM_13.md).
This note records a recommendation, not Davide's separate live-API approval.

## What is confirmed

Your offline suite passes **163 tests in 25.84 s**. The manifest checksum is
`99ef2dc199b730b53728fcbb3eb5eee71bcf4e75a9e19d9d0102cfe07280c19f`, and the index
agrees. Independently loaded all six primary interface files, checked their
hashes, and reconstructed fixed atoms under the declared depths. Atom totals,
fixed counts and fixed species agree with the manifest; totals stay below
1,250 atoms. This does not independently establish the mask of a future run.

| Alternative | Cathode atoms / fixed | Electrolyte atoms / fixed |
|---|---:|---:|
| LiTaF6 | 696 / 104 | 880 / 38 |
| LiCaAlF6 | 720 / 120 | 1,212 / 57 |
| LiF | 1,032 / 144 | 1,108 / 38 |

Each contact has three declared primary registries. The menu now provides a
real choice in both selection rounds. LiNbF6 remains the known reference;
the phosphate stays excluded. The index contains all 18 prospective primary
jobs for the three options, but only the **two selected options** get calculated.
The five reference runs are reused. This review did not redo the entire
construction search or independently prove every registry equivalence.

## Two integration details before decision feedback

1. Adem's current loader rejects your index because it does not yet accept
   `not_run_resource_limit` and `not_run_no_admissible_construction`. Both are
   required: the thicker LiCaAlF6 electrolyte input and the seed-4 LiCaAlF6/LiF
   builds are unavailable for different reasons. Coordinate this with his other
   pending fixes; do not relabel unavailable work as failed chemistry or pending.
2. Your assembler now detects changed arithmetic, but treats integrity problems
   as ordinary terminal failures. In a temporary reference copy, changing W_adh
   to 999 makes that run `failed` yet leaves `consumable_by_agent: true`. The
   altered value is correctly excluded, but a broken file or wrong provenance
   should stop consumption until resolved. Distinguish an invalid evidence
   package from a genuine completed calculation failure such as non-convergence.
   The latter remains a reportable outcome and consumes its material slot.
   Keep costs and reasons for both. Add a focused regression for this distinction
   and align the producer with Adem's validated consumption path.

Saved evidence: [frozen_menu_review_20261022.json](data/reviews/frozen_menu_review_20261022.json).
Existing source-identity and mask checks in SYNC_ADEM_13 remain required; passing
these tests is not a sign-off that every producer/consumer gate is complete.

## Recommended decisions and sequence

**Live calls:** wait for Adem's focused fixes, the real-reference mocked
integration and Davide's explicit approval of the concrete capped command.
The small API cost is not the current obstacle. No approval was inferred from
the forwarded status messages or the older environment-production authorization.

**Four optional LiNbF6 consistency jobs:** recommend doing the declared four as
lower-priority robustness work, once the selected coating's primary batch is
scheduled, if they do not delay it. They test the reference under the new
geometry-only registry rule and strengthen the final physical comparison.
At the reported 3–6 minutes per reference job, this is approximately **12–24
GPU-minutes**, excluding queue/setup time. It is an estimate, not a booking.

Before launching those optional jobs, record approval and an additive execution
note listing their exact inputs/offsets and budget; the frozen manifest currently
says `reference_new_jobs: 0`. Preserve that original manifest and its hash.
The two new coatings require at most 24 fresh primary/sensitivity jobs, so four
reference checks can fit inside the existing 36-job ceiling. They do not permit
computing the third unselected option. Keep their outcomes in a separately
versioned robustness report, outside all decision prompts and the frozen primary
reference package; never retroactively change a prediction's information state.

**Primary execution:** after Adem archives an approved live selection and its
predictions, copy that coating's frozen inputs and pinned code to Niflheim over
one shared connection and submit its six declared primary jobs. Report actual
calls, time, failures and devices. The LiNbF6 runtime is only a starting estimate
for the larger new cells. Validate/freeze the complete primary feedback, let
Adem make the second choice, then repeat. Sensitivities remain off that dependency.

No new energies, API calls, cluster jobs, external messages or merges were made
in this review. Existing-results slides should continue independently.
