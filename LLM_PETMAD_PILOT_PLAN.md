# LLM-guided PET-MAD pilot: one known coating, two adaptive choices

21 October 2026. Planning amendment following Davide's clarification that the
LLM should participate in the new coating exploration. This supersedes the
fixed-cohort selection and no-new-LLM-call instructions in SYNC_ADEM_11.md and
SYNC_CLAUDE_8.md. Their code safeguards and physical construction rules remain
applicable. No pilot code, new live calls or calculations were executed while
writing this plan. The completed 450-run environment study remains immutable.

## Question and role of the LLM

Can an LLM use computed interface behaviour to revise a chemical hypothesis
and choose the next coating to evaluate? The LLM owns the next-material choice
and a short, testable prediction. Deterministic code owns candidate eligibility,
construction, simulation, numerical validation and accounting. We are replacing
the scientist's proposal–observation–revision step, not asking the model to
invent energies or treating its explanation as proof of sound reasoning.

The deliverable is three evaluated coating slots: the existing LiNbF6 reference
and two prospectively selected coatings, each against LiCoO2 and Li6PS5Cl.
Failed evaluations still consume their slot and remain visible. Three slots
demonstrate a working feedback loop; they cannot establish search superiority,
statistical significance, exhaustive discovery or practical coating performance.

## Fixed scientific brief

Seek favourable trade-offs between the frozen sulfide thermodynamic penalty
(lower is better) and the weaker of the two validated contact adhesion works
(higher is better). Report both original contact values as well as this minimum.
The minimum is a summary of two model interfaces, not a measured device strength.
Keep the frozen acceptance label, insulation check and numerical-validity flags
separate. A thermodynamically rejected material may be chosen as a diagnostic
comparator, but cannot become an acceptable coating merely by adhering strongly.

Present the two axes and descriptive nondominated candidates among the evaluated
set; do not invent a weighted score, a new acceptance threshold or a unique
overall winner. A candidate dominates another on these two axes only when its
penalty is no greater and its weaker-contact W_adh is no lower, with one strict
improvement. Flag overlapping sensitivity ranges and numerical differences
below 0.1 J/m²; point-estimate dominance is not evidence of a robust advantage.
Invalid/missing contact work is null, not zero, and cannot enter that comparison.
W_sep, reconstruction and sensitivity are supporting observations. Polar-model
limitations and absent Li transport remain explicit for every recommendation.

This objective is a new, declared pilot brief; it does not replace or rerank
the completed thermodynamic benchmark. Freeze it before new coating energies.

## Candidate menu and information boundary

Claude starts construction screening with the five previously named IDs:

| Coating | ID | Role before new energies |
|---|---|---|
| LiNbF6 | mp-aaacjjwh | Known reference, reused only with compatible provenance |
| LiCaAlF6 | mp-aaaaajby | Prospective option |
| LiZr2(PO4)3 | mp-aaabevhd | Prospective near-threshold comparator |
| LiF | mp-aaaaabru | Prospective conventional, thermodynamically rejected comparator |
| LiTaF6 | mp-aaacjmqp | Prospective option |

Use the bounded physical rules in MLIP_COMPARISON_PLAN.md and SYNC_CLAUDE_8.md:
300 then at most 600 Å², 1,200 atoms, unchanged strain tolerances, reviewed
substrate cuts, protected PS4/PO4, recorded exposed coordination, physical
thickness and fixed depths. Complete necessary bulk checks and freeze feasible
builds/registry and sensitivity rules before the agent selects. Geometry and
bulk preparation costs belong in the campaign accounting.

For a meaningful choice at both rounds, aim for at least **three unevaluated,
feasible alternatives plus LiNbF6**. Five formulas is the current construction
cap; this is a small, researcher-curated menu, not unrestricted exploration of
the 141-ID database. If fewer than three alternatives qualify, report that
before live pilot calls. We can still make a physical comparison, but must
not present a forced final choice as evidence of adaptive selection. Enlarging
the construction pool requires a separately recorded resource/scope amendment.

LiF and LiTaF6 are now menu candidates rather than automatic replacements.
LiCaAlF6 and the phosphate are no longer guaranteed selections. Retain excluded
IDs and reasons; exclude only under the frozen pre-energy rules. If any new
interface energies already exist when this amendment reaches Claude, report
their provenance first and label them pre-existing: do not call them prospective.

Every agent card contains the same allowed information: exact ID, composition,
frozen thermodynamic values/labels, available structural/build descriptors and
limitations. The runner supplies validated feedback bundles only for revealed
evaluations. It must not expose unrevealed result files, future summaries or
hidden rankings to the model. Humans may already know the reference result;
this is a prospective model interaction, not a blinded human experiment.

## Sequence and a modest comparison

1. **Freeze the menu, objective and protocol.** Record hashes, builds,
   settings, allowed prompt fields, output schema, evaluator version, budgets
   and failure handling. Implement the code safeguards first.
2. **Optional prior snapshot (one response).** With candidate cards only, save
   the model's initial ranking and brief predictions. This records chemical
   priors but is not a matched no-feedback baseline.
3. **Reveal LiNbF6 and choose coating 2 (one response).** Supply a validated,
   consistently formatted two-contact reference package with numerical and
   physical caveats. Ask for an ordered shortlist of remaining IDs, the first
   selection, its testable hypothesis, predicted weak contact and an observation
   that would change the next choice. Freeze this ordered shortlist.
4. **Calculate coating 2, then choose coating 3 (one response).** Claude runs
   both contacts and the predeclared checks. Adem validates and supplies the
   complete feedback package, including failures and costs. The model selects
   one still-unevaluated feasible ID and identifies the observations supporting
   its decision, whether its choice changes or stays the same. Archive the
   choice before any interface energy for coating 3.
5. **Calculate coating 3 and summarise (one response).** Run the same protocol,
   validate the results, and report which predictions were supported, contradicted
   or unresolved, alongside the thermodynamic/adhesion trade-offs and limitations.

Compare the chosen third coating with the next unevaluated ID in step 3's frozen
shortlist. This is a descriptive decision comparison at a common initial
information state. A changed selection is not necessarily a better selection.
An unchosen coating has no measured outcome: do not invent its energy, plot a
counterfactual performance curve or claim that the adaptive order beats the
upfront order. The optional step-2 snapshot has less information and must be
labelled accordingly. No random/shuffled performance claim comes from this pilot.

Do not require the LLM to change its mind, discard a disappointing trajectory,
or retry until it chooses an interesting coating. Keep failure records, paid
attempts and consumed material slots. A material with one failed contact has
an incomplete physical assessment and cannot receive a validated two-contact
adhesion summary. Do not silently buy a replacement evaluation.

## Implementation, budgets and deliverables

- **Adem:** retain F3/F4 polishing and the MLIP reader/validator; add a small
  resumable propose–evaluate–feedback runner. State transitions must require
  validated feedback and prevent duplicate selection, hidden-result leakage,
  out-of-menu IDs and retry-driven selection changes. Use archived fixtures and
  mocked responses for development. Save prompt/response, structured hypotheses,
  hashes, selected IDs, feedback, model/settings and transport/token accounting.
- **Claude:** retain F1/F2 fixes; supply the feasible menu, per-candidate builds,
  declared checks and a standard feedback package. Prepare all eligible inputs,
  but run new interface energies only for the IDs chosen at each stage. Within
  each selected coating, the two contacts and independent jobs can run in
  parallel. Keep immutable snapshots and publish complete raw evidence.
- **Davide/Codex:** fix the scientific brief, review the manifest, code and
  evidence independently, maintain the viewer and reports, and integrate the
  campaign. Keep the controlled environment findings separate in the slides.

Use direct Anthropic `claude-haiku-5-5`, temperature 1.0 and 4096 output tokens;
record actual returned model identity. Plan four scientific responses if the
optional prior snapshot is included, plus at most one integration smoke response
if needed. Proposed hard ceiling: **10 HTTP attempts total**, including all
smoke, formatting and transport retries. No automatic extension. Adem should
first report expected/conservative tokens and current-rate cost for this exact
cap; this document requests preparation and cost estimation, not an unbounded
paid run or reuse of the earlier 450-run production authorization.

The physical cap stays at 18 registry plus 18 sensitivity full jobs across the
three material slots, before compatible archive reuse. The earlier conditional
2–6 GPU-hour estimate covers those interface jobs only; bulk/menu preparation,
new loop implementation and queue delays are additional. Adaptive stages wait
for feedback, so they cannot all be launched together. Do not promise the
previous 1–2-day schedule before the geometry and integration checkpoints.

Keep physical results/index under `data/petmad/coating_comparison_v1/` and the
new interaction trace under `data/experiments/llm_petmad_pilot_v1/`. Freeze the
whole menu/protocol first, then append hashed selection records prospectively;
the final cohort is intentionally unknown at the initial freeze. Deliver the
three-slot outcome table, decision timeline, prediction checks, cost report,
replayable records and viewer structures. Work is pending, not a new result.
