"""Check that an Anthropic API key (from .env) can call its model, and what one call used.

    python scripts/check_anthropic_key.py [--model MODEL_ID]

Reads ANTHROPIC_API_KEY, falling back to MY_ANTHROPIC_KEY (this project's name
for an OpenRouter-routed Anthropic key — see interphaise/backends.py). Without
--model, the newest Haiku model the key can list is used. The API does not
report the account balance to a regular key: check it in the Console under
Billing. The usage printed here is for this one call.
"""
import argparse
import os

import anthropic
from dotenv import load_dotenv


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model")
    args = parser.parse_args()
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("MY_ANTHROPIC_KEY")
    client = anthropic.Anthropic(api_key=api_key)

    models = [m.id for m in client.models.list()]           # newest first
    print("models this key can see:", ", ".join(models) or "none")
    model = args.model or next((m for m in models if "haiku" in m), None)
    if model is None:
        raise SystemExit("no Haiku model listed; pass --model with the ID from the Console")

    raw = client.messages.with_raw_response.create(
        model=model, max_tokens=64, messages=[{"role": "user", "content": "Say hello in five words."}])
    message = raw.parse()
    print("model:", message.model)
    print("reply:", next((b.text for b in message.content if b.type == "text"), ""))
    print(f"usage: {message.usage.input_tokens} input, {message.usage.output_tokens} output tokens")
    for name, value in sorted(raw.headers.items()):
        if name.startswith("anthropic-ratelimit"):
            print(f"{name}: {value}")


if __name__ == "__main__":
    try:
        main()
    except anthropic.AuthenticationError:
        raise SystemExit("key rejected (401): check ANTHROPIC_API_KEY (or MY_ANTHROPIC_KEY) in .env")
    except anthropic.PermissionDeniedError as e:
        raise SystemExit(f"key not allowed for this model (403): {e.message}")
    except anthropic.NotFoundError as e:
        raise SystemExit(f"model not found (404): {e.message}")
    except anthropic.BadRequestError as e:
        raise SystemExit(f"bad request (400), e.g. no credit left: {e.message}")
