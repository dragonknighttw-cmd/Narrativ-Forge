from __future__ import annotations

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.routes.characters import CharacterImportPayload, _import_manual_pack
from app.db import Base
from app.models import CharacterRegistry, Organization


def _pack(actor_id: str = "actor_offline_demo") -> CharacterImportPayload:
    return CharacterImportPayload(
        actor_id=actor_id,
        actor_name="Offline Demo",
        voice_binding={"engine": "edge-tts", "voice_id": "my-MM-NilarNeural"},
        vrm_model_path="/models/sample_avatar_a.vrm",
        character_meta={"tags": ["manual-transfer"]},
    )


@pytest.fixture
def registry_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        organization = Organization(
            id="org-manual-transfer-test",
            name="Manual Transfer Test",
            slug="manual-transfer-test",
        )
        db.add(organization)
        db.commit()
        yield db, organization.id
    engine.dispose()


def test_manual_persona_transfer_imports_then_skips_duplicate(registry_db):
    db, organization_id = registry_db
    seen_actor_ids: set[str] = set()

    imported = _import_manual_pack(
        _pack(),
        organization_id=organization_id,
        db=db,
        seen_actor_ids=seen_actor_ids,
    )
    db.commit()
    duplicate = _import_manual_pack(
        _pack(),
        organization_id=organization_id,
        db=db,
        seen_actor_ids=seen_actor_ids,
    )

    assert imported["status"] == "imported"
    assert duplicate["status"] == "skipped"
    assert db.query(CharacterRegistry).filter_by(organization_id=organization_id).count() == 1


def test_manual_persona_transfer_rejects_path_traversal(registry_db):
    db, organization_id = registry_db
    unsafe = _pack()
    unsafe.vrm_model_path = "../outside.vrm"

    with pytest.raises(HTTPException) as error:
        _import_manual_pack(
            unsafe,
            organization_id=organization_id,
            db=db,
            seen_actor_ids=set(),
        )

    assert error.value.status_code == 422
