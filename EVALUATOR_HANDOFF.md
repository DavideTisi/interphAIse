# Evaluator handoff — 21 October 2026

Branch: `davide`, based on merged `main`. Davide owns the evaluator; Adem owns
search strategies. This checkpoint deliberately leaves the legacy discovery CLI
unchanged. It still runs the old objective and must not be used for v2 claims.

## What exists

- `interphaise/discovery_evaluator.py`: an offline, pinned-entry evaluator.
- `scripts/build_candidate_pool.py`: live MP retrieval and offline replay.
- `data/pools/mp_candidates_v2.json`: 50 selected candidates with IDs, primitive
  structures, gaps, property origins, retrieval metadata, filters and SHA-256.
- Offline tests for oxidation, an interior mixing reaction, metastable polymorphs,
  formula-unit normalization, insulation, missing entries, bins and pool sampling.

The pool contains ten each of phosphates, borates, silicates, other oxides and
halides. There were 3,770 unique summary records, 141 locally eligible records and
50 selected records. All selected gaps are known; 48 are at least 2 eV.
Polymorphs are retained as separate material IDs. Examples such as LiO8 warrant
inspection: passing database filters does not establish experimental suitability.
The pool is a draft, not a claim that all candidates are useful coatings.

Selection requires Li, at most four elements from a recorded restricted element
set, summary hull distance at most 25 meV/atom, ordered sites and a primitive
cell of at most 40 atoms. Seed 2026 samples round-robin across five families.
There is no band-gap prefilter. The scope restriction keeps subsequent chemical
systems manageable but is not exhaustive coverage of coating chemistry.

## Scientific role of the LLM

The LLM substitutes the researcher's judgement in choosing which coating to test,
explaining why, interpreting the returned failure or success, and deciding whether
to refine or abandon that chemical hypothesis. The evaluator calculates properties
and applies an immutable criterion. It cannot establish that the LLM uses feedback:
that requires Adem's true-feedback, prior-only/no-feedback and random controls.

For HELLMM, the analogous intellectual task is imagining reaction mechanisms.
Here it is proposing and revising materials hypotheses. A fixed pool limits the
creative space; it gives a controlled test of selection rather than proof of
inventing a new material. Cheap-mode results measure sample efficiency, not saved
wall time. PET-MAD follow-up remains separate from MP thermodynamic energies.

## Proposed v2 objective — not yet frozen

```python
evaluate_candidate(
    candidate_id, coating_entry,
    electrode_entry=electrode, electrolyte_entry=electrolyte,
    entries=entries, voltage=4.0, band_gap_eV=gap,
    energy_source="record-the-compatible-dataset", objective=Objective(),
)
```

Returns a JSON-compatible dictionary.
Entries are pymatgen entries with corrected total energies. The caller must supply
a consistent thermodynamic dataset, all pinned reactants and elemental references;
recording an energy-source string alone does not establish compatibility.

At the imposed voltage, mu(Li) = elemental Li reference energy minus voltage.
All energies use **eV per non-Li atom**, including coating self-decomposition and
both contact curves. Contact energies are measured from the actual pinned reactants,
not their ground-state substitutes. The piecewise-linear hull is evaluated at all
critical compositions, including endpoints. Product lists identify phases, not
balanced reaction equations. Negative contact energies mean favourable reaction.

The positive penalty is the maximum of coating self-decomposition and the two
contact driving forces. Smaller is better. Contact penalties include endpoint
decomposition, so unstable electrode/electrolyte endpoints can impose a shared
floor. Full-pool diagnostics must measure this effect before freezing the design.
It would be misleading to adjust the objective after inspecting strategy results.

Draft thresholds: band gap >= 2 eV; acceptable penalty <= 0.050 eV/non-Li atom;
fixed bins of width 0.020 eV/non-Li atom. These are operational assumptions,
not calibrated physical error bars. The non-Li basis differs from total-atom
normalization, so these values need scientific review before freezing.

`ranking_key(result)` ranks insulating candidates by ascending penalty bin,
preserving ties. `ranking_key(result, require_adhesion=True)` uses
`weakest_adhesion_J_m2` within each bin, with larger adhesion better. Missing adhesion
fails full-mode ranking. Unknown gaps produce `status=incomplete`; metals produce
`status=ok` but fail insulation. Failed/incomplete/ineligible outcomes rank below
eligible ones. Invalid inputs raise; the runner should log them and charge budget.
Pure-Li endpoints are rejected because this cathode evaluator's normalization is
undefined for them. No Li-transport or kinetic criterion is implemented.

## Handoff and next steps

1. Resolve the main cathode/electrolyte to pinned IDs (existing case: LiCoO2 /
   Li6PS5Cl at 4 V). Retrieve compatible corrected thermo entries for each union
   chemical system. Cache energy scheme, IDs and dataset provenance. Do not use
   summary hull energies or PET-MAD energies to reconstruct MP phase diagrams.
2. Validate material/entry correspondence, including structure/property origins.
   The summary pool aligns properties by material ID but does not prove that all
   properties were calculated with the same functional or identical geometry.
3. Evaluate every candidate and inspect failures, penalty components, shared-floor
   effects, acceptable fraction and tie multiplicities. Freeze the task/objective
   only after this diagnostic, before running strategy comparisons.
4. Adem's runner should query by `candidate_id`, not formula. Expose only outcomes
   already queried; keep the complete benchmark and summary hull metadata out of
   the proposer prompt. Log objective and pool hashes. Use the returned ranking
   convention consistently in regret/success analyses, including tied optima.
5. Add an adapter for the legacy `Evaluation` schema or migrate it explicitly.
   The old `quality()` and CLI do not automatically use v2.
6. PET-MAD shortlist evaluation: add converged structures, adhesion, per-candidate
   compute counts and a baseline comparator. Then test the full-mode adapter.

Pool replay from the ignored raw snapshot:

```sh
MPLCONFIGDIR=/private/tmp/interphaise-mpl .venv/bin/python scripts/build_candidate_pool.py \
  --offline --output /private/tmp/mp_candidates_v2_replay.json
```

The builder refuses to overwrite an existing output. SHA-256 is computed over
canonical JSON excluding the hash field. Keep the raw snapshot in
`runs/mp_pool_snapshot.json` for offline reconstruction; selected structures and
selection provenance are tracked in the pool file. Credentials never enter either.

Validation at this checkpoint: 62 tests pass; no live LLM call or new MLIP run.
Materials Project query conventions follow the
[official API documentation](https://docs.materialsproject.org/downloading-data/using-the-api/querying-data).
