"""LLM access.

Every reasoner takes an ``llm`` callable ``(system, user) -> dict | list`` so
that tests (and the human-baseline mode) can swap in something else without
touching the reasoners. ``make_llm`` builds the real one.

Live calls use Claude Haiku 5.5 with the Anthropic key, or (DeepSeek repeat only, see AGENTS.md)
DeepSeek V3.2 through OpenRouter with Adem's own key and one pinned provider. No fallbacks.
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
DEEPSEEK_MODEL = "deepseek/deepseek-v3.2"   # OpenRouter id; reasoning on, one provider, fallbacks off
MALFORMED_TEXT_LIMIT = 4000  # characters of malformed model output kept for replay

LLM = Callable[[str, str], "dict | list"]


def extract_json(text: str):
    """Return the first JSON object/array in ``text`` (handles fences/preamble)."""
    start = next((i for i, c in enumerate(text) if c in "{["), None)
    if start is None:
        raise ValueError(f"No JSON found in model response:\n{text[:500]}")
    obj, _ = json.JSONDecoder().raw_decode(text, start)
    return obj


def make_llm(model: str, temperature: float | None = None, retries: int = 3,
             max_tokens: int = 2048, provider: str | None = None, reasoning_max_tokens: int | None = None) -> LLM:
    """Build a direct Haiku 5.5 client, or the pinned DeepSeek V3.2 client; reject everything else."""
    if model == DEEPSEEK_MODEL:
        return _make_openrouter(provider, temperature, retries, max_tokens, reasoning_max_tokens)
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
        # Accounting per logical call: every HTTP attempt is listed with safe identifiers only
        # (status, provider request-id, elapsed time); never credentials, headers or raw error bodies.
        _anthropic.last_metadata = None  # Do not attribute a previous call's usage to a failure.
        payload = {"model": model_id, "max_tokens": max_tokens, "system": system,
                   "messages": [{"role": "user", "content": user}]}
        if temperature is not None:
            payload["temperature"] = temperature
        attempts = []

        def finish(final_error=None, data=None, **extra):
            data = data or {}
            _anthropic.last_metadata = {
                "requested_model": model_id, "returned_model": data.get("model"), "response_id": data.get("id"),
                "usage": data.get("usage"), "stop_reason": data.get("stop_reason"),
                "temperature": temperature, "max_tokens": max_tokens,
                "http_attempts": len(attempts), "transport_retries": max(0, len(attempts) - 1),
                "attempts": attempts, "final_error": final_error, **extra}

        for attempt in range(retries):
            request = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=json.dumps(payload).encode(),
                headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                         "content-type": "application/json"}, method="POST")
            started = time.monotonic()
            try:
                with urllib.request.urlopen(request, timeout=90) as response:
                    request_id = (getattr(response, "headers", None) or {}).get("request-id")
                    try:
                        data = json.load(response)
                    except ValueError:
                        attempts.append({"status": "invalid_response_json", "request_id": request_id,
                                         "elapsed_s": round(time.monotonic() - started, 3)})
                        finish("response body was not JSON")
                        raise RuntimeError("Anthropic response body was not JSON") from None
                attempts.append({"status": 200, "request_id": request_id,
                                 "elapsed_s": round(time.monotonic() - started, 3)})
            except urllib.error.HTTPError as error:
                # Never include raw provider responses or headers in logs.
                code, request_id = error.code, (error.headers or {}).get("request-id")
                error.close()
                attempts.append({"status": code, "request_id": request_id,
                                 "elapsed_s": round(time.monotonic() - started, 3)})
                if code in (429, 500, 502, 503, 504, 529) and attempt + 1 < retries:
                    time.sleep(2 ** attempt)
                    continue
                finish(f"HTTP {code}")
                raise RuntimeError(f"Anthropic request failed (HTTP {code})") from None
            except (urllib.error.URLError, OSError):   # includes timeouts; HTTPError is handled above
                attempts.append({"status": "connection_error", "request_id": None,
                                 "elapsed_s": round(time.monotonic() - started, 3)})
                finish("connection failed")
                raise RuntimeError("Anthropic connection failed") from None
            if data.get("stop_reason") == "max_tokens":
                finish("output-token limit", data)
                raise RuntimeError("Anthropic response reached the output-token limit")
            text = "".join(block.get("text", "") for block in data.get("content", [])
                           if block.get("type") == "text")
            try:
                parsed = extract_json(text)
            except (ValueError, TypeError):
                # Bounded copy of the malformed text, so future archives can replay the parse.
                finish("response was not valid JSON", data, malformed_text=text[:MALFORMED_TEXT_LIMIT])
                raise RuntimeError("Anthropic response was not valid JSON") from None
            finish(None, data)
            return parsed
        finish("retries exhausted")
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


def _make_openrouter(provider, temperature, retries, max_tokens, reasoning_max_tokens=None) -> LLM:
    """DeepSeek V3.2 via OpenRouter: one pinned provider tag (e.g. "gmicloud/fp8"), no fallbacks, reasoning on.

    ``reasoning_max_tokens`` caps reasoning (honoured by siliconflow/fp8, not by gmicloud/fp8; tested 2026-10-22).
    Metadata mirrors the Anthropic client (safe identifiers only) plus the serving provider and
    OpenRouter's reported cost. Usage is normalised to input/output/thinking token names."""
    if not provider:
        raise ValueError("DeepSeek runs must pin one OpenRouter provider (e.g. gmicloud/fp8)")
    key = (os.environ.get("MY_OPENROUTER_API_KEY") or "").strip()
    if not key:
        raise EnvironmentError("OpenRouter credential is not configured in the local environment")
    if max_tokens < 1 or retries < 1:
        raise ValueError("max_tokens and retries must be positive")
    reasoning = {"enabled": True} if reasoning_max_tokens is None else {"max_tokens": reasoning_max_tokens}

    def _openrouter(system: str, user: str):
        _openrouter.last_metadata = None
        payload = {"model": DEEPSEEK_MODEL, "max_tokens": max_tokens, "reasoning": reasoning,
                   "provider": {"order": [provider], "allow_fallbacks": False, "require_parameters": True},
                   "usage": {"include": True},
                   "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        if temperature is not None:
            payload["temperature"] = temperature
        attempts = []

        def finish(final_error=None, data=None, **extra):
            data = data or {}
            u = data.get("usage") or {}
            usage = {"input_tokens": u.get("prompt_tokens"), "output_tokens": u.get("completion_tokens"),
                     "cache_read_input_tokens": (u.get("prompt_tokens_details") or {}).get("cached_tokens") or 0,
                     "output_tokens_details": {"thinking_tokens":
                                               (u.get("completion_tokens_details") or {}).get("reasoning_tokens")},
                     "openrouter_cost_usd": u.get("cost")} if u else None
            choice = (data.get("choices") or [{}])[0]
            _openrouter.last_metadata = {
                "requested_model": DEEPSEEK_MODEL, "returned_model": data.get("model"), "response_id": data.get("id"),
                "provider_requested": provider, "provider_served": data.get("provider"), "reasoning": reasoning,
                "usage": usage, "stop_reason": choice.get("finish_reason"),
                "temperature": temperature, "max_tokens": max_tokens,
                "http_attempts": len(attempts), "transport_retries": max(0, len(attempts) - 1),
                "attempts": attempts, "final_error": final_error, **extra}

        for attempt in range(retries):
            request = urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions", data=json.dumps(payload).encode(),
                headers={"authorization": f"Bearer {key}", "content-type": "application/json"}, method="POST")
            started = time.monotonic()
            try:
                with urllib.request.urlopen(request, timeout=300) as response:
                    try:
                        data = json.load(response)
                    except ValueError:
                        attempts.append({"status": "invalid_response_json", "elapsed_s": round(time.monotonic() - started, 3)})
                        finish("response body was not JSON")
                        raise RuntimeError("OpenRouter response body was not JSON") from None
            except urllib.error.HTTPError as error:
                code = error.code
                error.close()
                attempts.append({"status": code, "elapsed_s": round(time.monotonic() - started, 3)})
                if code in (429, 500, 502, 503, 504, 529) and attempt + 1 < retries:
                    time.sleep(2 ** attempt)
                    continue
                finish(f"HTTP {code}")
                raise RuntimeError(f"OpenRouter request failed (HTTP {code})") from None
            except (urllib.error.URLError, OSError):
                attempts.append({"status": "connection_error", "elapsed_s": round(time.monotonic() - started, 3)})
                finish("connection failed")
                raise RuntimeError("OpenRouter connection failed") from None
            attempts.append({"status": 200, "elapsed_s": round(time.monotonic() - started, 3)})
            if "error" in data:   # OpenRouter can return 200 with an upstream error body
                finish(f"upstream error {(data['error'] or {}).get('code')}")
                raise RuntimeError("OpenRouter upstream error")
            if data.get("provider") and data["provider"].lower() != provider.split("/")[0].replace("-", "").lower():
                finish(f"served by unexpected provider {data['provider']}", data)
                raise RuntimeError("OpenRouter served the request from an unpinned provider")
            choice = (data.get("choices") or [{}])[0]
            if choice.get("finish_reason") == "length":
                finish("output-token limit", data)
                raise RuntimeError("OpenRouter response reached the output-token limit")
            text = (choice.get("message") or {}).get("content") or ""
            try:
                parsed = extract_json(text)
            except (ValueError, TypeError):
                finish("response was not valid JSON", data, malformed_text=text[:MALFORMED_TEXT_LIMIT])
                raise RuntimeError("OpenRouter response was not valid JSON") from None
            finish(None, data)
            return parsed
        finish("retries exhausted")
        raise RuntimeError("OpenRouter retries exhausted")

    _openrouter.last_metadata = None
    return _openrouter
