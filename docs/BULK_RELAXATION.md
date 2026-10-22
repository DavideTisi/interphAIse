# PET-MAD bulk relaxation — 21 October 2026

Step 1 of the PET-MAD plan in [EXPERIMENT_AMENDMENT.md](EXPERIMENT_AMENDMENT.md): relax
the five pinned bulk structures before any slab is rebuilt. **No interface has been
rebuilt yet.** Two findings need decisions first (see the end).

## Protocol

- Inputs: pymatgen conventional standard cells of the pinned entries in
  `data/thermo/mp_gga_v2.json.gz` (the same cells the slab builder uses).
  LiCoO2 `mp-aaaabhik`, Li6PS5Cl `mp-aaacebzk`, LiNbF6 `mp-aaacjjwh`,
  LiCaAlF6 `mp-aaaaajby`, LiZr2(PO4)3 `mp-aaabevhd`.
- Model: PET-MAD S 1.6.0 (r²SCAN), CPU, two threads, offline checkpoint SHA-256
  `3f52e97c459b2a28a94fc49b8a2f9a92551231a0ea4f5b5db2396f12d8ffa1e9`.
- **Symmetric relaxation:** positions and lattice, FIRE + `FrechetCellFilter`, space
  group kept with `FixSymmetry`. Converged means max force ≤ 0.01 eV/Å **and** max
  |stress| ≤ 0.05 GPa, evaluated on the symmetry-projected forces/stress of the final
  structure. Raw (unprojected) values are recorded too; they stay at 0.012–0.021 eV/Å
  because PET-MAD is not exactly equivariant, and a symmetric relaxation cannot remove
  that part.
- **Stability check:** rattle the converged cell (σ = 0.02 Å, seed 0) and relax again
  with the same criteria but **no symmetry constraint**. A clear energy drop means the
  model prefers a lower-symmetry structure. One seed only; it finds *a* lower minimum, not
  the lowest one.

`FrechetCellFilter` divides the stress term by the atom count, so FIRE's own `fmax` exit
is too loose for stress (a first attempt stopped LiCoO2 at 0.198 GPa). The helper
therefore restarts FIRE with a halved `fmax` until both criteria hold, and never trusts
the optimizer's flag. The aborted first attempt is kept in ignored
`runs/bulk_relaxation_aborted_v0/` and is not used.

## Results

All ten relaxations converged. 2,944 calculator executions, 548.8 s in total.

| Material | MP a, c (Å) | PET-MAD a, c (Å) | ΔV vs MP | Steps | Stability check ΔE (meV/atom) | Space group after check (0.1 Å) |
|---|---|---|---:|---:|---:|---|
| LiCoO2 | 2.843, 14.146 | 2.809, 14.044 | −3.10 % | 43 | −0.003 | R-3m (unchanged) |
| Li6PS5Cl | 10.279 | 10.209 | −2.04 % | 57 | **−63.81** | **Pc** (from F-43m) |
| LiNbF6 | 5.411, 13.751 | 5.237, 13.607 | −7.30 % | 213 | −0.049 | R-3 (unchanged) |
| LiCaAlF6 | 5.083, 9.750 | 4.988, 9.681 | −4.39 % | 68 | +0.012 | P-31c (unchanged) |
| LiZr2(PO4)3 | 8.939, 22.332 | 8.849, 21.901 | −3.88 % | 630 | **−7.57** | **P1** (from R-3c) |

PET-MAD contracts all five cells relative to the MP GGA(+U) entries. No comparison with
experimental lattice constants has been made with verified sources; earlier chat remarks
on agreement with experiment are withdrawn. Symmetric runs converge on symmetry-projected
values. Raw maxima remain 0.012–0.021 eV/Å for forces and up to 0.110 GPa (LiCoO2) for
stress. The unconstrained checks meet both limits on raw values.

**Stable under the check:** LiCoO2, LiNbF6 and LiCaAlF6. Atoms move ≤ 0.023 Å, the cell
changes ≤ 0.6 % in volume, and coordination is unchanged.

**Li6PS5Cl is not a PET-MAD minimum in its MP F-43m form.** Without symmetry, the energy
drops 63.8 meV/atom and the volume shrinks a further 6.2 %. The cell becomes
10.163 / 9.910 / 9.922 Å with α = 87.5°, an effective cubic edge of about 9.99 Å. The PS4
framework is intact (P moves 0.05 Å; every P keeps four S within 2.4 Å). The rearrangement
is in the Li sublattice (RMS displacement 0.72 Å) and Cl (0.64 Å, uniformly); some Li
gain a Cl neighbour. PET-MAD therefore finds a lower-energy distorted structure. One
hypothesis, not established by these calculations, is that the fully occupied ordered MP
approximant (83 meV/atom above the MP hull) places Li where real argyrodite has disordered
split sites. DFT symmetry breaking in Li6PS5Cl has been reported (see
BULK_REVIEW_AND_NEXT_STEPS.md). The 216-atom electrolyte pilot showed Li/Cl rearrangement
in the top argyrodite layers, which may partly reflect this bulk relaxation. Contributions
can cancel between joined and separated references, so the size and sign of any effect on
0.43 J/m² are unknown until a consistent recalculation.

**LiZr2(PO4)3 also prefers a distorted structure** (−7.6 meV/atom, P1, +2.4 % volume).
Only Li moves substantially (RMS 1.63 Å; Li–O coordination 6 → 4 within 2.6 Å). The PO4
and ZrO6 units are intact. A low-symmetry, low-temperature form of LiZr2(PO4)3 is
reported besides rhombohedral R-3c, so this is physically plausible. It has not been
compared against such a structure here.

## Consequence for interface matching

Relaxed lattices change which interfaces pass the unchanged gates (ZSL 5 % / 3 %,
strain ≤ 6 %, area ≤ 300 Å²). Symmetric relaxed cells; `scripts/scan_interface_matches.py`:

| Contact | Smallest valid interface | Atoms | Strain | Area |
|---|---|---:|---:|---:|
| LiCoO2 (any low-index facet) \| LiNbF6 | LiCoO2(101) \| LiNbF6(110) | 128 | 2.86 % | 133 Å² |
| LiCoO2 (001), as in the pilot \| LiNbF6 | LiCoO2(001) \| LiNbF6(110) | 456 | 2.73 % | 116 Å² |
| Li6PS5Cl \| LiNbF6 | Li6PS5Cl(111) \| LiNbF6(001) | 440 | 2.86 % | 180 Å² |

The 224-atom cathode pilot and 216-atom electrolyte pilot matches **no longer exist**:
LiNbF6 contracts 3.2 % in-plane against LiCoO2's 1.2 %. Under the 256-atom cap there is
no valid electrolyte contact at all. The earlier "~185 Å² cap" applied to unrelaxed MP
lattices and is superseded. Statements about "no match" refer to the tested symmetry-
distinct low-index facets (index ≤ 1) only. Enumeration keeps at most 60 candidates per
facet pair, so "smallest" means smallest among returned candidates. These sizes use the
symmetric cells and must be recomputed once the Li6PS5Cl reference bulk is chosen.

## Decisions needed before rebuilding

1. **Which Li6PS5Cl (and LiZr2(PO4)3) bulk to build slabs from?**
   (a) The symmetric relaxed cell. Its facets and terminations are well defined, but the
   slab will relax along the 64 meV/atom pathway during the interface calculation.
   (b) The distorted structure from this one rattle. Lower energy, but an arbitrary Li
   arrangement and a non-cubic cell.
   (c) A small search for a better ordered structure: several rattle seeds or a short
   MD anneal, then pick the lowest after relaxation. Do this before slab building;
   Niflheim is suited to it.
2. **Atom cap and facet freedom.** The electrolyte contact needs at least 440 atoms
   under the current strain gates. Raising the cap to about 512 atoms for both contacts
   keeps one rule. Alternatively, keep LiCoO2(001) fixed (456 atoms) or allow all
   cathode facets (128 atoms). Larger cells increase cost; the pilot rate suggests a few
   minutes per contact on CPU.

## Reproduce

```sh
MPLCONFIGDIR=/private/tmp/interphaise-mpl HF_HUB_OFFLINE=1 .venv/bin/python scripts/relax_bulk.py \
  --output runs/bulk_relaxation_repeat --checkpoint ~/.cache/interphaise/pet-mad-s-v1.6.0.ckpt
.venv/bin/python scripts/inspect_bulk_relaxation.py runs/bulk_relaxation_repeat
.venv/bin/python scripts/scan_interface_matches.py runs/bulk_relaxation_repeat/Li6PS5Cl/symmetric/final.extxyz \
  runs/bulk_relaxation_repeat/LiNbF6/symmetric/final.extxyz --names Li6PS5Cl LiNbF6 --max-atoms 700
```

Evidence in `data/petmad/bulk_relaxation_v1/` (480 KB): summary, inspection, matching
scans, the filtered run log, and per material the relaxed CIF plus initial/final structures
and FIRE logs for both relaxations. The inspection replays identically from these files.
Trajectories remain in ignored `runs/bulk_relaxation/`. Code: `relax_cell_record` in
`interphaise/tools/relaxation.py` (two new tests), `scripts/relax_bulk.py`,
`scripts/inspect_bulk_relaxation.py`, `scripts/scan_interface_matches.py`. No LLM, MP
API or cluster calls.

## Multistart follow-up (option c)

Per BULK_REVIEW_AND_NEXT_STEPS.md: seeds 1–5 at σ = 0.02 Å from the saved symmetric cell,
no symmetry, same checkpoint, zero pressure, 0.01 eV/Å and 0.05 GPa targets, 1,000-step
budget. Seed 0 is the earlier stability check, reused without recomputation. Distinct
minima are grouped with pymatgen `StructureMatcher` (default tolerances); only converged
seeds are grouped or selected. Local CPU, four threads per material, run in parallel.
Cost: Li6PS5Cl 2,299 calls in 342 s; LiZr2(PO4)3 4,917 calls in 1,225 s.

**Li6PS5Cl.** All six seeds converged, and each is a **distinct minimum**. ΔE relative to
the symmetric cell: seed 0 −63.81, seed 4 −61.79, seed 3 −60.63, seed 5 −59.75,
seed 2 −57.75, seed 1 −57.73 meV/atom. All are valid: no overlap violations, minimum
distance 2.04–2.05 Å, every P keeps 4 S, and every Li has 3 S within 3.0 Å. The minima
differ in Li–Cl contacts (2–7 Li without a Cl neighbour) and in the cell (991–1036 Å³,
angles within ±2.5° of 90°). Seed 0 is the only one with residual symmetry (Pc). It does
not match any other seed even with loose tolerances (ltol 0.3, stol 0.6, 8°), whereas
seeds 1–5 resemble each other under those tolerances. This samples nearby basins of a
rugged landscape; it is not a search over Li/S/Cl disorder and gives no global minimum.

**LiZr2(PO4)3.** Five of six seeds converged. Seed 5 exhausted the budget (max force
0.0114 eV/Å) and is excluded. The five converged seeds are distinct but close: seed 0
−7.57, seed 1 −7.27, seed 4 −6.37, seed 3 −6.13, seed 2 −6.07 meV/atom. Cells are nearly
identical (1519–1521 Å³). PO4 and ZrO6 are intact; Li is 4-coordinated by O within 2.6 Å
(one 3-coordinated Li in seed 2). The 1,000-step budget binds for this 108-atom cell:
seeds 1–3 reached the cap. Seed 1 ended at 0.001 eV/Å, which suggests a halved-fmax round
ran past the point where the criteria were first met. The criteria are only re-checked
between rounds, so step counts here overstate the steps actually needed.

**Selected references.** In both materials the lowest minimum is the original seed 0.
- Li6PS5Cl: reference **seed 0** (Pc). Sensitivity alternative **seed 4** (+2.0 meV/atom,
  P1, structurally distinct).
- LiZr2(PO4)3: reference **seed 0**. Alternative **seed 1** (+0.3 meV/atom).

Both keep the parent conventional basis (relaxed from it, no transformation applied).
Model-level references only: these are PET-MAD minima, not established experimental phases.

## Rematch with the selected references (cap 512 atoms; scan to 700)

LiNbF6 and LiCoO2 use their symmetric relaxed cells (stable under the check). Same gates
as before. Lower-symmetry cells make more facets symmetry-distinct, so new
near-coincidences pass the tolerance. All valid electrolyte matches up to 700 atoms are
≤ 512 atoms.

| LiNbF6 facet | Cathode LiCoO2(001) | Electrolyte, seed 0 | Electrolyte, seed 4 |
|---|---|---|---|
| (001), same on both contacts | 504 atoms, 2.17 %, \|p\|/A 0.61 / 2.06 | (111), 440, 2.92 %, 0.56 / 0.17 | (111), 440, 2.74 %, 0.55 / 0.13 |
| (110) | 456, 2.73 %, 0.41 / 2.06 | (100), 356, 3.22 %, 0.00 / 0.11 | none |
| (100) | none ≤ 512 | **(011), 200, 2.27 %, 0.00 / 0.00** | (011), 200, 3.37 %, 0.00 / 0.03 |

Polarity is film / substrate formal |p_z|/A in e/Å. LiCoO2(001) slabs carry 2.06 e/Å at
every termination returned. The cathode (101) option (128 atoms) is unchanged and remains
a separately labelled orientation-sensitivity case.

**Open protocol choice.** Either the same coating facet on both sides (LiNbF6(001):
504 + 440 atoms, available for both Li6PS5Cl minima), or the fewest-atoms rule per
contact (cathode (110) 456; electrolyte (011)|(100) 200, non-polar). The first matches a
single oriented coating film and isolates the bulk-minimum sensitivity. The second is
cheaper on the electrolyte side but changes the coating facet between contacts.

Evidence: `data/petmad/bulk_multistart_v1/` (692 KB): per material `multistart.json`,
per seed initial/final structures and FIRE logs, the run log, and the three matching
scans. Code: `scripts/multistart_bulk.py`. Reproduce, e.g.:

```sh
MPLCONFIGDIR=/private/tmp/interphaise-mpl HF_HUB_OFFLINE=1 .venv/bin/python scripts/multistart_bulk.py Li6PS5Cl \
  --output runs/bulk_multistart_repeat/Li6PS5Cl --checkpoint ~/.cache/interphaise/pet-mad-s-v1.6.0.ckpt --threads 4
.venv/bin/python scripts/scan_interface_matches.py data/petmad/bulk_relaxation_v1/Li6PS5Cl/stability_check/final.extxyz \
  data/petmad/bulk_relaxation_v1/LiNbF6/symmetric/final.extxyz --names Li6PS5Cl LiNbF6 --max-atoms 700
```
