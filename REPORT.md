# interphAIse — project report

> **Purpose of this file.** A self-contained brief for people and for LLM sessions that pick this
> project up later. It records what the project is, every design decision taken so far and why, what
> is built, what is verified and what is not. Read this before the code. Last updated 2026-10-20
> (rules arm added).

**Event:** OSI Hackathon (formerly LLM Hackathon for Materials & Chemistry), 21–22 October 2026.
Judging: impact, innovativeness, scalability, relevance to materials science and chemistry.
**Repo:** `OSI_Hackathon/interphAIse` (git), next to `OSI_Hackathon/hellmm`. Python package: `interphaise`.
**Shared version:** a Claude Docs report with the same content exists for the team.

---

## 1. One-paragraph summary

interphAIse answers a battery question: **which buffer coating makes a solid-state cathode interface
stable, and what atomistic model of each contact should be simulated?** The flagship case is
LiCoO₂ | coating | Li₆PS₅Cl at 4 V, screening six coatings against the uncoated cathode. An LLM makes
the modelling decisions an expert makes by judgement (which facets touch, whether a contact stays sharp
or grows a reaction layer, what that layer contains, whether it passivates, whether a relaxed structure
is physical). Thermodynamics, lattice matching and machine-learned interatomic potentials (MLIPs)
compute every number. The output is a ranked table of coatings, a verdict and structures per contact,
and a decision log.

## 2. The question and the output

For each candidate coating (plus "none"), two contacts are modelled: cathode | coating and
coating | electrolyte. For each coating the tool returns:

- **rank and tier**: 1 = both contacts stay sharp, 2 = a passivating (insulating, self-limiting) layer
  forms, 3 = a growing (electronically conducting) layer forms;
- **verdict per contact**: sharp or interphase, the layer phases in order, passivating or growing, with
  the reasoning;
- **simulation-ready structures** (`*_best.extxyz`) and the **work of adhesion** W_adh of each contact;
- **decision log** (`decision_log.json`): every LLM decision, its consensus agreement, every gate result
  and rejected candidate;
- `ranking.md` / `ranking.json` with the arm's ranking and a thermodynamics-only ranking side by side.

The same screen runs with three **decision arms** (§5): the LLM, deterministic rules, and a person.

Flagship candidate list (`config.py`): LiNbO₃, Li₃PO₄, Li₂ZrO₃, LiTaO₃, Li₃BO₃ (oxides used as
coatings in sulfide cells) and Li₃InCl₆ (halide). "Used in practice" is not yet backed by DOIs — see §10.

## 3. Prior art and positioning

| Work | What it does | What it leaves out |
|---|---|---|
| pymatgen ZSL / CoherentInterfaceBuilder, MPInterfaces, Ogre | Lattice matching, slab and interface generation | Which interface to build; no chemistry judgement |
| InterOptimus (J. Energy Chem. 106, 631, 2025) | Termination scan + ranking with universal MLIPs, battery interfaces (Li₂S\|Ni₃S₂, LiF\|NCM, Li₃PS₄\|Li) | Interphase decision; no LLM |
| AGAPI-Agents (arXiv 2512.11935) | LLM agent with a Zur-matching heterostructure tool | Battery chemistry, reactivity; demo is GaN/AlN |
| Paimon (arXiv 2606.09422) | Multi-agent MD workflows incl. Li diffusion in Li₆PS₅Cl | Interface construction |
| Lang2MLIP (arXiv 2605.14527) | Agents build SEI structures for MLIP training | Liquid electrolytes, not coherent solid–solid interfaces |
| **Xiao, Miara, Wang, Ceder, Joule 3, 1252 (2019)** | **Deterministic computational screen of cathode coatings for solid-state batteries**: phase stability, (electro)chemical stability, ionic conductivity. Top: polyanionic oxides LiH₂PO₄, LiTi₂(PO₄)₃, LiPO₃; some borates | No atomistic interface models, no adhesion, no kinetic/experimental judgement |

**Consequence of Xiao et al. 2019:** a coating screen by itself is not new. interphAIse must be pitched
on (a) the expert-judgement layer and its measured value over deterministic rules, (b) atomistic
interface structures with adhesion, (c) LLM orchestration. Use Xiao et al. as the deterministic
reference and as a source of expected answers; consider adding LiH₂PO₄, LiTi₂(PO₄)₃, LiPO₃ to the
screen. Check what that paper reports for LiNbO₃ (widely used in practice) before claiming anything.

## 4. The decisions the LLM makes instead of a human

There are three LLM decisions per contact. Each is sampled `N_RUNS` (default 3) times; the majority
answer and its agreement fraction are logged.

### Decision 1 — does a reaction layer form, and what is it? (`reasoners/interphase_reasoner.py`)

- **Today:** a modeller reads the convex-hull reactivity analysis, weighs it against what experiments
  report, and decides what structure to build.
- **LLM input:** the two materials, voltage, temperature, a one-line setting, and the hull analysis:
  reaction energy (eV/atom) per mixing ratio and the products.
- **LLM output:** (i) **sharp or interphase**; (ii) the **layer stack**, electrode side to electrolyte
  side; (iii) **passivating or growing**; plus rationale and kinetic argument.
- **Why it is judgement:** the hull gives the driving force, not what happens. Li | LLZO is slightly
  unstable on paper but kinetically stable → model it sharp. Li | Li₆PS₅Cl reacts to Li₂S, Li₃P, LiCl,
  all insulating → passivating. Li | Li₁₀GeP₂S₁₂ forms an electron-conducting Li–Ge alloy → growing. The
  hull alone cannot separate the last two.
- **Checks:** phases must be hull products of the pair; every adjacent pair in the stack must be
  mutually stable (`tools/reactivity.check_stack`), otherwise the LLM gets the reason and retries.
- **Weight:** passivating vs growing sets the coating's tier, so this is the decision that most
  changes the ranking.

### Decision 2 — which facets are in contact? (`reasoners/facet_reasoner.py`)

- **Today:** chosen from knowledge of the real material: particle morphology, microscopy, texture
  (e.g. LiCoO₂ particles mainly expose (104) and (003)).
- **LLM input:** both phases, space groups, lattice parameters, context.
- **LLM output:** up to three facet pairs ranked by experimental relevance, each with a reason.
- **Deliberately not given:** lattice mismatch, strain, energies (they are computed for every pair it
  proposes). HELLMM lesson: an LLM asked to guess stability discards exactly the cases that matter.
- **Check:** lattice matching must find a cell within strain and atom limits; failed pairs are fed
  back and the LLM proposes again.

### Decision 3 — is the relaxed structure physical? (`reasoners/judge.py`)

- **Today:** the modeller opens the structure in a viewer (OVITO) before trusting the numbers.
- **LLM input:** descriptors before/after relaxation (displacements, gap change, atoms crossing the
  interface, coordination numbers, shortest distance), validation warnings (polar slab,
  non-stoichiometric termination), W_adh.
- **LLM output:** accept / accept with caveat / reject, and for reject one action: thicker slabs, next
  termination, different facets, or larger cell.
- **Check:** none directly — it is the check. Its action drives the next step.

### Orchestration

The LLM does not write code or call tools freely. Its answers choose branches of a fixed state machine
(`orchestrator.py`):

| LLM answer | Next step |
|---|---|
| "interphase, 3 layers" | Build and compute each adjacent pair instead of one interface |
| stack fails the check | Back to decision 1 with the reason |
| facets with no valid match | Back to decision 2 with the reason |
| "reject: thicker slabs" etc. | Rebuild accordingly and recompute |

### Not decided by the LLM

All numbers (reaction energies, strain, energies, W_adh); the ranking rules; the candidate coatings
(chosen by a person in `config.py` — LLM-proposed candidates would be a natural extension, not built).

### Principles carried over from HELLMM

Generation separated from verification; gates not critics (hard, logged rejections); information
barrier (prompts never contain downstream-computed quantities or benchmark answers); never ask the LLM
what is computed; self-consistency by repeated sampling.

## 5. Can the decisions be made deterministically? — the rules arm

Largely yes, and since 2026-10-20 the rules are **implemented as a third arm** (`RulesPolicy` in
`interphaise/policies.py`). They are the baseline the LLM must beat; the older "thermodynamics-only"
ablation (every reactive contact = growing) is too weak to be the comparison.

| Decision | Deterministic rule | What the rule misses | LLM likely adds value? |
|---|---|---|---|
| Sharp or interphase | Threshold on reaction energy (sharp if > −X meV/atom) | Kinetic stabilisation (Li \| LLZO); arbitrary threshold | **Yes** — kinetics and experimental knowledge |
| Layer phases and order | Decomposition products of the electrolyte as μ_Li sweeps from the electrode value to the electrolyte (grand-potential phase diagrams; "chemical potential profile" approach) | Nucleation order, amorphous products | **Probably not** — the rule is well founded |
| Passivating or growing | Band gap of each product from Materials Project; any metallic product → growing (mixed conducting interphase) | PBE gap underestimation, small-gap phases, insulating but Li-blocking layers | **Marginal** — edge cases only |
| Facets | BFDH (larger d_hkl first, zero cost); Wulff shape from MLIP surface energies; or exhaustive low-index pairs (`run_bruteforce.py`) | Synthesis morphology, texture, which facet touches the electrolyte | **Possibly**, but hard to separate from recall of papers |
| Physicality | Thresholds on descriptors + fixed mapping to actions | Multi-signal trade-offs, explanation | **Weakest case** — rules probably as good and more reproducible |
| Orchestration | Already a fixed state machine; with rule answers the pipeline is fully deterministic | — | No |

### What is implemented (2026-10-20)

**Policy layer.** The orchestrator never calls an LLM directly; it asks a *policy* for each decision
(`decide_interface_type`, `propose_facets`, `judge`). Same pipeline, gates and numbers for every arm.

| Arm | `--policy` | Class | Decisions by |
|---|---|---|---|
| LLM | `llm` (default) | `LLMPolicy(make_llm(model))` | LLM reasoners, majority over `N_RUNS` samples |
| Rules | `rules` | `RulesPolicy(RuleSettings())` | Deterministic rules below; agreement always 1 |
| Human | `human` | `LLMPolicy(HumanLLM())` | A person answering the same prompts |

A bare `llm(system, user)` callable passed to `Orchestrator` or `run_screen` is still accepted and
wrapped in `LLMPolicy` (backwards compatible). Every decision event in `decision_log.json` now has
kind `"decision"` and `inputs.policy`; `ranking.json` carries `policy` and `policy_settings`
(all rule thresholds).

**The rules as implemented** (`RuleSettings` defaults):

| Decision | Rule | Default |
|---|---|---|
| Sharp or interphase | Sharp if the min reaction energy (hull) > threshold | `sharp_threshold = -0.05` eV/atom |
| Layer phases | Dominant products of the most favourable reaction, by atoms in the balanced equation | `max_intermediate = 3` |
| Layer order | First permutation whose adjacent pairs all pass `check_stack`; ties by Li fraction (Li-rich phases on the Li-richer side) | — |
| Passivating or growing | Growing if any layer phase has MP band gap < threshold; metal-only composition when the gap is unknown | `metallic_gap = 0.1` eV |
| Facets | BFDH: rank symmetry-distinct facets by effective d_hkl (d / smallest n with non-zero Z-weighted structure factor of n·hkl, so extinctions are handled); pair the top ones by rank sum; retries skip tried pairs | `facet_max_index = 2`, `facets_per_phase = 3` |
| Physicality | min distance < 1.0 Å or gap opened > 1.5 Å or W_adh ≤ 0 → reject, next termination; > 5 % of atoms crossed the interface → reject, different facets; mean interface displacement > 1.0 Å or coordination change > 30 % → reject, thicker slabs; validation warnings → accept with caveat; else accept | see `RuleSettings` |

Band gaps come from Materials Project (`tools/materials.get_band_gap`, needs `mp-api`; cached in
`data/band_gaps.json`).

**Layer-order caveat found while building the rule:** when all products are mutually stable (e.g.
Li₂S, Li₃P, LiCl against Li), thermodynamics does not fix their order; the rule falls back to Li
fraction. The order is therefore weakly determined by either arm, and scoring of decision 1-order
should be given less weight than sharp/interphase and passivating/growing.

**Comparison.** `scripts/compare_arms.py runs/` takes the latest screen of each arm and prints (and
with `--out` writes) the rankings side by side with the thermodynamics-only ablation, every contact
where the arms disagree, the number of contacts where the LLM overrides the rules, and each arm's
score against `benchmark/literature_cases.yaml`.

**Tests:** 21 offline tests pass, 9 of them for the rules arm (each rule, BFDH extinctions, retry
skipping, judge thresholds, full pipeline with `RulesPolicy`, screen + `compare_arms`).

### Still to do

1. **Hybrid mode (likely strongest).** Give the LLM the rule outputs as inputs (ordered products,
   their band gaps, the BFDH facet ranking). It decides where they conflict with known chemistry.
   Report the **override rate** and **override accuracy** against the literature.
2. **Threshold sensitivity.** The rule thresholds are judgement calls themselves; sweep
   `sharp_threshold` (e.g. −0.01 to −0.2 eV/atom) and report how the rules ranking changes.
3. **Better rules if time allows:** layer order from the chemical-potential profile (electrolyte
   decomposition as μ_Li sweeps from electrode to electrolyte); Wulff facets from MLIP surface energies.
4. Framing: decision 1 sharp/interphase and decision 2 are where the LLM is expected to win; layer
   order and the physicality check are explanation and exception handling.

## 6. Architecture and code map

One state machine per contact; the screen runs it twice per coating; the ranker orders coatings.

```
REACTIVITY ─▶ INTERFACE_TYPE ─▶ STACK_CHECK ─┐      reactive neighbours → feedback → INTERFACE_TYPE
   [det]         [LLM, dec. 1]      [det]    ▼
for each adjacent pair in the stack:
   FACETS ─▶ MATCH+VALIDATE ─▶ ENERGETICS ─▶ JUDGE ─▶ next pair / DONE
 [LLM, dec. 2]    [det]           [det]    [LLM, dec. 3]
     ▲             │ no valid match              │ reject + action
     └─────────────┴──────── feedback ◀──────────┘
screen.py: all contacts × coatings → ranker.py → ranking.md / ranking.json
```

| Path | Role |
|---|---|
| `interphaise/context.py` | Dataclasses passed between stages (all JSON-loggable) |
| `interphaise/orchestrator.py` | State machine for one contact; asks a policy for every decision; `build_structures=False` stops after decision 1 |
| `interphaise/policies.py` | `LLMPolicy` (LLM, human), `RulesPolicy` + `RuleSettings` + `bfdh_ranking`, `make_policy` |
| `interphaise/screen.py` | Coating screen: contacts per coating + uncoated baseline |
| `interphaise/ranker.py` | Tiered ranking; `mode="decisions"` (the arm's calls) and `mode="thermo"` |
| `interphaise/reasoners/` | `interphase_reasoner`, `facet_reasoner`, `judge`, `consensus`, all prompts in `prompts.py` |
| `interphaise/tools/materials.py` | MP bulk structures, entries and band gaps, cached under `data/` |
| `interphaise/tools/reactivity.py` | Interfacial reactivity (closed system for Li metal, grand potential with Li open otherwise); `check_stack` |
| `interphaise/tools/matcher.py` | ZSL matching over all terminations, symmetry-duplicate removal |
| `interphaise/tools/validation.py` | Gates: atom budget, strain, overlapping atoms, charged slabs (reject); polar, non-stoichiometric (warn) |
| `interphaise/tools/energetics.py` | Registry scan (in-plane offset × gap), FIRE relaxation, W_adh, evaluation counters |
| `interphaise/tools/descriptors.py` | Structural descriptors for the judge |
| `interphaise/tools/mlip.py` | `pet-mad`, `metatomic:<path>`, MACE-MP / UMA via HELLMM, `lj` toy |
| `interphaise/llm.py` | `make_llm` (litellm or HELLMM router), `HumanLLM` (person answers the prompts), `ScriptedLLM` (tests) |
| `benchmark/literature_cases.yaml` | Expected expert decisions and `coating_screens` expectations (all `verified: false`) |
| `benchmark/score_agreement.py` | Scores decision logs and rankings against the yaml |
| `scripts/run_screen.py` | Flagship: `--decision-only`, `--dry-run`, full |
| `scripts/run_cases.py`, `scripts/run_bruteforce.py` | Single contacts; exhaustive no-LLM baseline |
| `scripts/compare_arms.py` | Arms side by side, disagreements, LLM overrides of the rules, scores |
| `config.py` | LLM model, MLIPs, cases, `COATING_SCREEN` |

**Ranking rule** (worst contact decides): tier → worst reaction energy (closer to 0 better) → weakest
W_adh (higher better) → consensus agreement.

**Potential convention:** both contacts of a cathode coating are evaluated with Li open at the cathode
potential. Conservative for the coating | electrolyte side; state it when reporting.

**MLIP choice:** PET-MAD is PBEsol without +U or spin; magnetic TM-oxide cathodes need an
MPtrj-trained model (`MLIP_CATHODE = "mace-mp-medium-0b3"`). LiCoO₂ (low-spin Co³⁺) is the safer
flagship.

## 7. How to run

```bash
pip install -e ".[dev,llm]"           # + pet-mad / mace-torch for energetics
pip install -e ../hellmm              # optional: reuse HELLMM's LLM router and MLIP loader
cp .env.example .env                  # MY_MP_API_KEY, MY_OPENROUTER_API_KEY, MY_ANTHROPIC_KEY
pytest                                # offline: toy Li–S chemistry, scripted LLM, LJ calculator
python scripts/run_screen.py --decision-only                  # LLM arm
python scripts/run_screen.py --decision-only --policy rules   # rules arm
python scripts/run_screen.py --decision-only --policy human   # human arm (interactive)
python scripts/compare_arms.py runs/ --out runs/compare.md
python scripts/run_screen.py --policy rules                   # full pipeline, any arm
python benchmark/score_agreement.py runs/
```

`LLM_MODEL = "deepseek-v3.2"` is a HELLMM alias; without HELLMM installed use
`openrouter/deepseek/deepseek-v3.2`.

## 8. Compute cost

No long simulations: every number is a single point or a relaxation of at most a few hundred steps.
Only the stretch goals (MD anneal, Li transport across the interface) need nanoseconds of MD.

| Mode | What runs | Estimated time, 13 contacts |
|---|---|---|
| `--decision-only` | Hull reactivity + ~3–10 LLM calls per contact | 5–15 min, < $1 LLM |
| `--dry-run` | + facets and lattice matching | 15–30 min, CPU |
| full, `--no-relax` | + registry scan, single points | < 1 h, one GPU |
| full | + 3 relaxations per candidate | 1–3 h on one GPU; ~a day on laptop CPU |

These are estimates from typical MLIP speeds, not measurements. Contacts are independent: one per GPU
brings the full screen under an hour. First pass: `registry_n_xy=2`, two gaps, `top_k_candidates=1`.

## 9. Evaluation plan

Target headline: *known-good coatings outrank the bare cathode, and the LLM's calls beat the
deterministic rules in the cases where kinetics or experiment matter.* All arms run through the same
pipeline; `compare_arms.py` produces items 1, 3 and 4.

1. **Ranking vs experiment**: known-good coatings above the uncoated cathode, for LLM, rules and
   thermodynamics-only rankings.
2. **Decisions vs published studies**: 7–15 systems in `literature_cases.yaml`; sharp/interphase,
   phases and order, facets. Only DOI-verified entries count.
3. **Rules vs LLM vs human, blind**: `--policy rules | llm | human`, same pipeline.
4. **Override metric**: how often the LLM overrides the rules (`compare_arms.py`, available now), and how
   often it is right (check each override against the literature). Hybrid mode will sharpen this.
5. **Efficiency**: relaxations to the best interface, LLM-guided vs `run_bruteforce.py`.
6. **Reproducibility**: repeat runs, second LLM vendor; per-decision agreement.

## 10. Status (2026-10-20)

**Built and committed:** scaffold, coating screen, ranker, benchmark scorer, renaming to interphAIse,
**rules arm** (policy layer, `RulesPolicy`, `--policy` flag, `compare_arms.py`).
**Tested:** 21 offline tests pass (toy Li–S chemistry, scripted LLM, Lennard-Jones calculator).
**Not yet run:** anything against Materials Project, a real LLM or a real MLIP.
**Unverified:** every entry in `benchmark/literature_cases.yaml`, including which coatings work in
practice — all `verified: false`, need DOIs.
**Not implemented:** hybrid mode and the threshold sweep (§5); merged multilayer interphase cells (stacks
are built as pairwise interfaces); interface energy γ_int (only W_adh); MD anneal and Li transport.

## 11. Risks

- The rules may match the LLM on most decisions; the pitch then rests on the few cases where they
  differ (measure, don't assume).
- LLM recall vs reasoning on well-studied systems; separate with the blind human baseline and
  less-studied coatings.
- Cell size: garnet and argyrodite interfaces can exceed the 600-atom budget.
- Disorder: argyrodites and garnets use MP ordered approximants; record the MP id.
- MLIP domain for magnetic cathodes (see §6).

## 12. Two-day plan

First milestone, Wednesday noon: `run_screen.py --decision-only` end to end on real MP data and a real
LLM (no MLIP needed). Pre-fetch all MP data Wednesday morning and commit `data/`.

| Work package | People | Wed 21 Oct | Thu 22 Oct |
|---|---|---|---|
| A. Benchmark | 2 | Verify `literature_cases.yaml` and `coating_screens` with DOIs | Human blind baseline; scoring |
| B. Reasoners, rules, prompts | 1–2 | Decision-only screen with the LLM and rules arms; prompt iteration; rule thresholds | Hybrid mode, override accuracy, threshold sweep, repeat runs |
| C. MLIP and energetics | 1–2 | PET-MAD / MACE-MP; Li \| LLZO adhesion sanity check | Full screen; brute-force baseline counts |
| D. Demo | 1 | Structure and decision-log viewer | Slides and video |

## 13. Project history (decisions taken in brainstorming)

- Ideas considered: agent benchmark for atomistic simulations (crowded: ASE-Bench, MDGym, MDArena);
  transport agent with statistical error bars (partly done by Paimon); MLIP fit-for-purpose checker;
  reproducibility auditor; MLIP dataset health check; trajectory-analysis notebooks; derivation checker.
- Chosen: extend HELLMM's design (LLM proposes, deterministic stages compute) to solid–solid battery
  interfaces, because the team owns a working pipeline and an MLIP stack, and interface modelling has a
  clear human-judgement step.
- Reframed from "build an interface model" (a modelling tool) to a **coating screen** (a battery result
  checkable against experiment), with LiCoO₂ | Li₆PS₅Cl as flagship.
- Hackathon requirement adopted: a clear component where human reasoning is replaced by an LLM, in
  addition to LLM orchestration (§4).
- Name: **interphAIse**; Python package `interphaise`.
- Asked whether the decisions could be deterministic: largely yes. Found Xiao et al. 2019 (deterministic
  coating screen). Decided to make deterministic rules a full third arm (built 2026-10-20) so the LLM is
  measured against expert rules, not against the crude thermodynamics-only ablation.

## Sources

- Xiao, Miara, Wang, Ceder, *Computational Screening of Cathode Coatings for Solid-State Batteries*,
  Joule 3, 1252 (2019): https://escholarship.org/uc/item/3mb3d98h
- InterOptimus, J. Energy Chem. 106, 631 (2025):
  https://cityudg.globalimpact.cn/en/publications/interoptimus-an-ai-assisted-robust-workflow-for-screening-ground-/
- AGAPI-Agents: https://arxiv.org/html/2512.11935v2
- Paimon: https://arxiv.org/pdf/2606.09422
- Lang2MLIP: https://arxiv.org/pdf/2605.14527
- MPInterfaces: https://ar5iv.labs.arxiv.org/html/1602.07784 · Ogre: https://arxiv.org/pdf/2103.13947
- OSI Hackathon: https://llmhackathon.github.io/
