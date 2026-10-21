# Reply to Adem's second sync note

21 October 2026. Prepared for Davide to share; not sent automatically.
Read `origin/work/agent-experiments` at `40e79c3`, including SYNC_DAVIDE_2.md,
the discovery implementation, experiment runner and analysis script. No merge,
paid calls or new experiment was performed. Reported live-run outcomes below
are from Adem's note, not independently reproduced from raw data.

## Interpretation of the first results

The reported 7/10 iterative versus 1/10 sequential successes is promising evidence
for a feedback benefit on this frozen task. It is preliminary: obtain raw runs,
inspect exclusions/retries and compare uncertainty before making a strong claim.
The reported upfront sensitivity (2/10 acceptable but 10/10 reaching bin <= 2)
shows how strongly the conclusion depends on the precise target. Keep both results
visible; do not describe prior knowledge as generally ineffective.

Our review-motivated deterministic fluoride-first baseline reaches an acceptable
candidate at query 2. This was selected after inspecting the exhaustive table,
so disclose its provenance. It is a useful simple chemical heuristic, not a blind
preregistered competitor. See EXPERIMENT_AMENDMENT.md and the saved chemical-prior
audit. Removing fluorine leaves zero acceptable candidates and is not an acceptance
control under the same objective.

## Answers to the five questions

1. **Threshold:** retain the frozen <= 0.050 eV/non-Li atom acceptance threshold.
   Binning and acceptance serve different purposes; it is possible and consistent
   for a bin to contain passing and failing candidates. Bin 2 is [0.040,0.060),
   so bin <= 2 is a looser target. Report it only as the explicitly post-hoc
   sensitivity check, not a replacement primary endpoint. Small differences near
   the threshold are not evidence of corresponding physical predictive accuracy.
2. **Run data:** yes, recommend a compact, sanitized archive under data/experiments/.
   Include original upfront runs as well as the rerun, all failures and retries,
   prompts/responses, manifests, usage, source commit and selection rule for which
   batch enters the primary figure. Exclude credentials, headers and environment
   dumps. Hash artifacts. Make benchmark paths repository-relative or allow an
   explicit analysis path override: the current manifest records absolute paths
   and the analyser opens that path directly, which is not portable to Davide's
   checkout. Raw evidence is needed before validating the reported counts/traces.
3. **Shuffled feedback:** useful as a next controlled experiment, after the accounting
   issue below is resolved and the shuffle definition is fixed. No new calls were
   launched or authorized to another agent by this reply. Freeze a coherent mapping
   of full feedback records, maintain real scoring separately, and log the mapping.
   Existing runs already exist, so extensions and changed protocols must be labelled
   prospective follow-ups, not retroactive preregistration. The suggested >=30 runs
   per arm is a practical target, not a power guarantee; do not pool incompatible
   prompt/accounting/token-limit batches silently.
4. **MLIP selection:** yes. The frozen shortlist contains LiNbF6 (mp-aaacjjwh),
   LiCaAlF6 (mp-aaaaajby), and LiZr2(PO4)3 (mp-aaabevhd). The seeded random comparator
   overlaps LiCaAlF6; keep that overlap. Saved geometries now cover both LiNbF6
   contacts and the viewer displays both. This does not mean the whole shortlist
   has been calculated or that adhesion is physically validated. Bulk preparation,
   polar surfaces and convergence checks remain necessary. The older follow-up
   manifest has not yet been reconciled with the newly saved electrolyte pilot.
5. **Merge:** review the raw-data archive, accounting policy and analysis portability
   before main integration. The agent branch already contains our evaluator and
   earlier pilot through 8f97726, but does not contain the viewer/review update
   05757ee. Nothing was merged during this review; Davide still has separate local
   edits to the preparation/inspection scripts.

## Integration issues found by code inspection

- `propose()` rejects unavailable/repeated IDs before `queries.query()` and retries
  them without consuming the evaluation budget. BenchmarkQueries itself correctly
  charges invalid/repeated queries, but these proposals never reach it. This differs
  from the note's claim and current public task wording. Distinguish malformed
  messages (no identifiable query) from invalid ID attempts. Either enforce the
  existing policy or explicitly document and version an alternative. Audit the
  existing runs to establish the actual effect; do not assume that it changes the
  result or relabel the runs as compliant without checking.
- The analyser divides by the number of files it finds rather than the expected
  repeats. Missing run files could therefore disappear from the denominator.
  Validate expected run IDs, statuses and hashes before producing a figure, and
  fail clearly on a missing file. Existing failed files are retained by the code.
- Combining experiment folders selects the last folder for each entire arm. It
  does not combine disjoint repeats when extending from 10 to 30. Add explicit
  repeat identity/merge policy and reject duplicate conflicting runs; preserve a
  transparent exclusion table for intentionally replaced batches.
- Cross-folder validation checks hashes and budget, but not model, prompt,
  temperature or token cap. Record and flag those differences in analysis. The
  upfront 4096 rerun versus 2048 other arms needs the explanation already in the
  sync note, not an assumption of identical settings.

These findings come from source inspection; no tests on Adem's branch were run
here. They do not establish that published counts are wrong. The raw trace audit
is the next evidence needed. For the shared candidate-order seeds, preserve the
run pairing and report a paired sensitivity analysis as appropriate rather than
relying only on aggregate counts; seed here controls order, not deterministic
sampling from the provider.
