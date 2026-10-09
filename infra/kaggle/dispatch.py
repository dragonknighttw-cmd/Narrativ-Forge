from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import psycopg2

ROOT = Path(__file__).resolve().parent
META = ROOT / "kernel-metadata.json"
KERNEL_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+/[A-Za-z0-9_-]+$")
ACTIVE_KERNEL_STATES = {
    "QUEUED",
    "RUNNING",
    "CANCEL_REQUESTED",
    "CANCEL_ACKNOWLEDGED",
}
TERMINAL_KERNEL_STATES = {"COMPLETE", "ERROR", "CANCELLED", "IDLE"}


def validate_kernel_id(value: str | None) -> str:
    """Validate the non-secret Kaggle owner/kernel-slug identifier."""
    candidate = (value or "").strip()
    if not KERNEL_ID_PATTERN.fullmatch(candidate):
        raise ValueError(
            "KAGGLE_KERNEL_ID must use owner/kernel-slug format "
            "(for example: thuwon/narrativ-forge); value was not printed."
        )
    return candidate


def queued_job_exists(database_url: str) -> bool:
    conn = psycopg2.connect(database_url, connect_timeout=10)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM processing_jobs
                WHERE job_type = %s
                  AND status = %s
                  AND (next_run_at IS NULL OR next_run_at <= NOW())
                LIMIT 1
                """,
                ("real_processing", "queued"),
            )
            return cur.fetchone() is not None
    finally:
        conn.close()


def kernel_status(kernel_id: str) -> str:
    result = subprocess.run(
        ["kaggle", "kernels", "status", kernel_id],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if result.returncode != 0:
        # Do not echo CLI output: provider errors may contain sensitive details.
        raise RuntimeError(
            "Kaggle kernel status lookup failed. Verify KAGGLE_API_TOKEN, "
            "kernel ownership/access, and the configured kernel ID."
        )

    output = (result.stdout or "") + "\n" + (result.stderr or "")
    match = re.search(r"KernelWorkerStatus\.([A-Z_]+)", output)
    if not match:
        raise RuntimeError(
            "Kaggle returned an unrecognized kernel status; refusing to push "
            "a new session to avoid duplicate dispatch."
        )
    status = match.group(1)
    if status not in ACTIVE_KERNEL_STATES | TERMINAL_KERNEL_STATES:
        raise RuntimeError(
            f"Kaggle returned unsupported kernel status {status!r}; "
            "refusing to dispatch."
        )
    return status


def main() -> int:
    kernel_id = validate_kernel_id(os.environ.get("KAGGLE_KERNEL_ID"))
    database_url = os.environ.get("DATABASE_URL", "").strip()
    if not database_url:
        raise ValueError(
            "DATABASE_URL is required (set Actions secret "
            "KAGGLE_DISPATCH_DATABASE_URL); the value is not printed."
        )
    if not os.environ.get("KAGGLE_API_TOKEN", "").strip():
        raise ValueError(
            "KAGGLE_API_TOKEN is required; configure it as a GitHub Actions "
            "secret. The value is not printed."
        )

    if not queued_job_exists(database_url):
        print("No due real_processing jobs are queued; Kaggle was not launched.")
        return 0

    status = kernel_status(kernel_id)
    print(f"Kaggle kernel status: {status}")
    if status in ACTIVE_KERNEL_STATES:
        print("A Kaggle session is already active; skipping duplicate dispatch.")
        return 0

    metadata = json.loads(META.read_text(encoding="utf-8"))
    metadata["id"] = kernel_id
    META.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    subprocess.run(
        ["kaggle", "kernels", "push", "-p", str(ROOT), "--timeout", "3600"],
        check=True,
        timeout=180,
    )
    print("Kaggle ephemeral worker push submitted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
