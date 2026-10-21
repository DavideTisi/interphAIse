"""Minimal JSON smoke test of the configured, Haiku-only Anthropic client."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from interphaise.llm import ANTHROPIC_MODEL, make_llm


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', choices=[ANTHROPIC_MODEL], default=ANTHROPIC_MODEL)
    args = parser.parse_args()
    llm = make_llm(args.model, max_tokens=32, retries=1)
    result = llm('Return only a JSON object.',
                 'For the interphAIse connection test, return {"ok":true}.')
    if result != {'ok': True}:
        raise SystemExit('Unexpected response to the connection test')
    print('Haiku 5.5 generation test passed')
    print(json.dumps(llm.last_metadata, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, EnvironmentError) as error:
        raise SystemExit(str(error)) from None
