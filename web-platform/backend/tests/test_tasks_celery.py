import pytest
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from uuid import uuid4

from app.db import Base
from app.models import Episode, ProcessingJob
import app.db as app_db

from app.workers import tasks as tasks_module
from app.workers import real_worker
from app.workers.celery_app import make_celery


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


def test_real_worker_dispatches_queued_jobs_without_running_them(testing_db, monkeypatch):
    Session = testing_db
    db = Session()
    ep = Episode(public_id="TST-DISPATCH", series_id="s1", episode_number=1, title="dispatch")
    db.add(ep)
    db.commit()
    job = ProcessingJob(episode_id=ep.id, job_type="real_processing", status="queued", progress=0)
    db.add(job)
    db.commit()
    job_id = job.id
    db.close()

    calls = {}

    class DummyCelery:
        def send_task(self, name, args=None, **kwargs):
            calls["name"] = name
            calls["args"] = args
            return None

    monkeypatch.setattr(real_worker, "get_celery", lambda: DummyCelery())
    dispatched_db = Session()
    try:
        dispatched = real_worker.run_once(dispatched_db)
        assert dispatched == 1
        assert calls["name"] == "narrativ.process_real_job"
        assert calls["args"] == [job_id]
        assert dispatched_db.get(ProcessingJob, job_id).status == "queued"
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
    dispatch_db = Session()
    with pytest.raises(RuntimeError, match="broker unavailable"):
        real_worker.run_once(dispatch_db)
    dispatch_db.close()

    verify_db = Session()
    assert verify_db.get(ProcessingJob, job_id).status == "queued"
    verify_db.close()

    class AvailableCelery:
        def send_task(self, name, args=None, **kwargs):
            assert name == "narrativ.process_real_job"
            assert args == [job_id]

    monkeypatch.setattr(real_worker, "get_celery", lambda: AvailableCelery())
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

    monkeypatch.setattr("app.workers.tasks.run_real_job", fake_run_real_job)

    try:
        res = process_task.apply(args=(job_id,))
        assert res.get() == job_id
        assert process_task.apply(args=(job_id,)).get() == job_id
        assert called["count"] == 1
        db2 = Session()
        j2 = db2.get(ProcessingJob, job_id)
        assert j2.status == "running"
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
        with pytest.raises(Exception):
            process_task.apply(args=(job_id,))
        # verify job is marked failed
        db3 = Session()
        j3 = db3.get(ProcessingJob, job_id)
        assert j3.status == "failed"
        assert j3.error_message is not None
        db3.close()
        assert last_session["obj"]._closed_flag is True
    finally:
        app_db.SessionLocal = orig_SessionLocal
