# Local structure and interface viewer

Build from the repository root:

```bash
.venv/bin/python scripts/build_structure_viewer.py
open runs/structure_viewer.html
```

The generated HTML is self-contained: no server, credentials, external JavaScript,
internet connection or calculations are required. It contains 50 frozen bulk
structures plus the initial interface, relaxed interface and both separated slabs
from each saved PET-MAD pilot. Currently there are 58 structures, covering both
LiCoO2 | LiNbF6 and Li6PS5Cl | LiNbF6. Share the HTML itself to share
the viewer. Generated output stays under ignored `runs/`; the generator and
template are versioned.

## Controls

- Use Contact to load the initial and relaxed states of either contact together.
- Use Compare contacts to show the relaxed cathode-side and electrolyte-side
  interfaces together (or the available geometry if a relaxed one is absent).

- Select each structure independently; formula and MP ID distinguish polymorphs.
- Compare initial and relaxed states with a shared orientation and Å-to-pixel scale.
  Each panel centres its geometry independently; this is not a displacement map.
- Drag to rotate; scroll to zoom; use side, top or oblique presets and Fit to reset zoom.
- Show the saved cell and translated 2×2 or 3×3 copies along lattice vectors a and b.
- Colour by element, coating/cathode membership or stored fixed-atom constraints.
  Filter coating or cathode atoms. Bulk structures have neither interface label;
  select All atoms when inspecting bulk candidates.
- Hover to see the original atom index (one-based), displayed coordinates in Å,
  membership, constraint flag and replica offset.
- Save PNG exports the selected canvas. Save XYZ exports the selected original
  geometry in extended XYZ format with its cell, not the replicated display.

The browser uses an orthographic sphere rendering with depth sorting. Sphere radii
are scaled for readability, not a depiction of occupied volume. No chemical bonds
are inferred. Wrap a/b (enabled by default) brings periodic in-plane coordinates into the cell
for display only. Disable it to inspect the stored unwrapped positions. Downloads
always preserve the original coordinates; wrapping is not an atomic relaxation. Fixed-atom colouring reads ASE FixAtoms constraints;
the initial pilot file does not contain the constraints later used in relaxation.
The browser is intended for these small structures, not large MD trajectories.

## Add new calculations

```bash
.venv/bin/python scripts/build_structure_viewer.py \
  --structure path/to/new_structure.extxyz \
  --structure path/to/bulk.cif \
  --output runs/updated_viewer.html
```

Additional structures use ASE format detection; for multi-frame files the final
frame is loaded. Use `--pilot path/to/pilot_directory` for another directory with
`initial.extxyz`, `interface/final.extxyz`, `film/final.extxyz` and/or
`substrate/final.extxyz`. Repeat `--pilot` to include multiple directories. By
default, all directories with `data/petmad/*/selected.json` are discovered; material
names come from their saved metadata. Only geometry files present are included. Use `--pool` to choose
another pool in the existing JSON structure schema. Rebuild after data changes.

## Scientific scope and verification

This is a geometry-inspection tool, not evidence that the pilot adhesion estimate
is converged or that a coating is viable. See `PETMAD_INTERFACE_PILOT.md` and
`EXPERIMENT_AMENDMENT.md` for the unresolved bulk/surface issues. The viewer does
not embed the frozen benchmark's outcome table.

Verified the original 54 geometry exports by re-reading them with ASE and checking species,
coordinates, cells and PBC. The relaxed interface contains 64 stored fixed atoms
and 32 coating atoms. The multi-contact test additionally verifies all four
electrolyte geometries against their source files and the two distinct contact labels. Browser checks covered desktop comparison, narrow layout,
bulk selection, layer filtering, replication and view presets; no JavaScript
errors were observed. The scientific data check is reproducible with:

```bash
.venv/bin/python -m pytest tests/test_structure_viewer.py -q
```
