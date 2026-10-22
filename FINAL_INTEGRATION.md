# Final integration and reproducibility review

## Published to main and made public

On 22 October 2026, following Davide's explicit instruction, `main` was
fast-forwarded from `247e0dc` to the tested release `7ee0092`. Both `main` and
`work/final-integration-20261022` were pushed atomically. All completed contributor
histories are included; no branch was rebased, deleted or force-pushed. GitHub
confirmed `visibility: PUBLIC` and default branch `main`.

Anonymous requests returned HTTP 200 for the repository, README, full results
synthesis, DeepSeek comparison, accessible v4 PPTX/PDF, public viewer and
offline viewer ZIP. Downloaded artifacts matched their local bytes, and the
viewer matched the previously verified release hash. The
[publication receipt](data/reviews/public_release_20261022.json) records these
checks and links the preflight evidence. No credentials were sent in the
anonymous requests.

The original davide checkout and its ongoing presentation edits remain intact.
The completed decks are available as checkpoints; a newer deck covering both
LLM configurations is still being prepared in the presentation chat. The public
social post, final presentation update and event submission remain separate.
No new paid experiment was launched.

## Public-release preflight, 22 October 2026

The user explicitly requested merging and making the repository public. The
completed DeepSeek branch at `550391b` is now integrated in merge `3a93e17`,
following synthesis commit `3410f9b`. The earlier Haiku and PET-MAD work below
is preserved. Only the append-only development log conflicted; both histories
were retained. All contributor heads are ancestors of the release branch.

The final integrated suite passed **246 tests in 38.25 s** with the pinned
dependencies. The offline reproduction wrapper now replays **9,600 queries**:
1,500 from the original benchmark, 4,500 Haiku environment queries and 3,600
DeepSeek queries. It regenerates the model comparison and exploratory LLZO
audit, validates the physics/pilot and exports the full viewer. All checks
passed and **1,859 evidence files remained unchanged**. The original independent
DeepSeek recount is also checked; corruption regressions reject changed scores,
corrected p values, policy and duplicate random accounting.

Completed mixed-audience v3/v4 decks, their builders and illustration were
copied from the original checkout. All four PPTX/PDF hashes match that chat's
recorded validation. The new two-configuration presentation is still in progress
there; no unfinished deck or PowerPoint lock file is included. No original
checkout file was modified. Existing rendered decks remain clearly labelled
as Haiku/PET-MAD checkpoints.

The release performs a credential scan over reachable Git history and tracked
contents, including gzip/ZIP members. A literal fake token in a rejection test
is narrowly classified as a fixture. No `.env` or private-key filename is tracked
or present in reachable history; `.env` and its local backup variants are ignored.
The receipt records scope rather than claiming an exhaustive security audit.

The sections below record earlier checkpoints. Their statements that main had
not advanced describe those earlier reviews, not the intended release outcome.
Publication and anonymous-access verification are recorded above.

## Earlier integrated checkpoint

22 October 2026. The completed agent, physics and presentation work is combined
on `work/final-integration-20261022`. This branch preserves both collaborators'
Git histories. `main` and `davide` have not been advanced by this integration;
the unrelated uncommitted README in Davide's checkout remains untouched.

## Integrated sources

- Davide `7bd5878`: reviewed 24-slide presentation, synthesis and earlier audits.
- Claude `1b76eeb`: final physical index, source calculations and later robustness.
- Adem `1f7bf11`: completed experiment archives, pilot, final-index reader patch
  and generated comparison from `5b76988`, plus the fresh-environment test
  record. The reader fix was already present at the first integration and did
  not need to be applied a second time.

The physics merge is `70a33d8`; the agent merge is `4b5fca4`. Only the dated
development logs and report conflicted, and both contributors' entries were
retained. Current status is stated at the top of the report; earlier entries
remain historical.

Follow-up review of `1f7bf11` found only seven additional development-log lines.
Those were merged after `fef1aab`; no code, dependency, frozen evidence, slide
or generated figure changed. Both contributors' log entries were preserved.

## Verification

- Merged baseline: **220 tests passed** with pymatgen 2026.9.24 and
  pymatgen-core 2026.10.16. The four failures from Adem's older environment do
  not occur with these pins.
- After viewer/reproduction changes: **227 tests passed in 31.61 s**.
  Warnings are upstream ASE/NumPy and spglib deprecations.
- Adem independently reports **200 passed, 0 failed** at `5b76988`, using a fresh
  environment installed from requirements.txt with the pinned pymatgen versions.
  This checks his branch; the 227-test result above checks the integrated tree.
  His new commit records that run without changing tested code. The suite was
  not rerun for this documentation-only follow-up; the non-document tree and
  whitespace were checked instead.
- The offline wrapper replays **1,500 original and 4,500 production queries**,
  validates production settings, reproduces the analyses and verifies agreement
  with the presentation source. It checks the 17 evaluated primary rows remain
  identical between the summary-time and final indices and validates snapshot
  hashes. **1,452 JSON, compressed and geometry evidence files stayed unchanged**
  during execution.
- Final physical analysis has no invalid runs, four consistency records,
  12 explicitly unselected LiF rows and **6,632 new runner calls**. The six
  selected W_adh/W_sep values and all four prospective forecasts agree with the
  presentation; the choice order remains unchanged.
- The final catalogue has **460 saved geometries, 141 candidate IDs and six
  selected contact shortcuts**. Browser inspection confirmed the Nb default and
  Ta/Ca selections, correct displayed energies, rendered structures and no
  browser errors. Geometry round-trips, labels and fixed masks pass the tests.
- The final comparison and forecast figures were visually inspected. A caption
  was added to the comparison figure to keep the polar-model, uncomputed LiF
  and unquantified Ca sensitivity qualifications with the exported image.
- The 24-slide PPTX and PDF hashes still match their earlier full visual review.
  They are scientifically consistent with the merged evidence and were not
  rebuilt. This is not a new Microsoft PowerPoint application-level check.

Machine-readable receipt:
[final_integration_20261022.json](data/reviews/final_integration_20261022.json).
The suite used the existing Python 3.12 environment with the pinned packages;
a separate clean installation was not performed. All analyses ran from this
integration checkout, not from the original editable package path.

## What changed for the reader

[REPRODUCE.md](REPRODUCE.md) is the short entry point; its offline command writes
to `runs/reproduced_results/`. A new `analysis` installation extra supplies
Matplotlib. Five deliberate corruption regressions reject changed acceptance,
physical energies, forecast ranges, choice order and compute accounting.

The viewer obtains selected contacts from the validated final index rather
than assuming the reference material is the only coating. Primary evidence and
later sensitivity/consistency results have separate labels. LiF remains
uncomputed. Missing or inconsistent selected geometry stops export. The same
final index drives the comparison table and figure.

## Scientific limits and release

No LLM call, Materials Project query, PET-MAD evaluation, model download or
cluster job was launched. The live pilot state, prompts, responses, amendments,
decision-time snapshots and frozen criteria were preserved. No additional
experiment is needed to reproduce this bounded study.

The materials conclusions remain provisional: formally polar contact models,
unquantified LiCaAlF6 electrolyte thickness and bulk sensitivity, and a Nb/Ta
gap smaller than the known construction sensitivity. The LLM pilot has two
prospective choices with unchanged order; it does not establish search gains.

The remaining release action is joint review and merge of this integration
branch into the team's chosen shared branch. No contributor branch is rebased
or force-pushed. The main checkout's unrelated README changes must be preserved
when it is later updated.
