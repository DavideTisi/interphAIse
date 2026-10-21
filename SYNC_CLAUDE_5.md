# Vacuum/thickness audit and bounded registry plan

21 October 2026, `davide`, reviewed at `d0bd1f3`.

**Recommendation: publish `d0bd1f3` and proceed with the bounded checks below.**
GitHub currently points to `84f1c76`; the new commit is local. This review did
not push, send an external message or launch calculations.

## Audit result

The saved results support the reported working values:

| Contact | Substrate / coating layers | Atoms | W_adh | W_sep |
|---|---|---:|---:|---:|
| LiCoO2 / LiNbF6 | 2 / 4 | 696 | 3.60014 | 5.12754 |
| Li6PS5Cl / LiNbF6, seed 0 Cl cut | 4 / 4 | 880 | 1.63294 | 2.96690 |

Energies are J/m². The electrolyte 544-atom value (1.53173 / 2.85790) is now
the thinner-coating comparison, not the current working setting.

Independently recomputed both works for the four new thickness runs and
checked all 12 saved relaxation records for their finite, force-target and
overlap conditions. The physical fixed sites match the corresponding baseline
after accounting for substrate height and species; separated-substrate masks
also agree. Accounting is 1,054 calculator calls plus eight separation single
points. The electrolyte final increments are 0.01318 / 0.01436 J/m². The
cathode two-layer substrate is retained because both thicker checks agree
with it within about 0.001 J/m²; this is a stated economical choice supported
by the full tested range, not an untested extrapolation.

The 30 archived vacuum single points reproduce the reported energy spreads:
at most 0.0000441 J/m². All three relaxed structures per contact remain within
the free-force target. Rigid fragments intentionally have large forces and
must not be included in a claim that every structure is relaxed. The script's
printed maximum includes those fragments; use the separately recorded relaxed
interface/film/substrate forces for the convergence statement.

**Vacuum scope:** the electrolyte scan was at 4 + 2 layers (544 atoms), before
the coating became four layers. The final 880-atom interface has an independently
checked empty gap of 15.73147 Å, but no separate archived vacuum sweep. Keep
that distinction in the report. A single 15-versus-25 Å confirmation on the
final geometry is enough to close the numerical bookkeeping if desired;
there is no need for another broad vacuum campaign. Isolation under the
finite-range model does not address real polar electrostatics.

## Final-geometry constraint check

Before calling the final working values insensitive to constraints, repeat
the endpoints of the existing brackets at the new coating thicknesses:

- Cathode, 696 atoms: the prior 0.17 / 0.34 / 0.50 substrate-fraction bracket
  remains well defined because its two-layer substrate is unchanged. Reuse
  the 0.34 baseline only after matching all settings; add the two endpoints.
- Electrolyte, 880 atoms: depths 1.628801 / 3.257602 / 6.515204 Å. Reuse the
  middle-depth baseline after checking settings; add the two endpoints.

That is four additional settings, not another thickness sweep. Keep registry
(0,0), initial gap 2 Å, 15 Å vacuum, fixed in-plane cells, terminations,
checkpoint and optimizer. Verify physical masks and carry them to separated
references. Report both works and their full bracket spreads against the
existing 0.1 J/m² tolerance. If a bracket fails, retain the failure and resolve
or explicitly report constraint sensitivity before interpreting registry gains.
The earlier brackets remain valid evidence for their earlier geometries only.

## Declare a small relaxed registry comparison before computing it

Suggested bounded set for **each** final contact, in fractional matched-cell
in-plane offsets: **(0,0), (0,0.5), (0.5,0), (0.5,0.5)**, all with initial
gap 2 Å. Use the selected reference constraint and all other working settings.
This reuses the existing lateral grid but tests its relaxed outcomes, which
the unrelaxed scan cannot establish. It is a coarse sensitivity check, not
an exhaustive search over translations, gaps, terminations or facets.

Save this set and selection rule before launching it. Reuse (0,0) only if the
full inputs and protocol match; otherwise rerun it. With valid reused
baselines, six new settings remain across the two contacts. Preserve failed
and converged outcomes alike, and record whether distinct starts relax to the
same arrangement.

**Select the lowest relaxed joined-interface energy among converged runs at
the same atom count, composition and cell.** Do not choose the largest W_adh:
different metastable separated-slab minima can change that number without
making the joined interface more stable. Report each joined energy relative
to the lowest, both W_adh and W_sep, and both separated-reference energies.
Use one documented reference policy consistently; do not silently mix isolated
slabs from different runs or change constraints. Report reference-minimum
differences if independent slab relaxations end differently.

## Seed comparison and stopping point

After the working protocol is chosen, build seed 4 at the same layer counts,
mapped Cl framework cut and fixed-depth rule. For the direct bulk-arrangement
sensitivity comparison, hold the same selected fractional registry in both
seeds and record cell/strain differences and physical fixed counts. Optimizing
each seed separately would answer a different question; label that separately
if later performed.

Keep this a bounded sensitivity study. The one-direction-at-a-time thickness
checks and finite registry set do not prove a global minimum or an infinite-slab
limit. Both contacts remain formally polar and model-dependent. No extra
coating ranking, DFT campaign or open-ended surface search is proposed here.
Adem's environment smoke batch is independent; LLM production still requires
its separate cost review.

The viewer subagent has been given the new exact values and is updating the
current-contact selection to 880 atoms. Presentation v4 still predates these
results and needs a later revision; it was not edited in this audit.

Evidence: [audit JSON](data/reviews/vacuum_thickness_review_20261021.json),
[CONTACT_PROTOCOL.md](CONTACT_PROTOCOL.md). This file is a handoff for Davide
to relay; Claude and Adem were not messaged directly.
