# interphAIse for battery coating discovery

We built interphAIse to test whether LLMs can guide the search for protective battery coatings by choosing what to calculate next. Across 810 search runs and a prospective three-coating atomistic pilot, we found that useful chemical knowledge and useful adaptation to numerical feedback are distinct capabilities whose value depends on the model and battery environment.

**Relevance to physical sciences.** Reactions between a cathode and a solid electrolyte can form resistive layers and degrade batteries. Protective coatings must suppress reactions, maintain contact and conduct lithium. Surface termination, strain and disorder complicate prediction.

**Where the LLM acts.** Candidates are 141 Materials Project crystal structures representing 100 formulas, considered as protective coatings; different atomic arrangements count separately. Haiku 5.5 and DeepSeek V3.2 select from this fixed pool and revise choices from numerical feedback. They do not generate new compositions or structures. Humans set objectives; code scores candidates and enforces budgets. Pymatgen screens coatings against LiCoO₂ at 4 V in sulfide, chloride and LLZO electrolytes.

**What acceptable means.** A candidate passes when its calculated band gap is ≥2 eV, an electronic-insulation proxy, and the driving forces for its own decomposition and additional reaction at either contact are each ≤50 meV per non-lithium atom at 4 V. Additional contact reactions are measured relative to separately equilibrated phases. These are screening criteria for further investigation, not demonstrated battery performance.

**How exploration is tested.** Four policies test an upfront shortlist, sequential choices without results, and iterative choices with correct or shuffled feedback. The 810 runs comprise 720 LLM and 90 shared random runs: 30 per model, policy and environment, with ten queries each. A successful run finds at least one acceptable candidate within those ten queries. Thus, 20/30 means twenty successful search attempts; different runs may find the same material. Exhaustive tables provide ground truth.

![Battery coating schematic, LLM proposal–evaluation–feedback loop, and correct-feedback success counts for Haiku and DeepSeek against random across three electrolytes; Haiku adhesion forecasts held for LiTaF6 and missed for LiCaAlF6.](https://raw.githubusercontent.com/DavideTisi/interphAIse/main/presentations/results_2026-10-22/interphaise_graphical_abstract_810_runs_2026-10-22_v2.png)

*Counts show runs finding at least one acceptable candidate within ten queries. Atoms are schematic; screening success does not establish improved battery performance.*

**Main results.** On sulfide, Haiku succeeds in 20/30 runs with correct feedback versus 2/30 without results and 6/30 with shuffled feedback; both contrasts survive Holm correction. DeepSeek shows the same direction (12/30 versus 2/30 and 3/30), without corrected significance. Chloride reaches 30/30 for every LLM policy and 29/30 for random. On LLZO, DeepSeek’s upfront shortlist reaches 20/30 versus Haiku’s 1/30, but iterative search reaches only 10/30 and 12/30, respectively, versus random’s 24/30. Starting knowledge and useful adaptation are distinct capabilities.

**Prospective physical test.** A separate Haiku pilot evaluates six interfaces using [PET-MAD S 1.6.0](https://github.com/lab-cosmo/upet), trained on r²SCAN, with ASE/UPET. Using LiNbF₆ as reference, Haiku selects LiTaF₆ and LiCaAlF₆ and forecasts adhesion before calculation. Both LiTaF₆ forecasts hold; both LiCaAlF₆ forecasts miss. The electrolyte is correctly predicted as the weaker contact, with relaxed adhesion of 1.63, 1.58 and 0.74 J/m² for LiNbF₆, LiTaF₆ and LiCaAlF₆, respectively. Selection order is unchanged.

**Potential for impact.** Battery-interface researchers could delegate candidate triage and forecast drafting, then review numerical checks and recorded decisions. This could reduce repetitive screening work and guide expensive follow-up; time savings remain unmeasured.

**Innovativeness.** Beyond an exhaustive material ranking, we make the selection strategy itself testable, combining controlled feedback experiments with prospective atomistic forecasts to examine when chemical intuition helps or misleads.

**Novelty.** LLM chemistry tools already exist, including [ChemCrow](https://www.nature.com/articles/s42256-024-00832-8). Our original tooling connects frozen feedback benchmarks with forecasts recorded before physical calculations. Shared tasks, decision traces and offline replay let others compare new policies and investigate failed chemical analogies.

**Limits and next steps.** Human-level judgment and superior coatings are unproven; model comparisons are descriptive because reasoning compute was unmatched. Polar interfaces remain provisional, the proxy admits questionable LLZO candidates, and transport and cycling are untested. Stronger chemistry baselines and higher-fidelity validation are next.

[Code and evidence](https://github.com/DavideTisi/interphAIse) · [Reproduction](https://github.com/DavideTisi/interphAIse/blob/main/REPRODUCE.md) · [Interface explorer](https://davidetisi.github.io/interphAIse/) · [Background](https://ceder.berkeley.edu/publications/Joule2019_coating.pdf).

246 tests passed; all 9,600 archived queries replay.
