"""
MetaJudge OpenRouter Client
============================
Minimal, robust client for querying multiple LLMs via OpenRouter.
Used for item generation, audit, and validation runs.

Never import API keys directly — reads from OPENROUTER_API_KEY env var.
Never commit keys or echo them to stdout.
"""

import json
import os
import time
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import urllib.request
import urllib.error


OPENROUTER_BASE = "https://openrouter.ai/api/v1/chat/completions"

# Tiered model routing
MODELS = {
    # Tier A — cheap / high-volume
    "deepseek-chat": "deepseek/deepseek-chat",
    "grok-3-mini": "x-ai/grok-3-mini",
    # Tier B — mid-tier critical review
    "gemini-2.5-pro": "google/gemini-2.5-pro",
    # Tier C — frontier final-pass
    "claude-sonnet-4.5": "anthropic/claude-sonnet-4.5",
    "gpt-4.1": "openai/gpt-4.1",
}

# 5-model validation suite
VALIDATION_SUITE = [
    "anthropic/claude-sonnet-4.5",
    "openai/gpt-4.1",
    "google/gemini-2.5-pro",
    "x-ai/grok-3-mini",
    "deepseek/deepseek-chat",
]


def get_api_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        raise RuntimeError(
            "OPENROUTER_API_KEY not set. Provide it as an environment variable."
        )
    return key


def query(
    model: str,
    messages: list[dict[str, str]],
    temperature: float = 0.3,
    max_tokens: int = 2048,
    timeout: int = 60,
    retries: int = 2,
    json_mode: bool = False,
) -> dict[str, Any]:
    """
    Query a model via OpenRouter. Returns a dict with:
      - model, timestamp, prompt_hash, response_text, latency_ms,
        usage (if returned), error (if any)
    """
    api_key = get_api_key()

    # Resolve short name to full model ID
    model_id = MODELS.get(model, model)

    prompt_hash = hashlib.sha256(
        json.dumps(messages, sort_keys=True).encode()
    ).hexdigest()[:16]

    payload = {
        "model": model_id,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/seanmichaelmcgee/metajudge",
        "X-Title": "MetaJudge-AGI",
    }

    result = {
        "model": model_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt_hash": prompt_hash,
        "response_text": None,
        "latency_ms": None,
        "usage": None,
        "error": None,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        OPENROUTER_BASE, data=data, headers=headers, method="POST"
    )

    for attempt in range(retries + 1):
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = json.loads(resp.read().decode("utf-8"))

            result["latency_ms"] = int((time.monotonic() - t0) * 1000)
            result["usage"] = body.get("usage")

            choices = body.get("choices", [])
            if choices:
                result["response_text"] = choices[0]["message"]["content"]
            else:
                result["error"] = "No choices in response"

            return result

        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace") if e.fp else ""
            result["error"] = f"HTTP {e.code}: {err_body[:500]}"
            result["latency_ms"] = int((time.monotonic() - t0) * 1000)
            if e.code == 429 and attempt < retries:
                time.sleep(2 ** (attempt + 1))
                continue
            return result

        except (urllib.error.URLError, TimeoutError, OSError) as e:
            result["error"] = f"Network error: {str(e)[:300]}"
            result["latency_ms"] = int((time.monotonic() - t0) * 1000)
            if attempt < retries:
                time.sleep(2 ** (attempt + 1))
                continue
            return result

    return result


def query_all(
    models: list[str],
    messages: list[dict[str, str]],
    **kwargs,
) -> list[dict[str, Any]]:
    """Query multiple models with the same prompt. Returns list of results."""
    results = []
    for m in models:
        r = query(m, messages, **kwargs)
        results.append(r)
    return results


def save_results(
    results: list[dict[str, Any]],
    output_path: str | Path,
    task_name: str = "",
) -> None:
    """Append results to a JSONL file for auditability."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        for r in results:
            r["task_name"] = task_name
            f.write(json.dumps(r) + "\n")


def smoke_test() -> dict[str, str]:
    """Quick test of all configured models. Returns {model: status}."""
    messages = [{"role": "user", "content": "Reply with exactly: OK"}]
    statuses = {}
    for short_name, model_id in MODELS.items():
        r = query(model_id, messages, max_tokens=10, timeout=30)
        if r["error"]:
            statuses[short_name] = f"FAIL: {r['error'][:100]}"
        elif r["response_text"] and "OK" in r["response_text"].upper():
            statuses[short_name] = f"OK ({r['latency_ms']}ms)"
        else:
            statuses[short_name] = f"UNEXPECTED: {(r['response_text'] or '')[:50]}"
    return statuses


if __name__ == "__main__":
    print("=== MetaJudge OpenRouter Smoke Test ===")
    results = smoke_test()
    for model, status in results.items():
        print(f"  {model:20s} {status}")
