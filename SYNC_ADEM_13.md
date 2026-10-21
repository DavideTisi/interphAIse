# Adem: pilot readiness review and focused fixes before live calls

**Physics update, 22 October:** Claude has pushed frozen menu/inputs/index and
contract response at `work/petmad-comparison:38e4872`, manifest `99ef2dc1…`.
Read [SYNC_CLAUDE_11.md](SYNC_CLAUDE_11.md): all three intended alternatives
are present. Your current loader rejects both unavailable sensitivity statuses;
support `not_run_resource_limit` and `not_run_no_admissible_construction` with
their reasons. Distinguish evidence-integrity errors from terminal calculation
failures before allowing feedback. The readiness fixes below still apply.

22 October 2026, Copenhagen. Reviewed your pushed `2d2cac3` in an isolated
archive with the pinned environment. **183 tests pass in 20.46 s**, and
`analyse_environment_study.py --production` replays the real 450-run archive
with unchanged counts and six Holm comparisons. The completed scientific
results stand. The mocked pilot and comparison reader are useful progress,
but the live path needs the three corrections below before approval/execution.

Saved audit: [adem_pilot_review_20261022.json](data/reviews/adem_pilot_review_20261022.json).
All adversarial cases used temporary copies and mocked transport. No real API
request, potential calculation, cluster job or branch merge occurred.

## 1. Put source validation on the decision path

`interphaise/pilot.py:209–219` calls the shallow `load_index` and
`feedback_bundle`; it never calls the source checks in the comparison reader.
Changing a genuine reference index's W_adh to **999 J/m²** reaches the choose-2
prompt. The separate reader rejects that same record with an arithmetic
mismatch. Validation after a decision cannot protect the decision itself.

Share one validated feedback interface between the pilot and the reader. It
must verify source arithmetic/provenance, convergence and finite quantities
before a value can reach a prompt. Keep failed calculations visible with
reasons and costs; an integrity mismatch blocks consumption, whereas a genuine
terminal calculation failure remains a valid reported outcome.

Freeze the expected primary run IDs and candidate/contact/build/protocol
identity independently of mutable result statuses. In a second reproduction,
deleting a pending reference registry from the index allowed choose-2 to run.
Require exact planned coverage and terminal outcomes before selecting the
lowest joined energy. Missing work must not disappear from the denominator.

The reader currently groups cells only by area and atom count. Equal area/count
does not establish comparable composition, full cell, bulk seed, endpoint,
thickness or physical fixed mask. Agree those identities with Claude and verify
them against the sources/build manifest, allowing intentional lateral shifts.
Do not require shifted registries to have identical coordinate hashes. Check
all numerical inputs explicitly for finiteness, including W_sep and areas.

## 2. Make the attempt cap survive errors and resumes

The current 10-attempt guard is not durable. Two offline reproductions:

- Mock each transport sequence as HTTP 429, HTTP 429, then HTTP 200 with invalid
  outer response JSON. Two logical attempts make **6 HTTP attempts**, but the
  saved counter is **2** because `last_metadata` is unset. Restarting the stopped
  pilot advances to choose-2 and reaches **12 HTTP attempts**, with **4 recorded**.
- Interrupt immediately after a mocked submission and restart. Eleven such
  submissions leave the disk counter at **0**, because state is saved only after
  the call returns. No live requests were involved in either test.

Reserve attempts durably **before** transport and finalize each attempt even
when response decoding, timeout or interruption fails. Conservative reservations
that cannot be resolved must still consume budget. Enforce one owner of the
state file. The transport and pilot should share the same accounting boundary;
do not default an unknown multi-retry call to one HTTP attempt.

A terminal failed stage must remain stopped on resume, not count as a successful
completed stage and silently advance. Pin execution mode, settings and evidence
identity; a mocked state must not become live evidence on resume. Add regression
tests for both failures above and for ordinary 429-then-success accounting.

## 3. Let the model revise its own recorded prediction

The choose-3 prompt contains results and IDs but none of the previous hypothesis,
predicted ranges, change trigger or ordered shortlist. Every API call starts a
fresh message. An offline sentinel hypothesis and trigger recorded at choose-2
are both absent from choose-3. The loop can react to data, but it cannot explicitly
revisit the prediction we asked it to make.

Supply the already-revealed structured decision history and ask whether the
observations support or contradict the previous prediction and whether the
choice should change. This is the scientist's hypothesis–observation–revision
step we want to demonstrate. We need concise recorded predictions and evidence,
not hidden reasoning. Keep unrevealed results and sensitivity values excluded.

Persist primary-feedback snapshots when first revealed and reuse their hashes
and contents. Later prompts currently reconstruct old feedback from a mutable
index. Verify stored record hashes and the actual frozen-table contents on
resume, not just a declared `sha256` field. Later sensitivity results belong in
the separate final assessment and must not rewrite a past information state.

## Contract and small corrections in the same patch

- Follow [SYNC_CLAUDE_10.md](SYNC_CLAUDE_10.md): uniform **1,250 atoms**, intended
  alternatives **LiTaF6, LiF and LiCaAlF6**, pending Claude's final manifest. The
  LLM selects two; the runner's three-alternative requirement remains appropriate.
  Your branch includes `davide` at `3cb606b`; read the later amendment at `aa24d9d`.
- Record fixed physical depth and actual mask/build identity, not only
  `fixed_fraction`. Support `not_run_resource_limit` with a reason: LiCaAlF6's
  1,302-atom thicker film cannot run under the cap. Keep availability visible
  while withholding sensitivity values; unavailable is neither pending nor pass.
- Predictions should be **finite ordered intervals**, as planned. Remove the
  undocumented 0–20 J/m² clamp: a negative-work prediction must be expressible.
  The current validator rejects an otherwise valid interval `[-1, 0.5]`.
- Preserve unknown compute as unknown, separately from known zero; keep failed
  and reused costs. Primary bundles should not change when late sensitivity
  costs arrive. Report those costs separately in the final accounting.
- F3 now catches changed metadata, but missing metadata on a successful proposal
  still passes. Removing it from copied sulfide `upfront_r200.json` returns no
  production-validation problems. Require the expected fields on successful
  recorded calls; document narrow historical failure exceptions explicitly.
  Do not invent missing historical HTTP counts. The genuine archive still passes.

## Cost and next checkpoint

At your recorded list rates, 14k input + 8k output tokens gives **USD 0.0054**.
Ten attempts at 6k input and 4,096 output each gives **USD 0.02648**. The arithmetic
is consistent with your estimate. The runner does not enforce the assumed 6k
input bound, so USD 0.03 is currently a conditional estimate, not a hard dollar
ceiling. State/enforce a conservative input bound and account for the added
decision history. These figures are estimates, not newly verified prices or
billed amounts. This review does not grant the separate live-call approval.

Please make one focused patch plus regressions, coordinate the final contract
with Claude, and return a mocked trace using genuine validated LiNbF6 feedback.
Show that altered/missing sources stop before the mock call, retries/resumes
stay within 10 attempts, previous predictions appear at choose-3, and frozen
snapshots survive late results. Then we can review the concrete live command
and bounded cost for Davide's approval. No new large LLM study is requested.

Claude can prepare the amended menu/builds while you fix this path. Keep the
Thursday checkpoints and existing-results slides moving independently; these
corrections do not call for a new scientific objective or a broad refactor.
