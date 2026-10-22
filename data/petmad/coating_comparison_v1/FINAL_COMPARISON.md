# Coating pilot: final PET-MAD comparison (robustness-inclusive)

22 October 2026, branch `work/petmad-comparison`. **`index_final.json` is the robustness-inclusive
version**, released after the pilot's final live call (`origin/work/agent-experiments` `c0a0546`). The
decision-time states are preserved unchanged in `snapshots/`: indices for choose-2 (`b02750fe…`),
choose-3 (`4577b2ab…`) and the summary (`7ba8cc4a…`, which also stays as `index.json`), plus the
producer bundles LiTaF6 `91e80b06…` and LiCaAlF6 `2f274f11…`. Primary rows and registry selections in
`index_final.json` are identical to those snapshots. No value below entered a decision unless it is
marked "primary".

| Coating | Role | Cathode W_adh / W_sep (selected) | Electrolyte W_adh / W_sep (selected) | Weaker contact, min W_adh |
|---|---|---|---|---|
| LiNbF6 | reference | 3.617 / 5.168 | 1.633 / 2.967 | electrolyte, 1.633 |
| LiTaF6 | LLM choice 2 | 3.339 / 4.728 | 1.577 / 2.911 | electrolyte, 1.577 |
| LiCaAlF6 | LLM choice 3 | 1.427 / 4.322 | 0.744 / 1.490 | electrolyte, 0.744 |
| LiF | not selected | — | — | not run |

Values in J/m². These are model results (PET-MAD S 1.6.0) for two separately matched, formally polar
contact cells, not experimental adhesion.

**Sensitivity**, released after the summary, as ΔW_adh relative to the selected primary:
- **Registry (primary sets):** LiTaF6 cathode 0.012 range, electrolyte 0.044 range; LiCaAlF6 cathode
  0.085, **electrolyte 0.220** (joined energies span 3.5 eV); LiNbF6 under the geometry-only rule:
  cathode selection would be (1/12,1/4), +0.010 (consistency runs; reference package unchanged).
- **Thickness +1 coating layer:** LiTaF6 +0.002 (cathode), −0.005 (electrolyte); LiCaAlF6 +0.007
  (cathode); **LiCaAlF6 electrolyte unquantified** (`not_run_resource_limit`, 1,302 > 1,250 atoms).
- **Deeper fixed region:** LiTaF6 −0.005 / +0.024; LiCaAlF6 −0.001 / +0.014.
- **Cathode with 3 LiCoO2 layers:** LiTaF6 +0.000; LiCaAlF6 +0.009.
- **Bulk-structure (seed-4 Li6PS5Cl) on the electrolyte:** **LiNbF6 −0.121, LiTaF6 −0.114** (above
  the 0.1 J/m² tolerance; a combined bulk/cell/basis/registry construction sensitivity, not an error
  bar). **LiCaAlF6 unquantified** (`not_run_no_admissible_construction`).

**Accounting (new full jobs; ceiling 36):** 26 = 12 primary (selected coatings) + 10 sensitivity + 4
LiNbF6 consistency. 6,632 calculator calls, 52 rigid-separation single points, 1,525 s of runner time
on RTX 3090 (`sm3090el9_devel`). This excludes the five reused LiNbF6 primaries, bulk preparation
(LiF/LiTaF6: 389 CPU calls) and queue/setup time. All 26 jobs converged; none failed.

Built by `scripts/finalize_coating_index.py`, which checks every snapshot hash against the live records
and re-validates every released run through the F2 gate with works recomputed from source energies.
