"""LLM access.

Every reasoner takes an ``llm`` callable ``(system, user) -> dict | list`` so
that tests (and the human-baseline mode) can swap in something else without
touching the reasoners. ``make_llm`` builds the real one.

All live calls use the configured Claude Haiku 5.5 model and the Anthropic key.
No other provider, router or model fallback is supported.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
import time
from typing import Callable

from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_MODEL = "claude-haiku-5-5"

LLM = Callable[[str, str], "dict | list"]


def extract_json(text: str):
    """Return the first JSON object/array in ``text`` (handles fences/preamble)."""
    start = next((i for i, c in enumerate(text) if c in "{["), None)
    if start is None:
        raise ValueError(f"No JSON found in model response:\n{text[:500]}")
    obj, _ = json.JSONDecoder().raw_decode(text, start)
    return obj


def make_llm(model: str, temperature: float | None = None, retries: int = 3,
             max_tokens: int = 2048) -> LLM:
    """Build a direct Haiku 5.5 client; reject every other live model/provider."""
    # Never send the collaborator's Anthropic key through an external router.
    model_id = model.removeprefix("anthropic/")
    if model_id != ANTHROPIC_MODEL:
        raise ValueError(f"Project Anthropic credential is restricted to {ANTHROPIC_MODEL}")
    key = (os.environ.get("MY_ANTHROPIC_KEY") or os.environ.get("ANTHROPIC_API_KEY") or "").strip()
    if not key:
        raise EnvironmentError("Anthropic credential is not configured in the local environment")
    if max_tokens < 1 or retries < 1:
        raise ValueError("max_tokens and retries must be positive")

    def _anthropic(system: str, user: str):
        payload = {"model": model_id, "max_tokens": max_tokens, "system": system,
                   "messages": [{"role": "user", "content": user}]}
        if temperature is not None:
            payload["temperature"] = temperature
        if model.startswith("anthropic/"):
            # .env uses MY_ANTHROPIC_KEY (not the ANTHROPIC_API_KEY name litellm
            # looks up on its own) — see scripts/check_anthropic_key.py.
            kwargs["api_key"] = os.getenv("ANTHROPIC_API_KEY") or os.getenv("MY_ANTHROPIC_KEY")
        last: Exception | None = None
        for attempt in range(retries):
            request = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=json.dumps(payload).encode(),
                headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                         "content-type": "application/json"}, method="POST")
            try:
                with urllib.request.urlopen(request, timeout=90) as response:
                    data = json.load(response)
            except urllib.error.HTTPError as error:
                # Never include raw provider responses or headers in logs.
                code = error.code
                error.close()
                if code in (429, 500, 502, 503, 504, 529) and attempt + 1 < retries:
                    time.sleep(2 ** attempt)
                    continue
                raise RuntimeError(f"Anthropic request failed (HTTP {code})") from None
            except urllib.error.URLError:
                raise RuntimeError("Anthropic connection failed") from None
            _anthropic.last_metadata = {"requested_model": model_id, "returned_model": data.get("model"),
                                        "usage": data.get("usage"), "stop_reason": data.get("stop_reason"),
                                        "temperature": temperature, "max_tokens": max_tokens}
            if data.get("stop_reason") == "max_tokens":
                raise RuntimeError("Anthropic response reached the output-token limit")
            text = "".join(block.get("text", "") for block in data.get("content", [])
                           if block.get("type") == "text")
            try:
                return extract_json(text)
            except (ValueError, TypeError):
                raise RuntimeError("Anthropic response was not valid JSON") from None
        raise RuntimeError("Anthropic retries exhausted")

    _anthropic.last_metadata = None
    return _anthropic

class HumanLLM:
    """Human-baseline mode: a team member answers the same prompts.

    Prints the prompt the LLM would see and reads a JSON answer from stdin
    (end with an empty line). Run the orchestrator with ``llm=HumanLLM()`` on
    the benchmark systems to get the human-vs-LLM comparison under identical
    information.
    """

    def __call__(self, system: str, user: str):
        print("\n" + "=" * 80 + "\n" + system + "\n" + "-" * 80 + "\n" + user + "\n" + "=" * 80)
        print("Answer with JSON (finish with an empty line):")
        lines = []
        while (line := input()) != "":
            lines.append(line)
        return extract_json("\n".join(lines))


class ScriptedLLM:
    """Deterministic stand-in for tests and dry runs.

    ``responses`` maps a substring of the *system* prompt (the reasoner's
    role tag, see reasoners/prompts.py) to either a fixed response or a
    callable ``(system, user) -> response``. The same mechanism is how a
    human expert can answer in place of the LLM (human-baseline mode).
    """

    def __init__(self, responses: dict[str, object]):
        self.responses = responses
        self.calls: list[tuple[str, str]] = []

    def __call__(self, system: str, user: str):
        self.calls.append((system, user))
        for tag, resp in self.responses.items():
            if tag in system:
                return resp(system, user) if callable(resp) else resp
        raise KeyError(f"ScriptedLLM has no response for system prompt: {system[:80]}")
