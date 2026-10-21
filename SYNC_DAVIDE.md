# Agent side status and open questions for Davide

21 October 2026. From Adem.

## Done

Branch `work/agent-experiments`, pushed.

- **Search arms:** random, upfront shortlist, sequential with no results shown (the control), and iterative with real feedback. Each proposal comes with a hypothesis, the observation that motivated it, and whether it explores a new family or refines an earlier one.
- **No leaks:** a test checks that the control arm never sees outcomes, status or timing.
- **Experiment scripts:** `scripts/run_discovery_experiment.py` runs repeats with the same pool order for every arm and keeps failed runs. `scripts/analyse_discovery_experiment.py` plots P(acceptable found) against the number of evaluations, next to the exact random baseline 1 − C(N−M,k)/C(N,k).
- **Synthetic fixture:** a fake 50-candidate pool, so you can see the expected format:

  ```bash
  python scripts/run_discovery_experiment.py --synthetic --repeats 3 --budget 10
  python scripts/analyse_discovery_experiment.py runs/<stamp>_experiment --accept -0.05
  ```

- **Live run on real data** (iterative, budget 2, thermodynamic mode): Haiku picked LiNbO₃, read the result, and switched to Li₃PO₄, citing the reaction energy and products.

## What the real run showed about the evaluator

| Coating | Cathode contact (eV/atom) | Products | Coating–electrolyte (eV/atom) | Products |
|---|---|---|---|---|
| LiNbO₃ | 0.0 | Li, Nb₂O₅, O₂ | −0.294 | Li, Nb₃ClO₇, NbPO₅, S |
| Li₃PO₄ | 0.0 | Li, Li(CoO₂)₂ | −0.341 | Li, P₂O₅, SCl₂O, SO₂ |

1. **The cathode contact scores 0.0 for both coatings, but the products show the coating itself breaking down at 4 V** (LiNbO₃ → Nb₂O₅ + O₂ + Li). This is the self-decomposition gap from the plan; it currently looks like a perfect contact.
2. **The coating–electrolyte energies are about −0.3 eV/atom, with products SO₂, SCl₂O and S.** That looks like Li₆PS₅Cl oxidising at the cathode potential, not a reaction with the coating. If so, most coatings will score about the same and the benchmark has no signal.

## Questions to settle before we freeze anything

1. **Potential convention:** should the coating–electrolyte contact be evaluated at the cathode's 4 V with Li open? If yes, how do we separate electrolyte oxidation from coating reactivity? Should we change the conditions?
2. **Objective:** how is self-decomposition scored, and how are the three penalties combined? The plan suggests the maximum of the normalised penalties. Which energy basis do we use?
3. **Acceptance:** what thresholds for each contact and for self-decomposition? Is the band-gap gate 2 eV? I'll treat missing data as unknown or failed, never as a pass.
4. **Candidate identity:** what does the LLM see per candidate? I'd suggest ID + formula + MP ID, but not hull energy or band gap, since those are evaluator outputs.
5. **Your evaluator's output:** my code currently expects `Evaluation(coating, status, worst_reaction_energy, weakest_adhesion, details, error)`. Will you return a single score plus its components, so I adapt to your v2 schema, or should I write the mapping?
6. **Answer table:** can you also give me all outcomes for the whole pool as a frozen file? I need it for the exact random curve and the tie-aware best-of-k.
7. **Budget and timing:** pool of about 50, budget of 10, 10 repeats per LLM arm? That's roughly 200 Haiku calls, which is cheap. When will the frozen pool be ready?
