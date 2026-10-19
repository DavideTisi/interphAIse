# interphase

**Which buffer coating makes a solid-state cathode interface stable — and what atomistic model of each contact should be simulated?**

OSI Hackathon 2026 (21–22 October). Built on the design principles of [HELLMM](../hellmm).

**Flagship:** LiCoO₂ | coating | Li₆PS₅Cl at 4 V, six candidate coatings plus the uncoated baseline.
For each coating the output is a rank and tier, a verdict per contact (sharp / passivating / growing
interphase, with the reasoning), simulation-ready structures with their work of adhesion, and a decision
log. A thermodynamics-only ranking is produced next to it as the ablation.

```bash
python scripts/run_screen.py --decision-only   # reactivity + LLM calls: minutes, no MLIP
python scripts/run_screen.py                   # full pipeline, writes ranking.md / ranking.json
```

### How the ranker orders coatings (worst contact decides)

1. **Tier** from the LLM's call on each contact: 1 = both contacts stay sharp, 2 = a passivating
   (insulating, self-limiting) layer forms, 3 = a growing (electronically conducting) layer forms.
2. **Worst thermodynamic driving force** (min reaction energy over both contacts, closer to 0 is better).
3. **Weakest work of adhesion** (higher is better).
4. **Consensus agreement** of the LLM decisions.

`mode="thermo"` replaces the tier with "reactive → growing", i.e. no expert call. The gap between the two
rankings, scored against experiment (`coating_screens` in `benchmark/literature_cases.yaml`), is the
measured value of the LLM's judgement.

---

## The problem

Every electrode | solid-electrolyte simulation starts with a modelling decision that is made by hand and rarely justified: *what structure do I build?* Which facets touch? Is the interface sharp, or does a reaction layer form? If it does, which phases, in which order?

Deterministic tools already handle the mechanics. pymatgen's ZSL/`CoherentInterfaceBuilder`, MPInterfaces and Ogre do lattice matching. InterOptimus (J. Energy Chem. 2025) adds termination scanning and ranking with universal MLIPs for battery interfaces. AGAPI-Agents gives an LLM a Zur-matching tool. **None of them makes the modelling decisions.** Given Li | Li₆PS₅Cl, they will happily build a sharp interface that thermodynamics and XPS both say does not exist.

## What is replaced by the LLM

| # | Decision a human makes today | LLM component | Deterministic check |
|---|---|---|---|
| 1 | Which facets are in contact (morphology, TEM, texture) | `reasoners/facet_reasoner.py` | ZSL match within strain/size limits; failure → re-plan with feedback |
| 2 | Sharp interface or interphase? (thermodynamics vs kinetics vs experiment) | `reasoners/interphase_reasoner.py` | phases restricted to convex-hull reaction products |
| 3 | Which interphase phases, in which order from the electrode | `reasoners/interphase_reasoner.py` | `check_stack`: every adjacent pair must be mutually stable |
| 4 | Is the relaxed model physical? (what you check in OVITO) | `reasoners/judge.py` | — its *action* drives the next transition |

**Orchestration:** `orchestrator.py` is a state machine. The LLM chooses transitions at the branch points; numbers and gates are deterministic. Every decision is logged with its inputs and consensus agreement to `runs/<stamp>_<case>/decision_log.json`.

```
REACTIVITY ─▶ INTERFACE_TYPE ─▶ STACK_CHECK ─┐      reactive neighbours → feedback → INTERFACE_TYPE
   [det]         [LLM 2+3]         [det]     ▼
for each adjacent pair in the stack:
   FACETS ─▶ MATCH+VALIDATE ─▶ ENERGETICS ─▶ JUDGE ─▶ next pair / DONE
  [LLM 1]        [det]            [det]      [LLM 4]
     ▲             │ no valid match              │ reject + action
     └─────────────┴──────── feedback ◀──────────┘  thicker_slabs | next_termination | different_facets | larger_cell
```

### Principles carried over from HELLMM
- **Generation separated from verification.** The LLM proposes; everything that produces a number is deterministic.
- **Gates, not critics.** Validation is hard and logged with a reason (`tools/validation.py`).
- **Information barrier.** Prompts never contain what is computed downstream (strain, energies) or the benchmark answer.
- **Don't ask the LLM what you compute.** The facet reasoner is told explicitly that lattice match is computed, so it ranks by experimental relevance, not by guessed stability (the HELLMM pruner lesson).
- **Self-consistency.** Every decision is sampled `N_RUNS` times; the agreement fraction is logged.

---

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,llm]"          # + pip install pet-mad / mace-torch for energetics
pip install -e ../hellmm              # optional: reuse HELLMM's LLM router + MLIP loader
cp .env.example .env                  # MP key + LLM keys (same names as HELLMM)

pytest                                # offline: toy Li–S chemistry, scripted LLM, LJ calculator
python scripts/run_cases.py --dry-run --case 1     # reactivity + LLM decisions + matching, no MLIP
python scripts/run_cases.py --case 1               # full run with the MLIP from config.py
python scripts/run_bruteforce.py --case 1          # exhaustive baseline (no LLM)
python benchmark/score_agreement.py runs/          # agent vs literature decisions
```

MP structures and entries are cached under `data/`. Fetch everything once with network access, then commit `data/` so the cluster runs offline.

## Layout

```
config.py                      cases, LLM, MLIP, consensus settings
interphase/
  context.py                   dataclasses passed between stages (all JSON-loggable)
  orchestrator.py              state machine (one contact)
  screen.py                    coating screen: runs both contacts per coating + uncoated baseline
  ranker.py                    tiered ranking, LLM vs thermodynamics-only
  llm.py                       make_llm (litellm / HELLMM router), HumanLLM, ScriptedLLM
  log.py                       run dir + decision log
  reasoners/                   the LLM decisions (prompts.py holds all prompts)
  tools/                       deterministic: materials, reactivity, matcher, validation,
                               energetics (registry scan, relax, W_adh), descriptors, mlip
benchmark/
  literature_cases.yaml        expert decisions to score against (fill + verify on day 1)
  score_agreement.py
scripts/run_screen.py, scripts/run_cases.py, scripts/run_bruteforce.py
tests/                         offline end-to-end tests
```

## Evaluation plan (what goes on the slides)

0. **Coating ranking vs experiment.** Known-good coatings must outrank the uncoated cathode; report the
   LLM ranking and the thermodynamics-only ablation side by side (`score_agreement.py` prints both).
1. **Agent vs published expert decisions.** Run on the ~7–15 systems in `literature_cases.yaml` and score decisions 1–3. Only `verified: true` entries count. Each needs a DOI.
2. **Agent vs team members, blind.** Same prompts, same information: run with `llm=HumanLLM()` on 5 systems.
3. **Efficiency vs brute force.** Same or better best-W_adh interface with far fewer relaxations (`counters` in both summaries).
4. **Reproducibility.** Repeat runs, and use two LLM vendors if time allows (HELLMM's protocol). Report the per-decision agreement fractions.

Headline we are aiming for: *"the LLM makes the expert modelling decisions as published studies did in X/N cases and turns them into simulated interfaces with Y× fewer relaxations than exhaustive search."*

## Suggested work packages (2 days)

| WP | Who | Day 1 | Day 2 |
|---|---|---|---|
| A. Literature benchmark | 2 people | fill + verify `literature_cases.yaml` with DOIs | human blind baseline, scoring |
| B. Reasoners & prompts | 1–2 | real-LLM runs on the 3 config cases, prompt iteration | reproducibility runs, second LLM vendor |
| C. MLIP & energetics | 1–2 | PET-MAD / fine-tuned LPSCl model in `tools/mlip.py`, sanity check on Li\|LLZO W_adh vs literature | brute-force baseline, counters |
| D. Demo & slides | 1 | structure viewer for `*_best.extxyz`, decision-log viewer | slides, video |

## Known gaps / TODO

- **Multilayer cell.** An interphase stack is currently built as pairwise interfaces (electrode|P1, P1|P2, …). Merging them into one cell with a common in-plane supercell is the main open task.
- **γ_int.** Only W_adh is computed. Interface energy needs surface energies and chemical potentials for non-stoichiometric slabs (`validation` already flags them).
- **MD anneal and interfacial Li transport** (stretch): short NVT on the accepted structure, Li MSD across the interface.
- **MLIP domain.** PET-MAD is PBEsol without +U or spin. Use an MPtrj model for magnetic TM-oxide cathodes (`MLIP_CATHODE` in config).
- **Disorder.** Argyrodites and garnets are partially disordered; MP's ordered approximant is used. Record the MP id actually used.
- Energy counters are process-global; run one case per process when comparing with brute force.
