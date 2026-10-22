# DeepSeek repeat of the three-environment study: pre-registration

22 October 2026. Drafted by Adem, following Davide's design. Written after the smoke batch and **before any production run**. Production starts only after Davide reviews the smoke cost (AGENTS.md exception).

## 1. Question

Do the Haiku findings persist with a different LLM?
- Does correctly attributed feedback help both models?
- Is the LLZO failure (random 24/30 against iterative 12/30 for Haiku) specific to Haiku's chemical preferences, or shared by DeepSeek?
- Does any advantage come from stronger initial knowledge or from better use of feedback? The upfront and shuffled arms separate these.

This compares **model configurations** (model, provider, precision, reasoning setting), not model names.

## 2. Frozen, identical to the Haiku study ([ENVIRONMENT_PROTOCOL.md](ENVIRONMENT_PROTOCOL.md))

- **Pool, objective and tables:**
  - pool `data/exploration/environment_expansion_v1/pool.json`;
  - the three frozen tables `data/benchmarks/environment_v1/lco_{lpscl,lic,llzo}_4v.json`, with the same hashes.
- **Prompt:** `v3-2026-10-21c-charged-ids`, unchanged.
- **Arms:** upfront, sequential, iterative and shuffled. 30 runs each, seeds 200–229, budget 10.
- **Charging:** invalid, repeated and failed queries are charged.
- **Random baseline:** reused from the Haiku archive, not rerun.
- **Evaluation:** the same cached evaluator. No new materials calculations.
- **Volume:** 360 LLM runs, about 2,790 calls before retries.

## 3. DeepSeek configuration (fixed after the smoke batch)

| Setting | Value |
|---|---|
| Model | `deepseek/deepseek-v3.2` via OpenRouter (Adem's own key) |
| Provider | `siliconflow/fp8`, pinned, fallbacks disabled, `require_parameters` |
| Reasoning | on, capped at `reasoning.max_tokens = 3072` |
| Output cap | 4,096 tokens in total (Haiku's 4,096 also included its thinking) |
| Temperature | 1.0 |
| Retries | the same client policy as Haiku (3 HTTP attempts for 429/5xx); format failures are charged |

**Why this provider:** OpenRouter offers about 12 providers for this model. In a test on 22 October, GMICloud ignored both the reasoning cap and the 4,096 output cap (calls used 1k–34k reasoning tokens). AtlasCloud enforced only the total cap. SiliconFlow enforced the reasoning cap exactly. An uncapped run is a different configuration from Haiku's, so it is archived only as a smoke reference.

## 4. Analysis, declared before production

- **Primary, per environment, DeepSeek alone:**
  - iterative against sequential, and iterative against shuffled;
  - paired by seed, exact McNemar;
  - Holm correction over the 6 tests at α = 0.05. This mirrors the Haiku family and is a separate family.
- **Cross-model, descriptive only, with no significance claim:**
  - for each environment and arm: success rate by query 10, DeepSeek against Haiku, with Wilson intervals;
  - the feedback benefit for each model: iterative minus sequential, and iterative minus shuffled.
- **LLZO:**
  - report DeepSeek iterative and upfront against the reused random baseline (24/30);
  - report fluoride fraction and pick concentration as for Haiku;
  - apply the same chemistry-audit caveat (SYNC_ADEM_10).
- **Secondary:** as for Haiku. That covers first-acceptable query index, best-bin rate, the median best bin against the exact random curve, and the fluoride fraction.
- **Usage:**
  - input, output and reasoning tokens; latency; retries; valid-response rate;
  - the cost OpenRouter reports for each call. This is what the account was charged, not a list-price estimate.
- **Not done:**
  - pooling DeepSeek with Haiku runs, or dropping an environment after seeing results;
  - changing thresholds or settings mid-run;
  - extending or rerunning arms because of their outcomes;
  - any replacement of a crashed run needs a recorded technical reason, as in the Haiku protocol.

## 5. Smoke batch (excluded from results)

Archived in `data/experiments/deepseek_v1/smoke/`. Per environment, seed 999: iterative and upfront at budget 10, sequential and shuffled at budget 3. That is 51 calls per configuration.

| | Capped, SiliconFlow (chosen) | Uncapped, GMICloud (reference) |
|---|---|---|
| Valid responses / retries | 51/51, 0 | 51/51, 0 |
| Output tokens per call (median) | 2,346 (6 calls reached the 3,072 reasoning cap; none truncated) | ~9,300 |
| Latency per call | median 171 s, max 421 s | median 161 s, max 578 s |
| Ten-query trajectory | 33–36 min | 18–45 min |
| Cost (charged, as reported by OpenRouter) | USD 0.156 (0.0031 per call) | USD 0.224 |

Provider and cap tests cost about USD 0.08 more. 20 and 60 parallel SiliconFlow calls all succeeded, with no 429s.

**Projection:** production costs about **USD 9** (range 8–11). Wall time is about **2.5 h** with 60 calls in flight (20 workers per environment, three environments in parallel); the floor is one 35-minute trajectory.

The smoke batch ran from working-tree code on top of `1f7bf11`, with hashes in each `experiment.json`. Production runs from the committed version. Between them, the runner's parallel-run limit was raised from 4 to 64 and the per-call client is unchanged.

## 6. Production command (after approval)

```bash
for env in lpscl lic llzo; do
  python scripts/run_discovery_experiment.py --model deepseek/deepseek-v3.2 --provider siliconflow/fp8 \
    --reasoning-max-tokens 3072 --arms upfront sequential iterative shuffled --repeats 30 --start-seed 200 \
    --budget 10 --temperature 1.0 --max-tokens 4096 --workers 20 \
    --pool data/exploration/environment_expansion_v1/pool.json \
    --benchmark data/benchmarks/environment_v1/lco_${env}_4v.json --out runs/deepseek_v1/${env} &
done; wait
```

Archive to `data/experiments/deepseek_v1/{lpscl,lic,llzo}`. The Haiku archive `data/experiments/environment_v1/` stays unchanged.

## Sign-off

- [x] Adem: configuration fixed and smoke batch measured (this document).
- [ ] Davide: smoke cost reviewed and production approved.
