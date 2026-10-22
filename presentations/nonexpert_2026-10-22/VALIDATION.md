# Completed presentation checkpoint provenance

Copied for the public release without editing the slides. The four PPTX/PDF
hashes match the completed presentation chat's handoff. This records its
reported visual verification; publication did not perform a new visual review.
These versions cover Haiku and PET-MAD and predate the DeepSeek repeat.
The newer presentation remains in progress in its separate chat.

## 2026-10-22 — tools and candidate shortlist added to the accessible presentation

**Branch and purpose:** `davide`, HEAD `7bd5878` (uncommitted artifact work).
The user asked the interphAIse talk to explain the tools used and whether the
method ends with a few optimal candidates. Read the project instructions,
latest handoff, frozen sulfide score table, numerical synthesis and relevant
implementation. The older GOALS_AND_RESULTS physical-status section predates
the completed three-coating pilot, so current physical claims use the final
pilot review and pinned evidence instead.

**Delivered:** v4 PowerPoint and PDF under
`presentations/nonexpert_2026-10-22/`, 18 main slides plus six technical backups.
Slide 5 explains Haiku's choices, Materials Project reference data,
pymatgen/SciPy chemical screening, ASE/PET-MAD atomic calculations, the Python
workflow, and Niflheim/Slurm execution and human 3D inspection. Slide 16 explains
that the sulfide screen accepts four structures representing three formulas:
LiNbF6, LiCaAlF6 and two LiTaF6 polymorphs. The evaluated Nb/Ta pair is suggested
for further testing, while Ca–Al has weaker calculated adhesion. The slide and
notes explicitly avoid a proven-optimum claim. The four IDs, exact penalties,
best-bin distinction and environment-specific limitations are preserved in
notes. The LLM selected known materials from a menu; it did not invent the
formulas or independently produce the entire precomputed pool shortlist.

Imported v3 with Artifact Tool and added two native tables. All 22 existing
slides retain their visible content except page numbers. Notes now point to
the renumbered backups. The three unchanged charts and their original workbook
parts are preserved byte for byte. REPORT and the presentation README point
to v4. Kept v3, earlier decks, the unrelated root README edit and the open
PowerPoint lock file. No branch merge, commit or push occurred.

**Verification actually performed:** Exported 24 slides/notes, 11 native tables,
three native charts and three embedded workbooks. Package, font, workbook and
reimport checks pass. The existing three plotted datasets match pinned JSON
within 1e-8. Verified forecast ranges, the four accepted IDs and the new
shortlist values. A first verification-script attempt hit a missing
`acceptable` key on a failed source row; corrected the checker to treat absent
flags as false, matching the builder, and the full check passed. This did not
change any scientific source or slide outcome.

Rendered all final slides, visually reviewed both new slides at full size and
scanned the whole deck. Every retained slide is pixel-identical to v3 outside
the page-number region. Three nonblocking layout heuristics concern the new
tools table's estimated height and the two inherited frame/table warnings;
actual renders fit without clipping or overlap. Native Microsoft PowerPoint
execution was not tested. The PDF contains 24 losslessly embedded slide images,
all exactly equal to the PPTX renders. Rendered all pages with Poppler and
visually checked the new pages; the layout is preserved. Documentation links
and whitespace were checked. No scientific test-suite rerun was needed.

**Reproduction and records:** Run
`presentations/source/add_tools_and_shortlist_2026-10-22.mjs` with bundled Node,
then `package_tools_shortlist_pdf_2026-10-22.py` and
`verify_tools_shortlist_2026-10-22.py` in the same directory with bundled Python.
The editor invokes `preserve_nonexpert_chart_packages_2026-10-22.py` before
finalization. Follow the skill marker workflow and use fresh output names.
Private inspection, shortlist extraction, renders and receipts live in
`presentations/.build/nonexpert_tools_shortlist/`.

PPTX SHA-256: `66f0d9011e0f290a3fd18677d658ecc610666acbaceb86022b725d14eac8180f`.
PDF SHA-256: `3f7775f7099a38b7468c63ca3622f966bb5a6ba54d80d3182d1487ab61b4d495`.
No live project LLM/API request, MLIP calculation, SSH/Slurm job, new image
request or collaborator message occurred. Next: present slides 1–18, use
19–24 for technical questions. Any stronger optimum or useful-coating claim
requires new evidence on physical reliability, transport and battery behavior.
