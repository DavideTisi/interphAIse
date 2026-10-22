# Hackathon submission package

Checked on 22 October 2026 against the
[official campaign page](https://scientificintelligence.org/campaigns/osi-hackathon-2026).
The public page was read in a browser; the general web reader could not access it.

## Requirements and release status

Deadline: **23 October 2026 at 02:00 CEST in Copenhagen**, equivalent to
22 October at 19:00 CDT. The official submission checklist calls for a public
social-media post, a write-up, a publicly readable repository with a README, and
confirmation of the event rules. A video is optional; if included in the post,
it must be no longer than four minutes. The interactive viewer is supplementary.

| Item | Current deliverable or remaining action |
|---|---|
| Write-up | The [detailed synthesis](RESULTS_SYNTHESIS_2026-10-22.md) includes both LLM configurations and the completed physical pilot. The [short overview](presentations/source/interphaise_overview_2026-10-22.txt) and [illustrated Word document](presentations/results_2026-10-22/interphaise_project_overview_2026-10-22.docx) predate DeepSeek and need that update before use as a complete final summary. |
| Public repository | **Complete:** [DavideTisi/interphAIse](https://github.com/DavideTisi/interphAIse), tested release on `main`. Davide explicitly authorized merging/publication; the visibility change and anonymous downloads are verified in [the release record](FINAL_INTEGRATION.md). |
| Public social post | Still required. No post has been published or authorized in this session. An updated draft with the public repository link is below. |
| Rules confirmation | A human must read and confirm the rules at submission. The campaign's separate “How the hackathon works” link returned 404 during this check, so that link did not establish any additional eligibility conditions. |
| Supporting demo | [Public six-interface viewer](https://davidetisi.github.io/interphAIse/) is verified without login; [offline download](https://davidetisi.github.io/interphAIse/interphaise-referee-viewer.zip) is also verified. |
| Slides | [Accessible checkpoint](presentations/nonexpert_2026-10-22/interphAIse_the_idea_and_LLM_results_2026-10-22_v4.pptx) and [detailed checkpoint](presentations/results_2026-10-22/interphAIse_results_synthesis_2026-10-22_v2.pptx) are public. The newer deck covering both configurations remains in progress in its separate chat. Slides support the write-up rather than replace it. |
| Optional video | Not recorded in this work. If useful, show the problem, controlled LLM results, one forecast success and one failure, then the viewer. Keep it under four minutes. |

## Fit to the judging criteria

The official page lists four equally presented criteria scored from 1 to 5:
potential for impact, innovativeness, novelty, and relevance to physical sciences
and mathematics. The following is our interpretation of how to present this
project, not a prediction of the judges' scores.

| Criterion | Evidence to emphasize | Boundary to keep explicit |
|---|---|---|
| Potential for impact | Battery-interface researchers could delegate candidate triage and prospective forecasts while retaining a computational audit trail. The sulfide controls show that useful numerical feedback changes outcomes. | No human-efficiency study, experimental coating improvement or general compute-saving result has been demonstrated. |
| Innovativeness | Connect thermodynamic screening, controlled feedback experiments and a live atomistic forecast–calculation–revision sequence. Show what the model predicted before the calculation. | LLM selection and coating screening are not individually new ideas. Explain the combination and its testability rather than calling the project unprecedented. |
| Novelty | The implemented contribution is reproducible tooling for testing chemistry priors against numerical evidence, plus the linked decision-time and later robustness archives. | Do not claim discovery of a new material or a first-of-its-kind capability without a wider literature comparison. The physical pilot's selection order stayed unchanged. |
| Scientific relevance | Coatings address reaction-driven degradation at solid-state battery interfaces. The project models both contacts and checks construction sensitivity. | Transport, cycling and polar electrostatics remain outside the demonstrated validation. |

The viewer is useful because judges can inspect what was actually simulated,
switch between the three coatings and see the two separately computed contacts.
It does not demonstrate LLM reasoning by itself. The discovery curves, controls
and archived forecasts carry that part of the argument.

## Suggested public post draft

We built interphAIse for the OSI Hackathon to test whether an LLM can guide the
search for solid-state battery coatings. Across 810 runs in three environments,
we compared Haiku and DeepSeek configurations with shared random baselines.
Correct feedback helped Haiku on sulfide. DeepSeek proposed useful LLZO
candidates upfront, but both iterative configurations remained below random
there. In a prospective Haiku atomistic pilot, LiTaF6 adhesion forecasts held
and LiCaAlF6 forecasts missed. We make scientific choices testable while keeping
the limitations of the LLM and physical models visible. These are computational
results, not experimentally validated battery coatings.

Explore the six computed interfaces: https://davidetisi.github.io/interphAIse/

Code, evidence and write-up: https://github.com/DavideTisi/interphAIse

This remains an unsent draft for the team to review and publish.

## Final sequence

1. **Complete:** integrated histories merged into `main`, 246 tests passed,
   repository public and anonymous links checked. The README links the write-up,
   reproduction command, completed slides and viewer. LiF remains uncomputed.
2. Finish and verify the newer presentation and short overview incorporating
   DeepSeek, then add them to the public repository.
3. Publish the team's chosen social post and copy its public permalink.
4. Complete the write-up and rules confirmation in the event form, add the public
   links, and submit before the deadline. No submission was made by this agent.
