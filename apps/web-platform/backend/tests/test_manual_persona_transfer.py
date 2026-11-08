from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.api.routes.characters import CharacterImportPayload, _import_manual_pack


def _pack(actor_id: str = "actor_offline_demo") -> CharacterImportPayload:
    return CharacterImportPayload(
        actor_id=actor_id,
        actor_name="Offline Demo",
        voice_binding={"engine": "edge-tts", "voice_id": "my-MM-NilarNeural"},
        vrm_model_path="/models/sample_avatar_a.vrm",
        character_meta={"tags": ["manual-transfer"]},
    )


def test_manual_persona_transfer_imports_then_skips_duplicate():
    registry: list[dict] = []

    imported = _import_manual_pack(_pack(), registry)
    duplicate = _import_manual_pack(_pack(), registry)

    assert imported["status"] == "imported"
    assert duplicate["status"] == "skipped"
    assert len(registry) == 1


def test_manual_persona_transfer_rejects_path_traversal():
    registry: list[dict] = []
    unsafe = _pack()
    unsafe.vrm_model_path = "../outside.vrm"

    with pytest.raises(HTTPException) as error:
        _import_manual_pack(unsafe, registry)

    assert error.value.status_code == 422
