# Common-protocol coating comparison: feasibility and bounded plan

**Resource amendment:** the current pilot uses a uniform **1,250-atom cap**,
recorded with energy-free verification in [SYNC_CLAUDE_10.md](https://github.com/DavideTisi/interphAIse/blob/786029128ad234e34aaa880d2bff5250c79277ed/SYNC_CLAUDE_10.md).
The 1,200 limit below records the original assessment. Other physical rules
remain unchanged; sensitivity inputs above 1,250 are explicitly unavailable.

**Selection amendment, later on 21 October:** the active scientific/selection
plan is [LLM_PETMAD_PILOT_PLAN.md](LLM_PETMAD_PILOT_PLAN.md), with assignments in
[SYNC_ADEM_12.md](https://github.com/DavideTisi/interphAIse/blob/786029128ad234e34aaa880d2bff5250c79277ed/SYNC_ADEM_12.md) and [SYNC_CLAUDE_9.md](https://github.com/DavideTisi/interphAIse/blob/786029128ad234e34aaa880d2bff5250c79277ed/SYNC_CLAUDE_9.md).
It uses LiNbF6 as the known reference and lets the LLM select two new coatings
sequentially using validated PET-MAD feedback. The construction rules, audit
and job cap below remain the engineering basis. The fixed cohort, automatic
fallback order and no-paid-LLM wording below describe the previous design and
are superseded. The final cohort is selected prospectively from a frozen menu;
the objective, geometry rules and feedback schema are frozen first.

21 October 2026, branch `davide`, assessment against `8975d4b`.
**Active next deliverable, confirmed by Davide; new campaign calculations have
not started in this planning work.**

## Recommendation and scientific value

Deliver a bounded comparison of three coatings at both contacts. Construction
is the first milestone; the assignment continues through calculations,
validated archives and comparison figures. Focused code polishing supports
that outcome. This closes a gap in the original project: the completed MLIP
work characterises only LiNbF6. Five final coatings are outside this campaign.

Claude owns safeguards, construction and calculations through completion;
Adem owns analysis validation, the campaign reader and comparison figures;
Davide/Codex owns scientific scope, independent review, integration and the
viewer. Detailed instructions are in [SYNC_CLAUDE_8.md](https://github.com/DavideTisi/interphAIse/blob/786029128ad234e34aaa880d2bff5250c79277ed/SYNC_CLAUDE_8.md) and
[SYNC_ADEM_11.md](https://github.com/DavideTisi/interphAIse/blob/786029128ad234e34aaa880d2bff5250c79277ed/SYNC_ADEM_11.md).

The useful question is whether thermodynamically promising coatings also give
credible, mechanically attached interfaces under a consistently specified
atomistic model. Adhesion is an additional property, not a confirmation of the
thermodynamic objective. A strongly adhering interface can still be chemically
unsuitable. Show the thermodynamic penalty, both contact works and limitations
separately; do not invent a weighted score after observing the new results.

This would strengthen the materials follow-up. It would not establish better
LLM reasoning, superiority to a human expert, lithium transport, practical
coating performance or real search savings. The LLM chose and revised coating
hypotheses in the completed benchmark; this study would be a separate physical
assessment of a shortlist. It is not an MLIP-feedback experiment. Preserve all
frozen agent results and keep the existing bounded LiNbF6 batch closed.

## The original shortlist is already specified

`data/benchmarks/mlip_followup_plan.json` contains three distinct IDs:

| Coating | Candidate ID | Sulfide thermodynamic penalty, eV/non-Li atom | Role |
|---|---|---:|---|
| LiNbF6 | mp-aaacjjwh | 0.02877 | Acceptable; existing interface reference |
| LiCaAlF6 | mp-aaaaajby | 0.04772 | Acceptable; alternative fluoride |
| LiZr2(PO4)3 | mp-aaabevhd | 0.05632 | Near-threshold phosphate comparator; not acceptable at 0.050 |

These values are from the frozen expanded sulfide table. All three have
relaxed bulk references. The earlier seed-2026 random comparator is also
LiCaAlF6: this is three unique coatings, not four independent materials or an
independent statistical LLM-versus-random validation. Retain this provenance.

## Offline checks performed now

Evidence: `data/reviews/mlip_shortlist_feasibility_20261021.json`, including
source commit, package versions, input hashes, bounded geometry samples and
lattice-match counts. No potential was loaded and no cluster/API call occurred.

Used the existing released bulk references and matcher, LiCoO2(001) and seed-0
Li6PS5Cl(111), area cap 300 Å², length tolerance 0.05, angle tolerance 0.03,
area-ratio tolerance 0.10, validation strain cap 0.06 and atom cap 1,200.
Geometry samples use the previously chosen substrate terminations, two layers
per material, and at most eight unique matches per film termination. These are
construction probes, not final physically comparable thicknesses.

- **LiCaAlF6(001):** sampled cathode cells pass basic gates and preserve AlF6,
  but there is no electrolyte lattice match at these settings.
- **LiCaAlF6(100):** the only coating facet among the five returned low-index
  facets with lattice matches to both substrates. Sampled neutral,
  stoichiometric cells pass basic gates: 408 atoms on the cathode and 336 on
  the electrolyte for the smallest sampled cases. The CaF2-labelled cut breaks
  AlF6 coordination (2 and 5 undercoordinated Al centres, respectively); the
  electrolyte PS4 units remain intact. This is a surface-model review issue,
  not proof that the coating is impossible. These cells have not been relaxed.
- **LiZr2(PO4)3:** no electrolyte lattice match for the seven low-index facets
  returned by the helper. Only (001) matches the cathode, and all sampled
  two-layer cathode cells exceed 1,200 atoms. This does not exclude larger
  areas, other facets, a different physical-thickness construction or other
  interface models. It does show that the original three are not ready for
  an unchanged-protocol production launch.

The lattice scan creates `CoherentInterfaceBuilder` for each facet returned by
`interphaise.tools.matcher.low_index_millers`, with `ZSLGenerator` at the limits
above, and records `len(builder.zsl_matches)`. The bounded geometry probes use
`enumerate_interfaces(..., terminations=[term], report=report)` with the selected
substrate labels before the cap, followed by `validate`, `is_stoichiometric`
and `scripts.build_contact.cut_polyhedra`. The saved JSON identifies each term,
input hash, truncation flag and tested facet. Existing `scan_interface_matches.py`
is useful for further exploration but its global cap is not a proof that a
specific termination has no match.

## Implementation sequence and stop rules

1. **Resolve construction before energies.** Budget 2–4 hours for the first
   surface/construction checkpoint. Use a 300 Å² area cap first, then a bounded
   second tier up to 600 Å² available under the same rule to every coating.
   Keep the 1,200-atom cap and existing length/angle/strain tolerances. Preserve
   endpoint cuts and PS4/PO4 groups. Report exposed metal coordination; prefer
   fewer broken metal–ligand bonds per area and lower formal polarity with a
   deterministic ordering frozen before energies. Require neutral,
   stoichiometric, non-overlapping primary slabs. Use the same coating
   orientation on both primary contacts, recording their independently matched
   cells and strains. Use physical thickness and a shared adequacy/sensitivity
   criterion, not equal crystallographic layer counts. Keep the physical fixed
   depths and record atom masks. Detailed bounds are in Claude's handoff.
2. **Keep failures visible and apply the predeclared contingency.** If an
   original new member cannot supply both contacts within the construction and
   bulk-reference rules, retain its failure record and fill its slot from
   **LiF `mp-aaaaabru`**, then **LiTaF6 `mp-aaacjmqp`**, without duplicates.
   These are declared fallback candidates, not verified interface inputs;
   prepare/check their bulk references and apply the same gates. LiF fails the
   frozen thermodynamic criterion and is a conventional comparator; LiTaF6
   passes it. Examine at most these five formulas and freeze three before
   interface energies. If used, label this an amended cohort and preserve the
   original failed members. Never replace a material because adhesion is poor
   or an interface relaxation later fails. If three admissible materials cannot
   be assembled within these bounds, report the obstruction and viable subset;
   the three-coating goal remains incomplete.
3. **Freeze a manifest.** Record IDs, input and checkpoint hashes, endpoints,
   surfaces, physical thicknesses, fixed depths, strain/cell limits, force and
   step targets, registry selection and the failure policy. Reuse LiNbF6 runs
   only where the manifest actually matches; otherwise count the reruns.
   Use `data/petmad/coating_comparison_v1/` and agree the record fields with
   Adem. Once the manifest is committed and safeguards pass, continue through
   the planned calculations within these bounds; this is not a new permission
   checkpoint for routine work.
4. **Run the initial comparison on Niflheim.** Two contacts per coating; three
   physically distinct lateral registries per contact, rather than three
   fractional offsets that may be equivalent. Choose the working registry by
   the lowest relaxed joined energy within the same cell/composition/mask.
   Each job relaxes the joined interface and both separated slabs; evaluate
   rigid-fragment separation separately. Deduplicate registries and record
   any smaller number of distinct classes.
5. **Use a fixed sensitivity budget.** As a planning allocation, reserve three
   extra full jobs per contact: one thickness increment, one fixed-depth
   variation, and one declared robustness case. For the electrolyte the latter
   can use seed 4 with a mapped surface; on the cathode it can probe the other
   slab thickness. Declare the concrete cases before energies. This is a
   bounded screen, not exhaustive convergence. A change above 0.1 J/m² is
   reported as sensitivity, not a reason to run until a pass appears.
6. **Publish outcomes and costs.** Produce one comparison table and a plot of
   both contact works alongside the existing thermodynamic criterion. Include
   failed builds, unconverged runs, geometry differences, surface reconstruction,
   free/fixed forces, polarity, calculator calls, jobs and elapsed GPU time.
   Add the structures to the viewer. Keep polar-model error unquantified;
   the measured seed difference is not a statistical error bar.

## Time and compute estimate

Measured anchor: the five archived 696–880-atom RTX 3090 jobs took
**2:43–2:57 each**, including startup and separation; their interface runner
took 61–85 seconds. Each full job contains three relaxations. These are
measurements for LiNbF6, not performance guarantees for new chemistry.

Planning allocation before reusing old results:

| Scope | Initial registry jobs | Sensitivity jobs | Total full jobs | GPU allocation estimate | End-to-end working time |
|---|---:|---:|---:|---|---|
| 3 coatings, 2 contacts each | 18 | 18 | 36 | about 2–6 GPU-hours | about 1–2 working days |
| 5 coatings, 2 contacts each | 30 | 30 | 60 | about 3–10 GPU-hours | about 2–3 working days |

GPU estimates use roughly 3–10 minutes per full job, rounded, conditional on
cells staying within 1,200 atoms and reasonably similar relaxation behaviour.
Thirty-six jobs mean 108 relaxations plus 72 rigid-fragment single points;
sixty mean 180 plus 120. Bulk preparation, extensive surface searches or
additional registry single-point grids are not included in those counts.
Reusable reference jobs reduce the new work. Larger cells, unconverged
optimisations or a changed construction strategy invalidate this simple range.

Working-time estimates include preparation, review and analysis; queue delays
are additional and were not checked. Parallel jobs reduce elapsed calculation
time but not summed GPU-hours. This offline follow-up needs no paid LLM calls.
There is no verified monetary rate for Niflheim here, so no dollar cost is
claimed. A definitive three-coating comparison is conditional on the initial
geometry gate; a documented infeasibility result is still a valid outcome.

**Execution:** fix the calculation safeguards and prepare the geometry manifest
while Adem builds the reader/validator against existing fixtures. Then run the
bounded three-coating campaign, validate and plot its outcomes, and update the
viewer and presentation. The completed 450-run LLM study remains unchanged.
