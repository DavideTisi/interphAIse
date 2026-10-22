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
| Write-up | [Approved overview](presentations/source/interphaise_overview_2026-10-22.txt), [illustrated Word document](presentations/results_2026-10-22/interphaise_project_overview_2026-10-22.docx), and [detailed synthesis](RESULTS_SYNTHESIS_2026-10-22.md) are ready. Adapt to the submission form if necessary. |
| Public repository | The integrated branch is ready for joint review; the repository is still private. Davide explicitly chose to make it public himself after everything is merged. Check the final README/code links without signing in before submission. |
| Public social post | Still required. No post has been published or authorized in this session. A draft is below. Add the final public repository link. |
| Rules confirmation | A human must read and confirm the rules at submission. The campaign's separate “How the hackathon works” link returned 404 during this check, so that link did not establish any additional eligibility conditions. |
| Supporting demo | [Public six-interface viewer](https://davidetisi.github.io/interphAIse/) is verified without login; [offline download](https://davidetisi.github.io/interphAIse/interphaise-referee-viewer.zip) is also verified. |
| Slides | [Reviewed 24-slide deck](presentations/results_2026-10-22/interphAIse_results_synthesis_2026-10-22_v2.pptx) and [PDF](presentations/results_2026-10-22/interphAIse_results_synthesis_2026-10-22_v2.pdf) are supporting assets, not a substitute for the write-up. |
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
search for solid-state battery coatings. Across 450 controlled runs, numerical
feedback helped in the sulfide setting, but random search won in LLZO. In an
atomistic follow-up, the model's LiTaF6 adhesion forecasts held; its LiCaAlF6
forecasts missed. The result is a reproducible way to test scientific intuition,
with its failures visible—not a claim of an experimentally validated coating.

Explore the six computed interfaces: https://davidetisi.github.io/interphAIse/

Code, evidence and write-up: **add the repository link after the final merge and
public-visibility change**. No post should be sent with this placeholder.

## Final sequence

1. Jointly review and merge the integrated work into the submission branch/main.
2. Davide makes the repository public as requested, then verifies anonymous access.
3. Put the write-up, reproduction entry point, slides and viewer link near the top
   of the final README. Preserve evidence hashes and leave LiF uncomputed.
4. Publish the team's chosen social post and copy its public permalink.
5. Complete the write-up and rules confirmation in the event form, add the public
   links, and submit before the deadline. No submission was made by this agent.
