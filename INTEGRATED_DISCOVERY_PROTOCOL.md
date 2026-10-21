# Integrated discovery follow-up — fixed before production

21 October 2026, branch davide. This is a prospective follow-up after reading Adem's
initial ten-repeat results; it is not the original preregistration. The frozen v3
pool/objective/answer table are unchanged. Do not pool this batch with the earlier
runs using uncharged invalid-ID retries or different output limits.

## Scope and settings

- Thirty runs for each of random, upfront, sequential-no-results and iterative.
- Seeds 100–129, paired candidate display order across arms; seeds control list
  order, not provider sampling. New independent query boundary and client per run.
- Budget 10 evaluations. Every submitted candidate_id costs budget, including
  invalid/non-string/repeated IDs and evaluator failures. Malformed messages or
  missing schema fields have at most three proposal attempts, with their API cost
  logged; they do not represent an identifiable submitted query. A schema-valid
  upfront list is executed as supplied, charging duplicates and unknown IDs.
- Direct Anthropic claude-haiku-5-5 only, temperature 1.0, max output 4096 per call.
  Prompt v3-2026-10-21c-charged-ids. Up to three independent runs concurrently;
  no changes to prompts/settings in response to interim performance.
- Primary target: acceptable candidate found by evaluation 10. Main comparison:
  iterative versus sequential without outcomes. Report counts, rates, 95% Wilson
  intervals and paired discordant outcomes; a small or uncertain difference remains
  inconclusive. Upfront is the prior-selection comparison, with interaction/call
  count differences disclosed.
- Secondary: success curves at queries 1–10 and reaching the best eligible bin.
  Report exact uniform-random baseline and the review-motivated post-hoc fixed
  fluoride-first baseline. The heuristic was selected after reviewing the table.
- Keep all completed, failed and short runs. Success already achieved in a short
  run persists in its cumulative curve. Missing files or unfinished statuses are
  an analysis error, not grounds for a smaller denominator.
- Record prompts, responses, usage including metadata available for failed calls,
  source commit, workflow file hashes and benchmark hashes. Do not log credentials
  or HTTP headers. HTTP-level retry costs without provider usage remain unknown.
- Pilot seed 90, budget 3, one run per LLM arm is an integration test only and is
  excluded. Separate offline random checks are also excluded from production.
- Shuffled feedback is a future additional control; it is not silently substituted
  for any arm. No nonfluoride acceptance condition is run: it has zero successes.

## Readiness and reporting

The branch merge was clean. Offline tests passed (92 existing/integration tests,
then four added analysis-validation tests). The live integration test must finish
before production starts. If authentication/infrastructure fails, preserve all
attempts and report the failure rather than changing providers/models or counting
missing outcomes as chemical evidence. Any resumption or replacement batch requires
an explicit recorded rule and a fresh manifest; do not stop on statistical significance.

This experiment evaluates search on cached thermodynamic outcomes. It does not
establish real compute savings, coating synthesis feasibility, lithium transport,
or physically converged interfacial adhesion. The LLM's proposed chemistry is a
hypothesis; traces alone are not proof of valid reasoning.
