# Reproduce the interphAIse results

Use this entry point to regenerate the completed analyses from committed evidence.
The default workflow is offline: it makes no LLM call, Materials Project request,
PET-MAD evaluation or cluster submission. Installing dependencies requires internet
access once. Use a full Git clone, because production provenance checks inspect
historical workflow commits.

## Set up and run

From the repository root, with Python 3.12 (the tested version):

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev,analysis,mp]'
python -m pytest -q
python scripts/reproduce_results.py
```

The matcher requires the pinned `pymatgen==2026.9.24` and
`pymatgen-core==2026.10.16`. An older version previously caused four interface
tests to fail. Do not replace the pins when reproducing these constructions.
The `analysis` extra installs the plotting dependency. The `mp` extra supplies
`mp-api` and its `emmet-core` dependency, which the offline tests use to normalize
Materials Project IDs. Installing these packages does not require an API key,
and the tests do not query Materials Project. No MLIP extra is needed.

Open `runs/reproduced_results/structure_viewer.html` in a browser, or share that
single HTML file. Outputs also include the original discovery curve, both models'
production environment statistics, their comparison table, the exploratory
LLZO audit, final physical table/figure and pilot forecast report.
`VERIFICATION.json` records package versions, source-code hashes, unchanged
evidence and agreement with the presentation data. Each command has a log.
Use `--skip-viewer` to omit the larger HTML export.

The wrapper replays the original 1,500, Haiku production 4,500 and DeepSeek
production 3,600 charged queries, checks each production policy, validates
physical runs against their saved sources,
checks preserved decision snapshots and compares all selected contact values
and forecast outcomes with the presentation source. It writes only under `runs/`;
archived experiment outputs stay unchanged. The full test suite is a separate
command above, not implicitly rerun by the wrapper. DeepSeek's counts and six
corrected contrasts must also match the independently archived review. The
810 distinct environment runs include only one shared set of 90 random runs.

## Evidence and outputs

| Evidence | Location |
|---|---|
| Frozen original benchmark | `data/benchmarks/coating_v3.json` |
| Original 120 runs and 30 shuffled runs | `data/experiments/integrated_v3_20261021_s100/`, `data/experiments/shuffled_v3_20261021_s100/` |
| Frozen three-environment tables | `data/benchmarks/environment_v1/` |
| Production 450 runs, settings and usage | `data/experiments/environment_v1/` |
| DeepSeek 360 additional runs, settings and usage | `data/experiments/deepseek_v1/` |
| Independent DeepSeek recount and input hashes | `data/reviews/deepseek_results_review_20261022.json` |
| Live physical-pilot prompts, responses and amendment | `data/experiments/llm_petmad_pilot_v1/state.json` |
| Decision-time physical indices and bundles | `data/petmad/coating_comparison_v1/snapshots/` |
| Summary-time index, preserved | `data/petmad/coating_comparison_v1/index.json` |
| Final physical index with later robustness | `data/petmad/coating_comparison_v1/index_final.json` |
| Final comparison table and figure | `data/petmad/coating_comparison_v1/analysis_final/` |
| Reviewed slides and PDF | `presentations/results_2026-10-22/` |

The final index SHA-256 is
`47d69f7dd75dff89e1d2e5191f2f1d31fad002581521c39eeee7593c90d83c41`.
Its primary results are identical to those available to the live pilot.
Later sensitivities cannot be fed back into those archived decisions.
LiF is `not_run_not_selected`, not a zero-energy result. Two LiCaAlF6 electrolyte
sensitivity slots are explicitly unquantified, not successful tests.

## Run a single analysis

```bash
python scripts/analyse_environment_study.py \
  data/experiments/environment_v1/lpscl \
  data/experiments/environment_v1/lic \
  data/experiments/environment_v1/llzo --production \
  --json runs/environment_summary.json

python scripts/analyse_environment_study.py \
  data/experiments/deepseek_v1/lpscl \
  data/experiments/deepseek_v1/lic \
  data/experiments/deepseek_v1/llzo --production --policy deepseek_v1 \
  --json runs/deepseek_summary.json

python scripts/analyse_mlip_comparison.py \
  --index data/petmad/coating_comparison_v1/index_final.json \
  --out runs/final_comparison

python scripts/report_llm_petmad_pilot.py \
  --state data/experiments/llm_petmad_pilot_v1/state.json \
  --out runs/pilot_report

python scripts/build_structure_viewer.py --output runs/structure_viewer.html
```

Run `mkdir -p runs` first if necessary. The wrapper also reproduces the original
five-arm curve and records its exact commands. Slide-building sources and visual
validation are in [the presentation guide](presentations/README.md); the offline
wrapper verifies their scientific data without requiring the slide-design runtime.

## New experiments are separate

- **New LLM runs:** require the authorised credential in a git-ignored `.env`,
  a defined protocol and spending approval. The default is direct Anthropic
  Haiku 5.5. The completed DeepSeek repeat used Adem's separate OpenRouter key
  with SiliconFlow pinned and no fallback; see
  [the DeepSeek protocol](docs/DEEPSEEK_PROTOCOL.md) and [AGENTS.md](AGENTS.md).
  Existing approval for completed experiments does not schedule new paid runs.
  Analysis does not require credentials. Do not rerun or overwrite the completed
  live pilot to regenerate its report.
- **New database queries:** require a Materials Project key; the saved structures
  and frozen tables already suffice for reproduction.
- **New PET-MAD energies:** require UPET/PET-MAD, the recorded checkpoint and
  the construction protocol. CPU is possible; a GPU speeds up these cells.
  See [CONTACT_PROTOCOL.md](docs/CONTACT_PROTOCOL.md),
  [the comparison plan](docs/MLIP_COMPARISON_PLAN.md) and [NIFLHEIM.md](docs/NIFLHEIM.md).
  Reading saved energies and geometries needs none of these resources.

Interpretation and limitations: [results synthesis](docs/RESULTS_SYNTHESIS_2026-10-22.md).
