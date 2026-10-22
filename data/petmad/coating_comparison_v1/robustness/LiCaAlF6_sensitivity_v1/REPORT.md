# LiCaAlF6 declared sensitivity checks (robustness; not decision feedback)

22 October 2026. The declared sensitivity slots of the frozen manifest (`99ef2dc1…`) for LiCaAlF6,
which was selected at choose-3. Jobs 11017275–11017278 ran on the RTX 3090 at `--nice=50` from code
`0ad7a53`, after the LiCaAlF6 primary package was frozen. All 12 relaxations converged and pass the F2
gate; works were recomputed from source energies. **These values were not part of any decision bundle**
and stay outside `index.json` until the pilot's final summary call is complete.

| Contact | Check | Atoms | Fixed | W_adh (J/m²) | ΔW_adh | W_sep (J/m²) | ΔW_sep |
|---|---|---:|---:|---:|---:|---:|---:|
| Cathode | primary R2 (1/4,1/6), reference | 720 | 120 | 1.4267 | — | 4.3218 | — |
| Cathode | thickness +1 coating layer | 756 | 120 | 1.4332 | +0.007 | 4.2799 | −0.042 |
| Cathode | fixed depth 13.385 Å | 720 | 180 | 1.4258 | −0.001 | 4.3234 | +0.002 |
| Cathode | 3 LiCoO2 layers | 900 | 120 | 1.4354 | +0.009 | 4.2966 | −0.025 |
| Electrolyte | primary R3 (0,1/2), reference | 1,212 | 57 | 0.7436 | — | 1.4903 | — |
| Electrolyte | fixed depth 6.515204 Å | 1,212 | 102 | 0.7578 | +0.014 | 1.5000 | +0.010 |
| Electrolyte | thickness +1 coating layer | — | — | — | **not_run_resource_limit** (1,302 atoms > 1,250) | — | — |
| Electrolyte | seed-4 Li6PS5Cl | — | — | — | **not_run_no_admissible_construction** (300 and 600 Å²) | — | — |

Every completed check stays within 0.015 J/m² in W_adh and 0.05 J/m² in W_sep of the selected primary
run. The two unavailable electrolyte slots were declared unavailable in the manifest before any LiCaAlF6
energy existed; the electrolyte thickness and bulk-reference sensitivities therefore stay
**unquantified** for this coating. The primary electrolyte registry spread (0.524–0.744 J/m²) is the
largest documented sensitivity for LiCaAlF6. The broken Al–F coordination at the (100) cut and the
large film relaxation on separation (about 2.7 J/m² on the cathode side) are surface caveats. Both
contacts remain formally polar.

Evidence: per-run results, records, scans, separation, structures and FIRE logs; `summary.json`;
`sacct.txt`.
