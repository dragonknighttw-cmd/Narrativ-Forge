"""Automated real-worker smoke test used by CI and release verification.

This intentionally uses local storage and a generated media fixture so it does not
need production credentials. It still exercises the real Docker worker, Celery,
PostgreSQL, Redis, FFmpeg, Whisper CLI, storage write path, transcript creation,
and subtitle creation.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Asset, Episode, ProcessingJob, Series, Subtitle
from app.workers.celery_app import get_celery


def run(command: list[str], timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, text=True, capture_output=True, timeout=timeout)


def make_fixture(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            os.getenv("FFMPEG_BINARY", "ffmpeg"),
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=black:s=640x360:r=30:d=3",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:sample_rate=48000:duration=3",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-shortest",
            str(path),
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-dir", default="/app/storage/worker-smoke")
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()

    work_dir = Path(args.work_dir)
    source = work_dir / "source.mp4"
    make_fixture(source)

    database_url = os.environ["DATABASE_URL"]
    engine = create_engine(database_url, pool_pre_ping=True)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    db = session_factory()
    try:
        series = Series(title="CI worker smoke series")
        db.add(series)
        db.flush()
        episode = Episode(
            public_id=f"CI-WORKER-{int(time.time())}",
            series_id=series.id,
            episode_number=1,
            title="CI worker smoke episode",
            status="in_production",
            current_step="processing",
        )
        db.add(episode)
        db.flush()
        asset = Asset(
            episode_id=episode.id,
            asset_type="video",
            original_filename=source.name,
            storage_provider="local",
            local_path=str(source),
            mime_type="video/mp4",
            file_size_bytes=source.stat().st_size,
            version=1,
            status="uploaded",
        )
        db.add(asset)
        db.flush()
        job = ProcessingJob(
            episode_id=episode.id,
            job_type="real_processing",
            status="queued",
            input_asset_id=asset.id,
            max_retries=0,
        )
        db.add(job)
        db.commit()
        job_id = job.id
    finally:
        db.close()

    celery = get_celery()
    celery.send_task("narrativ.process_real_job", args=[job_id])

    deadline = time.monotonic() + args.timeout
    while time.monotonic() < deadline:
        db = session_factory()
        try:
            current = db.get(ProcessingJob, job_id)
            if current and current.status in {"completed", "failed"}:
                if current.status == "failed":
                    raise RuntimeError(
                        f"worker smoke failed: code={final.error_code} "
                        f"message={final.error_message or final.last_error}"
                    )
                output = db.get(Asset, final.output_asset_id) if final.output_asset_id else None
                transcript = (
                    db.query(Asset)
                    .filter(Asset.episode_id == current.episode_id, Asset.asset_type == "transcript")
                    .order_by(Asset.version.desc())
                    .first()
                )
                subtitle = (
                    db.query(Subtitle)
                    .filter(Subtitle.episode_id == current.episode_id, Subtitle.is_current.is_(True))
                    .first()
                )
                if output is None or transcript is None or subtitle is None:
                    raise RuntimeError("worker smoke completed without output/transcript/current subtitle")
                if not output.local_path or not Path(output.local_path).is_file():
                    raise RuntimeError("processed output file is missing")
                if not transcript.local_path or not Path(transcript.local_path).is_file():
                    raise RuntimeError("transcript file is missing")
                print(
                    "WORKER_SMOKE_OK",
                    f"job={job_id}",
                    f"output={output.local_path}",
                    f"transcript={transcript.local_path}",
                    f"subtitle_version={subtitle.version}",
                    f"duration={current.duration_seconds}",
                )
                return 0
        finally:
            db.close()
        time.sleep(3)

    raise TimeoutError(f"worker smoke timed out after {args.timeout}s; job_id={job_id}")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"WORKER_SMOKE_FAILED: {exc}", file=sys.stderr)
        raise
