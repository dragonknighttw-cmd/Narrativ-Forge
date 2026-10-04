import errno
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import Settings, settings
from app.db import Base
from app.models import Asset, Episode, ProcessingJob, Series
from app.services import real_processing


def _pid_is_running(pid: int) -> bool:
    if os.name == "posix" and sys.platform.startswith("linux"):
        stat_path = Path(f"/proc/{pid}/stat")
        if stat_path.exists() and stat_path.read_text(encoding="utf-8").split()[2] == "Z":
            return False
    try:
        os.kill(pid, 0)
    except OSError as exc:
        if exc.errno == errno.ESRCH or getattr(exc, "winerror", None) in {87, 1168}:
            return False
        if exc.errno == errno.EPERM or getattr(exc, "winerror", None) == 5:
            return True
        raise
    return True


def _wait_until_dead(pid: int) -> None:
    deadline = time.monotonic() + 5
    while _pid_is_running(pid) and time.monotonic() < deadline:
        time.sleep(0.05)
    assert not _pid_is_running(pid)


def test_run_captures_successful_process_output():
    result = real_processing._run(
        [sys.executable, "-c", "print('stdout'); import sys; print('stderr', file=sys.stderr)"],
        timeout=5,
    )

    assert result.stdout.strip() == "stdout"
    assert result.stderr.strip() == "stderr"
    assert result.returncode == 0


def test_run_preserves_nonzero_exit_and_captured_output():
    with pytest.raises(subprocess.CalledProcessError) as raised:
        real_processing._run(
            [
                sys.executable,
                "-c",
                "import sys; print('failure output'); print('failure detail', file=sys.stderr); sys.exit(7)",
            ],
            timeout=5,
        )

    assert raised.value.returncode == 7
    assert raised.value.output.strip() == "failure output"
    assert raised.value.stderr.strip() == "failure detail"


def test_timeout_terminates_child_tree_and_reaps_parent(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "processing_timeout_grace_seconds", 0.2)
    child_pid_file = tmp_path / "child.pid"
    child_code = "import time; time.sleep(60)"
    parent_code = (
        "import subprocess,sys,time; "
        "child=subprocess.Popen([sys.executable,'-c',sys.argv[2]]); "
        "open(sys.argv[1],'w').write(str(child.pid)); "
        "print('started',flush=True); time.sleep(60)"
    )
    processes = []
    original_popen = subprocess.Popen

    def tracking_popen(*args, **kwargs):
        process = original_popen(*args, **kwargs)
        processes.append(process)
        return process

    monkeypatch.setattr(real_processing.subprocess, "Popen", tracking_popen)
    started = time.monotonic()
    with pytest.raises(subprocess.TimeoutExpired) as raised:
        real_processing._run(
            [sys.executable, "-c", parent_code, str(child_pid_file), child_code],
            timeout=0.2,
        )
    elapsed = time.monotonic() - started

    assert child_pid_file.exists()
    child_pid = int(child_pid_file.read_text(encoding="utf-8"))
    assert raised.value.output.strip() == "started"
    assert elapsed >= 0.2
    assert processes[0].poll() is not None
    _wait_until_dead(child_pid)


@pytest.mark.skipif(os.name != "posix", reason="POSIX process-group signals are unavailable")
def test_process_exiting_on_sigterm_does_not_receive_sigkill(monkeypatch):
    monkeypatch.setattr(settings, "processing_timeout_grace_seconds", 1)
    sent_signals = []
    original_killpg = os.killpg

    def tracking_killpg(process_group_id, sig):
        if sig in (signal.SIGTERM, signal.SIGKILL):
            sent_signals.append(sig)
        return original_killpg(process_group_id, sig)

    monkeypatch.setattr(real_processing.os, "killpg", tracking_killpg)
    code = (
        "import signal,time; "
        "signal.signal(signal.SIGTERM, lambda *_: exit(0)); "
        "time.sleep(60)"
    )

    with pytest.raises(subprocess.TimeoutExpired):
        real_processing._run([sys.executable, "-c", code], timeout=0.2)

    assert sent_signals == [signal.SIGTERM]


@pytest.mark.skipif(os.name != "posix", reason="POSIX process-group signals are unavailable")
def test_stubborn_process_receives_sigkill_after_grace(monkeypatch):
    grace_seconds = 0.25
    monkeypatch.setattr(settings, "processing_timeout_grace_seconds", grace_seconds)
    sent_signals = []
    original_killpg = os.killpg

    def tracking_killpg(process_group_id, sig):
        if sig in (signal.SIGTERM, signal.SIGKILL):
            sent_signals.append(sig)
        return original_killpg(process_group_id, sig)

    monkeypatch.setattr(real_processing.os, "killpg", tracking_killpg)
    started = time.monotonic()

    with pytest.raises(subprocess.TimeoutExpired):
        real_processing._run(
            [sys.executable, "-c", "import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(60)"],
            timeout=0.2,
        )

    elapsed = time.monotonic() - started
    assert sent_signals == [signal.SIGTERM, signal.SIGKILL]
    assert elapsed >= 0.2 + grace_seconds - 0.05


def test_timeout_failure_is_persisted_as_processing_failure(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = session_factory()
    try:
        series = Series(title="Timeout processing test")
        db.add(series)
        db.flush()
        episode = Episode(
            public_id="TST-PROCESS-TIMEOUT",
            series_id=series.id,
            episode_number=1,
            title="Timeout processing",
            status="processing",
            current_step="processing",
        )
        db.add(episode)
        db.flush()
        asset = Asset(
            episode_id=episode.id,
            asset_type="video",
            original_filename="source.mp4",
            storage_provider="local",
            local_path="unused-source.mp4",
            mime_type="video/mp4",
            file_size_bytes=1,
            version=1,
            status="uploaded",
        )
        db.add(asset)
        db.flush()
        job = ProcessingJob(
            episode_id=episode.id,
            job_type="real_processing",
            status="running",
            input_asset_id=asset.id,
        )
        db.add(job)
        db.commit()

        monkeypatch.setattr(real_processing, "materialize_asset", lambda *_args: Path("unused-source.mp4"))

        def timed_out(command, *, timeout):
            raise subprocess.TimeoutExpired(command, timeout, output="partial output", stderr="partial error")

        monkeypatch.setattr(real_processing, "_run", timed_out)
        result = real_processing.run_real_job(job.id, db, already_claimed=True)

        assert result.status == "failed"
        assert result.error_code == "PROCESSING_TIMEOUT"
        assert result.last_error == "Real media processing exceeded the configured timeout"
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_timeout_settings_are_read_from_environment(monkeypatch):
    monkeypatch.setenv("PROCESSING_TIMEOUT_SECONDS", "45")
    monkeypatch.setenv("PROCESSING_TIMEOUT_GRACE_SECONDS", "3")

    configured = Settings(_env_file=None)

    assert configured.processing_timeout_seconds == 45
    assert configured.processing_timeout_grace_seconds == 3
