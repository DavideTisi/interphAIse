# Pilot interpretation (reviewed, 22 October 2026)

Read this beside [report_live/report.md](report_live/report.md), which is generated from `state.json`. The original prompts, responses, the uncharged size stop and the hashed summary-only amendment are kept unchanged in `state.json`. This pilot is not rewritten or rerun.

- **Forecasts:**
  - LiTaF₆: both W_adh ranges supported (cathode 3.34 in [3.2, 3.9]; electrolyte 1.58 in [1.4, 1.9]).
  - LiCaAlF₆: both missed (cathode 1.43 against [3.0, 3.8]; electrolyte 0.74 against [1.4, 1.9]).
  - The weaker contact (electrolyte) was correct for both.
- **Order:** the candidate order was unchanged by feedback. LiCaAlF₆ was already next on the choose-2 shortlist.
- **Correction:** `min_W_adh_J_m2` in the prompt is the weaker of the two selected contact values. It is not the minimum across registries. Haiku's suspicion in the summary came from misreading that definition; the LiCaAlF₆ value is correct.
  - A rename to `weaker_contact_W_adh_J_m2` is kept for a future protocol version.
- **Final ranking:** LiNbF₆ > LiTaF₆ > LiCaAlF₆ > LiF. This is the model's assessment, not a measured result.
  - LiF was not physically evaluated.
  - The small LiNbF₆–LiTaF₆ difference does not establish a robust winner.
- **Scope:** one reference plus two adaptive choices cannot show search superiority. Usage was 5 of 10 HTTP attempts, about USD 0.006 at list price (not billed).
