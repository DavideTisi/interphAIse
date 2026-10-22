# LiTaF6 declared sensitivity checks (robustness; not decision feedback)

22 October 2026. These are the six declared sensitivity slots of the frozen manifest (`99ef2dc1…`) for
LiTaF6, which was selected at choose-2. Jobs 11017102–11017108 ran on the RTX 3090 at `--nice=50` from
code `d5ab477`, after the LiTaF6 primary package was frozen. All 18 relaxations converged and pass the
F2 gate; works were recomputed from source energies. **These values were not part of the choose-3
decision bundle** and stay outside `index.json` until the pilot's final summary call is complete.

| Contact | Check | Atoms | Fixed | W_adh (J/m²) | ΔW_adh | W_sep (J/m²) | ΔW_sep |
|---|---|---:|---:|---:|---:|---:|---:|
| Cathode | primary R1 (0,0), reference | 696 | 104 | 3.3387 | — | 4.7277 | — |
| Cathode | thickness +1 coating layer | 792 | 104 | 3.3410 | +0.002 | 4.7288 | +0.001 |
| Cathode | fixed depth 13.385 Å | 696 | 156 | 3.3337 | −0.005 | 4.7244 | −0.003 |
| Cathode | 3 LiCoO2 layers | 852 | 104 | 3.3391 | +0.000 | 4.7266 | −0.001 |
| Electrolyte | primary R2 (1/4,1/2), reference | 880 | 38 | 1.5774 | — | 2.9106 | — |
| Electrolyte | thickness +1 coating layer | 1,048 | 38 | 1.5721 | −0.005 | 2.9129 | +0.002 |
| Electrolyte | fixed depth 6.515204 Å | 880 | 68 | 1.6015 | +0.024 | 2.9188 | +0.008 |
| Electrolyte | seed-4 Li6PS5Cl, (0,0) | 880 | 36 | 1.4637 | **−0.114** | 2.7066 | **−0.204** |

Δ values are relative to the selected primary registry. Thickness, constraint and cathode-substrate
changes stay within 0.025 J/m². The seed-4 electrolyte case exceeds the 0.1 J/m² reporting tolerance,
as it did for LiNbF6 (−0.12). That case combines a different bulk Li/Cl arrangement, a different
matched cell and supercell basis (172.9 Å²), a different fixed count and fractional registry (0,0),
which is not the same physical alignment as the seed-0 R2. It is a combined construction sensitivity,
not an isolated disorder effect or a statistical error bar. Both contacts remain formally polar.

Evidence: per-run results, records, scans, separation, structures and FIRE logs; `summary.json`;
`sacct.txt`.
