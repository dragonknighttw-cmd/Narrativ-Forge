#!/usr/bin/env python3
"""
Narrativ-Forge: End-to-End Production Verification & Smoke Test Runner
---------------------------------------------------------------------
Pings backend health endpoints, database readiness, AI usage failover,
frontend server, and verifies Telegram alert bot connectivity.

Usage:
    python scripts/verify_production.py [--api-url http://127.0.0.1:8000] [--frontend-url http://127.0.0.1:3000]
"""

from __future__ import annotations

import argparse
import os
import sys
import json
import urllib.request
import urllib.error


def make_request(url: str, timeout: float = 8.0) -> tuple[int, dict | str]:
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "NarrativForge-SmokeTest/1.0", "Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status = response.status
            body = response.read().decode("utf-8")
            try:
                return status, json.loads(body)
            except Exception:
                return status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        return e.code, body
    except Exception as e:
        return 0, str(e)


def main() -> int:
    parser = argparse.ArgumentParser(description="Narrativ-Forge Production Smoke Test")
    parser.add_argument("--api-url", default=os.getenv("API_URL", "http://127.0.0.1:8000"), help="FastAPI Base URL")
    parser.add_argument("--frontend-url", default=os.getenv("FRONTEND_URL", "http://127.0.0.1:3000"), help="Next.js Frontend URL")
    args = parser.parse_args()

    api_base = args.api_url.rstrip("/")
    frontend_base = args.frontend_url.rstrip("/")

    print("=" * 65)
    print("  Narrativ-Forge: End-to-End Production Verification")
    print(f"  Target Backend:  {api_base}")
    print(f"  Target Frontend: {frontend_base}")
    print("=" * 65)

    checks_passed = 0
    checks_total = 0

    # 1. Backend /health
    checks_total += 1
    health_url = f"{api_base}/health"
    print(f"[*] Checking Backend Health ({health_url})...", end=" ")
    status, body = make_request(health_url)
    if status == 200:
        print("[PASS] (HTTP 200 OK)")
        checks_passed += 1
    else:
        print(f"[FAIL] (HTTP {status}: {body})")

    # 2. Backend /ready (DB & Cache)
    checks_total += 1
    ready_url = f"{api_base}/ready"
    print(f"[*] Checking Backend Readiness & Database ({ready_url})...", end=" ")
    status, body = make_request(ready_url)
    if status == 200 and isinstance(body, dict) and body.get("status") == "ready":
        print("[PASS] (Database & Cache Ready)")
        checks_passed += 1
    elif status == 200:
        print(f"[WARN] (HTTP 200, but degraded status: {body})")
        checks_passed += 1
    else:
        print(f"[FAIL] (HTTP {status}: {body})")

    # 3. AI Usage & Failover API
    checks_total += 1
    ai_url = f"{api_base}/api/v1/ai/usage"
    print(f"[*] Checking AI Usage & Failover Tracker ({ai_url})...", end=" ")
    status, body = make_request(ai_url)
    if status == 200 and isinstance(body, dict) and "providers" in body:
        active_models = sum(1 for p in body["providers"].values() if p.get("status") == "active")
        print(f"[PASS] (HTTP 200 - {active_models} active providers tracked)")
        checks_passed += 1
    else:
        print(f"[FAIL] (HTTP {status}: {body})")

    # 4. Frontend Root
    checks_total += 1
    print(f"[*] Checking Frontend Web Shell ({frontend_base})...", end=" ")
    status, body = make_request(frontend_base)
    if status in (200, 307, 308):
        print(f"[PASS] (HTTP {status})")
        checks_passed += 1
    else:
        print(f"[FAIL] (HTTP {status}: {body})")

    # 5. Frontend /usage
    checks_total += 1
    usage_url = f"{frontend_base}/usage"
    print(f"[*] Checking AI Usage Frontend View ({usage_url})...", end=" ")
    status, body = make_request(usage_url)
    if status == 200:
        print("[PASS] (HTTP 200 Rendered)")
        checks_passed += 1
    else:
        print(f"[FAIL] (HTTP {status})")

    # 6. Telegram Alert Bot Connectivity Check
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    tg_chat = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if tg_token and tg_chat:
        checks_total += 1
        print("[*] Verifying Telegram Alert Bot Connectivity...", end=" ")
        tg_url = f"https://api.telegram.org/bot{tg_token}/getMe"
        status, body = make_request(tg_url)
        if status == 200 and isinstance(body, dict) and body.get("ok"):
            bot_name = body.get("result", {}).get("username", "Bot")
            print(f"[PASS] (Verified @{bot_name})")
            checks_passed += 1
        else:
            print(f"[FAIL] (Telegram API error: HTTP {status})")
    else:
        print("[*] Telegram Token not set in environment: Skipping live bot ping.")

    print("-" * 65)
    print(f"Smoke Test Summary: {checks_passed}/{checks_total} checks passed.")
    print("=" * 65)

    return 0 if checks_passed == checks_total else 1


if __name__ == "__main__":
    sys.exit(main())
