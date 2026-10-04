from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.orm import Session, sessionmaker

from app.api.dependencies import issue_session
from app.db import engine, get_db
from app.main import app
from app.models import Episode, ProcessingJob, Series, User
from app.services.passwords import hash_password


pytestmark = pytest.mark.integration


def test_postgres_concurrent_same_key_creates_one_job():
    if engine.dialect.name != "postgresql":
        pytest.skip("Concurrent idempotency race test requires PostgreSQL row/unique locking")

    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with session_factory() as db:
        user = User(
            email=f"idem-{uuid4()}@test.local",
            role="owner",
            password_hash=hash_password("idempotency-test-password"),
            is_active=True,
        )
        series = Series(title="Idempotency concurrency test")
        db.add_all([user, series])
        db.flush()
        episode = Episode(
            public_id=f"IDEM-{uuid4()}",
            series_id=series.id,
            episode_number=1,
            title="Concurrent idempotency test",
        )
        db.add(episode)
        db.commit()
        user_id, user_email, episode_id, series_id = user.id, user.email, episode.id, series.id

    barrier = Barrier(2)
    previous_override = app.dependency_overrides.get(get_db)

    def override_db():
        db = session_factory()
        db.info["idempotency_race_barrier"] = barrier
        try:
            yield db
        finally:
            db.close()

    def before_flush(session, _flush_context, _instances):
        race_barrier = session.info.pop("idempotency_race_barrier", None)
        if race_barrier:
            race_barrier.wait(timeout=15)

    clients = [
        TestClient(app, base_url="http://localhost", client=("127.0.0.21", 12345)),
        TestClient(app, base_url="http://localhost", client=("127.0.0.22", 12345)),
    ]
    for client in clients:
        client.cookies.set("nf_session", issue_session(user_email, "owner"))
    app.dependency_overrides[get_db] = override_db
    event.listen(Session, "before_flush", before_flush)

    try:
        key = str(uuid4())

        def create_job(client):
            return client.post(
                "/api/v1/jobs/real",
                json={"episode_id": episode_id},
                headers={"Idempotency-Key": key},
            )

        with ThreadPoolExecutor(max_workers=2) as executor:
            responses = list(executor.map(create_job, clients))
        assert [response.status_code for response in responses] == [201, 201]
        assert responses[0].json() == responses[1].json()

        with session_factory() as db:
            assert db.query(ProcessingJob).filter(
                ProcessingJob.episode_id == episode_id,
            ).count() == 1
            assert db.query(User).filter(User.id == user_id).count() == 1
    finally:
        event.remove(Session, "before_flush", before_flush)
        for client in clients:
            client.close()
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override
        with session_factory() as db:
            db.query(ProcessingJob).filter(ProcessingJob.episode_id == episode_id).delete()
            db.query(Episode).filter(Episode.id == episode_id).delete()
            db.query(Series).filter(Series.id == series_id).delete()
            db.query(User).filter(User.id == user_id).delete()
            db.commit()
