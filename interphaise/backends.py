"""LLM routing via litellm Router.

How it works
------------
litellm.Router maps short aliases (e.g. "claude-sonnet") to the real model
string + provider credentials. Callers only ever use the alias — switching
providers is a config change here, not a code change anywhere else.

API keys are loaded from a .env file at repo root (never committed). Add
whichever of these you need:
    MY_OPENROUTER_API_KEY=sk-or-...   # OpenRouter (most aliases below)
    ANTHROPIC_API_KEY=sk-ant-...      # direct Anthropic billing

Ported from smartselucidator (src/agents/backends.py) as a standalone,
self-contained alternative to interphaise.llm.make_llm — use this when you
want the full curated model menu without depending on hellmm being
importable.

Usage
-----
    from interphaise.backends import router_chat
    chat_fn = router_chat("claude-sonnet")
    response = chat_fn(system="You are...", user="What is...")
"""

import json
import os

from dotenv import load_dotenv
from litellm.router import Router

load_dotenv()

_OLLAMA_BASE = "http://localhost:11434"

router = Router(
    model_list=[
        # ── Local (Ollama) ────────────────────────────────────────────────────
        {
            "model_name": "qwen2.5:32b",
            "litellm_params": {
                "model":    "ollama/qwen2.5:32b",
                "api_base": _OLLAMA_BASE,
            },
        },
        {
            "model_name": "qwen3:32b",
            "litellm_params": {
                "model":    "ollama/qwen3:32b",
                "api_base": _OLLAMA_BASE,
            },
        },
        # ── Anthropic (direct) ────────────────────────────────────────────────
        {
            "model_name": "claude-sonnet",
            "litellm_params": {
                "model":   "anthropic/claude-sonnet-4-6",
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
            },
        },
        {
            "model_name": "claude-haiku",
            "litellm_params": {
                "model":   "anthropic/claude-haiku-5-5",
                "api_key": os.getenv("ANTHROPIC_API_KEY") or os.getenv("MY_ANTHROPIC_KEY"),
            },
        },
        # ── OpenRouter (one API key, many providers) ──────────────────────────
        {
            "model_name": "claude-sonnet",
            "litellm_params": {
                "model": "openrouter/anthropic/claude-sonnet-4.6",
                "api_key": os.getenv("MY_ANTHROPIC_KEY"),
            },
        },
        {
            "model_name": "qwen-72b",
            "litellm_params": {
                "model":   "openrouter/qwen/qwen-2.5-72b-instruct",
                "api_key": os.getenv("MY_OPENROUTER_API_KEY"),
            },
        },
        {
            "model_name": "gemini-flash",
            "litellm_params": {
                "model":   "openrouter/google/gemini-2.5-flash-lite",
                "api_key": os.getenv("MY_OPENROUTER_API_KEY"),
            },
        },
        {
            "model_name": "deepseek-v3.2",
            "litellm_params": {
                "model":   "openrouter/deepseek/deepseek-v3.2",
                "api_key": os.getenv("MY_OPENROUTER_API_KEY"),
            },
        },
        {
            "model_name": "qwen3-coder-plus",
            "litellm_params": {
                "model":   "openrouter/qwen/qwen3-coder-plus",
                "api_key": os.getenv("MY_OPENROUTER_API_KEY"),
                "max_tokens": 8000,
            },
        },
        {
            "model_name": "gpt-5-mini",
            "litellm_params": {
                "model":   "openrouter/openai/gpt-5-mini",
                "api_key": os.getenv("MY_OPENROUTER_API_KEY"),
                "max_tokens": 8000,
            },
        },
        {
            "model_name": "deepseek-r1",
            "litellm_params": {
                "model":   "openrouter/deepseek/deepseek-r1-0528",
                "api_key": os.getenv("MY_OPENROUTER_API_KEY"),
                "rpm":     2,
            },
        },
        # Pinned max_tokens deliberately. Without it litellm infers max_tokens
        # from the context window, and OpenRouter may route to a provider with
        # a lower cap (e.g. a 98k-token ceiling), so the same alias can work one
        # day and fail the next. Every reply here is a small JSON object, so
        # this is far more than needed — it also bounds cost on output-heavy
        # models.
        {
            "model_name": "kimi-k2",
            "litellm_params": {
                "model":   "openrouter/moonshotai/kimi-k2",
                "api_key": os.getenv("MY_OPENROUTER_API_KEY"),
                "max_tokens": 8000,
            },
        },
        {
            "model_name": "tencent-hy3",
            "litellm_params": {
                "model":   "openrouter/tencent/hy3-preview:free",
                "api_key": os.getenv("TENCENT_API_KEY"),
                "rpm":     3,
            },
        },
    ],
    num_retries=3,
    retry_after=10,
)


def _call_router(model: str, system: str, user: str, timeout: int = 180) -> str:
    """
    Raw router call. Streams to handle thinking models (DeepSeek-R1, etc.)
    that return content=None in non-streaming mode.
    Returns the full response as a plain string.
    Retries up to 3 times on connection drops.
    """
    import time
    messages = [
        {"role": "system", "content": system},
        {"role": "user",   "content": user},
    ]
    for attempt in range(3):
        t0 = time.time()
        try:
            stream = router.completion(
                model=model,
                messages=messages,
                stream=True,
                timeout=timeout,
            )
            content = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    content += delta
            elapsed = time.time() - t0
            print(f"  [LLM {model}] {elapsed:.1f}s, {len(content)} chars", flush=True)
            return content.strip()
        except Exception as e:
            elapsed = time.time() - t0
            print(f"  [LLM {model}] attempt {attempt+1} failed after {elapsed:.1f}s: {e!r}", flush=True)
            if attempt < 2:
                time.sleep(10 * (attempt + 1))
    raise RuntimeError(f"[{model}] failed after 3 attempts")


def parse_json(text: str) -> dict | list:
    """
    Extract a JSON object or array from a string.

    Uses raw_decode so it stops exactly where the JSON ends, ignoring preamble
    text or trailing explanation from the LLM.

    Tries every candidate start position rather than only the first. Taking the
    first '{' and giving up if it did not decode meant a brace anywhere in the
    preamble -- an example, a prose aside, a markdown artifact -- discarded a
    perfectly good object further down.

    Prefers an object carrying a known payload key (interphAIse's reasoners
    always emit "chain_of_thought", plus "action"/"verdict" on decision nodes),
    so an incidental fragment earlier in the text cannot shadow the real answer.

    Raises ValueError if no JSON is found.
    """
    decoder = json.JSONDecoder()
    fallback = None
    for i, ch in enumerate(text):
        if ch not in "{[":
            continue
        try:
            result, _ = decoder.raw_decode(text, i)
        except ValueError:
            continue
        if isinstance(result, dict) and (
                {"chain_of_thought", "action", "verdict"} & result.keys()):
            return result
        if fallback is None:
            fallback = result
    if fallback is None:
        raise ValueError(f"No JSON found in:\n{text}")
    return fallback


def router_chat(model: str):
    """
    Return a chat_fn for the given model alias.

    The returned function has signature: (system: str, user: str) -> str

    Args:
        model: alias from the router model_list above,
               e.g. "claude-sonnet", "qwen-72b", "gemini-flash"
    """
    def chat(system: str, user: str) -> str:
        return _call_router(model=model, system=system, user=user)
    return chat
