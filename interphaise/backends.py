"""Compatibility chat backend for Adem's agent code.

All live calls are restricted to direct Anthropic Haiku 5.5. The router_chat
and parse_json interfaces are preserved; no other model/provider is authorised.
"""

import json
import os

from dotenv import load_dotenv
from litellm.router import Router

load_dotenv()

ALLOWED_MODEL = "claude-haiku"


def _require_model(model: str):
    if model != ALLOWED_MODEL:
        raise ValueError("Project backend is restricted to claude-haiku (Haiku 5.5)")


router = Router(
    model_list=[{
        "model_name": ALLOWED_MODEL,
        "litellm_params": {
            "model": "anthropic/claude-haiku-5-5",
            "api_key": os.getenv("MY_ANTHROPIC_KEY") or os.getenv("ANTHROPIC_API_KEY"),
            "max_tokens": 2048,
        },
    }],
    num_retries=0,
)


def _call_router(model: str, system: str, user: str, timeout: int = 180) -> str:
    """
    Raw router call. Streams to handle thinking models (DeepSeek-R1, etc.)
    that return content=None in non-streaming mode.
    Returns the full response as a plain string.
    Retries up to 3 times on connection drops.
    """
    _require_model(model)
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
            print(f"  [LLM {model}] attempt {attempt+1} failed after {elapsed:.1f}s: {type(e).__name__}", flush=True)
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
               only "claude-haiku"
    """
    _require_model(model)
    def chat(system: str, user: str) -> str:
        return _call_router(model=model, system=system, user=user)
    return chat
