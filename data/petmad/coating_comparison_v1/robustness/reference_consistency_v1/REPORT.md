# LiNbF6 reference under the geometry-only registry rule (robustness, not decision feedback)

22 October 2026. Approved by Davide as lower-priority robustness work (`execution_notes/reference_consistency_v1.json`).
**This result is versioned separately and must not enter any decision prompt or the frozen LiNbF6
primary package**, which keeps its archived selection.

Four jobs, Niflheim RTX 3090 (`sm3090el9_devel`, `--nice=100`), code `4743120`, checkpoint `3f52e97c…`:
11014613–11014616, all COMPLETED in 2:35–2:37. Inputs are the frozen-rule LiNbF6 builds, which are
bit-identical to the archived builds. Fixed depths 9.10044154 Å (cathode) and 3.257602 Å
(electrolyte); the cathode depth gives the same mask as the archived 0.34 fraction. All 12
relaxations converged and pass the F2 gate. Rigid separation ran on CUDA.

| Contact | Registry | Joined energy above lowest (eV) | W_adh (J/m²) | W_sep (J/m²) | Source |
|---|---|---:|---:|---:|---|
| Cathode | **G3 (1/12, 1/4)** | **0** | **3.6271** | **5.1634** | new |
| Cathode | R3 (1/3, 1/3), archived selection | +0.0552 | 3.6171 | 5.1676 | archive |
| Cathode | G2 (1/4, 1/4) | +0.1357 | 3.6026 | 5.1083 | new |
| Cathode | R1 (0, 0) | +0.1479 | 3.6004 | 5.1277 | archive |
| Cathode | R2 (1/6, 0) | +0.1665 | 3.5970 | 5.0908 | archive |
| Electrolyte | **R1 (0, 0)**, archived selection | **0** | **1.6334** | **2.9672** | archive |
| Electrolyte | R2 (0, 1/2) (CPU) | +0.0156 | 1.6316 | 3.0647 | archive |
| Electrolyte | G3 (1/12, 3/4) | +0.0166 | 1.6318 | 3.0560 | new |
| Electrolyte | G2 (1/4, 1/2) | +0.1074 | 1.6234 | 2.9881 | new |

**Outcome.** The geometric rule's set (R1, G2, G3) would select:
- cathode **G3**, W_adh 3.627 / W_sep 5.163 J/m². That differs from the frozen reference (3.617 / 5.168)
  by +0.010 / −0.004 J/m², well below the 0.1 J/m² reporting tolerance. G3 is also the lowest of all
  five sampled cathode registries.
- electrolyte **R1** (unchanged).

Across all sampled registries, W_adh spans 3.597–3.627 (cathode) and 1.623–1.633 J/m² (electrolyte).
The LiNbF6 reference values are therefore insensitive to how the registry set was chosen, within
this coarse sample. The relaxed ordering again differs from the unrelaxed one. This is a finite
registry sample, not a global search; polar-model limitations are unchanged.

Evidence: per-run results, records, scans, separation, structures and FIRE logs in this directory;
`comparison.json`; `sacct.txt`; filtered job logs. Cost: see `comparison.json` (calls) and `sacct.txt`.
