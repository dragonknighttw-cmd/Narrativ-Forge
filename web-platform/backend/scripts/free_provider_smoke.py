#!/usr/bin/env python3
"""Opt-in, one-request smoke test for one explicitly selected non-OpenRouter provider.

Only redacted metadata is written. Never emit credentials, prompt/response text,
raw provider errors, or response bodies. This test does not retry requests.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

PROVIDER_NAMES = {
    "groq": "groq",
    "cloudflare-workers-ai": "cloudflare-ai",
    "gemini": "gemini",
    "mistral": "mistral",
    "cohere": "cohere",
    "nvidia": "nvidia",
}


def write_result(path: Path, result: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    path.write_text(rendered, encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", required=True, choices=sorted(PROVIDER_NAMES))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    started = None
    result = {
        "provider": args.provider,
        "model": None,
        "request_sent": False,
        "success": False,
        "http_status_class": None,
        "latency_ms": None,
        "script_chars": 0,
        "scene_count": 0,
        "error_code": None,
        "error_type": None,
    }

    if os.environ.get("CONFIRM_FREE_TIER", "").strip().lower() != "true":
        result["error_code"] = "free_tier_confirmation_required"
        write_result(output, result)
        return 2

    try:
        from app.services.ai_adapter import (
            CloudflareWorkersAIAdapter,
            OpenAICompatibleAdapter,
            _configured_chat_providers,
        )

        expected_name = PROVIDER_NAMES[args.provider]
        candidates = [p for p in _configured_chat_providers() if p.name == expected_name]
        if not candidates:
            result["error_code"] = "provider_key_missing_or_provider_not_enabled"
            write_result(output, result)
            return 2

        provider = candidates[0]
        result["model"] = provider.model
        adapter = (
            CloudflareWorkersAIAdapter(provider)
            if provider.name == "cloudflare-ai"
            else OpenAICompatibleAdapter(provider)
        )
        started = time.monotonic()
        result["request_sent"] = True
        plan = adapter.create_content_plan(
            idea='Synthetic smoke-test only: a fictional "blue paper boat". Return a tiny Burmese plan.',
            category="synthetic-test",
        )
        result["latency_ms"] = round((time.monotonic() - started) * 1000)
        result["http_status_class"] = "2xx"
        result["script_chars"] = len(plan.script)
        result["scene_count"] = len(plan.scenes)
        result["success"] = bool(plan.script.strip() and plan.scenes)
        if not result["success"]:
            result["error_code"] = "empty_normalized_content_plan"
    except Exception as exc:
        if started is not None:
            result["latency_ms"] = round((time.monotonic() - started) * 1000)
        response = getattr(exc, "response", None)
        status = getattr(response, "status_code", None)
        if isinstance(status, int):
            result["http_status_class"] = f"{status // 100}xx"
            result["error_code"] = f"http_{status}"
        else:
            result["error_code"] = "provider_request_or_validation_failed"
        result["error_type"] = type(exc).__name__[:80]

    write_result(output, result)
    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
