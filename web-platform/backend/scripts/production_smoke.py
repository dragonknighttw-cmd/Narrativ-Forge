import os
import subprocess
import sys
import urllib.request
from pathlib import Path

api_url = os.environ.get("SMOKE_API_URL", "http://127.0.0.1:8000/api/v1")
checks = []

def check(name, fn):
    try:
        fn()
        checks.append((name, True, "ok"))
    except Exception as exc:
        checks.append((name, False, str(exc)))

check("health", lambda: urllib.request.urlopen(api_url + "/health", timeout=10).read())

def tool_version(binary):
    return lambda: subprocess.run([binary, "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=20)

check("ffmpeg", tool_version(os.environ.get("FFMPEG_BINARY", "ffmpeg")))
check("whisper", lambda: subprocess.run(
    [os.environ.get("WHISPER_COMMAND", "whisper"), "--help"],
    check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30,
))

if os.environ.get("SMOKE_VIDEO"):
    video = Path(os.environ["SMOKE_VIDEO"])
    if not video.exists():
        raise SystemExit(f"SMOKE_VIDEO not found: {video}")
    check("source-video-readable", lambda: video.stat().st_size > 0)

failed = [item for item in checks if not item[1]]
for name, ok, detail in checks:
    print(("PASS" if ok else "FAIL") + f" {name}: {detail}")
if failed:
    raise SystemExit(1)
