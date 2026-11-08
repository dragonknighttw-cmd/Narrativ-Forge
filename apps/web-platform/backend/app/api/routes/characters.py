from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..dependencies import get_current_membership, require_roles
router = APIRouter(prefix="/characters", tags=["characters-avatar-studio"])

STORAGE_DIR = Path(__file__).resolve().parents[2] / "storage" / "characters"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

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

def _registry_file(organization_id: str) -> Path:
    safe_id = re.sub(r"[^a-zA-Z0-9_-]", "", str(organization_id))
    if not safe_id:
        raise HTTPException(status_code=403, detail="Workspace membership required")
    return STORAGE_DIR / f"{safe_id}_character_registry.json"


def _read_registry(organization_id: str) -> List[Dict[str, Any]]:
    registry_file = _registry_file(organization_id)
    if not registry_file.exists():
        return []
    try:
        with open(registry_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _write_registry(organization_id: str, items: List[Dict[str, Any]]) -> None:
    with open(_registry_file(organization_id), "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)


@router.get("")
def list_narrativ_characters(membership=Depends(get_current_membership)):
    """List all virtual actors imported from AuraCraft Studio or custom created."""
    return _read_registry(membership.organization_id)


def _import_manual_pack(payload: CharacterImportPayload, registry: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Import one explicit file-selected pack without replacing existing work."""
    if payload.vrm_model_path and (".." in payload.vrm_model_path or not payload.vrm_model_path.startswith("/models/")):
        raise HTTPException(status_code=422, detail="VRM model path must stay inside /models/")
    if any(character.get("actor_id") == payload.actor_id for character in registry):
        return {"status": "skipped", "actor_id": payload.actor_id, "reason": "actor_id already exists"}
    char_entry = payload.model_dump()
    registry.append(char_entry)
    return {
        "status": "imported",
        "actor_id": payload.actor_id,
        "actor_name": payload.actor_name,
        "source_studio": payload.source_studio,
        "voice_engine": payload.voice_binding.get("engine", "edge-tts"),
        "voice_id": payload.voice_binding.get("voice_id", "my-MM-NilarNeural")
    }


@router.post("/import-avatar")
def import_avatar_character(
    payload: CharacterImportPayload,
    membership=Depends(get_current_membership),
    _=Depends(require_roles("owner", "editor")),
):
    """Import one manually selected AuraCraft-compatible JSON pack."""
    registry = _read_registry(membership.organization_id)
    result = _import_manual_pack(payload, registry)
    if result["status"] == "imported":
        _write_registry(membership.organization_id, registry)
    return result


@router.post("/import-avatar-batch")
def import_avatar_character_batch(
    batch: CharacterImportBatch,
    membership=Depends(get_current_membership),
    _=Depends(require_roles("owner", "editor")),
):
    """Import user-selected packs only; no call is made to any other project."""
    registry = _read_registry(membership.organization_id)
    results = [_import_manual_pack(pack, registry) for pack in batch.packs]
    if any(item["status"] == "imported" for item in results):
        _write_registry(membership.organization_id, registry)
    return {
        "imported": sum(item["status"] == "imported" for item in results),
        "skipped": sum(item["status"] == "skipped" for item in results),
        "results": results,
    }
