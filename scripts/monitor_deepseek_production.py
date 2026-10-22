"""Spending and cap guard for the DeepSeek production repeat (DEEPSEEK_PROTOCOL.md).

    python scripts/monitor_deepseek_production.py runs/deepseek_v1 --budget 12 --margin 1.0

Every --interval seconds:
- reads the key's cumulative OpenRouter usage, relative to the value at start. This covers every call,
  including retries;
- scans the run files for calls over the reasoning/output caps or served by another provider.
It stops the production processes (SIGTERM) when spend reaches budget - margin (the margin covers calls
in flight) or a cap/provider violation appears. One JSON line per check goes to <runs>/monitor.jsonl.
The key itself is never printed.
"""
import argparse
import glob
import json
import os
import subprocess
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
PATTERN = "run_discovery_experiment.py --model deepseek"


def key_usage():
    key = os.environ["MY_OPENROUTER_API_KEY"].strip()
    request = urllib.request.Request("https://openrouter.ai/api/v1/key", headers={"authorization": f"Bearer {key}"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)["data"]["usage"]


def scan(runs, reasoning_cap, output_cap, provider):
    calls, violations, recorded = 0, [], 0.0
    for path in glob.glob(f"{runs}/*/*_experiment/*_r*.json"):
        try:
            run = json.loads(Path(path).read_text())
        except ValueError:   # file being rewritten; picked up next round
            continue
        for i, attempt in enumerate(run.get("proposal_attempts", [])):
            meta = attempt.get("llm_metadata") or {}
            usage = meta.get("usage") or {}
            calls += 1
            recorded += usage.get("openrouter_cost_usd") or 0
            reasoning = (usage.get("output_tokens_details") or {}).get("thinking_tokens") or 0
            where = f"{Path(path).parent.parent.name}/{Path(path).name}#{i}"
            if reasoning > reasoning_cap or (usage.get("output_tokens") or 0) > output_cap:
                violations.append(f"{where}: reasoning {reasoning}, output {usage.get('output_tokens')}")
            if meta.get("provider_served") not in (None, provider):
                violations.append(f"{where}: served by {meta.get('provider_served')}")
    return calls, recorded, violations


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("runs", type=Path)
    p.add_argument("--budget", type=float, default=12.0)
    p.add_argument("--margin", type=float, default=1.0)
    p.add_argument("--interval", type=int, default=60)
    p.add_argument("--reasoning-cap", type=int, default=3072)
    p.add_argument("--output-cap", type=int, default=4096)
    p.add_argument("--provider", default="SiliconFlow")
    args = p.parse_args()
    load_dotenv(ROOT / ".env")
    start = key_usage()
    log = args.runs / "monitor.jsonl"
    seen = False   # start before production: only "finished" once processes have been seen
    while True:
        spent = key_usage() - start
        calls, recorded, violations = scan(args.runs, args.reasoning_cap, args.output_cap, args.provider)
        running = subprocess.run(["pgrep", "-f", PATTERN], capture_output=True, text=True).stdout.split()
        reason = ("budget" if spent >= args.budget - args.margin else "cap_or_provider" if violations else None)
        entry = dict(at=datetime.now(timezone.utc).isoformat(timespec="seconds"), key_spend_usd=round(spent, 4),
                     recorded_cost_usd=round(recorded, 4), calls=calls, processes=len(running),
                     violations=violations[:10], action="pause:" + reason if reason else None)
        with log.open("a") as f:
            f.write(json.dumps(entry) + "\n")
        if reason:
            subprocess.run(["pkill", "-TERM", "-f", PATTERN])
            print(f"PAUSED ({reason}): {entry}", flush=True)
            return
        seen = seen or bool(running)
        if seen and not running:
            print(f"Production finished: {entry}", flush=True)
            return
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
