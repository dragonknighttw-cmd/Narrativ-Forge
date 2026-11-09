from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ...db import get_db
from ..dependencies import get_current_membership, require_roles
from ...models import CharacterRegistry

router = APIRouter(prefix="/characters", tags=["characters-avatar-studio"])


class CharacterImportPayload(BaseModel):
    export_version: str = "1.0.0"
    source_studio: str = "AuraCraft Studio"
    actor_id: str = Field(min_length=1, max_length=120)
    actor_name: str = Field(min_length=1, max_length=100)
    role: str = Field(default="Virtual Actor", max_length=100)
    voice_binding: Dict[str, Any] = Field(default_factory=dict)
    vrm_model_path: Optional[str] = Field(default=None, max_length=500)
    expression_map: Optional[Dict[str, str]] = None
    character_meta: Optional[Dict[str, Any]] = None


class CharacterImportBatch(BaseModel):
    packs: List[CharacterImportPayload] = Field(min_length=1, max_length=50)


def _decode_json(value: str | None, fallback: Any) -> Any:
    if not value:
        return fallback
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return fallback


def _serialize_character(record: CharacterRegistry) -> Dict[str, Any]:
    return {
        "export_version": "1.0.0",
        "source_studio": record.source_studio,
        "actor_id": record.actor_id,
        "actor_name": record.actor_name,
        "role": record.role,
        "voice_binding": _decode_json(record.voice_binding_json, {}),
        "vrm_model_path": record.vrm_model_path,
        "expression_map": _decode_json(record.expression_map_json, None),
        "character_meta": _decode_json(record.character_meta_json, None),
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "updated_at": record.updated_at.isoformat() if record.updated_at else None,
    }


def _import_manual_pack(
    payload: CharacterImportPayload,
    *,
    organization_id: str,
    db: Session,
    seen_actor_ids: set[str],
) -> Dict[str, Any]:
    """Persist one explicit file-selected pack without replacing existing work."""
    if payload.vrm_model_path and (
        ".." in payload.vrm_model_path or not payload.vrm_model_path.startswith("/models/")
    ):
        raise HTTPException(status_code=422, detail="VRM model path must stay inside /models/")
    if payload.actor_id in seen_actor_ids:
        return {"status": "skipped", "actor_id": payload.actor_id, "reason": "actor_id already exists"}
    existing = (
        db.query(CharacterRegistry.id)
        .filter(
            CharacterRegistry.organization_id == organization_id,
            CharacterRegistry.actor_id == payload.actor_id,
        )
        .first()
    )
    if existing:
        seen_actor_ids.add(payload.actor_id)
        return {"status": "skipped", "actor_id": payload.actor_id, "reason": "actor_id already exists"}

    db.add(CharacterRegistry(
        organization_id=organization_id,
        actor_id=payload.actor_id,
        actor_name=payload.actor_name,
        role=payload.role,
        source_studio=payload.source_studio,
        voice_binding_json=json.dumps(payload.voice_binding, ensure_ascii=False),
        vrm_model_path=payload.vrm_model_path,
        expression_map_json=json.dumps(payload.expression_map, ensure_ascii=False) if payload.expression_map is not None else None,
        character_meta_json=json.dumps(payload.character_meta, ensure_ascii=False) if payload.character_meta is not None else None,
    ))
    db.flush()
    seen_actor_ids.add(payload.actor_id)
    return {
        "status": "imported",
        "actor_id": payload.actor_id,
        "actor_name": payload.actor_name,
        "source_studio": payload.source_studio,
        "voice_engine": payload.voice_binding.get("engine", "edge-tts"),
        "voice_id": payload.voice_binding.get("voice_id", "my-MM-NilarNeural"),
    }


@router.get("")
def list_narrativ_characters(
    membership=Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    """List only virtual actors belonging to the active organization."""
    records = (
        db.query(CharacterRegistry)
        .filter(CharacterRegistry.organization_id == membership.organization_id)
        .order_by(CharacterRegistry.created_at.desc(), CharacterRegistry.actor_id.asc())
        .all()
    )
    return [_serialize_character(record) for record in records]


@router.post("/import-avatar")
def import_avatar_character(
    payload: CharacterImportPayload,
    membership=Depends(get_current_membership),
    _=Depends(require_roles("owner", "editor")),
    db: Session = Depends(get_db),
):
    """Import one manually selected AuraCraft-compatible JSON pack."""
    try:
        result = _import_manual_pack(payload, organization_id=membership.organization_id, db=db, seen_actor_ids=set())
        db.commit()
        return result
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Character already exists in this workspace") from exc
    except Exception:
        db.rollback()
        raise


@router.post("/import-avatar-batch")
def import_avatar_character_batch(
    batch: CharacterImportBatch,
    membership=Depends(get_current_membership),
    _=Depends(require_roles("owner", "editor")),
    db: Session = Depends(get_db),
):
    """Import user-selected packs only; no call is made to any other project."""
    seen_actor_ids: set[str] = set()
    try:
        results = [
            _import_manual_pack(pack, organization_id=membership.organization_id, db=db, seen_actor_ids=seen_actor_ids)
            for pack in batch.packs
        ]
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="A character already exists in this workspace") from exc
    except Exception:
        db.rollback()
        raise
    return {
        "imported": sum(item["status"] == "imported" for item in results),
        "skipped": sum(item["status"] == "skipped" for item in results),
        "results": results,
    }
