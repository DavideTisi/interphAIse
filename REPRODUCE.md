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
python -m pip install -e '.[dev,analysis]'
python -m pytest -q
python scripts/reproduce_results.py
```

The matcher requires the pinned `pymatgen==2026.9.24` and
`pymatgen-core==2026.10.16`. An older version previously caused four interface
tests to fail. Do not replace the pins when reproducing these constructions.
The `analysis` extra installs the plotting dependency; no MLIP extra is needed.

Open `runs/reproduced_results/structure_viewer.html` in a browser, or share that
single HTML file. Outputs also include the original discovery curve, production
environment statistics, final physical table/figure and pilot forecast report.
`VERIFICATION.json` records package versions, source-code hashes, unchanged
evidence and agreement with the presentation data. Each command has a log.
Use `--skip-viewer` to omit the larger HTML export.

The wrapper replays the original 1,500 and production 4,500 charged queries,
checks production settings, validates physical runs against their saved sources,
checks preserved decision snapshots and compares all selected contact values
and forecast outcomes with the presentation source. It writes only under `runs/`;
archived experiment outputs stay unchanged. The full test suite is a separate
command above, not implicitly rerun by the wrapper.

## Evidence and outputs

| Evidence | Location |
|---|---|
| Frozen original benchmark | `data/benchmarks/coating_v3.json` |
| Original 120 runs and 30 shuffled runs | `data/experiments/integrated_v3_20261021_s100/`, `data/experiments/shuffled_v3_20261021_s100/` |
| Frozen three-environment tables | `data/benchmarks/environment_v1/` |
| Production 450 runs, settings and usage | `data/experiments/environment_v1/` |
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

- **New LLM runs:** require the authorised Anthropic credential in a git-ignored
  `.env`, the configured Haiku 5.5 model, a defined protocol and spending approval.
  Analysis does not require credentials. Do not rerun or overwrite the completed
  live pilot to regenerate its report.
- **New database queries:** require a Materials Project key; the saved structures
  and frozen tables already suffice for reproduction.
- **New PET-MAD energies:** require UPET/PET-MAD, the recorded checkpoint and
  the construction protocol. CPU is possible; a GPU speeds up these cells.
  See [CONTACT_PROTOCOL.md](CONTACT_PROTOCOL.md),
  [the comparison plan](MLIP_COMPARISON_PLAN.md) and [NIFLHEIM.md](NIFLHEIM.md).
  Reading saved energies and geometries needs none of these resources.

Interpretation and limitations: [results synthesis](RESULTS_SYNTHESIS_2026-10-22.md).
