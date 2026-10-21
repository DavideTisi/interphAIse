# More coatings across several battery environments

21 October 2026, branch `davide`. The user selected this expansion after reviewing
the first experiment. This is a prepared exploratory study, not a new measured
LLM result or a change to the frozen v3 benchmark.

## Scientific question and the human decision being automated

Does calculated feedback help the LLM select coatings across different electrolyte
chemistries, rather than succeed only on one small pool with a fluoride shortcut?
The model receives the battery environment and public candidate metadata. It must
choose a material, interpret the calculated failure, and revise the next choice.
For example, distinguishing failure at the cathode contact from failure at the
electrolyte contact should change which chemical substitution it considers. This
is an illustrative decision process, not a claim that a particular substitution
will work or an instruction to reveal benchmark answers in the prompt.

The human intuition being substituted is the decision about which earlier chemical
assumption remains useful when the environment changes. The evaluator computes
the evidence; the LLM chooses what to investigate. Merely increasing the candidate
count does not prove reasoning or make the LLM necessary. Matched no-feedback,
random and chemical-rule baselines remain essential.

## Prepared search space

The existing summary snapshot contains 3,770 MP records. Applying the **unchanged**
chemical scope, near-hull, ordering and primitive-cell filters yields **141 coating
structures, representing 100 distinct formula strings**. These include every one
of the original 50 candidates. There are 61 other oxides, 29 halides, 23 silicates,
16 phosphates and 12 borates. All eligible records are retained; no selection uses
the new environment scores. Polymorphs remain separate budgeted candidates.

An initial target of 200 was not possible under those filters: the builder correctly
refused it. We used all 141 rather than weakening the filters to reach a round number.

Keep LiCoO2 and imposed voltage 4.0 V fixed initially, and vary the electrolyte:

| Environment | Electrolyte | Pinned MP ID (numeric alias) | Ordered cached model |
|---|---|---|---|
| Existing sulfide reference | Li6PS5Cl | mp-985592 | F-43m, 13 primitive sites; existing v3 approximant |
| Chloride extension | Li3InCl6 | mp-676109 | C2, 60 primitive sites; phase review required |
| Oxide extension | Li7La3Zr2O12 (LLZO) | mp-942733 | I4_1/acd, 96 primitive sites; phase review required |

This makes **141 × 3 = 423 coating–environment combinations**, each involving two
coating contacts. The cathode remains the same pinned v3 LiCoO2 structure. New
electrolytes were selected as the lowest-summary-hull ordered matching record in
the available cache; this is not an unrestricted MP polymorph search. Li3YCl6 was
considered but absent from this prefiltered cache; that does not mean it is absent
from MP or unsuitable. Li3InCl6 provides a cached chloride alternative.

Li3InCl6 has been studied as a solid electrolyte with oxide cathodes
([Li et al., 2019](https://onlinelibrary.wiley.com/doi/10.1002/anie.201909805)).
The LiCoO2–LLZO interface has also been studied experimentally
([interface characterization, 2011](https://www.sciencedirect.com/science/article/abs/pii/S0378775310012966)).
These motivate the environment choices; they do not validate the particular MP
polymorphs or our computed scores. In particular, the cached LLZO model is ordered
tetragonal LLZO, not a model of a disordered or doped cubic conducting material.
The imposed Li chemical potential is also not a modeled cathode state of charge.

## What is implemented and checked

- `scripts/build_candidate_pool.py`: `select_pool(..., size=None)` now selects all
  eligible structures. Fixed-size defaults and filtering are preserved.
- `scripts/prepare_environment_expansion.py`: uses local data only, preserves the
  original candidates, pins endpoints, copies the existing objective, and saves
  hashed pool/plan/coverage records to a fresh directory. It refuses overwrites.
- `data/exploration/environment_expansion_v1/pool.json`: structures, gaps, provenance
  and fixed filters for all 141 candidates.
- `data/exploration/environment_expansion_v1/plan.json`: endpoint structures and IDs,
  objective, source hashes, environment definitions and scientific limitations.
- `data/exploration/environment_expansion_v1/coverage.json`: missing chemical-system
  queries and pinned IDs, per environment and per coating. It explicitly declares
  that no scores were computed and the expansion is not ready for LLM runs.

Pool SHA-256: `833d5a687d4413cab1ab7cdd9007b56b924e3b2d2802ae26170d9f6a7f82e71d`.
The original benchmark and its 120 archived runs are unchanged.

The current 4,887-entry energy dataset was fetched for the original pool. It
contains IDs for 117 of the 141 coatings, but ID presence alone is insufficient:
missing competing phases can make a candidate appear too stable.

| Environment | Additional chemical-system queries needed | Coatings with IDs and required queries already covered |
|---|---:|---:|
| Li6PS5Cl | 496 | 104/141 |
| Li3InCl6 | 536 | 0/141; endpoint entry also missing |
| LLZO | 724 | 0/141; endpoint entry also missing |

There are **1,430 distinct additional chemical systems** after deduplication across
environments. These are subsystem queries, not necessarily 1,430 materials or
network requests; many may return no phases and they can be batched. The 104/141
figure checks ID and query coverage only; exact structure matching and evaluator
validation still precede scoring. No partial phase diagram was scored.

Verification: 12 targeted tests pass across pool selection, expansion coverage and
thermodynamic-data helpers. Tests specifically prevent missing competitor systems
or missing pinned IDs from being mistaken for complete coverage. A fractional-
occupancy test initially exposed a composition-normalization issue in endpoint
selection; comparison now uses fractional compositions. All three saved artifact
hashes and pool links verify; the original 50-candidate selection replays with its
original hash. No new MP request, paid LLM call or PET-MAD calculation occurred.

## Implementation and experiment sequence

1. **Resolve endpoint models.** Review the new ordered structures and record whether
   they are suitable thermodynamic representatives. Any replacement must be based
   on structural/provenance considerations, recorded before scoring; do not select
   an endpoint because it makes the LLM result stronger.
2. **Fetch complete compatible energies.** Extend the fetcher to consume this plan,
   retrieve the union of missing subsystems in resumable batches, and build a new
   dataset manifest. Reuse cached entries only at the same MP database version and
   correction scheme; fail on conflicts. If the live MP version differs, build a
   separate complete snapshot instead of combining vintages. Resolve exact pinned
   IDs and structures; keep unavailable entries as explicit failures. Retain
   corrected GGA/GGA+U, consistent with the original evaluator. MP distinguishes
   correction schemes for combining energy calculations
   ([MP energy corrections](https://docs.materialsproject.org/methodology/materials-methodology/thermodynamic-stability/thermodynamic-stability)).
   PET-MAD r²SCAN energies must not be inserted into these phase diagrams.
3. **Evaluate and audit all three environments offline.** Extend the exhaustive
   evaluator to consume each environment and its validated dataset. Retain the v3
   additional-contact criterion, gap gate, 0.020 bins and 0.050 acceptance threshold.
   Report failures, acceptable counts, best bins, exact random curves, the same
   fluoride-first rule and cross-environment rank changes. Check which component
   controls the penalty: coating self-instability may still make all environments
   prefer the same candidates. That is a valid result; keep all environments and do
   not discard one merely because it is easy, difficult or favours a baseline.
4. **Freeze a separate experiment.** Save the complete new pool, per-environment
   benchmark hashes, prompts, budget and statistical analysis before new LLM
   production. The new study is informed by v3; it is not a blind independent
   replication. The expanded sulfide task overlaps all original 50 candidates and
   both old winners. Label that overlap. Do not pool its runs with the old cohort.
   If no coatings pass in an environment, report that and its best-bin regret;
   a changed acceptance threshold would require a separately labelled study.
5. **Run matched controls.** Start each run with fresh history and expose the same
   environment and candidate information to every arm. Use iterative, sequential
   without results, upfront and random, plus the validated shuffled control when
   available. Proposed production: 30 repeats per arm per environment, budget 10,
   the same allowed Haiku settings. Compare per-environment acceptance and best-bin
   regret; predeclare any equal-weight average across environments and any multiple-
   comparison procedure. A fixed small smoke batch is excluded from those results.
   Three environments at these settings use about 1,890 LLM proposal calls before
   retries without shuffled feedback, or 2,790 with it; the larger pool also increases
   prompt length. These are counts, not a price quote. No batch is launched here.
6. **Validate selected interfaces selectively.** Keep the current bulk/slab validation
   work on its existing shortlist. Once a usable protocol exists, choose follow-up
   structures from the new environments under a documented selection rule. Their
   larger endpoint cells may increase cost. Do not attempt PET-MAD on all 423
   combinations before establishing a defensible interface protocol.

Davide owns steps 1–3 and 6; Adem owns agent integration, controls and analysis in
steps 4–5; both review the scope and interpretation. This expansion proceeds as a
separate study alongside the current shuffled-control and interface-validation
work, and must not prevent submission of the completed experiment.

## Reproduction

On this checkout, the original raw MP summary cache is available in ignored `runs/`:

```bash
MPLCONFIGDIR=/private/tmp/interphaise-mpl .venv/bin/python scripts/prepare_environment_expansion.py \
  --output runs/environment_expansion_replay
MPLCONFIGDIR=/private/tmp/interphaise-mpl .venv/bin/python -m pytest -q \
  tests/test_candidate_pool.py tests/test_environment_expansion.py tests/test_thermo_dataset.py
```

Use a fresh output path. The prepared pool and plan contain the selected structures;
the full raw summary cache is not required to inspect or use that package, but is
required to rerun the original selection from all 3,770 downloaded records.
