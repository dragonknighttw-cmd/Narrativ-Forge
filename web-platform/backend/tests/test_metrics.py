import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from celery import Celery
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.requests import Request
from starlette.responses import Response

from app import metrics
from app.db import Base
from app.models import Episode, ProcessingJob, Series
from app.workers import tasks as tasks_module

pytestmark = pytest.mark.unit


class FakePipeline:
    def __init__(self):
        self.updates = []
        self.executed = False

    def hincrby(self, key, field, value):
        self.updates.append((key, field, value))
        return self

    def hincrbyfloat(self, key, field, value):
        self.updates.append((key, field, value))
        return self

    def execute(self):
        self.executed = True


class FakeRedis:
    def __init__(self, values=None):
        self.values = values or {}
        self.last_pipeline = None

    def pipeline(self, *, transaction):
        assert transaction is True
        self.last_pipeline = FakePipeline()
        return self.last_pipeline

    def hgetall(self, key):
        assert key == metrics.METRICS_KEY
        return self.values


@pytest.fixture
def metrics_db(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    monkeypatch.setattr(metrics.db, "SessionLocal", session_factory)
    yield session_factory
    engine.dispose()


def test_worker_metric_updates_are_atomic_and_use_bounded_fields(monkeypatch):
    client = FakeRedis()
    monkeypatch.setattr(metrics, "_shared_metrics_client", lambda: client)

    metrics.record_processing_finished("retry", 0.2, timed_out=True)

    assert client.last_pipeline.executed is True
    updates = client.last_pipeline.updates
    assert updates.count((metrics.METRICS_KEY, "counter|retry", 1)) == 1
    assert (metrics.METRICS_KEY, "counter|timeout", 1) in updates
    assert (metrics.METRICS_KEY, "histogram_count|retry", 1) in updates
    assert all(update[1].startswith(("counter|", "histogram_")) for update in updates)
    assert all("job" not in update[1] and "user" not in update[1] for update in updates)


def test_metrics_endpoint_exposes_worker_metrics_and_separate_queue_depth(
    monkeypatch, metrics_db
):
    session = metrics_db()
    series = Series(title="metrics")
    session.add(series)
    session.flush()
    episode = Episode(
        public_id="METRICS",
        series_id=series.id,
        episode_number=1,
        title="metrics",
    )
    session.add(episode)
    session.flush()
    session.add_all(
        [
            ProcessingJob(episode_id=episode.id, job_type="real_processing", status="queued"),
            ProcessingJob(
                episode_id=episode.id,
                job_type="real_processing",
                status="queued",
                next_run_at=datetime.now(timezone.utc) + timedelta(hours=1),
            ),
            ProcessingJob(episode_id=episode.id, job_type="real_processing", status="completed"),
        ]
    )
    session.commit()
    session.close()

    values = {
        b"counter|started": b"1",
        b"counter|completed": b"1",
        b"counter|timeout": b"1",
        b"histogram_count|completed": b"1",
        b"histogram_sum|completed": b"0.2",
        b"histogram_bucket|completed|+Inf": b"1",
    }
    values.update(
        {
            f"histogram_bucket|completed|{bound}".encode(): b"1"
            for bound in metrics.DURATION_BUCKETS
            if bound >= 0.2
        }
    )
    monkeypatch.setattr(metrics, "_shared_metrics_client", lambda: FakeRedis(values))

    response = metrics.metrics_endpoint()
    exposition = response.body.decode()

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain; version=")
    assert 'narrativ_processing_jobs_total{status="started"} 1.0' in exposition
    assert "narrativ_processing_timeouts_total 1.0" in exposition
    assert 'narrativ_processing_duration_seconds_count{outcome="completed"} 1.0' in exposition
    assert 'narrativ_job_queue_depth{schedule="due"} 1.0' in exposition
    assert 'narrativ_job_queue_depth{schedule="scheduled"} 1.0' in exposition
    assert 'narrativ_job_queue_depth{schedule="running"}' not in exposition


def test_metrics_source_failure_returns_generic_service_unavailable(monkeypatch):
    def unavailable():
        raise RuntimeError("private Redis connection details")

    monkeypatch.setattr(metrics, "_shared_metrics_client", unavailable)

    with pytest.raises(HTTPException) as error:
        metrics.metrics_endpoint()

    assert getattr(error.value, "status_code", None) == 503
    assert "private Redis connection details" not in str(error.value)


def test_worker_metrics_write_failure_is_best_effort(monkeypatch):
    def unavailable():
        raise RuntimeError("private Redis connection details")

    monkeypatch.setattr(metrics, "_shared_metrics_client", unavailable)
    metrics.record_processing_started()
    metrics.record_processing_finished("failed", 1.0)


@pytest.mark.parametrize(
    ("result_status", "error_code", "expected_outcome", "expected_job_status"),
    [
        ("completed", None, "completed", "completed"),
        ("failed", "PROCESSING_TIMEOUT", "retry", "queued"),
    ],
)
def test_celery_task_records_processing_metrics_without_affecting_outcome(
    monkeypatch,
    metrics_db,
    result_status,
    error_code,
    expected_outcome,
    expected_job_status,
):
    session = metrics_db()
    series = Series(title="task metrics")
    session.add(series)
    session.flush()
    episode = Episode(
        public_id=f"TASK-METRICS-{result_status}",
        series_id=series.id,
        episode_number=1,
        title="task metrics",
    )
    session.add(episode)
    session.flush()
    job = ProcessingJob(episode_id=episode.id, job_type="real_processing", status="queued")
    session.add(job)
    session.commit()
    job_id = job.id
    session.close()

    events = []
    monkeypatch.setattr(
        tasks_module.metrics,
        "record_processing_started",
        lambda: events.append(("started",)),
    )
    monkeypatch.setattr(
        tasks_module.metrics,
        "record_processing_finished",
        lambda outcome, duration, *, timed_out: events.append(
            ("finished", outcome, duration, timed_out)
        ),
    )

    def fake_run_real_job(_job_id, db, *, already_claimed):
        assert already_claimed is True
        current = db.get(ProcessingJob, job_id)
        if result_status == "completed":
            current.status = "completed"
        else:
            current.status = "failed"
            current.error_code = error_code
            current.last_error = "processing timed out"
        db.commit()
        return SimpleNamespace(
            status=result_status,
            error_code=error_code,
            last_error="processing timed out" if error_code else None,
        )

    monkeypatch.setattr(tasks_module, "run_real_job", fake_run_real_job)
    celery = Celery("metrics-test", broker="memory://", backend="rpc://")
    celery.conf.task_always_eager = True
    celery.conf.task_eager_propagates = True
    task = tasks_module.register_tasks(celery)

    assert task.apply(args=(job_id,)).get() == job_id
    assert events[0] == ("started",)
    assert events[1][0:2] == ("finished", expected_outcome)
    assert events[1][2] >= 0
    assert events[1][3] is (error_code == "PROCESSING_TIMEOUT")
    verify = metrics_db()
    assert verify.get(ProcessingJob, job_id).status == expected_job_status
    verify.close()


def test_http_metrics_use_route_templates_and_exclude_metrics_scrapes(monkeypatch):
    route = "/api/v1/metrics-test/{item_id}"
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": route,
        "raw_path": route.encode(),
        "query_string": b"private=value",
        "root_path": "",
        "headers": [],
        "server": ("test", 80),
        "client": ("127.0.0.1", 1234),
        "route": SimpleNamespace(path=route),
    }

    async def successful_response(_request):
        return Response(status_code=201)

    monkeypatch.setattr(metrics, "_shared_metrics_client", lambda: FakeRedis())
    request = Request(scope)
    response = asyncio.run(metrics.observe_http_metrics(request, successful_response))

    assert response.status_code == 201
    assert metrics.http_requests.labels("GET", route, "2xx")._value.get() == 1

    scrape_scope = dict(scope, path="/metrics", raw_path=b"/metrics")
    scrape_scope["route"] = SimpleNamespace(path="/metrics")
    asyncio.run(
        metrics.observe_http_metrics(Request(scrape_scope), successful_response)
    )
    assert ("GET", "/metrics", "2xx") not in metrics.http_requests._metrics
