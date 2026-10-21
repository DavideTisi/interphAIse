# Adem: polish the experiment code and deliver the three-coating comparison analysis

**Updated later on 21 October:** [SYNC_ADEM_12.md](SYNC_ADEM_12.md) replaces
the fixed-cohort and no-new-LLM-call directions below with a bounded physical
feedback pilot. Keep the safeguards and analysis infrastructure assignments.

21 October 2026. Davide confirmed the three-coating PET-MAD expansion as the
next deliverable. Claude owns the physical campaign through archived results;
you own the analysis and figures that turn those results into a comparison,
alongside the focused discovery-code fixes. Davide/Codex owns scientific
scope, independent review, the viewer and branch integration.

Read `JOINT_REVIEW_AND_HANDOFF.md` (F3/F4), `MLIP_COMPARISON_PLAN.md` and
`SYNC_CLAUDE_8.md`. Continue on `work/agent-experiments`. Keep the completed
450-run cohort and frozen criteria immutable; this work requires no new
paid LLM calls.

## 1. Close the two analysis/accounting gaps

- **F3:** make final production analysis replay charged outcomes against
  `BenchmarkQueries`, checking proposal/result correspondence and derived
  traces. Enforce the approved model, temperature 1.0, 4096-token limit, prompt
  version and workflow/provenance rules against manifests and available
  per-call metadata. A table hash alone does not validate stored outcomes.
- Test altered outcomes and wrong settings separately. Preserve the declared
  handling of failed runs; do not drop them from denominators. The real
  production archive must reproduce the same primary numbers and Holm tests.
- **F4:** distinguish proposal attempts, HTTP attempts, format retries and
  transport retries in the client and usage report. Add an offline 429-then-
  success test. Record safe request/response identifiers and final errors,
  never credentials or raw request headers. Historical transport retry counts
  stay unknown; 2,800 is the verified number of recorded proposal attempts.
  Keep list-price estimates distinct from billed cost. Future malformed output
  logging can improve parsing replay without modifying old archives.

These should be a focused polishing commit, not an agent redesign. The
recorded prompt/experiment execution is historical; avoid applying a new
workflow hash requirement to old runs without an explicit versioned policy.

## 2. Build the MLIP campaign reader and validator now

Do this in parallel with Claude's geometry work, using existing LiNbF6 result
packages as fixtures. Add a small analysis entry point, for example
`scripts/analyse_mlip_comparison.py`, accepting a campaign manifest rather
than globbing whichever run happens to be latest. Claude will write the new
manifest/index under `data/petmad/coating_comparison_v1/`.

The starting cohort is LiNbF6 `mp-aaacjjwh`, LiCaAlF6 `mp-aaaaajby` and
LiZr2(PO4)3 `mp-aaabevhd`, each against LiCoO2 and Li6PS5Cl. A bounded geometry
failure may trigger the predeclared LiF-then-LiTaF6 fallback in Claude's note,
before interface energies. Read the selected cohort and failures from the
manifest; do not hard-code three formulas or silently omit failed members.

Use a small shared contract rather than a large new framework. Minimum
campaign/index information is: candidate ID/formula/selection reason; endpoint
and contact side; bulk/build/protocol/checkpoint hashes; run path and source
commit; registry/thickness/constraint/seed settings; status/failure reason;
device/job identity; validated W_adh/W_sep or null; calls and elapsed time.
Agree on field names with Claude before he emits final records. Preserve raw
runner outputs and use the index for cross-material identity.

Validation and reporting must:

- require the declared candidate/contact/setting coverage and reject duplicate
  run identities, mismatched model/protocol references and missing source files;
- check the source numerical validity, force targets, energy arithmetic and
  matching cell/area/fragment identities before presenting a validated work;
- retain failed builds, exhausted relaxations and incomplete settings with
  clear statuses; do not turn missing work into zero adhesion;
- select a registry by the frozen lowest-relaxed-joined-energy rule within
  one comparable cell/composition/mask, never by comparing absolute total
  energies between coatings or between bulk seeds;
- distinguish reused compatible results from contextual legacy pilots and
  sum **new** versus reused compute separately, without double-counting runs;
- join the existing thermodynamic values by exact material ID, verifying the
  frozen table hash. Do not combine MP and PET-MAD total energies or rewrite
  the original thermodynamic ranking.

Tests should cover an incomplete campaign, duplicates, an unconverged result,
wrong checkpoint/protocol, and an energy/area mismatch, plus a valid existing
archive fixture. Add a fixture for an explicit fallback/failure record. These
are offline tests; no fresh simulation is needed to develop the reader.

## 3. Deliver the comparison and integrate it into the story

Produce a machine-readable summary, a readable comparison table and one
figure with separate cathode/electrolyte panels. Show each coating's frozen
thermodynamic penalty/acceptability alongside W_adh and W_sep, with recorded
construction and sensitivity flags. Keep registry, thickness/constraint and
bulk-reference sensitivities distinguishable; they are finite tested ranges,
not confidence intervals. Do not invent a combined score or retrospectively
declare an adhesion threshold after seeing the data.

The figure should support a concrete question: **do the shortlisted coatings
also produce attached, numerically credible interfaces, and what trade-offs
or model limitations appear?** Strong adhesion alone does not establish a good
battery coating. Both the finite-range/polar limitation and the absence of a
lithium-transport test remain visible.

Update the presentation in two connected parts:

1. The existing controlled result: the LLM chooses the next material and
   updates its chemical hypothesis from feedback; its benefit depends on the
   environment. Preserve sulfide improvement, chloride's ceiling and LLZO's
   random advantage, with the corrected caveat in `SYNC_ADEM_10.md`.
2. The new materials follow-up: a fixed shortlist is tested with PET-MAD at
   both contacts under declared rules. This extends physical assessment;
   it does not retroactively make the LLM experiment an MLIP-driven search
   or prove new reasoning, practical transport or experimental performance.

Prepare the table/figure layout using labelled fixture data while calculations
run, and replace it only with validated campaign outputs. Commit/push the
polishing, reader/tests, and final analysis/figures separately. Keep a scoped
handoff/log entry; coordinate shared status-file edits through Davide.

**Done means:** the old production results still reproduce, the new manifest
validates or explains every missing/failed item, and the three-coating table,
figure and slide text regenerate from committed inputs. Report blockers early,
but continue the independent code/figure work while Claude prepares structures.
