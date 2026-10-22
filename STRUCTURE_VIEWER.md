# Structure and interface viewer

Build the current catalogue from the repository root:

```bash
python scripts/build_structure_viewer.py
```

Open or share `runs/structure_viewer.html`. This self-contained HTML works offline
without credentials, external JavaScript or a server. The final catalogue has
460 saved geometries and 141 distinct Materials Project candidate IDs, including
polymorphs. It contains saved battery endpoints, bulk references, interface
builds, relaxed contacts and separated slabs. Chloride and LLZO have bulk
structures only; no atomistic contact energy was calculated for those environments.

## Inspect the final comparison

The three coating buttons load the selected cathode and electrolyte contacts
for LiNbF6, LiTaF6 or LiCaAlF6 with a shared camera and length scale. Their
selected-primary W_adh values are 3.617 / 1.633, 3.339 / 1.577 and
1.427 / 0.744 J/m², respectively. Selection follows the validated final index
and lowest relaxed joined energy, not the maximum adhesion value.

Selected primaries are labelled as evidence available to the live pilot.
Sensitivity and consistency runs are labelled **Robustness only**, withheld
from the live decisions. LiF inputs may be inspected but have no computed
interface energy. LiCaAlF6 electrolyte thickness and bulk-structure sensitivity
remain unquantified. The small LiNbF6–LiTaF6 gap is below the documented
construction sensitivities; this is not a robust materials ranking.

Use **Evidence comparison** for the original registry and bulk-reference pairs.
Search, environment, collection, study, state and contact filters select other
geometries. Initial builds and separated slabs do not inherit contact energies.
Historical pilots remain identified separately and are not comparable with the
final construction protocol.

## Controls and downloads

- Drag to rotate, scroll to zoom, or use side, top, oblique and Fit presets.
- Colour by element, coating/substrate membership or fixed-atom constraints.
- Show either component, the cell and periodic copies in a and b.
- Wrap changes only the display. XYZ downloads preserve saved coordinates,
  cell, species, verified atom labels and state-local fixed masks.
- Each panel is independently centred; a side-by-side pair is not a displacement
  map. Sphere sizes are illustrative and chemical bonds are not inferred.
- Source paths and hashes are available in each geometry's details.

```bash
python scripts/build_structure_viewer.py --structure path/to/structure.cif \
  --output runs/custom_viewer.html
python -m pytest tests/test_structure_viewer.py -q
```

`--pool` overrides the pools, and repeated `--pilot` options restrict the contact
folders. Default discovery is recursive. The final campaign additionally checks
its manifest and saved source evidence; missing or inconsistent selected contact
geometries stop the export rather than silently receiving another run's energy.

All interface values remain provisional results for formally polar models.
Finite-range vacuum isolation does not establish electrostatic accuracy, and no
lithium-transport conclusion follows. See [the final synthesis](RESULTS_SYNTHESIS_2026-10-22.md)
and [offline reproduction](REPRODUCE.md).
