"""Check that a local media worker has its prerequisites without processing data.

The check deliberately does not download a Whisper model, start Redis, or start a
worker. It makes missing local prerequisites explicit before a user starts the
canonical Celery worker.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


@dataclass(frozen=True)
class Check:
    name: str
    status: str
    detail: str


def redact_url(value: str) -> str:
    """Return a connection URL without its credentials."""
    try:
        parsed = urlsplit(value)
    except ValueError:
        return "<invalid REDIS_URL>"
    safe_netloc = parsed.netloc.rsplit("@", 1)[-1]
    return urlunsplit((parsed.scheme, safe_netloc, parsed.path, "", ""))


def command_check(name: str, command: list[str]) -> Check:
    executable = shutil.which(command[0])
    if not executable:
        return Check(name, "fail", f"{command[0]} was not found on PATH")
    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return Check(name, "fail", f"{command[0]} could not run: {type(exc).__name__}")
    return Check(name, "pass", f"{Path(executable).name} is available")


def writable_directory_check(path: Path) -> Check:
    try:
        path.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=path, prefix=".preflight-", delete=True) as probe:
            probe.write(b"ok")
            probe.flush()
    except OSError as exc:
        return Check("work_directory", "fail", f"{path}: {exc}")
    return Check("work_directory", "pass", f"{path} is writable")


def disk_space_check(path: Path, minimum_gb: float) -> Check:
    target = path if path.exists() else path.parent
    free_gb = shutil.disk_usage(target).free / (1024**3)
    if free_gb < minimum_gb:
        return Check("disk_space", "fail", f"{free_gb:.1f} GiB free; {minimum_gb:.1f} GiB required")
    return Check("disk_space", "pass", f"{free_gb:.1f} GiB free")


def whisper_model_check(model: str, cache_dir: Path, required: bool) -> Check:
    model_path = cache_dir / f"{model}.pt"
    if model_path.is_file() and model_path.stat().st_size > 0:
        return Check("whisper_model", "pass", f"{model} is cached at {model_path}")
    status = "fail" if required else "warn"
    return Check(
        "whisper_model",
        status,
        f"{model} is not cached at {model_path}; download it before offline processing",
    )


def redis_check(redis_url: str | None) -> Check:
    if not redis_url:
        return Check("redis", "fail", "REDIS_URL or --redis-url is required for the local Celery worker")
    try:
        import redis
    except ImportError:
        return Check("redis", "fail", "Python package 'redis' is not installed")
    try:
        redis.Redis.from_url(redis_url, socket_connect_timeout=2, socket_timeout=2).ping()
    except (redis.exceptions.RedisError, TypeError, ValueError) as exc:
        return Check("redis", "fail", f"could not ping {redact_url(redis_url)}: {type(exc).__name__}")
    return Check("redis", "pass", f"reachable at {redact_url(redis_url)}")


def default_whisper_cache_dir() -> Path:
    cache_root = Path(os.environ.get("XDG_CACHE_HOME", "~/.cache")).expanduser()
    return cache_root / "whisper"


def run_preflight(args: argparse.Namespace) -> list[Check]:
    return [
        command_check("ffmpeg", [args.ffmpeg_binary, "-version"]),
        command_check("ffprobe", [args.ffprobe_binary, "-version"]),
        command_check("whisper_cli", [args.whisper_command, "--help"]),
        redis_check(args.redis_url),
        writable_directory_check(args.work_dir),
        disk_space_check(args.work_dir, args.min_free_gb),
        whisper_model_check(args.model, args.whisper_cache_dir, args.require_model),
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--redis-url", default=os.environ.get("REDIS_URL"))
    parser.add_argument("--ffmpeg-binary", default=os.environ.get("FFMPEG_BINARY", "ffmpeg"))
    parser.add_argument("--ffprobe-binary", default=os.environ.get("FFPROBE_BINARY", "ffprobe"))
    parser.add_argument("--whisper-command", default=os.environ.get("WHISPER_COMMAND", "whisper"))
    parser.add_argument("--model", default=os.environ.get("WHISPER_MODEL", "small"))
    parser.add_argument("--whisper-cache-dir", type=Path, default=default_whisper_cache_dir())
    parser.add_argument("--work-dir", type=Path, default=Path("./storage/local-media-runtime"))
    parser.add_argument("--min-free-gb", type=float, default=5.0)
    parser.add_argument("--require-model", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    if args.min_free_gb < 0:
        parser.error("--min-free-gb must be zero or greater")
    return args


def main() -> int:
    args = parse_args()
    checks = run_preflight(args)
    if args.as_json:
        print(json.dumps([asdict(check) for check in checks], indent=2))
    else:
        for check in checks:
            print(f"{check.status.upper():4} {check.name}: {check.detail}")
    return 0 if all(check.status != "fail" for check in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
