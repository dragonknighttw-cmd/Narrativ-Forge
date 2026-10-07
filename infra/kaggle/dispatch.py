from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import psycopg2

ROOT = Path(__file__).resolve().parent
META = ROOT / "kernel-metadata.json"
KERNEL_ID = os.environ["KAGGLE_KERNEL_ID"]
DATABASE_URL = os.environ["DATABASE_URL"]

def queued_job_exists() -> bool:
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            cur.execute("""SELECT 1 FROM processing_jobs WHERE job_type=%s AND status=%s AND (next_run_at IS NULL OR next_run_at <= NOW()) LIMIT 1""", ("real_processing", "queued"))
            return cur.fetchone() is not None
    finally:
        conn.close()

def kernel_status() -> str:
    result = subprocess.run(["kaggle", "kernels", "status", KERNEL_ID], capture_output=True, text=True)
    output = (result.stdout or "") + "\n" + (result.stderr or "")
    match = re.search(r"KernelWorkerStatus\.([A-Z_]+)", output)
    return match.group(1) if match else "UNKNOWN"

def main() -> int:
    if not queued_job_exists():
        print("No queued processing job")
        return 0
    status = kernel_status()
    print(f"Kaggle kernel status: {status}")
    if status in {"QUEUED", "RUNNING", "CANCEL_REQUESTED", "CANCEL_ACKNOWLEDGED"}:
        return 0
    metadata = json.loads(META.read_text(encoding="utf-8"))
    metadata["id"] = KERNEL_ID
    META.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    subprocess.run(["kaggle", "kernels", "push", "-p", str(ROOT), "--timeout", "3600"], check=True)
    print("Kaggle ephemeral worker launched")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())