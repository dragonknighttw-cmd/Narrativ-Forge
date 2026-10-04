import multiprocessing
import os
from threading import Event, Lock
from types import SimpleNamespace
from uuid import uuid4

import pytest
from celery.contrib.testing.worker import start_worker
from pydantic import ValidationError

import app.db as app_db
from app.core.config import Settings, settings
from app.workers import concurrency
from app.workers import tasks as tasks_module
from app.workers.celery_app import make_celery

pytestmark = pytest.mark.unit


class FakeJob:
    def __init__(self, job_id):
        self.id = job_id
        self.status = "queued"


class FakeSession:
    def get(self, model, job_id):
        return FakeJob(job_id)

    def execute(self, _statement):
        return SimpleNamespace(rowcount=1)

    def commit(self):
        pass

    def close(self):
        pass


def install_fake_processing_db(monkeypatch):
    monkeypatch.setattr(app_db, "SessionLocal", FakeSession)
    monkeypatch.setattr(tasks_module, "_claim_job", lambda *_args: True)


@pytest.mark.parametrize("value", [1, 2])
def test_worker_max_concurrency_accepts_positive_integers(monkeypatch, value):
    monkeypatch.setenv("WORKER_MAX_CONCURRENCY", str(value))

    configured = Settings(_env_file=None)

    assert configured.worker_max_concurrency == value


@pytest.mark.parametrize("value", ["0", "-1", "invalid"])
def test_worker_max_concurrency_rejects_invalid_values(monkeypatch, value):
    monkeypatch.setenv("WORKER_MAX_CONCURRENCY", value)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_worker_max_concurrency_defaults_to_one(monkeypatch):
    monkeypatch.delenv("WORKER_MAX_CONCURRENCY", raising=False)

    assert Settings(_env_file=None).worker_max_concurrency == 1


@pytest.mark.parametrize(
    ("pool_concurrency", "limit"),
    [(1, 1), (2, 1), (2, 2)],
)
def test_celery_pool_and_processing_semaphore_enforce_limit(
    monkeypatch,
    pool_concurrency,
    limit,
):
    monkeypatch.setattr(settings, "worker_max_concurrency", limit)
    monkeypatch.setattr(concurrency, "processing_semaphore", concurrency.ProcessingSemaphore(limit))
    app = make_celery("memory://")
    app.conf.result_backend = "cache+memory://"
    assert app.conf.worker_concurrency == limit
    process_task = app.tasks["narrativ.process_real_job"]
    at_capacity = Event()
    all_started = Event()
    release = Event()
    all_complete = Event()
    lock = Lock()
    state = {"active": 0, "max_active": 0, "started": 0, "completed": 0}
    total_jobs = limit + 1

    install_fake_processing_db(monkeypatch)

    def simulated_real_processing(job_id, _db, *, already_claimed):
        assert already_claimed
        with lock:
            state["active"] += 1
            state["started"] += 1
            state["max_active"] = max(state["max_active"], state["active"])
            if state["active"] == limit:
                at_capacity.set()
            if state["started"] == total_jobs:
                all_started.set()

        try:
            if not release.wait(timeout=10):
                raise TimeoutError("test did not release simulated processing")
            return SimpleNamespace(status="completed")
        finally:
            with lock:
                state["active"] -= 1
                state["completed"] += 1
                if state["completed"] == total_jobs:
                    all_complete.set()

    monkeypatch.setattr(tasks_module, "run_real_job", simulated_real_processing)

    with start_worker(
        app,
        concurrency=pool_concurrency,
        pool="threads",
        perform_ping_check=False,
    ):
        job_ids = [
            f"processing-{pool_concurrency}-{limit}-{index}-{uuid4().hex}"
            for index in range(total_jobs)
        ]
        results = [process_task.delay(job_id) for job_id in job_ids]

        assert at_capacity.wait(timeout=5)
        assert not all_started.wait(timeout=0.2)
        release.set()
        assert all_complete.wait(timeout=5)
        assert [result.get(timeout=5) for result in results] == job_ids

    assert state["active"] == 0
    assert state["max_active"] == limit
    assert state["completed"] == total_jobs


def _run_process_with_semaphore(state, lock, all_attempting, at_capacity, release):
    with lock:
        state[2] += 1
        if state[2] == 3:
            all_attempting.set()
    with concurrency.processing_semaphore.acquire():
        with lock:
            state[0] += 1
            state[1] = max(state[1], state[0])
            if state[0] == 2:
                at_capacity.set()
        try:
            if not release.wait(timeout=10):
                raise TimeoutError("test did not release child processing")
        finally:
            with lock:
                state[0] -= 1


@pytest.mark.skipif(os.name != "posix", reason="Celery production prefork uses POSIX process sharing")
def test_processing_semaphore_is_shared_across_prefork_processes(monkeypatch):
    context = multiprocessing.get_context("fork")
    semaphore = concurrency.ProcessingSemaphore(2)
    monkeypatch.setattr(concurrency, "processing_semaphore", semaphore)
    state = context.Array("i", [0, 0, 0], lock=False)
    lock = context.Lock()
    all_attempting = context.Event()
    at_capacity = context.Event()
    release = context.Event()
    processes = [
        context.Process(
            target=_run_process_with_semaphore,
            args=(state, lock, all_attempting, at_capacity, release),
        )
        for _ in range(3)
    ]
    try:
        for process in processes:
            process.start()
        assert all_attempting.wait(timeout=5)
        assert at_capacity.wait(timeout=5)
        assert state[0] == 2
        assert state[1] == 2
        release.set()
        for process in processes:
            process.join(timeout=5)
            assert process.exitcode == 0
        assert state[0] == 0
        assert state[1] == 2
    finally:
        release.set()
        for process in processes:
            if process.is_alive():
                process.terminate()
                process.join(timeout=5)


def _hold_processing_slot(entered, release):
    with concurrency.processing_semaphore.acquire():
        entered.set()
        release.wait(timeout=10)


@pytest.mark.skipif(os.name != "posix", reason="Celery production prefork uses POSIX file locks")
def test_processing_slot_is_released_when_prefork_child_is_killed(monkeypatch):
    context = multiprocessing.get_context("fork")
    monkeypatch.setattr(concurrency, "processing_semaphore", concurrency.ProcessingSemaphore(1))
    holder_entered = context.Event()
    holder_release = context.Event()
    waiter_entered = context.Event()
    waiter_release = context.Event()
    holder = context.Process(target=_hold_processing_slot, args=(holder_entered, holder_release))
    waiter = context.Process(target=_hold_processing_slot, args=(waiter_entered, waiter_release))
    try:
        holder.start()
        assert holder_entered.wait(timeout=5)
        waiter.start()
        holder.terminate()
        holder.join(timeout=5)
        assert holder.exitcode is not None
        assert waiter_entered.wait(timeout=5)
        waiter_release.set()
        waiter.join(timeout=5)
        assert waiter.exitcode == 0
    finally:
        holder_release.set()
        waiter_release.set()
        for process in (holder, waiter):
            if process.is_alive():
                process.terminate()
                process.join(timeout=5)


@pytest.mark.parametrize(
    "outcome",
    ["success", "processing_failure", "timeout", "unexpected_exception"],
)
def test_celery_pool_slot_is_reusable_after_task_termination(monkeypatch, outcome):
    monkeypatch.setattr(settings, "worker_max_concurrency", 1)
    monkeypatch.setattr(concurrency, "processing_semaphore", concurrency.ProcessingSemaphore(1))
    app = make_celery("memory://")
    app.conf.result_backend = "cache+memory://"
    process_task = app.tasks["narrativ.process_real_job"]
    install_fake_processing_db(monkeypatch)
    completed = Event()
    followup_ran = Event()

    def finish_processing(job_id, _db, *, already_claimed):
        assert already_claimed
        if job_id == "first-job":
            completed.set()
            if outcome == "processing_failure":
                return SimpleNamespace(
                    status="failed",
                    error_code="PROCESSING_COMMAND_FAILED",
                    error_message="processing failed",
                    last_error="processing failed",
                )
            if outcome == "timeout":
                return SimpleNamespace(
                    status="failed",
                    error_code="PROCESSING_TIMEOUT",
                    error_message="processing timeout",
                    last_error="processing timeout",
                )
            if outcome == "unexpected_exception":
                raise RuntimeError("unexpected processing error")
            return SimpleNamespace(status="completed")
        else:
            followup_ran.set()
            return SimpleNamespace(status="completed")

    monkeypatch.setattr(tasks_module, "run_real_job", finish_processing)
    monkeypatch.setattr(
        tasks_module,
        "handle_attempt_failure",
        lambda *_args: ("scheduled", None),
    )

    with start_worker(
        app,
        concurrency=1,
        pool="threads",
        perform_ping_check=False,
    ):
        first_result = process_task.delay("first-job")
        assert completed.wait(timeout=5)
        assert first_result.get(timeout=5) == "first-job"
        followup_result = process_task.delay("followup-job")
        assert followup_ran.wait(timeout=5)
        assert followup_result.get(timeout=5) == "followup-job"
