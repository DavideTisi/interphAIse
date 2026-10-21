# Cathode coating-thickness review and next checks

21 October 2026, `davide`, reviewed at `84f1c76`.

**Recommendation: publish `84f1c76` and proceed with a bounded vacuum check.**
A fresh GitHub check found `origin/davide` at `40b80fa`, so the new cathode
commit is not yet published. This review did not push or launch calculations.
Preserve the concurrent, uncommitted report/presentation work.

## What the archive establishes

The coating-thickness result passes the declared final-two-setting criterion:

| LiNbF6 layers | Atoms | W_adh (J/m²) | W_sep (J/m²) |
|---|---:|---:|---:|
| 2 | 504 | 3.47935 | 5.05506 |
| 3 | 600 | 3.58547 | 5.10902 |
| 4 | 696 | 3.60014 | 5.12754 |

The final increments are 0.01467 and 0.01852 J/m². Keep four coating layers
as the working cathode setting. This is a coating-thickness check at a fixed
two-layer LiCoO2 substrate, not convergence of the whole contact.

Independent checks recomputed both works from saved energies, checked all nine
stored relaxations against their free-force targets and finite/overlap flags,
reconciled 426 calculator calls plus six rigid-separation single points, and
verified the same physical 104 substrate atoms are frozen at every thickness.
The substrate coordinates match the original baseline after a rigid z shift;
the joined-system global indices change. Baseline energies reproduce within
0.000245 eV. No new PET-MAD calculation was needed for this audit.

The persistent 1.44–1.49 J/m² film relaxation supports a substantial freed-surface
contribution; it does not prove that all finite-size effects are absent. The
cathode constraint bracket was measured at the original two coating layers,
not repeated at four. Keep that qualification with the constraint claim.
Both contacts remain formally polar, with large cathode fixed-atom forces.

## Bounded vacuum check

At the current working geometries (cathode 2 substrate + 4 coating layers;
electrolyte seed 0, 4 substrate + 2 coating layers), compare 15, 20 and 25 Å
vacuum. Keep the termination, registry, in-plane cell, Cartesian slab geometry,
constraints, model and optimizer settings fixed. Increase the normal cell
length without scaling atomic coordinates. Record the actual empty separation
after relaxation, not only the requested vacuum parameter.

Begin with energies and forces of the same saved relaxed interface and both
reference slabs under each cell length. Use matching cells/PBC and masks for
the joined and separated references. If the energy differences or free forces
change materially, relax under the larger vacuum and recompute both W_adh and
W_sep. Check whether the saved structures already satisfy the same force target
at the new vacuum before counting them as converged without further steps.
Keep the existing 0.1 J/m² tolerance for the final-two-setting energy changes;
report smaller differences and force differences explicitly.

This is a numerical periodic-image isolation check for the finite-range model.
Vacuum insensitivity does not establish that real polar-surface electrostatics
are described. Do not present it as resolving the polarity limitation.

## Close or explicitly retain the remaining thickness gaps

Before describing either entire contact as thickness-converged, address:

1. **Cathode substrate thickness.** LiCoO2 has remained at two layers. Prepare
   a bounded three/four-layer geometry and cost proposal with four coating
   layers held fixed, preserving cuts, strain and registry. Keep a constant
   bottom frozen depth, not 34% of an increasing substrate. The depth
   **9.10044154 Å** reproduces the physical 104-atom mask in the present
   baseline; verify correspondence again in every new build. Reuse the same
   physical bottom planes where the cut permits, and apply the same mask to
   the separated substrate. Do not silently apply the earlier 800-atom cap:
   thicker substrates may exceed it.
2. **Electrolyte-contact coating thickness.** This contact still has two
   LiNbF6 layers. The cathode-side coating test does not automatically transfer
   because strain, lateral cell and contacting material differ. Prepare a
   bounded coating-thickness comparison at four argyrodite layers, retaining
   the 3.257602 Å frozen substrate depth and mapped Cl cut.

These are proposed follow-ups, not completed or launched work. If time is
limited, keep these two gaps explicit and label the results as provisional
sensitivity checks; do not replace the predeclared study with an open-ended
convergence campaign. After working thickness/vacuum settings are chosen,
relax a small declared set of competing registries, then run the seed-4
electrolyte comparison with the equivalent framework cut. If the final geometry
changes substantially, recheck the constraint bracket there or retain the
scope of the original bracket result explicitly.

## Reporting and coordination

Current working values are cathode **3.60 / 5.13 J/m²** and electrolyte
**1.53 / 2.86 J/m²** (W_adh / W_sep). These are model results for two separate
strained contact cells; they are not a single continuous film calculation or
experimental adhesion. They remain supporting atomistic validation, not the
LLM benchmark objective. Adem's approved environment smoke batch can proceed
independently; expanded LLM production still awaits its cost review.

The v4 presentation predates `84f1c76`. A subsequent deck revision should
replace the old 3.48 / 5.05 cathode values with these working values, specify
four coating layers / 696 atoms, and keep both untested slab-thickness directions
and the polarity caveat visible. The deck was not edited in this review.

Evidence: [audit JSON](data/reviews/cathode_thickness_review_20261021.json) and
[CONTACT_PROTOCOL.md](CONTACT_PROTOCOL.md). This is a saved handoff for Davide
to relay; no message was sent to Claude or Adem.
