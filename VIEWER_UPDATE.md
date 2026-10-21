# Structure viewer update

21 October 2026 · branch `davide` · science archive through `d0bd1f3`.

The viewer now includes the expanded materials, all saved bulk references and the
nested interface studies. It is a single self-contained HTML file, using the existing
canvas renderer without a CDN, network request, external viewer library or API key.
No new MP, LLM, MLIP or cluster calculation was launched for this update.

## Open, regenerate and share

Generated output: `runs/structure_viewer.html` (about 13.3 MB). The existing local
server displays it at <http://127.0.0.1:8876/structure_viewer.html>. Refresh a previously
opened tab after rebuilding.

```bash
.venv/bin/python scripts/build_structure_viewer.py
```

Send **the HTML file itself** to Adem. Its scripts, geometry catalogue, coordinates,
metadata and XYZ download content are embedded. The recipient can open it in a
normal browser; the `127.0.0.1` URL points to the sender's own computer and is not a
share link. No adjacent data folder or server is required by the HTML. An optional
local server, started from the repository root, is:

```bash
python3 -m http.server 8876 --bind 127.0.0.1 --directory runs
```

Do not run that command if the existing server already owns port 8876. The generated
HTML and verification image are ignored build outputs; committed builder/template
and data are sufficient to regenerate them after a pull. No commit or push was made
by the viewer agent.

Optional arguments: repeat `--pool PATH` to override the candidate pools, repeat
`--pilot DIRECTORY` to restrict contact directories, `--structure PATH` for custom
ASE-readable geometries, and `--output PATH` for another export destination.
Bulk references and saved endpoint structures remain included when available.

## Coverage in this export

| Collection | Geometries | Meaning |
|---|---:|---|
| Coating candidates | 141 | 141 distinct MP IDs, 100 formulas; original 50 are a subset |
| Battery endpoints | 4 | LiCoO2, Li6PS5Cl, Li3InCl6 and Li7La3Zr2O12 |
| Bulk references | 40 | Initial/final geometries from symmetric relaxation, released-symmetry checks and multistart seeds |
| Interfaces and separated slabs | 93 | 20 calculated runs × 4 states, plus 13 build-only inputs |
| **Total** | **278** | **Two contact pairs, not 20 different coating chemistries** |

The 20 calculated runs include both historical pilots, six original constraint runs,
five electrolyte thickness/constraint runs, three cathode coating-thickness runs and
four newly committed remaining-thickness runs. The catalogue contains 33 contact
cases when the build-only directories are counted separately.

Candidates are deduplicated by **MP ID and geometry**, never formula. Identical
structures repeated in the original and expanded pools retain both source paths and
hashes. A polymorph or changed structure snapshot stays separate. Environment
membership comes from the three frozen benchmark tables; no benchmark scores,
acceptability labels or internal outcome fields are exported. A material appearing
in all three environments is one catalogue item with three memberships.

Original MP endpoints retain their recorded numeric IDs; bulk-study references retain
the alphabetic IDs recorded by that study. They are labelled independently rather
than silently treating every same-formula structure as the same phase. Seed 0 is
exported from the released-symmetry reference once, with the selected-reference label.
The unconverged LiZr2(PO4)3 seed 5 remains inspectable and explicitly excluded from
reference selection.

There are **no saved chloride or LLZO atomistic interfaces**. Filtering to these
environments shows their bulk endpoints and candidate/reference memberships, with a
visible explanation of the missing contact calculation. `vacuum_v1` contains
single-point JSON evidence without new saved geometries, so it does not create
invented structures or duplicate existing structures with new cells.

## Navigation and results

- Search formulas, MP IDs, contact names or seeds. Combine environment, collection,
  study, state and contact filters. State separates original MP, initial, relaxed,
  separated coating and separated substrate records.
- **Current contacts** selects the explicitly chosen protocol cases, without sorting
  by adhesion. The present pair is the 696-atom cathode and 880-atom electrolyte.
- **Initial ↔ relaxed** pairs states from the exact same run. **Compare thickness**
  selects the thinnest/thickest available relaxed members of the same study, contact,
  seed and frozen-depth setting. For the new electrolyte study, that is 3 vs 4 coating
  layers; the earlier 2-layer baseline remains available in the other study.
- Rotation, shared camera/scale, element/coating/substrate/fixed coloring, a/b wrapping,
  a/b replication, cell display, XYZ download and PNG export are retained.
- Captions display atom counts, layer counts, seeds, fixed count, facets, strain,
  convergence/free-force status, polarity warnings and source hashes. Expand
  **Geometry, constraints and source files** for the full provenance.

Only a numerically valid, completed **relaxed joined contact** receives energy cards:

| Current setting | Atoms | Fixed | W_adh (J/m²) | W_sep (J/m²) |
|---|---:|---:|---:|---:|
| Cathode: 2 LiCoO2 + 4 LiNbF6 layers | 696 | 104 | 3.600135993716124 | 5.127539830521539 |
| Electrolyte: 4 Li6PS5Cl + 4 LiNbF6 layers, seed 0 | 880 | 38 | 1.6329358066032293 | 2.9669046670178845 |

The earlier 544-atom electrolyte remains a thinner-coating baseline at
1.5317258429078906 / 2.8578983052814912 J/m², without a current-setting badge.
The two-layer MP-lattice pilots are grouped as historical; their changed lattices,
facets and cuts prevent an implicit comparison as a coating ranking.

W_adh uses independently relaxed separated slabs. W_sep uses rigid fragments of the
relaxed joined geometry. A build-only or initial record is not assigned a relaxed
energy, and a separated slab does not receive a contact adhesion card. Partial or
invalid runs can be inspected but do not publish an adhesion value.

## Data checks and verification

The builder associates a result with its own `initial.extxyz`, exact selected metadata
and state-local relaxation records. Build settings are joined only after matching
selection, ordered elements, cell, interface labels and slab-internal coordinates
(modulo in-plane wrapping and rigid registry translations). It never associates runs
by formula or folder-name similarity. Rigid separation metadata must agree on model
hash, area, joined energy, relaxed slab energies and W_adh.

If a final geometry omits labels, the builder recovers them from the exact run's
initial ordering. The separated substrate gets its own local fixed indices, not the
joined-system indices. Conflicting labels, masks, atom orders or cells are rejected
and reported. Initial-state masks are explicitly described as the planned masks
recorded by the relaxation. All downloaded coordinates remain the saved coordinates;
display wrapping/replication is not written back.

**Automated:** `.venv/bin/pytest -q tests/test_structure_viewer.py` → **11 passed**.
The checks cover existing pilot round trips, multi-contact identity, expanded-pool
membership and polymorph retention, nested energies/layers, incomplete runs, metadata
recovery/rejection, changed snapshots, bulk reference selection, all 278 geometry and
mask round trips, HTML delimiter escaping, and the new 880-atom shortcut. The suite
emits the existing ASE/NumPy array-shape deprecation warning. `git diff --check` is
clean. No full scientific suite was rerun for this viewer-only update.

**Browser:** rendered and visually inspected the complete page at the existing
localhost URL. Verified LLZO/chloride filtering and missing-interface notice,
four distinct LiZr2(PO4)3 polymorphs, empty search and reset, initial/relaxed pairing,
both thickness comparisons, separated-slab state with no contact energy cards,
fixed/group coloring, substrate-only filtering, 2×2 replication and top/side views.
An empty-search reset bug discovered during this check was fixed and retested. No
new browser errors were present in the final verification pass. The actual XYZ
download was read back with ASE: cathode 696 atoms, original coordinates and 104 fixed
sites were preserved. PNG export remains implemented but its download was not
separately exercised. Direct `file://` launch was not verified in the in-app browser;
the inspected HTML has no network dependencies. Preview:
`runs/structure_viewer_updated_preview.jpg`.

## Scientific scope and next work

Both contacts remain formally polar and provisional. The viewer does not validate
chemical accuracy, transport, experiment or long-range electrostatics. Constraint
brackets were tested at earlier two-coating-layer geometries, not repeated at the
current ones. The vacuum sweep covered the 696-atom cathode and **544-atom** electrolyte;
it is a finite-range periodic-image check, not a polar-electrostatics treatment or a
separate sweep for the 880-atom electrolyte. Registry competitors and seed-4 results
remain pending as of this checkpoint. The seed-4 contact input is visible as build-only.

Rebuild after completed new archives arrive. Recursive discovery includes new complete
runs without changing scientific inputs; current-contact shortcuts are explicit code
settings and should change only when the documented protocol changes. A new study
schema may require a small adapter before its metadata can be interpreted. Browser
navigation uses the existing projected canvas, with no inferred bonds, trajectories,
supercell relaxation or physical interaction implied.

Files changed by this work: `scripts/build_structure_viewer.py`,
`scripts/viewer/template.html`, `tests/test_structure_viewer.py`, this report, and a
narrow appended checkpoint in `DEVELOPMENT_LOG.md`. Parent-owned REPORT/protocol
edits and Claude's science inputs were untouched.
