from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models import IdempotencyRecord

MAX_IDEMPOTENCY_KEY_LENGTH = 255
MAX_STORED_RESPONSE_BYTES = 256 * 1024
KEY_PATTERN = re.compile(r"^[\x21-\x7e]{1,255}$")


@dataclass(frozen=True)
class IdempotencyClaim:
    record: IdempotencyRecord
    created: bool


@dataclass(frozen=True)
class StoredResponse:
    status_code: int
    body: str
    content_type: str

    def response(self) -> JSONResponse:
        return JSONResponse(
            status_code=self.status_code,
            content=json.loads(self.body),
            media_type=self.content_type,
        )


def validate_idempotency_key(key: str | None) -> str | None:
    if key is None:
        return None
    if len(key) > MAX_IDEMPOTENCY_KEY_LENGTH or not KEY_PATTERN.fullmatch(key):
        raise HTTPException(
            status_code=400,
            detail="Idempotency-Key must contain 1 to 255 printable ASCII characters",
        )
    return key


def request_fingerprint(method: str, target: str, request_data: object) -> str:
    canonical = json.dumps(
        {"method": method.upper(), "target": target, "request": request_data},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def cleanup_expired_idempotency_records(db: Session, *, limit: int = 500) -> int:
    expired_ids = (
        db.query(IdempotencyRecord.id)
        .filter(IdempotencyRecord.expires_at <= datetime.now(timezone.utc))
        .order_by(IdempotencyRecord.expires_at)
        .limit(limit)
        .all()
    )
    ids = [row[0] for row in expired_ids]
    if ids:
        db.query(IdempotencyRecord).filter(IdempotencyRecord.id.in_(ids)).delete(
            synchronize_session=False,
        )
        db.flush()
    return len(ids)


def begin_idempotency(
    db: Session,
    *,
    actor_id: str,
    key: str | None,
    method: str,
    target: str,
    fingerprint: str,
    resource_type: str,
    resource_id: str | None = None,
) -> IdempotencyClaim | StoredResponse | None:
    key = validate_idempotency_key(key)
    if key is None:
        return None

    cleanup_expired_idempotency_records(db)
    existing = (
        db.query(IdempotencyRecord)
        .filter(IdempotencyRecord.actor_id == actor_id, IdempotencyRecord.key == key)
        .with_for_update()
        .first()
    )
    if existing:
        if existing.request_fingerprint != fingerprint:
            raise HTTPException(status_code=409, detail="Idempotency-Key was already used for a different request")
        if existing.status == "completed":
            if existing.response_status is None or existing.response_body is None:
                raise HTTPException(status_code=500, detail="Stored idempotency response is incomplete")
            return StoredResponse(
                existing.response_status,
                existing.response_body,
                existing.response_content_type or "application/json",
            )
        return IdempotencyClaim(existing, created=False)

    record = IdempotencyRecord(
        actor_id=actor_id,
        key=key,
        method=method.upper(),
        target=target,
        request_fingerprint=fingerprint,
        status="processing",
        resource_type=resource_type,
        resource_id=resource_id or str(uuid4()),
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=settings.idempotency_ttl_seconds),
    )
    db.add(record)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        existing = (
            db.query(IdempotencyRecord)
            .filter(IdempotencyRecord.actor_id == actor_id, IdempotencyRecord.key == key)
            .first()
        )
        if not existing:
            raise HTTPException(status_code=503, detail="Unable to reserve idempotency key")
        if existing.request_fingerprint != fingerprint:
            raise HTTPException(status_code=409, detail="Idempotency-Key was already used for a different request")
        if existing.status == "completed":
            if existing.response_status is None or existing.response_body is None:
                raise HTTPException(status_code=500, detail="Stored idempotency response is incomplete")
            return StoredResponse(
                existing.response_status,
                existing.response_body,
                existing.response_content_type or "application/json",
            )
        return IdempotencyClaim(existing, created=False)
    return IdempotencyClaim(record, created=True)


def complete_idempotency(
    claim: IdempotencyClaim | None,
    response_value: object,
    *,
    status_code: int,
) -> StoredResponse | None:
    if claim is None:
        return None
    encoded = json.dumps(
        jsonable_encoder(response_value),
        separators=(",", ":"),
        ensure_ascii=False,
    )
    if len(encoded.encode("utf-8")) > MAX_STORED_RESPONSE_BYTES:
        raise HTTPException(status_code=500, detail="Response is too large to store for idempotent replay")
    record = claim.record
    record.status = "completed"
    record.response_status = status_code
    record.response_content_type = "application/json"
    record.response_body = encoded
    record.updated_at = datetime.now(timezone.utc)
    return StoredResponse(status_code, encoded, "application/json")
