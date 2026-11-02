from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...core.config import settings
from ...db import get_db

router = APIRouter(prefix="/characters", tags=["characters-avatar-studio"])

STORAGE_DIR = Path(__file__).resolve().parents[2] / "storage" / "characters"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
INDEX_FILE = STORAGE_DIR / "character_registry.json"

class CharacterImportPayload(BaseModel):
    export_version: str = "1.0.0"
    source_studio: str = "Logixa Avatar Studio"
    actor_id: str
    actor_name: str
    role: str = "Virtual Actor"
    voice_binding: Dict[str, Any] = Field(default_factory=dict)
    vrm_model_path: Optional[str] = None
    expression_map: Optional[Dict[str, str]] = None
    character_meta: Optional[Dict[str, Any]] = None

def _read_registry() -> List[Dict[str, Any]]:
    if not INDEX_FILE.exists():
        return []
    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _write_registry(items: List[Dict[str, Any]]) -> None:
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)


@router.get("")
def list_narrativ_characters():
    """List all virtual actors imported from Logixa Avatar Studio or custom created."""
    return _read_registry()


@router.post("/import-avatar")
def import_avatar_character(payload: CharacterImportPayload):
    """Import character asset pack directly from Logixa Avatar Studio."""
    registry = _read_registry()
    existing_idx = next((i for i, c in enumerate(registry) if c.get("actor_id") == payload.actor_id), None)
    
    char_entry = payload.dict()
    if existing_idx is not None:
        registry[existing_idx] = char_entry
    else:
        registry.append(char_entry)
        
    _write_registry(registry)
    return {
        "status": "imported",
        "actor_id": payload.actor_id,
        "actor_name": payload.actor_name,
        "voice_engine": payload.voice_binding.get("engine", "edge-tts"),
        "voice_id": payload.voice_binding.get("voice_id", "my-MM-NilarNeural")
    }
