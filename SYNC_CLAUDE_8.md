# Claude: deliver the three-coating PET-MAD comparison

21 October 2026. Davide confirmed the three-coating expansion as the next
deliverable. Your assignment covers the code safeguards, structure preparation,
bounded calculations and archived results. Carry the work through to the
comparison; the geometry check is its first milestone.

Read `JOINT_REVIEW_AND_HANDOFF.md` (F1/F2), `MLIP_COMPARISON_PLAN.md`, and the
current `CONTACT_PROTOCOL.md`. Keep the completed LiNbF6 and LLM archives
immutable. Work in a separate physics checkout/branch, for example
`work/petmad-comparison`, preserving any existing uncommitted work. Do not
switch the shared checkout out from under other work.

## 1. Fix the calculation safeguards first

- **F1:** eliminate the route from an exhausted relaxation to validated
  adhesion in `interphaise/tools/energetics.py` and the older orchestrator.
  Reuse the convergence-aware helper or disable that quantitative route
  explicitly. Keep failed candidates and their compute costs in the records.
- **F2:** before loading a calculator or writing derived results, require the
  supplied checkpoint hash to match every saved energy reference. Cover rigid
  separation, multistart and vacuum/reference checks. Invalid/unconverged
  source calculations cannot yield validated derived work values. Check
  fragment labels/order, cell/area and finite values.
- Add focused offline regressions for exhausted relaxation, a wrong reference
  hash and invalid derived inputs. No full MLIP rerun is needed to test these.
  Commit this separately from new scientific evidence.

Your primary implementation files are energetics/relaxation, matching/building
and PET-MAD scripts. Adem owns `llm.py` and analysis; avoid editing those files.

## 2. Build the three-material cohort under a bounded rule

Start with these previously pinned materials:

| Coating | Candidate ID | Role |
|---|---|---|
| LiNbF6 | mp-aaacjjwh | Existing acceptable reference |
| LiCaAlF6 | mp-aaaaajby | Alternative acceptable fluoride |
| LiZr2(PO4)3 | mp-aaabevhd | Near-threshold phosphate comparator |

Retain LiCoO2(001) and seed-0 Li6PS5Cl(111), using the reviewed substrate cuts.
Use the same coating orientation for its two primary contacts, while recording
their independently matched cells and strains. Two cells do not model one
mechanically continuous film.

The offline audit already found LiCaAlF6(100) matches both endpoints but exposes
undercoordinated Al. The tested phosphate facets have no electrolyte match at
300 Å² and its sampled two-layer cathode cells exceed 1,200 atoms. Resolve these
construction issues before interface energies:

- Begin at the current 300 Å² area cap. A bounded second tier up to **600 Å²**
  is allowed under the same rule for every coating. Keep the **1,200-atom cap**
  and existing length/angle/strain tolerances; do not compensate by weakening
  the strain limit. Record the tier and all construction failures.
- Start with the existing low-index film-facet enumeration. Record its symmetry
  settings, terminations and truncation; a capped enumeration is not proof of
  no possible interface. Inspect small matches before generating oversized
  thick slabs. Do not launch an unbounded high-index search.
- Preserve PS4 and PO4 groups. Treat exposed metal coordination, including
  Al–F, as a reported surface choice rather than automatically rejecting all
  such surfaces. Among otherwise admissible cuts, use a documented preference
  for fewer broken metal–ligand bonds per area and lower formal polarity,
  with a deterministic tie break. Freeze the precise ordering before energies.
  Require neutral, stoichiometric, non-overlapping primary slabs.
- Use physical slab thickness and a shared adequacy/sensitivity rule. Do not
  force the same crystallographic layer count or thin a slab just to pass the
  atom cap. Record baseline/thicker options before energies. The reference
  substrate spans are about 26.77 Å (cathode) and 21.28 Å (electrolyte); the
  existing LiNbF6 film spans 53.35 Å. These are reference measurements, not a
  universal 53.35 Å requirement for every coating. Preserve fixed physical
  depths, approximately 9.10 Å and 3.257602 Å respectively, and record the
  resulting atom masks.

**Predeclared fallback:** if an original new coating cannot supply both
admissible contacts under this bounded construction/bulk-reference protocol,
retain its failure record and fill that slot from **LiF `mp-aaaaabru`**, then
**LiTaF6 `mp-aaacjmqp`**, in that order, without duplicates. Use the same gates
and relax/check their bulk references first. LiF is a conventional comparator
that fails the frozen thermodynamic acceptance criterion; it is not a newly
accepted discovery. LiTaF6 is an acceptable fluoride in that criterion. This
is a transparent amended cohort if a fallback is used, not completion of the
original phosphate comparison. Use at most these five formulas in construction
and freeze three for interface energies. Do not replace a material because its
adhesion is poor or its later interface relaxation fails.

The geometry pass is budgeted at roughly 2–4 hours as a first checkpoint. If
three admissible materials cannot be assembled inside these bounds, report
the concrete obstruction and the viable subset; do not silently change the
physical question or mark the three-coating goal complete.

## 3. Freeze inputs, then run the bounded comparison

Write a new campaign manifest under `data/petmad/coating_comparison_v1/`,
separate from all older batches. Record the chosen IDs and selection reasons,
bulk/build/source hashes, geometry rules and gates, model hash, force/step
limits, physical thicknesses/frozen depths, registry representatives, planned
sensitivity jobs and output paths. Include failed construction candidates and
any fallback decision. Share this contract with Adem before the first results;
he can develop against the existing LiNbF6 files in the meantime.

Within this scope, proceed after the manifest is committed and the safeguards
pass. Routine builds and planned jobs do not need another confirmation from
Davide. A change beyond the stated geometry/resource scope needs a revised
plan before more jobs.

- Use pinned PET-MAD S 1.6.0 r²SCAN, checkpoint
  `3f52e97c459b2a28a94fc49b8a2f9a92551231a0ea4f5b5db2396f12d8ffa1e9`.
- Use Niflheim Slurm via the established `fjorm` setup, immutable code snapshot
  and explicit inputs. Keep `.env` local and unrelated jobs untouched.
- Two contacts per coating; up to three **physically distinct** registry
  representatives per contact. Declare the sampling rule and representatives
  before relaxing them; deduplicate equivalent translations. Select by lowest
  relaxed joined energy only within one cell/composition/constraint setting.
- Keep the current free-force target 0.05 eV/Å and bounded 400-step relaxation
  limit. Each full job has joined, film and substrate relaxations, plus the
  two rigid-fragment single points for W_sep. Preserve failures; no automatic
  extension until a run passes.
- Allocate at most **18 registry jobs plus 18 declared sensitivity jobs** for
  the three selected coatings, before subtracting compatible archived results.
  Per contact, the sensitivity slots are one thickness increment, one constraint
  variation, and one declared robustness case (e.g. seed 4 on the electrolyte,
  other slab thickness on the cathode). Freeze the concrete cases first.
- Reuse old LiNbF6 outputs only where inputs and definitions match the new
  manifest. Label legacy contextual results if they do not. The 0.1 J/m²
  tolerance is a reporting criterion, not a promise that each material passes.

Planning estimate: about 2–6 GPU-hours and 1–2 working days after feasible
inputs, with queue delay additional. Larger cells or additional studies are
outside that estimate. Report actual costs and exhausted budgets.

## 4. Deliver evidence that Adem can analyse and Davide can inspect

For each candidate/contact/setting, expose its ID, contact side, protocol/build
hash, source run path, device/job ID, geometry/constraint settings, validation
status/failure reason, W_adh and W_sep (null where invalid), convergence records
and calls/time. Save initial/final structures, slab references and original
records. Keep the original runner files intact; a campaign index can normalise
their metadata for analysis.

Report polarity, reconstruction, thickness/constraint/registry sensitivity and
differences between seed geometries. The independently relaxed references are
not a measured relaxation trajectory from rigidly separated fragments. No
absolute total-energy comparison across different compositions or cells.

Commit/push in reviewable chunks: safeguards, frozen build/manifest inputs,
then complete result packages with a concise report. Keep a scoped handoff/log
entry; Davide consolidates the shared status documents. **Done means three
coatings have two documented contact outcomes each, their planned bounded
checks are reported, and the archive/manifest passes independent validation.**
An invalid result is an explicit outcome, not a valid adhesion value.
