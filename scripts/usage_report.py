"""Token usage and list-price cost of discovery experiments, per environment and arm.

    python scripts/usage_report.py runs/<smoke_env1> runs/<smoke_env2> ... [--json out.json]

Costs are ESTIMATES: logged `usage` x Anthropic public list prices for claude-haiku-5-5
(https://platform.claude.com/docs/en/about-claude/pricing, fetched 2026-10-21), global routing,
no batch discount. Billed amounts come only from the Anthropic Console. Thinking tokens are
included in `output_tokens`. Prompts over 100k tokens use the higher tier and are flagged.

Accounting terms: `calls` = proposal attempts (one per logical model call recorded in a run);
`retries` = format retries (attempts the runner rejected and re-asked); `http` = HTTP attempts and
`transport` = transport retries (429/5xx re-sends inside one call), known only for runs whose
metadata records `http_attempts`. Older archives did not record them: those calls are counted in
`http_unknown` and their HTTP totals are reported as unknown, never inferred.
"""
import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# USD per million tokens: (input, 5m cache write, 1h cache write, cache read, output)
PRICES = {"<=100k": (0.10, 0.125, 0.20, 0.01, 0.50), ">100k": (0.50, 0.625, 1.00, 0.05, 2.50)}


def call_cost(u):
    cache_write = u.get("cache_creation_input_tokens") or 0
    cache_read = u.get("cache_read_input_tokens") or 0
    prompt = (u.get("input_tokens") or 0) + cache_write + cache_read
    tier = ">100k" if prompt > 100_000 else "<=100k"
    p_in, p_w5, p_w1, p_read, p_out = PRICES[tier]
    split = u.get("cache_creation") or {}
    w1 = split.get("ephemeral_1h_input_tokens") or 0
    w5 = cache_write - w1
    usd = ((u.get("input_tokens") or 0) * p_in + w5 * p_w5 + w1 * p_w1 + cache_read * p_read
           + (u.get("output_tokens") or 0) * p_out) / 1e6
    return usd, tier


def environment(directory):
    exp = json.loads((directory / "experiment.json").read_text())
    path = Path(exp["benchmark"])
    path = path if path.is_absolute() else ROOT / path
    return json.loads(path.read_text())["endpoints"]["electrolyte"]["formula"]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("experiments", type=Path, nargs="+")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    rows = defaultdict(lambda: defaultdict(float))
    by_index = defaultdict(list)  # (arm, call index within run) -> prompt tokens
    for directory in args.experiments:
        env = environment(directory)
        for path in sorted(directory.glob("*_r*.json")):
            run = json.loads(path.read_text())
            r = rows[(env, run["strategy"])]
            r["runs"] += 1
            r["failed_runs"] += run["status"] != "complete"
            for i, a in enumerate(run["proposal_attempts"]):
                r["calls"] += 1
                r["retries"] += "error" in a
                meta = a.get("llm_metadata") or {}
                if "http_attempts" in meta:
                    r["http"] += meta["http_attempts"]
                    r["transport"] += meta.get("transport_retries", 0)
                else:
                    r["http_unknown"] += 1
                u = meta.get("usage")
                if not u:
                    r["missing_usage"] += 1
                    continue
                usd, tier = call_cost(u)
                r["usd"] += usd
                r["over_100k"] += tier == ">100k"
                for key in ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"):
                    r[key] += u.get(key) or 0
                r["thinking_tokens"] += (u.get("output_tokens_details") or {}).get("thinking_tokens") or 0
                prompt = sum(u.get(k) or 0 for k in ("input_tokens", "cache_creation_input_tokens",
                                                    "cache_read_input_tokens"))
                by_index[(run["strategy"], i)].append(prompt)

    cols = ("runs", "calls", "retries", "http", "transport", "http_unknown", "input_tokens", "output_tokens",
            "thinking_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "over_100k", "missing_usage")
    print(f"{'environment':<14}{'arm':<12}" + "".join(f"{c.split('_')[0][:9]:>10}" for c in cols) + f"{'USD':>9}")
    total = defaultdict(float)
    for (env, arm), r in sorted(rows.items()):
        print(f"{env:<14}{arm:<12}" + "".join(f"{int(r[c]):>10}" for c in cols) + f"{r['usd']:>9.4f}")
        for c in (*cols, "usd"):
            total[c] += r[c]
    print(f"{'TOTAL':<26}" + "".join(f"{int(total[c]):>10}" for c in cols) + f"{total['usd']:>9.4f}")
    print("(columns: runs, calls = proposal attempts, retries = format retries, http = HTTP attempts, transport ="
          " transport retries, http_unknown = calls without HTTP records, input, output incl. thinking, thinking,"
          " cache write, cache read, prompts >100k, calls without usage; USD = list-price estimate, not billed)")
    if total["http_unknown"]:
        print(f"HTTP attempts unknown for {int(total['http_unknown'])} of {int(total['calls'])} calls (not recorded"
              " in those archives); http/transport columns cover only calls with records.")

    print("\nmean prompt tokens by call index within a run (history growth):")
    for arm in sorted({a for a, _ in by_index}):
        idx = sorted(i for a, i in by_index if a == arm)
        print(f"  {arm:<12}" + " ".join(f"{i}:{statistics.mean(by_index[(arm, i)]):.0f}" for i in idx))

    if args.json:
        args.json.write_text(json.dumps({
            "pricing_source": "https://platform.claude.com/docs/en/about-claude/pricing (fetched 2026-10-21)",
            "prices_usd_per_mtok": PRICES, "cost_kind": "estimate at list price, not billed",
            "rows": [{"environment": e, "arm": a, **r} for (e, a), r in sorted(rows.items())],
            "total": total,
            "prompt_tokens_by_call_index": {f"{a}:{i}": statistics.mean(v) for (a, i), v in sorted(by_index.items())},
        }, indent=2) + "\n")


if __name__ == "__main__":
    main()
