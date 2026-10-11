#!/usr/bin/env python3
"""Opt-in, one-request OpenRouter free-model smoke test.

Only records metadata and validation outcome; never writes prompts, outputs, or API keys.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ALLOWED_MODELS = {
    "apodex/apodex-1.1-mini:free",
    "cohere/north-mini-code:free",
    "google/gemma-4-26b-a4b-it:free",
    "google/gemma-4-31b-it:free",
    "liquid/lfm-2.5-2.6b:free",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "nvidia/nemotron-3.5-lightning:free",
}

def extract_json(text: str) -> dict:
    value = text.strip()
    if value.startswith("```"):
        lines = value.splitlines()[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        value = "\n".join(lines).strip()
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise ValueError("response_not_object")
    if not isinstance(parsed.get("hook"), str) or not parsed["hook"].strip():
        raise ValueError("missing_hook")
    if not isinstance(parsed.get("script"), str) or not parsed["script"].strip():
        raise ValueError("missing_script")
    if not isinstance(parsed.get("scenes"), list) or not parsed["scenes"]:
        raise ValueError("missing_scenes")
    return parsed

def run(model: str, api_key: str) -> dict:
    if model not in ALLOWED_MODELS:
        raise ValueError("model_not_allowlisted")
    request_body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Return only a JSON object with hook, script, and scenes. Use a synthetic example, no external facts."},
            {"role": "user", "content": 'Create a tiny Burmese test plan for the fictional idea "blue paper boat". Return JSON with hook, script, and one scene object.'},
        ],
        "temperature": 0,
        "max_tokens": 400,
    }
    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(request_body).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    started = time.monotonic()
    result = {"model": model, "http_status": None, "latency_ms": None, "success": False, "validation": "not_run", "error_code": None}
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            result["http_status"] = response.status
            payload = json.loads(response.read().decode("utf-8"))
        choices = payload.get("choices") or []
        content = ((choices[0] if choices else {}).get("message") or {}).get("content")
        if not isinstance(content, str) or not content.strip():
            result["validation"] = "empty_response"
            result["error_code"] = "empty_response"
        else:
            try:
                extract_json(content)
                result["validation"] = "content_plan_json_valid"
                result["success"] = True
            except (ValueError, json.JSONDecodeError) as exc:
                result["validation"] = "content_plan_json_invalid"
                result["error_code"] = str(exc)[:80]
    except urllib.error.HTTPError as exc:
        result["http_status"] = exc.code
        result["error_code"] = f"http_{exc.code}"
    except urllib.error.URLError:
        result["error_code"] = "network_error"
    except (TimeoutError, OSError):
        result["error_code"] = "network_or_timeout"
    except (json.JSONDecodeError, UnicodeDecodeError):
        result["error_code"] = "invalid_api_json"
    finally:
        result["latency_ms"] = round((time.monotonic() - started) * 1000)
    return result

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if not api_key:
        result = {"model": args.model, "success": False, "error_code": "missing_openrouter_api_key"}
        output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result))
        return 2
    try:
        result = run(args.model, api_key)
    except ValueError as exc:
        result = {"model": args.model, "success": False, "error_code": str(exc)}
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0 if result.get("success") else 1

if __name__ == "__main__":
    sys.exit(main())