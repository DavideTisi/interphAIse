# Claude: uniform 1,250-atom amendment and feedback validation review

21 October 2026. Reviewed `work/petmad-comparison:49daa72`, including F1/F2
commit `b9f8468`. This amends [LLM_PETMAD_PILOT_PLAN.md](LLM_PETMAD_PILOT_PLAN.md)
before any new coating's interface energies. No potential was loaded during
this review and your checkout was untouched.

## Decision: proceed with option 2

Use a uniform **1,250-atom cap** for all candidates and declared jobs. Keep all
other physical gates and the existing material/job budgets. Retain the original
1,200-atom screen and record this as a construction-driven resource amendment
before LLM selection and new interface energies, not an outcome-driven exception.

I checked your saved LiCaAlF6 rows and independently rebuilt its (100)
LiAlF4_P2_6 termination against both reviewed substrate cuts. The 10-layer
electrolyte cell has 1,212 atoms, area 256.062 Å², film span 42.139 Å and about
2.22% strain. It passes the amended cap, neutrality/stoichiometry, overlaps and
protected PS4 gates. Its old-cap rejection is solely the 12 excess atoms.
Cathode builds pass too. Broken Al–F coordination occurs on both sides and
remains an explicit surface caveat, already allowed by the declared rules.

The intended menu is LiNbF6 reference plus **LiTaF6, LiF and LiCaAlF6** as three
unevaluated alternatives. Revalidate the menu under the amended cap and freeze
the actual inputs. LiZr2(PO4)3 stays excluded under the bounded construction
rules. Do not relax strain, increase area, thin the slabs or extend the search
to rescue it. The LLM still chooses only **two new coatings**: four menu members
do not mean four calculated coatings.

**One sensitivity remains unavailable:** the rebuilt 11-layer LiCaAlF6
electrolyte film has **1,302 atoms**. Record that thickness increment as
`not_run_resource_limit` if selected; its thickness sensitivity stays
unquantified. Do not mark it passed, thin the baseline or silently raise the
cap again. Feasible checks can run in their declared slots. The number of
jobs is unchanged, but runtime/memory depend on which materials are selected.

## Safeguards and feedback review

The complete offline suite reproduces **157 passes in 20.70 s** in an isolated
archive of your head with the pinned environment. Keep your completed F1 fix;
the later deferral advice does not require undoing tested work. F1 now rejects
unconverged energetics; F2 checks checkpoint identity before derived model
calls. These changes are on your branch, not merged into Davide's checkout.

The five genuine LiNbF6 feedback registry records have correct W_adh/W_sep
arithmetic and the bundle hash checks out. Their scientific values are unchanged.
However, the current assembler needs three gates before live decisions.
Reproductions used temporary copies only:

1. **Completeness:** declaring three planned registries per contact but supplying
   only one still produces selected values and a weakest-contact summary.
   Require exact manifest coverage, unique run/registry IDs and terminal outcomes.
   A missing job is pending, not a completed failure. Partial diagnostic bundles
   must be explicitly non-consumable by the agent.
2. **Comparable groups:** labelling an electrolyte run as another cathode registry
   is accepted and its different absolute total energy wins selection. Validate
   candidate/endpoint/build/protocol identity and comparable composition, cell,
   area and physical fixed masks. Do not trust CLI labels or require raw geometry
   hashes to match across intentionally shifted registries.
3. **Arithmetic:** changing stored `work_of_adhesion_J_m2` to 999 in a copied
   valid run still yields status `valid` and W_adh 999. Recompute W_adh from source
   energies/area; validate W_sep against its fragment/source energies, checkpoint
   and area. Reject inconsistent values and retain finite/converged-force gates.

Add focused offline regression fixtures. Adem's consumer should independently
enforce this manifest/coverage contract before the loop advances; passing F2
for each individual run is not sufficient.

Also preserve known failed-run costs: a copied invalid run with 136 calculator
calls currently contributes zero to bundle totals. Include known failures and
rigid-fragment calls, distinguish unknown from zero and reused from new work.
The `max_fixed_atom_force_eV_A` field currently holds the maximum raw force over
all atoms; rename it accurately or compute the actual fixed-atom maximum.

## Proceed without new energies

Revalidate the menu, select physically distinct registries for all three new
options by geometry alone, fix the feedback gates and freeze the manifest.
Record unavailable sensitivity inputs. Coordinate the schema with Adem, then
calculate each new coating only after he archives the LLM choice and numeric
predictions. Keep the existing deadlines, fallback and 36-full-job ceiling;
sensitivity jobs remain outside the decision dependency. Paid-call scope and
its cost/approval checkpoint are unchanged by this resource amendment.

Audit: `data/reviews/claude_screen_review_20261021.json` on `davide`. Adem should
read `data/petmad/coating_comparison_v1/SCREENING_REPORT.md` on your branch for
the original screen and feedback example, alongside this amendment. No feedback
fix, new material energy or branch merge was performed by this review.
