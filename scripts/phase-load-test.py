#!/usr/bin/env python3
"""Small dependency-free HTTP load probe for staging/CI environments."""
from __future__ import annotations

import argparse
import concurrent.futures
import statistics
import time
import urllib.request


def request(url: str, timeout: float) -> float:
    started = time.perf_counter()
    with urllib.request.urlopen(url, timeout=timeout) as response:
        response.read(256)
        if response.status >= 400:
            raise RuntimeError(f"HTTP {response.status}")
    return time.perf_counter() - started


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8000/api/v1/health")
    parser.add_argument("--requests", type=int, default=50)
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()
    if args.requests < 1 or args.concurrency < 1:
        parser.error("requests and concurrency must be positive")
    started = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = [pool.submit(request, args.url, args.timeout) for _ in range(args.requests)]
        latencies = []
        failures = 0
        for future in futures:
            try:
                latencies.append(future.result())
            except Exception:
                failures += 1
    elapsed = time.perf_counter() - started
    if latencies:
        print(f"requests={args.requests} success={len(latencies)} failures={failures}")
        print(f"p50={statistics.median(latencies):.4f}s max={max(latencies):.4f}s total={elapsed:.4f}s")
    else:
        print(f"requests={args.requests} success=0 failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
