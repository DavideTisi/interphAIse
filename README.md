# interphAIse

**Discovery benchmark update (21 October):** Use the frozen v3.0 query API in
[EVALUATOR_HANDOFF.md](EVALUATOR_HANDOFF.md). The legacy discovery CLI below still
uses the earlier objective. [BENCHMARK_VALIDATION.md](BENCHMARK_VALIDATION.md) records
the exhaustive results and scientific change; [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md)
records implementation history. No LLM performance result has been established.

**Which buffer coating makes a solid-state cathode interface stable — and what atomistic model of each contact should be simulated?**

OSI Hackathon 2026 (21–22 October). Built on the design principles of [HELLMM](../hellmm).
The Python package is `interphaise` (`pip install -e .`, `import interphaise`).
**Full project report and handoff brief: [REPORT.md](REPORT.md)** — read it first.

**Flagship:** LiCoO₂ | coating | Li₆PS₅Cl at 4 V, six candidate coatings plus the uncoated baseline.
For each coating the output is a rank and tier, a verdict per contact (sharp / passivating / growing
interphase, with the reasoning), simulation-ready structures with their work of adhesion, and a decision
log. A thermodynamics-only ranking is produced next to it as the ablation.

```bash
python scripts/run_screen.py --decision-only                  # reactivity + LLM calls: minutes, no MLIP
python scripts/run_screen.py                                  # full pipeline, writes ranking.md / ranking.json
python scripts/run_screen.py --decision-only --policy rules   # same, deterministic rules instead of the LLM
python scripts/compare_arms.py runs/                          # arms side by side + where the LLM overrides the rules
```

### Three decision arms, one pipeline

The expert decisions are made by a **policy** (`interphaise/policies.py`); everything else is identical.

| Arm | `--policy` | Who decides |
|---|---|---|
| LLM | `llm` (default) | LLM reasoners, consensus over `N_RUNS` samples |
| Rules | `rules` | Deterministic expert rules (`RulesPolicy`), no LLM — the baseline the LLM must beat |
| Human | `human` | A person answers the same prompts (`HumanLLM`), blind baseline |

Rules (thresholds in `RuleSettings`, logged with every screen):
- **Sharp or interphase:** sharp if the min reaction energy > `sharp_threshold` (−0.05 eV/atom).
- **Layer stack:** the dominant products of the most favourable reaction (≤ 3), in the first order whose
  neighbours are all mutually stable; ties broken by Li fraction (Li-rich phases on the Li-richer side).
- **Passivating or growing:** growing if any layer phase has a Materials Project band gap < 0.1 eV
  (metal-only composition when the gap is unknown).
- **Facets:** BFDH — rank facets by effective interplanar spacing (systematic absences handled through
  the structure factor), pair the top ones; retries skip tried pairs.
- **Physicality:** overlapping atoms (< 1.0 Å) or separated slabs (gap +1.5 Å, W_adh ≤ 0) → next termination;
  > 5 % of atoms crossed the interface → different facets; mean interface displacement > 1.0 Å or
  coordination change > 30 % → thicker slabs; validation warnings → accept with caveat.

### How the ranker orders coatings (worst contact decides)

1. **Tier** from the arm's call on each contact: 1 = both contacts stay sharp, 2 = a passivating
   (insulating, self-limiting) layer forms, 3 = a growing (electronically conducting) layer forms.
2. **Worst thermodynamic driving force** (min reaction energy over both contacts, closer to 0 is better).
3. **Weakest work of adhesion** (higher is better).
4. **Consensus agreement** of the decisions (always 1 for the rules).

`mode="thermo"` replaces the tier with "reactive → growing" (a crude ablation). The fair comparison is
LLM vs rules: their rankings, scored against experiment (`coating_screens` in
`benchmark/literature_cases.yaml`), and the list of contacts where the LLM overrides the rules
(`compare_arms.py`) measure the value of the LLM's judgement.

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
pip install -e ".[dev,llm,upet]"    # includes the selected PET-MAD backend
pip install -e ../hellmm              # optional: reuse HELLMM's LLM router + MLIP loader
cp .env.example .env                  # MP key + LLM keys (same names as HELLMM)

pytest                                # offline: toy Li–S chemistry, scripted LLM, LJ calculator
python scripts/run_cases.py --dry-run --case 1     # reactivity + LLM decisions + matching, no MLIP
python scripts/run_cases.py --case 1               # full run with the MLIP from config.py
python scripts/run_cases.py --case 1 --policy rules  # same contact, rules arm
python scripts/run_bruteforce.py --case 1          # exhaustive baseline (no LLM)
python benchmark/score_agreement.py runs/          # agent vs literature decisions
```

MP structures and entries are cached under `data/`. Fetch everything once with network access, then commit `data/` so the cluster runs offline.

## Layout

```
config.py                      cases, LLM, MLIP, consensus settings
interphaise/
  context.py                   dataclasses passed between stages (all JSON-loggable)
  orchestrator.py              state machine (one contact); asks a policy for every decision
  policies.py                  LLMPolicy (LLM / human), RulesPolicy (deterministic rules), make_policy
  screen.py                    coating screen: runs both contacts per coating + uncoated baseline
  ranker.py                    tiered ranking: the arm's decisions vs thermodynamics-only
  llm.py                       make_llm (litellm / HELLMM router), HumanLLM, ScriptedLLM
  log.py                       run dir + decision log
  reasoners/                   the LLM decisions (prompts.py holds all prompts)
  tools/                       deterministic: materials, reactivity, matcher, validation,
                               energetics (registry scan, relax, W_adh), descriptors, mlip
benchmark/
  literature_cases.yaml        expert decisions to score against (fill + verify on day 1)
  score_agreement.py
scripts/run_screen.py, scripts/run_cases.py, scripts/run_bruteforce.py, scripts/compare_arms.py
tests/                         offline end-to-end tests
```

## Evaluation plan (what goes on the slides)

0. **Coating ranking vs experiment, three arms.** Known-good coatings must outrank the uncoated cathode;
   report the LLM, rules and human rankings and the thermodynamics-only ablation (`compare_arms.py`).
   The LLM's overrides of the rules, checked against the literature, give the override accuracy.
1. **Agent vs published expert decisions.** Run on the ~7–15 systems in `literature_cases.yaml` and score decisions 1–3. Only `verified: true` entries count. Each needs a DOI.
2. **Agent vs team members, blind.** Same prompts, same information: `--policy human` on 5 systems.
3. **Efficiency vs brute force.** Same or better best-W_adh interface with far fewer relaxations (`counters` in both summaries).
4. **Reproducibility.** Repeat runs, and use two LLM vendors if time allows (HELLMM's protocol). Report the per-decision agreement fractions.

Headline we are aiming for: *"the LLM makes the expert modelling decisions as published studies did in X/N cases and turns them into simulated interfaces with Y× fewer relaxations than exhaustive search."*

## Suggested work packages (2 days)

| WP | Who | Day 1 | Day 2 |
|---|---|---|---|
| A. Literature benchmark | 2 people | fill + verify `literature_cases.yaml` with DOIs | human blind baseline, scoring |
| B. Reasoners, rules & prompts | 1–2 | LLM and rules arms on the decision-only screen, prompt iteration, rule thresholds | hybrid mode (rules as LLM input), override metric, repeat runs |
| C. MLIP & energetics | 1–2 | PET-MAD / fine-tuned LPSCl model in `tools/mlip.py`, sanity check on Li\|LLZO W_adh vs literature | brute-force baseline, counters |
| D. Demo & slides | 1 | structure viewer for `*_best.extxyz`, decision-log viewer | slides, video |

## Known gaps / TODO

- **Multilayer cell.** An interphase stack is currently built as pairwise interfaces (electrode|P1, P1|P2, …). Merging them into one cell with a common in-plane supercell is the main open task.
- **γ_int.** Only W_adh is computed. Interface energy needs surface energies and chemical potentials for non-stoichiometric slabs (`validation` already flags them).
- **MD anneal and interfacial Li transport** (stretch): short NVT on the accepted structure, Li MSD across the interface.
- **MLIP domain.** Both defaults use PET-MAD S 1.6.0 (r²SCAN) via UPET. Validate its behaviour on the target interfaces; do not mix its total energies with MP energies.
- **Disorder.** Argyrodites and garnets are partially disordered; MP's ordered approximant is used. Record the MP id actually used.
- Energy counters are process-global; run one case per process when comparing with brute force.
- **Hybrid mode** (rule outputs given to the LLM as inputs, override rate as metric) is not built yet.
- **Rule thresholds** (`RuleSettings`) are judgement calls themselves; report a sweep of `sharp_threshold`.

## Iterative discovery (new branch)

See [DISCOVERY_REPORT.md](DISCOVERY_REPORT.md) for the agreed scientific scope.
This outer loop selects coatings under a fixed evaluation budget. Candidate
quality uses calculated reactivity and optionally adhesion, never the proposing
LLM's stability labels. The existing screen/arm comparison remains separate.

```bash
python scripts/run_discovery.py --strategy random --budget 3 --seed 42
python scripts/run_discovery.py --strategy fixed --budget 3
python scripts/run_discovery.py --strategy upfront --budget 3 --model anthropic/claude-haiku-5-5
python scripts/run_discovery.py --strategy iterative --budget 3 --model anthropic/claude-haiku-5-5
# Add --full for fixed-RulesPolicy interface construction and MLIP adhesion.
```

Default mode requires Materials Project access but no MLIP. LLM strategies also
need the configured provider credentials. Each run writes `discovery.json` with
proposal attempts, evaluation failures, timings and best-so-far history. Failed
calculations consume budget. `fixed` follows configuration order; it is not an
expert baseline unless that order was independently specified by an expert.

### Explicit UPET checkpoints

The current PET model family uses the `upet` package. Install with
`pip install -e '.[upet]'` and pass an explicit model/version, for example
`--mlip upet:pet-mad-s@1.6.0` to `scripts/run_discovery.py --full`.
This public checkpoint is documented as r²SCAN-trained. The old `pet-mad`
loader remains a separate legacy backend; it does not select the new model.
Both anode and cathode defaults are pinned to PET-MAD S 1.6.0 (r²SCAN),
as confirmed for this project. Loader tests do not validate model accuracy or inference.
Reference: https://github.com/lab-cosmo/upet

Run the real-model software check with `.venv/bin/python scripts/smoke_mlip.py`.
It uses CPU, a slightly displaced two-atom Li crystal and at most five FIRE steps.
Results are written to ignored `runs/petmad_smoke.json`. This is not an interface
accuracy benchmark.

### Project LLM access

The configured model is `anthropic/claude-haiku-5-5` (Claude Haiku 5.5).
`make_llm` calls Anthropic directly with the local `MY_ANTHROPIC_KEY` (or
`ANTHROPIC_API_KEY`), bypassing HELLMM/OpenRouter routing. Every other live model/provider is rejected; the discovery CLI permits only the
configured default. No automatic model fallback is used. Credentials remain in
ignored `.env`. Calls have a default 2048-output-token cap and may be given an
explicit temperature; the direct client exposes response model and token usage
in `last_metadata`. The small authentication/generation test does not establish
scientific performance.
