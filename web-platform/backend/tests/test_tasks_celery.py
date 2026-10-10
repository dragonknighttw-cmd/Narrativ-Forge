import json
import pytest
from celery import Celery
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from uuid import uuid4

from app.db import Base
from app.models import AuditEvent, Episode, FailedJob, Organization, ProcessingJob, Series
import app.db as app_db

from app.api.routes.jobs import retry_job
from app.workers import tasks as tasks_module
from app.workers import real_worker
from app.workers.celery_app import make_celery
from app.workers.tasks import handle_attempt_failure, retry_delay_seconds

pytestmark = pytest.mark.unit


@pytest.fixture
def testing_db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    TestingSession = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Monkeypatch the app's SessionLocal to use the testing engine so the
    # task will create sessions against this in-memory DB.
    orig_engine = app_db.engine
    orig_SessionLocal = app_db.SessionLocal
    app_db.engine = engine
    app_db.SessionLocal = TestingSession
    try:
        yield TestingSession
    finally:
        app_db.engine = orig_engine
        app_db.SessionLocal = orig_SessionLocal


def make_test_celery():
    celery = Celery("test", broker="memory://", backend="rpc://")
    celery.conf.task_always_eager = True
    celery.conf.task_eager_propagates = True
    return celery


def test_task_registration_and_config(testing_db):
    celery = make_celery("memory://")
    assert "narrativ.process_real_job" in celery.tasks
    assert "narrativ.dead_letter" in celery.tasks
    assert "narrativ.dispatch_due_real_jobs" in celery.tasks
    dispatch_schedule = celery.conf.beat_schedule["dispatch-due-real-jobs"]
    assert dispatch_schedule["task"] == "narrativ.dispatch_due_real_jobs"
    assert dispatch_schedule["schedule"] == 15.0
    assert celery.conf.result_backend is None
    assert not celery.conf.task_annotations
    assert celery.conf.task_serializer == "json"


def test_periodic_dispatch_task_calls_real_worker_dispatcher(testing_db, monkeypatch):
    celery = make_celery("memory://")
    dispatched = []
    monkeypatch.setattr(real_worker, "run_once", lambda db: dispatched.append(db) or 3)

    result = celery.tasks["narrativ.dispatch_due_real_jobs"].run()

    assert result == 3
    assert len(dispatched) == 1


def test_real_worker_dispatches_queued_jobs_without_running_them(testing_db, monkeypatch):
    Session = testing_db
    db = Session()
    ep = Episode(public_id="TST-DISPATCH", series_id="s1", episode_number=1, title="dispatch")
    db.add(ep)
    db.commit()
    job = ProcessingJob(episode_id=ep.id, job_type="real_processing", status="queued", progress=0)
    db.add(job)
    future_job = ProcessingJob(
        episode_id=ep.id,
        job_type="real_processing",
        status="queued",
        progress=0,
        next_run_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    db.add(future_job)
    due_job = ProcessingJob(
        episode_id=ep.id,
        job_type="real_processing",
        status="queued",
        progress=0,
        next_run_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )
    db.add(due_job)
    db.commit()
    job_id = job.id
    future_job_id = future_job.id
    due_job_id = due_job.id
    db.close()

    calls = {}

    class DummyCelery:
        def send_task(self, name, args=None, **kwargs):
            calls.setdefault("messages", []).append((name, args, kwargs))
            return None

    monkeypatch.setattr(real_worker, "get_celery", lambda: DummyCelery())
    monkeypatch.setattr(
        real_worker,
        "enqueue_real_job",
        lambda job_id: calls.setdefault("enqueued", []).append(job_id) or True,
    )
    dispatched_db = Session()
    try:
        dispatched = real_worker.run_once(dispatched_db)
        assert dispatched == 2
        assert set(calls["enqueued"]) == {job_id, due_job_id}
        assert dispatched_db.get(ProcessingJob, job_id).status == "queued"
        assert dispatched_db.get(ProcessingJob, future_job_id).status == "queued"
    finally:
        dispatched_db.close()


def test_dispatch_failure_leaves_job_queued_for_next_poll(testing_db, monkeypatch):
    Session = testing_db
    db = Session()
    ep = Episode(public_id="TST-DISPATCH-FAIL", series_id="s1", episode_number=1, title="dispatch fail")
    db.add(ep)
    db.commit()
    job = ProcessingJob(episode_id=ep.id, job_type="real_processing", status="queued", progress=0)
    db.add(job)
    db.commit()
    job_id = job.id
    db.close()

    class FailingCelery:
        def send_task(self, name, args=None, **kwargs):
            raise RuntimeError("broker unavailable")

    monkeypatch.setattr(real_worker, "get_celery", lambda: FailingCelery())
    monkeypatch.setattr(real_worker, "enqueue_real_job", lambda _job_id: False)
    dispatch_db = Session()
    assert real_worker.run_once(dispatch_db) == 0
    dispatch_db.close()

    verify_db = Session()
    assert verify_db.get(ProcessingJob, job_id).status == "queued"
    verify_db.close()

    class AvailableCelery:
        def send_task(self, name, args=None, **kwargs):
            assert name == "narrativ.process_real_job"
            assert args == [job_id]

    monkeypatch.setattr(real_worker, "get_celery", lambda: AvailableCelery())
    monkeypatch.setattr(real_worker, "enqueue_real_job", lambda _job_id: True)
    next_poll_db = Session()
    try:
        assert real_worker.run_once(next_poll_db) == 1
        assert next_poll_db.get(ProcessingJob, job_id).status == "queued"
    finally:
        next_poll_db.close()


def test_dispatcher_loop_repeats_and_closes_each_session(monkeypatch):
    sessions = []
    attempts = []

    class Session:
        def close(self):
            self.closed = True

    def session_factory():
        session = Session()
        sessions.append(session)
        return session

    def run_once(db):
        attempts.append(db)

    class StopLoop(Exception):
        pass

    def stop_after_second_sleep(seconds):
        assert seconds == 0
        if len(attempts) == 2:
            raise StopLoop

    monkeypatch.setattr(real_worker, "SessionLocal", session_factory)
    monkeypatch.setattr(real_worker, "run_once", run_once)
    with pytest.raises(StopLoop):
        real_worker.run_forever(poll_interval=0, sleep_fn=stop_after_second_sleep)

    assert len(attempts) == 2
    assert all(session.closed for session in sessions)


def test_task_skips_already_running_jobs(testing_db):
    celery = make_test_celery()
    process_task = tasks_module.register_tasks(celery)

    Session = testing_db
    db = Session()
    ep = Episode(public_id="TST-RUNNING", series_id="s1", episode_number=1, title="running")
    db.add(ep)
    db.commit()
    job = ProcessingJob(episode_id=ep.id, job_type="real_processing", status="running", progress=0)
    db.add(job)
    db.commit()
    job_id = job.id
    db.close()

    called = {"count": 0}

    def fake_run_real_job(job_id_arg, db_arg):
        called["count"] += 1

    orig = tasks_module.run_real_job
    tasks_module.run_real_job = fake_run_real_job
    try:
        result = process_task.apply(args=(job_id,))
        assert result.get() == job_id
        assert called["count"] == 0
    finally:
        tasks_module.run_real_job = orig


def test_task_skips_completed_jobs(testing_db, monkeypatch):
    celery = make_test_celery()
    process_task = tasks_module.register_tasks(celery)

    Session = testing_db
    db = Session()
    ep = Episode(public_id="TST-COMPLETED", series_id="s1", episode_number=1, title="completed")
    db.add(ep)
    db.commit()
    job = ProcessingJob(episode_id=ep.id, job_type="real_processing", status="completed", progress=100)
    db.add(job)
    db.commit()
    job_id = job.id
    db.close()

    monkeypatch.setattr(
        tasks_module,
        "run_real_job",
        lambda *_args, **_kwargs: pytest.fail("completed job executed"),
    )
    assert process_task.apply(args=(job_id,)).get() == job_id


def test_missing_job_fails_cleanly(testing_db):
    celery = make_test_celery()
    process_task = tasks_module.register_tasks(celery)
    fake_job_id = str(uuid4())
    with pytest.raises(Exception):
        # eager mode will execute synchronously and raise
        process_task.apply(args=(fake_job_id,))


def test_successful_execution_calls_run_real_job_and_closes_session(monkeypatch, testing_db):
    celery = make_test_celery()
    process_task = tasks_module.register_tasks(celery)

    # Create an Episode and ProcessingJob in the test DB
    Session = testing_db
    db = Session()
    ep = Episode(public_id="TST-1", series_id="s1", episode_number=1, title="t1")
    db.add(ep)
    db.commit()

    job = ProcessingJob(episode_id=ep.id, job_type="real_processing", status="queued", progress=0)
    db.add(job)
    db.commit()
    job_id = job.id
    db.close()

    called = {"count": 0}

    # Wrap the SessionLocal to capture close
    orig_SessionLocal = app_db.SessionLocal

    last_session = {"obj": None}

    def session_factory(*a, **kw):
        s = orig_SessionLocal(*a, **kw)
        last_session["obj"] = s
        orig_close = s.close

        def _close():
            s._closed_flag = True
            return orig_close()

        s.close = _close
        s._closed_flag = False
        return s

    app_db.SessionLocal = session_factory

    def fake_run_real_job(job_id_arg, db_arg, *, already_claimed=False):
        assert job_id_arg == job_id
        assert hasattr(db_arg, "execute")
        assert already_claimed is True
        assert db_arg.get(ProcessingJob, job_id_arg).status == "running"
        called["count"] += 1
        db_arg.execute(
            update(ProcessingJob)
            .where(ProcessingJob.id == job_id_arg)
            .values(status="completed")
        )
        db_arg.commit()
        return SimpleNamespace(status="completed")

    monkeypatch.setattr("app.workers.tasks.run_real_job", fake_run_real_job)

    try:
        res = process_task.apply(args=(job_id,))
        assert res.get() == job_id
        assert process_task.apply(args=(job_id,)).get() == job_id
        assert called["count"] == 1
        db2 = Session()
        j2 = db2.get(ProcessingJob, job_id)
        assert j2.status == "completed"
        db2.close()
        # verify the task's DB session was closed
        assert last_session["obj"]._closed_flag is True
    finally:
        app_db.SessionLocal = orig_SessionLocal


def test_failure_marks_job_failed_and_closes_session(monkeypatch, testing_db):
    celery = make_test_celery()
    process_task = tasks_module.register_tasks(celery)

    Session = testing_db
    db = Session()
    ep = Episode(public_id="TST-FAIL", series_id="s1", episode_number=1, title="t-fail")
    db.add(ep)
    db.commit()

    job = ProcessingJob(episode_id=ep.id, job_type="real_processing", status="queued", progress=0)
    db.add(job)
    db.commit()
    job_id = job.id
    db.close()

    orig_SessionLocal = app_db.SessionLocal
    last_session = {"obj": None}

    def session_factory(*a, **kw):
        s = orig_SessionLocal(*a, **kw)
        last_session["obj"] = s
        orig_close = s.close

        def _close():
            s._closed_flag = True
            return orig_close()

        s.close = _close
        s._closed_flag = False
        return s

    app_db.SessionLocal = session_factory

    def fake_run_real_job_raises(job_id_arg, db_arg, *, already_claimed=False):
        assert already_claimed is True
        raise RuntimeError("simulated failure")

    monkeypatch.setattr("app.workers.tasks.run_real_job", fake_run_real_job_raises)

    try:
        assert process_task.apply(args=(job_id,)).get() == job_id
        # A raised processing failure is recorded and scheduled for a later poll.
        db3 = Session()
        j3 = db3.get(ProcessingJob, job_id)
        assert j3.status == "queued"
        assert j3.retry_count == 1
        assert j3.next_run_at is not None
        assert j3.last_error == "simulated failure"
        db3.close()
        assert last_session["obj"]._closed_flag is True
    finally:
        app_db.SessionLocal = orig_SessionLocal


def test_failure_retry_schedule_uses_exact_first_backoff(testing_db, monkeypatch):
    fixed_now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    monkeypatch.setattr(tasks_module, "_now", lambda: fixed_now)
    celery = make_test_celery()
    task = tasks_module.register_tasks(celery)
    Session = testing_db
    db = Session()
    episode = Episode(public_id="TST-BACKOFF", series_id="s1", episode_number=1, title="backoff")
    db.add(episode)
    db.commit()
    job = ProcessingJob(episode_id=episode.id, job_type="real_processing", status="queued")
    db.add(job)
    db.commit()
    job_id = job.id
    db.close()

    def fail(job_id_arg, task_db, *, already_claimed=False):
        raise RuntimeError("first failure")

    monkeypatch.setattr(tasks_module, "run_real_job", fail)
    assert task.apply(args=(job_id,)).get() == job_id
    verify = Session()
    next_run_at = verify.get(ProcessingJob, job_id).next_run_at
    assert next_run_at.replace(tzinfo=timezone.utc) == fixed_now + timedelta(seconds=60)
    verify.close()


def test_retry_delay_is_capped_exponential():
    assert [retry_delay_seconds(attempt) for attempt in (1, 2, 3)] == [60, 120, 240]
    assert retry_delay_seconds(7) == 3600


def test_processing_timeout_failure_schedules_retry(testing_db, monkeypatch):
    celery = make_test_celery()
    task = tasks_module.register_tasks(celery)
    Session = testing_db
    db = Session()
    episode = Episode(public_id="TST-RETURN-FAIL", series_id="s1", episode_number=1, title="failed return")
    db.add(episode)
    db.commit()
    job = ProcessingJob(episode_id=episode.id, job_type="real_processing", status="queued")
    db.add(job)
    db.commit()
    job_id = job.id
    db.close()

    def failed_result(job_id_arg, task_db, *, already_claimed=False):
        assert already_claimed
        processing_job = task_db.get(ProcessingJob, job_id_arg)
        processing_job.status = "failed"
        processing_job.error_code = "PROCESSING_TIMEOUT"
        processing_job.error_message = "processing timeout"
        processing_job.last_error = "processing timeout"
        processing_job.completed_at = datetime.now(timezone.utc)
        task_db.commit()
        return processing_job

    monkeypatch.setattr(tasks_module, "run_real_job", failed_result)
    assert task.apply(args=(job_id,)).get() == job_id

    verify = Session()
    failed_job = verify.get(ProcessingJob, job_id)
    assert failed_job.status == "queued"
    assert failed_job.retry_count == 1
    assert failed_job.error_code == "PROCESSING_TIMEOUT"
    assert failed_job.last_error == "processing timeout"
    assert failed_job.next_run_at is not None
    verify.close()


def test_duplicate_failure_accounting_consumes_only_one_retry(testing_db):
    Session = testing_db
    db = Session()
    episode = Episode(public_id="TST-FAIL-CAS", series_id="s1", episode_number=1, title="cas")
    db.add(episode)
    db.commit()
    claimed_at = datetime.now(timezone.utc)
    job = ProcessingJob(
        episode_id=episode.id,
        job_type="real_processing",
        status="running",
        retry_count=0,
        started_at=claimed_at,
    )
    db.add(job)
    db.commit()

    first = handle_attempt_failure(db, job.id, claimed_at, "failure")
    second = handle_attempt_failure(db, job.id, claimed_at, "duplicate failure handler")
    assert first == ("scheduled", None)
    assert second == ("superseded", None)
    db.refresh(job)
    assert job.retry_count == 1
    assert job.status == "queued"
    db.close()


@pytest.mark.integration
def test_concurrent_postgresql_failure_handlers_consume_one_retry():
    if app_db.engine.dialect.name != "postgresql":
        pytest.skip("PostgreSQL is required to verify concurrent retry accounting")

    Session = sessionmaker(bind=app_db.engine)
    seed = Session()
    organization = Organization(
        name="Concurrent retry workspace",
        slug=f"concurrent-retry-{uuid4().hex}",
        plan="trial",
    )
    seed.add(organization)
    seed.flush()
    series = Series(title="Concurrent retry test", organization_id=organization.id)
    seed.add(series)
    seed.commit()
    episode = Episode(
        public_id=f"TST-CONCURRENT-{uuid4().hex[:8]}",
        series_id=series.id,
        organization_id=organization.id,
        episode_number=1,
        title="concurrent retry",
    )
    seed.add(episode)
    seed.commit()
    claimed_at = datetime.now(timezone.utc)
    job = ProcessingJob(
        episode_id=episode.id,
        job_type="real_processing",
        status="running",
        retry_count=0,
        started_at=claimed_at,
    )
    seed.add(job)
    seed.commit()
    job_id = job.id
    seed.close()

    from threading import Barrier

    barrier = Barrier(2)

    def fail_concurrently():
        session = Session()
        try:
            barrier.wait(timeout=5)
            return handle_attempt_failure(session, job_id, claimed_at, "concurrent failure")
        finally:
            session.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(lambda _: fail_concurrently(), range(2)))

    verify = Session()
    job = verify.get(ProcessingJob, job_id)
    assert sorted(outcome[0] for outcome in outcomes) == ["scheduled", "superseded"]
    assert job.retry_count == 1
    assert job.status == "queued"
    verify.close()


@pytest.mark.integration
def test_concurrent_postgresql_manual_retry_only_transitions_once():
    if app_db.engine.dialect.name != "postgresql":
        pytest.skip("PostgreSQL is required to verify concurrent manual retry")

    Session = sessionmaker(bind=app_db.engine)
    seed = Session()
    organization = Organization(
        name="Concurrent manual retry workspace",
        slug=f"manual-retry-{uuid4().hex}",
        plan="trial",
    )
    seed.add(organization)
    seed.flush()
    series = Series(title="Concurrent manual retry test", organization_id=organization.id)
    seed.add(series)
    seed.commit()
    episode = Episode(
        public_id=f"TST-MANUAL-CONCURRENT-{uuid4().hex[:8]}",
        organization_id=organization.id,
        series_id=series.id,
        episode_number=1,
        title="concurrent manual retry",
    )
    seed.add(episode)
    seed.commit()
    episode_id = episode.id
    organization_id = organization.id
    job = ProcessingJob(episode_id=episode_id, job_type="real_processing", status="failed")
    seed.add(job)
    seed.commit()
    job_id = job.id
    seed.close()

    from threading import Barrier

    barrier = Barrier(2)

    def retry_concurrently():
        session = Session()
        try:
            barrier.wait(timeout=5)
            try:
                retry_job(job_id, SimpleNamespace(organization_id=organization_id), None, session)
                return "queued"
            except Exception as exc:
                if getattr(exc, "status_code", None) == 409:
                    return "conflict"
                raise
        finally:
            session.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(lambda _: retry_concurrently(), range(2)))

    verify = Session()
    job = verify.get(ProcessingJob, job_id)
    assert sorted(outcomes) == ["conflict", "queued"]
    assert job.status == "queued"
    assert verify.query(ProcessingJob).filter_by(episode_id=episode_id).count() == 1
    verify.close()


def test_exhausted_job_is_persisted_audited_and_sent_to_dlq(testing_db, monkeypatch):
    celery = make_test_celery()
    task = tasks_module.register_tasks(celery)
    sends = []
    monkeypatch.setattr(
        celery,
        "send_task",
        lambda name, args=None, **kwargs: sends.append((name, args, kwargs)),
    )
    Session = testing_db
    db = Session()
    episode = Episode(public_id="TST-EXHAUST", series_id="s1", episode_number=1, title="exhaust")
    db.add(episode)
    db.commit()
    job = ProcessingJob(
        episode_id=episode.id,
        job_type="real_processing",
        status="queued",
        retry_count=3,
        max_retries=3,
    )
    db.add(job)
    db.commit()
    job_id = job.id
    db.close()

    orig_session_local = app_db.SessionLocal
    task_session = {}

    def tracked_session_factory():
        session = orig_session_local()
        task_session["session"] = session
        original_close = session.close
        session.close = lambda: (task_session.update(closed=True), original_close())[1]
        return session

    monkeypatch.setattr(app_db, "SessionLocal", tracked_session_factory)
    def fail(job_id_arg, task_db, *, already_claimed=False):
        raise RuntimeError("terminal failure")

    monkeypatch.setattr(tasks_module, "run_real_job", fail)
    assert task.apply(args=(job_id,)).get() == job_id

    verify = Session()
    exhausted = verify.get(ProcessingJob, job_id)
    failed_job = verify.query(FailedJob).filter_by(processing_job_id=job_id).one()
    event = verify.query(AuditEvent).filter_by(resource_id=job_id, action="processing.retry_exhausted").one()
    assert exhausted.status == "failed"
    assert exhausted.retry_count == exhausted.max_retries == 3
    assert exhausted.next_run_at is None
    assert failed_job.reason == "terminal failure"
    assert failed_job.dlq_published_at is not None
    assert json.loads(event.metadata_json)["retry_count"] == 3
    assert sends == [("narrativ.dead_letter", [job_id], {"queue": "dead_letter"})]
    assert task_session["closed"] is True
    verify.close()


def test_dlq_publish_failure_is_recovered_from_failed_jobs(testing_db, monkeypatch):
    celery = make_test_celery()
    task = tasks_module.register_tasks(celery)
    Session = testing_db
    db = Session()
    episode = Episode(public_id="TST-DLQ-RECOVER", series_id="s1", episode_number=1, title="recover")
    db.add(episode)
    db.commit()
    job = ProcessingJob(
        episode_id=episode.id,
        job_type="real_processing",
        status="queued",
        retry_count=3,
        max_retries=3,
    )
    db.add(job)
    db.commit()
    job_id = job.id
    db.close()

    monkeypatch.setattr(
        tasks_module,
        "run_real_job",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("exhausted")),
    )
    monkeypatch.setattr(
        celery,
        "send_task",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("broker offline")),
    )
    assert task.apply(args=(job_id,)).get() == job_id

    verify = Session()
    failed_job = verify.query(FailedJob).filter_by(processing_job_id=job_id).one()
    assert failed_job.dlq_published_at is None
    verify.close()

    sent = []
    monkeypatch.setattr(
        real_worker,
        "get_celery",
        lambda: SimpleNamespace(send_task=lambda *args, **kwargs: sent.append((args, kwargs))),
    )
    dispatcher_db = Session()
    assert real_worker.run_once(dispatcher_db) == 1
    failed_job = dispatcher_db.query(FailedJob).filter_by(processing_job_id=job_id).one()
    assert failed_job.dlq_published_at is not None
    assert sent == [(("narrativ.dead_letter",), {"args": [job_id], "queue": "dead_letter"})]
    dispatcher_db.close()


def test_manual_real_retry_preserves_identity_and_budget(testing_db):
    Session = testing_db
    db = Session()
    episode = Episode(public_id="TST-MANUAL-RETRY", series_id="s1", episode_number=1, title="manual")
    db.add(episode)
    db.commit()
    job = ProcessingJob(
        episode_id=episode.id,
        job_type="real_processing",
        status="failed",
        retry_count=1,
        max_retries=3,
        last_error="previous attempt",
        error_message="previous attempt",
        next_run_at=datetime.now(timezone.utc),
    )
    db.add(job)
    db.commit()
    job_id = job.id

    membership = SimpleNamespace(organization_id=episode.organization_id)
    retried = retry_job(job_id, membership, {}, db)
    assert retried.id == job_id
    assert retried.retry_count == 1
    assert retried.status == "queued"
    assert retried.next_run_at is None
    assert retried.last_error is None
    assert db.query(ProcessingJob).filter_by(episode_id=episode.id).count() == 1
    with pytest.raises(Exception):
        retry_job(job_id, membership, {}, db)
    db.close()


def test_manual_exhausted_retry_resets_budget_and_resolves_dlq(testing_db):
    Session = testing_db
    db = Session()
    episode = Episode(public_id="TST-MANUAL-DLQ", series_id="s1", episode_number=1, title="manual dlq")
    db.add(episode)
    db.commit()
    job = ProcessingJob(
        episode_id=episode.id,
        job_type="real_processing",
        status="failed",
        retry_count=3,
        max_retries=3,
        last_error="terminal",
    )
    db.add(job)
    db.commit()
    failed_job = FailedJob(processing_job_id=job.id, reason="terminal", retry_count=3)
    db.add(failed_job)
    db.commit()
    job_id = job.id

    membership = SimpleNamespace(organization_id=episode.organization_id)
    retried = retry_job(job_id, membership, {}, db)
    assert retried.id == job_id
    assert retried.retry_count == 0
    assert retried.status == "queued"
    assert retried.next_run_at is None
    assert db.query(FailedJob).filter_by(processing_job_id=job_id).one().resolved_at is not None
    assert db.query(ProcessingJob).filter_by(episode_id=episode.id).count() == 1
    db.close()

def test_stale_real_processing_job_is_requeued_with_retry_metadata(testing_db, monkeypatch):
    monkeypatch.setattr(real_worker.settings, "processing_timeout_seconds", 60)
    monkeypatch.setattr(real_worker.settings, "processing_timeout_grace_seconds", 0)
    Session = testing_db
    db = Session()
    episode = Episode(
        public_id=f"TST-STALE-{uuid4().hex[:8]}",
        series_id="s1",
        episode_number=1,
        title="stale worker job",
    )
    db.add(episode)
    db.commit()
    started_at = datetime.now(timezone.utc) - timedelta(hours=1)
    job = ProcessingJob(
        episode_id=episode.id,
        job_type="real_processing",
        status="running",
        retry_count=0,
        max_retries=3,
        started_at=started_at,
        progress=37,
    )
    db.add(job)
    db.commit()
    try:
        assert real_worker.recover_stale_real_jobs(db) == 1
        db.refresh(job)
        assert job.status == "queued"
        assert job.retry_count == 1
        assert job.next_run_at is not None
        assert job.progress == 0
        assert "lease expired" in job.last_error.lower()
    finally:
        db.close()


def test_recent_real_processing_job_is_not_recovered(testing_db, monkeypatch):
    monkeypatch.setattr(real_worker.settings, "processing_timeout_seconds", 3600)
    monkeypatch.setattr(real_worker.settings, "processing_timeout_grace_seconds", 120)
    Session = testing_db
    db = Session()
    episode = Episode(
        public_id=f"TST-NOT-STALE-{uuid4().hex[:8]}",
        series_id="s1",
        episode_number=1,
        title="recent worker job",
    )
    db.add(episode)
    db.commit()
    job = ProcessingJob(
        episode_id=episode.id,
        job_type="real_processing",
        status="running",
        retry_count=0,
        max_retries=3,
        started_at=datetime.now(timezone.utc) - timedelta(seconds=30),
        progress=37,
    )
    db.add(job)
    db.commit()

    try:
        assert real_worker.recover_stale_real_jobs(db) == 0
        db.refresh(job)
        assert job.status == "running"
        assert job.retry_count == 0
        assert job.progress == 37
    finally:
        db.close()

