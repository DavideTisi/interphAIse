# Original goals and achieved results

21 October 2026. Synthesis against the 20 October discussion and
[implementation plan](DISCOVERY_IMPLEMENTATION_PLAN.md). Evidence comes from
the reviewed production archive, physics archive and subsequent audits. This
document introduces no experiment, objective change or new statistical test.

## The ambition and the question we actually tested

The original ambition was to substitute part of a materials scientist's thinking:
propose a promising material, interpret a calculation, revise a chemical
hypothesis and decide what to test next. Universal MLIPs could provide an
affordable approximate evaluation within a two-day project. This was intended
to go beyond calling tools or sorting an already known table.

The agreed implementation narrowed this to a controlled question: **does
computational feedback improve an LLM's candidate selection beyond its initial
chemical knowledge?** Design A uses an exhaustively evaluated thermodynamic
table, hidden behind a budgeted query interface. PET-MAD was planned as separate
follow-up on 3–5 coatings, including a baseline comparator. This distinction
was present in the original implementation plan, not invented after the results.

## Main result: useful feedback, conditional on the environment

The expanded study contains 141 candidate structure IDs, three electrolyte
environments paired with LiCoO2 at 4 V, five strategies and 30 runs per strategy
per environment: 450 runs with ten charged queries each. The frozen criterion
uses coating self-decomposition and additional reaction on contact, relative to
separately equilibrated reactants, with a band-gap gate. “Acceptable” means
meeting that criterion, not demonstrating a functioning coating.

| Electrolyte | Iterative true feedback | Sequential, no results | Shuffled feedback | Upfront shortlist | Sampled random |
|---|---:|---:|---:|---:|---:|
| Li6PS5Cl | 20/30 | 2/30 | 6/30 | 0/30 | 8/30 |
| Li3InCl6 | 30/30 | 30/30 | 30/30 | 30/30 | 29/30 |
| LLZO | 12/30 | 0/30 | 4/30 | 1/30 | 24/30 |

Sulfide supports useful feedback: iterative beats both planned controls after
Holm correction. Chloride is the predicted near-ceiling condition. LLZO shows
improvement over sequential, but not a significant corrected contrast with
shuffled; random has the higher observed success rate. Random comparisons
remain descriptive alongside the exact random reference curves.

This extends the original 50-candidate result (iterative 19/30, sequential and
upfront each 4/30, random 10/30; shuffled follow-up 6/30). The expanded sulfide
condition overlaps the earlier chemistry and is not an independent validation
across unrelated materials systems. The review-motivated fluoride-first
heuristic also solves the original task quickly; it was constructed after
inspecting the exhaustive results, not supplied by a blinded human expert.

The benefit concerns finding an acceptable candidate, not clearly finding the
best one. Expanded sulfide best-bin successes are 6/30 iterative versus 5/30
random. In LLZO no LLM arm reaches the best bin; random does in 2/30 runs.

Sources: [production review](SYNC_ADEM_9.md),
[original results](INTEGRATED_DISCOVERY_RESULTS.md),
[LLZO audit](SYNC_ADEM_10.md).

## What the LLM contributed

The LLM selects the next structure ID, gives a chemical hypothesis and revises
subsequent choices using returned outcomes. The calculations and acceptance
rules are deterministic and were designed by the team. The model cannot change
the criterion or inspect unqueried outcomes.

The sulfide control contrasts show that the choices benefit from appropriately
associated feedback. They do not establish that every written explanation is
chemically sound, prove human-like reasoning, or measure superiority to a human
materials scientist. Sequential self-history and shuffled-feedback limitations
remain documented in the production review.

LLZO shows the limitation concretely: ten of twelve successful iterative runs
first succeed at queries 8–10, and 26/29 acceptable iterative picks are LiAlSiO4
polymorphs. Selection adapts late and remains concentrated. Five acceptable
structure IDs belong to a post-hoc oxyhalogen practical-review set, but 18 of
random's 24 successful runs also find an unflagged acceptable candidate. This
descriptive partition does not replace the primary outcome. Benchmark/practical
chemistry mismatch is a caveat, not evidence that Haiku deliberately avoided
hazards or that the random advantage disappears.

Using Davide's HELLMM analogy, both projects place the model in a scientific
hypothesis/selection step. The tested interphAIse task is narrower: selecting
existing material structures from a fixed list, rather than proposing new
mechanistic pathways. The experiments address feedback's practical contribution
to those selections; they do not establish equivalent scientific creativity.

## Physical results and the unfinished part of the original plan

The sulfide screen accepts LiNbF6, LiCaAlF6 and two LiTaF6 polymorphs under the
fixed proxy. These are existing materials, not newly invented compositions.
The atomistic work develops LiNbF6 against both battery endpoints:

| Contact | W_adh | W_sep | Qualification |
|---|---:|---:|---|
| LiCoO2 / LiNbF6 | 3.62 | 5.17 | Lowest of three sampled distinct cathode registries |
| Li6PS5Cl / LiNbF6, seed 0 | 1.63 | 2.97 | Working electrolyte reference |
| Li6PS5Cl / LiNbF6, seed 4 | 1.51 | 2.81 | Combined reference/construction sensitivity |

Units are J/m². Bulk relaxation, bounded multistart, matching/surface-cut work,
thickness, constraints, vacuum, registries and CPU/GPU reproduction were
examined. The seed shifts exceed the declared 0.1 J/m² tolerance. Both contacts
remain formally polar and provisional; numerical checks do not establish
experimental accuracy. The newer cathode registry was selected after the
reference-registry thickness/constraint checks.

**The planned common-protocol MLIP comparison of 3–5 coatings was not completed.**
The completed work is a feasibility and sensitivity study of one coating's two
contacts. We have no MLIP-supported cross-coating ranking, no adaptive search
driven by MLIP outcomes, and no measured computational acceleration from using
the LLM. Cheap cached-query counts quantify benchmark sample efficiency only.
Transport, synthesis, full-stack performance and experimental validation are
also outside the established evidence. See [physics review](SYNC_CLAUDE_7.md).

## Assessment against the plan

| Initial aim | Achieved status |
|---|---|
| Let the LLM make the next scientific candidate choice | Implemented and exercised in recorded runs |
| Test whether feedback helps beyond prior knowledge | Demonstrated on the sulfide benchmark; conditional elsewhere |
| Broaden beyond a tiny hand-picked pool | Exceeded the initial scale: 141 IDs across three environments |
| Reliably choose the best material more efficiently | Not demonstrated; acceptability and best-bin results differ |
| Use universal MLIP as affordable physical follow-up | Demonstrated for one coating and two contacts, with substantial limitations |
| Compare a shortlist using a common MLIP protocol | Not completed |
| Discover a new, validated battery coating | Not demonstrated |

The defensible project claim is: **interphAIse automates feedback-conditioned
coating selection, shows when it helps and where it fails, and supplies a
reproducible atomistic follow-up with explicit limits.** It is a useful bounded
demonstration of the original idea; the broader claim of accelerated, validated
materials discovery remains a future objective. The next hackathon work is
presentation and integration, not retrospective changes to the frozen study.
