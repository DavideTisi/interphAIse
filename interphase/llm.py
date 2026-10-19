"""LLM access.

Every reasoner takes an ``llm`` callable ``(system, user) -> dict | list`` so
that tests (and the human-baseline mode) can swap in something else without
touching the reasoners. ``make_llm`` builds the real one.

If HELLMM is installed (``pip install -e ../hellmm``) its litellm Router and
model aliases are reused, so the same .env and aliases work in both projects.
Otherwise a plain ``litellm.completion`` call is used with a full litellm
model string (e.g. "openrouter/deepseek/deepseek-v3.2").
"""

from __future__ import annotations

import json
import time
from typing import Callable

from dotenv import load_dotenv

load_dotenv()

LLM = Callable[[str, str], "dict | list"]


def extract_json(text: str):
    """Return the first JSON object/array in ``text`` (handles fences/preamble)."""
    start = next((i for i, c in enumerate(text) if c in "{["), None)
    if start is None:
        raise ValueError(f"No JSON found in model response:\n{text[:500]}")
    obj, _ = json.JSONDecoder().raw_decode(text, start)
    return obj


def make_llm(model: str, temperature: float | None = None, retries: int = 3) -> LLM:
    """Build an ``llm(system, user)`` callable for ``model``.

    ``model`` is either a HELLMM alias (when hellmm is importable) or a litellm
    model string.
    """
    try:  # reuse HELLMM's router + aliases when available
        from hellmm.llm import call_llm as _hellmm_call  # type: ignore

        def _call(system: str, user: str):
            return _hellmm_call(system=system, user=user, model=model)

        return _call
    except Exception:
        pass

    import litellm  # imported lazily so offline tests don't need it

    def _call(system: str, user: str):
        kwargs = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        if temperature is not None:
            kwargs["temperature"] = temperature
        last: Exception | None = None
        for attempt in range(retries):
            try:
                resp = litellm.completion(**kwargs)
                return extract_json(resp.choices[0].message.content or "")
            except Exception as e:  # network, rate limit, malformed JSON
                last = e
                time.sleep(2**attempt)
        raise RuntimeError(f"LLM call failed after {retries} attempts: {last}")

    return _call


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
