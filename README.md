# interphAIse

<img src="assets/branding/interphaise-logo-battery-v2.png" alt="interphAIse logo: battery cross-section with layered electrodes, a teal interface and AI highlighted in teal" width="640">

interphAIse tests whether an LLM can choose the next useful calculation in the
search for protective solid-state battery coatings. The model proposes materials,
interprets feedback and forecasts properties. Materials Project thermodynamics
and PET-MAD atomistic calculations supply the numerical evidence.

Built for the OSI Hackathon 2026. The completed study compares Haiku 5.5 and
DeepSeek V3.2 across three battery environments and includes a prospective
three-coating physical pilot. Humans define the objectives and construction
rules; the LLM's scientific selection judgment is what we test.

**For reviewers:** [One-page report](docs/SUBMISSION_WRITEUP.md) ·
[Illustrated Word report](presentations/results_2026-10-22/interphaise_submission_2026-10-22.docx) ·
[Interactive interfaces](https://davidetisi.github.io/interphAIse/) ·
[Full results](docs/RESULTS_SYNTHESIS_2026-10-22.md)

## How it works

The LLM takes on the scientist's choice of **what to test next and why**. It
uses chemical knowledge, interprets the feedback it receives and, in the physical
pilot, predicts adhesion before the calculation. Humans fix the scientific
question, candidate menu, scoring rules and budget. Code validates choices,
runs or retrieves calculations, and preserves the evidence.

```mermaid
flowchart LR
    L{{"LLM<br/>Choose and explain"}}
    V["Code<br/>Validate and record"]
    E["Physics tools<br/>Evaluate candidate"]
    F{{"LLM<br/>Interpret feedback"}}

    L --> V --> E --> F
    F -- "Next choice" --> L

    classDef llm fill:#e3f3f1,stroke:#087f8c,color:#0b3b40
    classDef tools fill:#eef1f4,stroke:#7a8794,color:#1b2733
    class L,F llm
    class V,E tools
```

**Teal nodes are LLM decisions; grey nodes are validation and numerical
evaluation.** The loop shows the iterative workflow; each study has a fixed budget.

| Study | What the LLM decides | What the evaluator supplies |
|---|---|---|
| Discovery benchmark — Haiku and DeepSeek | Next candidate and chemical rationale | Selected candidate's precomputed thermodynamic scores |
| Physical pilot — Haiku | Next coating and predicted adhesion at both contacts | New ASE/PET-MAD calculations on frozen interface structures |

In the benchmark, upfront selects its entire shortlist before seeing results,
sequential receives no numerical outcomes, and shuffled receives misassigned
outcomes. Random selection provides the baseline. In the physical pilot,
choices and forecasts are archived before new energies are known. Primary
results inform the next decision; withheld sensitivity results are released
only after the final summary.

The two studies test complementary questions: does feedback improve the search,
and do the LLM's prospective physical predictions hold? They do not establish
that the LLM replaces a scientist's full judgment.

<details>
<summary>Original modelling-screen architecture</summary>

The earlier design also lets a decision policy choose sharp contacts or reaction
layers, facets and responses to structural validation. This is the historical
screen architecture, not the protocol used for the completed discovery results.
See [the original modelling screen](docs/LEGACY_SCREEN.md) for its detailed steps.

```mermaid
flowchart TD
    IN([electrode · electrolyte · voltage]) --> R[REACTIVITY<br/>convex-hull reaction energies]
    R --> IT{{INTERFACE_TYPE<br/>sharp or interphase? which layers, in which order?}}
    IT -- sharp --> S[stack = electrode, electrolyte]
    IT -- interphase --> SC[STACK_CHECK<br/>adjacent layers mutually stable?]
    SC -- yes --> S2[stack = electrode, layers, electrolyte]
    SC -- "no: reacting pairs as feedback" --> IT
    SC -. retries exhausted .-> S

    S --> P
    S2 --> P
    subgraph P [for each adjacent pair in the stack]
        F{{FACETS<br/>which facets are in contact?}} --> M[MATCH + VALIDATE<br/>lattice match within strain/size limits]
        M -- "no valid match: feedback" --> F
        M --> E[ENERGETICS<br/>MLIP relaxation, work of adhesion]
        E --> J{{JUDGE<br/>is the relaxed model physical?}}
        J -- "reject: thicker_slabs / larger_cell" --> M
        J -- "reject: next_termination" --> E
        J -- "reject: different_facets" --> F
    end
    J -- accept --> OUT([best structure per pair · ranking · decision log])

    classDef det fill:#eef1f4,stroke:#7a8794,color:#1b2733
    classDef llm fill:#e3f3f1,stroke:#087f8c,color:#0b3b40
    class R,SC,M,E,S,S2 det
    classDef io fill:#ffffff,stroke:#162b3a,color:#162b3a
    class IT,F,J llm
    class IN,OUT io
    style P fill:#fafafa,stroke:#b8c2cc
```

</details>

## Reproduce the results

Use Python 3.12 and a full Git clone. From the repository root:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev,analysis,mp]'
python -m pytest -q
python scripts/reproduce_results.py
```

After installation, this workflow is offline: no API credential, model download
or GPU is needed. It rebuilds the analyses and viewer, replays 9,600 archived
queries and checks the frozen evidence. The clean-install suite passes 246 tests.
Open `runs/reproduced_results/structure_viewer.html` for the complete catalogue.
Generated files go into `runs/`, which is created automatically and ignored by Git.
See [REPRODUCE.md](REPRODUCE.md) for dependencies and individual analysis commands.

## What we found

The environment study contains **810 distinct runs**: 720 LLM runs and 90 shared
random runs, with 30 repeats per policy/environment and ten queries per run.

- **Sulfide:** Haiku with correct feedback succeeds in 20/30 runs, versus 2/30
  without result feedback and 6/30 with shuffled feedback. Both paired comparisons
  survive Holm correction. DeepSeek shows the same direction without corrected
  significance.
- **Chloride:** all LLM policies succeed in 30/30 runs; the shared random baseline
  succeeds in 29/30. This was a predeclared near-ceiling condition.
- **LLZO:** DeepSeek's upfront shortlists succeed in 20/30 runs versus Haiku's
  1/30. Both iterative policies remain below random (10/30 and 12/30 versus 24/30).
  Useful starting knowledge and useful adaptation are distinct capabilities.

![Successful runs within ten queries for both models in three environments](figures/submission_results_2026-10-22.png)

Cross-model comparisons are descriptive, not matched reasoning compute. The
[full synthesis](docs/RESULTS_SYNTHESIS_2026-10-22.md) includes corrected tests,
controls, the earlier 150-run benchmark and the LLZO chemistry caveat.

In the prospective **Haiku/PET-MAD pilot**, both LiTaF6 adhesion forecasts held
and both LiCaAlF6 forecasts missed. The selection order did not change, so the
pilot demonstrates testable predictions rather than an adaptive-search advantage.

| Selected primary work of adhesion, J/m² | Cathode contact | Electrolyte contact |
|---|---:|---:|
| LiNbF6 | 3.617 | 1.633 |
| LiTaF6 | 3.339 | 1.577 |
| LiCaAlF6 | 1.427 | 0.744 |

These are provisional results for formally polar model interfaces. The small
Nb–Ta difference is below known construction sensitivities; LiCaAlF6 electrolyte
thickness and bulk-structure sensitivity remain unquantified. **LiF has no
computed interface energy.** Lithium transport, cycling and experimental coating
performance are not established. Decision-time evidence and later robustness
checks are archived separately.

## Explore the structures and evidence

[Open the public six-interface explorer](https://davidetisi.github.io/interphAIse/)
or [download the offline viewer](https://davidetisi.github.io/interphAIse/interphaise-referee-viewer.zip).
For the full local catalogue of 460 saved geometries and 141 candidate IDs:

```bash
python scripts/build_structure_viewer.py
```

Open `runs/structure_viewer.html`. The [viewer guide](docs/STRUCTURE_VIEWER.md)
explains comparison controls, provenance and downloads. The
[final physical comparison](data/petmad/coating_comparison_v1/FINAL_COMPARISON.md)
and [model comparison](data/experiments/deepseek_v1/model_comparison.md) link the
figures to their source evidence.

## Repository layout

| Folder | Contents |
|---|---|
| `interphaise/` | Scientific workflow, LLM policies and calculation tools |
| `scripts/` | Experiment runners, offline analyses and viewer exporters |
| `tests/` | Offline tests |
| `data/` | Frozen benchmarks, prompts, responses, structures and simulation evidence |
| `docs/` | Reports, protocols, guides and development history |
| `presentations/` | Slides, Word reports, source builders and validation records |
| `figures/` | Result plots and diagrams |
| `assets/` | Project branding |
| `benchmark/` | Literature cases for the earlier modelling screen |

The [documentation index](docs/README.md) separates current results from earlier
plans. See the [development log](docs/DEVELOPMENT_LOG.md) for the work history,
[release verification](docs/FINAL_INTEGRATION.md) for integration checks, and
[submission package](docs/SUBMISSION_PACKAGE.md) for the hackathon materials.
The [presentation guide](presentations/README.md) identifies which decks are
historical checkpoints.

New API or MLIP experiments are separate from offline reproduction. Follow
[the relevant protocols](docs/README.md) and [credential instructions](AGENTS.md).
The [earlier modelling screen](docs/LEGACY_SCREEN.md), including its orchestration
diagram and optional commands, is preserved as historical design.
