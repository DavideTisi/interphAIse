# Validation record: consolidated presentation

22 October 2026. Final revision v2.

- PowerPoint SHA-256: `fe867ae649a5d26a8e2c289d9fec44c0c79b5d3fcf13db10b631834ca8ce7adb` (561,524 bytes).
- PDF SHA-256: `ae7a36f0eb8c1b8e22a51e870dc9a3848c04d3523598ca6412d44c380e6948ce` (5,836,540 bytes).
- Evidence JSON SHA-256: `1a56555e6730a52461ffe51e3dd489f2e3c0c36532c1d0d1db9dfd3b1316f7a3`.
- 24 slides: 18 main plus six backups. 24 speaker-note parts.
- 16 native editable tables, five native editable charts with five embedded
  Excel data workbooks. Chart caches independently match the evidence JSON
  to 1e-9 after intentional ten-significant-digit workbook rounding.
- Package integrity: pass, zero findings. Geometry/font validation: pass,
  zero blocking findings. Native chart portability/data checks: pass.
  The finalized file also passes Artifact Tool reimport.
- The geometry heuristic emitted four nonblocking warnings on slides 7, 11,
  17 and 20. The flagged tables/text frames were checked in the actual final
  renders; text is legible and does not overlap. First-pass crowded layouts
  were repaired, and cumulative chart smoothing was disabled.
- Every finalized PowerPoint slide was rendered at 1280x720 and visually
  inspected individually. Every PDF page was rendered and visually inspected.
- PDF is a static visual companion made from 2560x1440 final slide renders,
  packaged losslessly with ReportLab. All 24 embedded page images match their
  source-render RGB pixels exactly. Edit the PowerPoint, not the PDF.
- Direct PDF export was unavailable due to a runtime font-module error.
  LibreOffice substituted fonts, so that intermediate was rejected. Neither
  intermediate is a delivered artifact. No bundled dependency was modified.
- Evidence extraction was rerun from immutable Git commits and produced
  byte-identical JSON. Counts, cumulative endpoints, all six Holm comparisons,
  source index hash and minimum-joined-energy physical selections were checked.
- This validates the package, data transcription and visual presentation.
  Microsoft PowerPoint was not used for an application-level opening check.
  Scientific evidence and its limits are in
  [the synthesis](../../docs/RESULTS_SYNTHESIS_2026-10-22.md).

No new live LLM, MLIP or cluster work was performed.
