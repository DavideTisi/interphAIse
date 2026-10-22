# Reviewed v9 presentations

Created on 22 October 2026 from the exact v8 decks selected by Davide. The
four-minute pitch has 8 slides. The fifteen-minute talk has 20 main slides and
4 technical backups. V8 and the separate authoring checkout are unchanged.

## What changed

- Define the menu early: 141 known Materials Project crystal structures,
  representing 100 compositions. Repeated searches may find the same material.
- Retain the acceptance rule and the meaning of a successful ten-query search.
- Put a numerical prospective miss in the pitch: Haiku's Ca–Al electrolyte
  forecast of 1.4–1.9 J/m² versus PET-MAD's 0.744 J/m².
- Replace the misleading “Only thermodynamics” caption on the physical result.
  Make polarity, untested transport, the small Nb–Ta gap and unquantified Ca–Al
  electrolyte sensitivities visible where appropriate.
- Make model-configuration and LLZO proxy limitations visible. Preserve all
  negative results and separate corrected feedback tests from descriptive
  cross-model and upfront comparisons.
- Close with the distinction between useful chemical knowledge and adaptation
  to feedback, next physical tests, and clickable public repository/viewer links.
- Replace local source paths in speaker notes with public repository URLs.
  The physical pilot remains explicitly Haiku-only.

## Verification

All 32 slides were rendered at 1920 × 1080 and individually inspected across
the draft/final review. Final PowerPoints passed package, layout, font,
native-chart/workbook and reimport checks. Two inherited heuristic warnings
on long-deck tables (slides 8 and 21) do not appear as clipping in the renders;
the original table XML is unchanged. This session did **not** inspect the decks
inside Microsoft PowerPoint. Rehearse there before recording to confirm native
rendering and timing on the presentation machine.

The edit workflow uses Artifact Tool for text, position and speaker-note changes.
A restricted transplant preserves all original native charts, embedded workbooks,
illustrations and tables. Each deck retains its three editable charts and the v8
value-axis placement fix. All 48 chart values were checked against the final
Haiku/DeepSeek environment summaries. Tables are byte-equivalent at XML element
level, retaining the previously reviewed values, forecasts and statistics.
All 19/20 unique public source paths in pitch/talk notes resolve in the repository.

Each PDF page embeds exactly the reviewed slide pixels. All 32 pages passed the
pixel-equality check; the modified physical slides were also rendered from the
PDFs and inspected. Both PDF closing slides have verified link annotations.
PDFs are static image companions; use the PowerPoints for editable content.

No API calls, new calculations, statistical reanalysis, or full scientific test
suite were needed. Source evidence and decision-time archives are unchanged.
The first verification attempt used the display label LLZO as a JSON key;
rerunning with the archive key Li7La3Zr2O12 passed all 48 checks.

## Hashes

| Artifact | SHA-256 |
|---|---|
| Pitch v9 PPTX | `d1ed3897010ced3fa996f5700754543cf775fb52776b10237b5cb84ffaef8d28` |
| Talk v9 PPTX | `ac113abad2f920f026d2c373b98481882c2a303168902cc3eff636027a70be5d` |
| Pitch v9 PDF | `085303af5051ba07f5d7beb70a9192cb626b05e57e8a0d492648b01e09962465` |
| Talk v9 PDF | `0e9bb05e18e3fb5249de52f6f772217dd4220b0f7db1f9b14b0136583c7956c9` |
| Pitch v8 source | `17a0ad836d84af269b1b358ea9ff578baecd0d35719064f78858090b667dcd85` |
| Talk v8 source | `dc50513addfc3421bde4baa81980c6349f5d54e44a3aa79b91b1e998d533315c` |

## Reproduction

The exact input files live in `presentations/source/reference_v8/`. Builders:

- `presentations/source/build_reviewed_v9_2026-10-22.mjs`
- `presentations/source/preserve_reviewed_deck_parts_v9.py`
- `presentations/source/package_reviewed_v9_pdfs_2026-10-22.py`
- `presentations/source/verify_reviewed_v9_2026-10-22.py`

Run from the repository root with the Codex bundled Node/Python runtime and
presentation skill. `CODEX_RUNTIME` and `PRESENTATION_SKILL` override the defaults.
The builder without `--finalize` writes private drafts/renders under
`runs/presentations_v9/`. Inspect those before finalizing. `--finalize` checks
and writes the final pair; the finalizer and PDF packager refuse to overwrite
existing outputs, so use a fresh revision path for a new publication.
Follow the artifact operation-marker workflow in the presentation/PDF skills.

```bash
# Private draft and renders
node presentations/source/build_reviewed_v9_2026-10-22.mjs
# After review, in a workspace with fresh output paths
node presentations/source/build_reviewed_v9_2026-10-22.mjs --finalize
python presentations/source/package_reviewed_v9_pdfs_2026-10-22.py
# Offline evidence verification of the committed decks
python presentations/source/verify_reviewed_v9_2026-10-22.py
```

The last command uses only Python's standard library. The packager uses
ReportLab, Pillow and pypdf; the preservation helper uses lxml. These authoring
utilities are separate from the project's scientific dependencies. Private
validation receipts, draft files and images stay in the ignored `runs/` tree.
