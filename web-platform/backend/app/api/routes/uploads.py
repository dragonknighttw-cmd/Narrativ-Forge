import asyncio
import hashlib
import logging
from datetime import datetime, timedelta, timezone
from math import ceil
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ...core.config import settings
from ...db import get_db
from ...models import Asset, Episode, Scene, UploadPart, UploadSession
from ...middleware.idempotency import (
    IdempotencyClaim,
    StoredResponse,
    begin_idempotency,
    complete_idempotency,
    request_fingerprint,
    validate_idempotency_key,
)
from ...workers.celery_app import get_celery
from ...workers.tasks import enqueue_asset_replica
from ...services.storage import (
    MultipartUploadAlreadyCompleted,
    StorageError,
    build_object_key,
    get_storage,
)
from .assets import safe_filename, validate_upload
from ..dependencies import get_current_membership, require_roles

router = APIRouter(prefix="/uploads", tags=["uploads"])
logger = logging.getLogger(__name__)
MAX_MULTIPART_PARTS = 10_000
MAX_ASSET_SIZE_BYTES = 2_147_483_647


class CreateUploadSession(BaseModel):
    episode_id: str
    original_filename: str = Field(min_length=1, max_length=255)
    mime_type: str = Field(min_length=1, max_length=100)
    asset_type: str = Field(min_length=1, max_length=40)
    expected_size: int = Field(gt=0)
    scene_id: str | None = None
    copyright_status: str = Field(default="unknown", max_length=40)


def _utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def _owned_session(db: Session, upload_id: str, user_id: str, organization_id: str, *, lock: bool = False) -> UploadSession:
    query = db.query(UploadSession).join(Episode, UploadSession.episode_id == Episode.id).filter(UploadSession.id == upload_id, Episode.organization_id == organization_id)
    if lock:
        query = query.with_for_update()
    session = query.first()
    if not session or session.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Upload session not found")
    return session


def _asset_for_session(db: Session, session: UploadSession) -> Asset:
    asset = db.query(Asset).filter(
        Asset.episode_id == session.episode_id,
        Asset.version == session.reserved_version,
    ).first()
    if not asset:
        raise HTTPException(status_code=500, detail="Committed upload asset is missing")
    return asset


def _expire_session(db: Session, session: UploadSession) -> None:
    if session.provider_upload_id:
        try:
            get_storage(session.storage_provider).abort_multipart_upload(
                session.provider_upload_id,
                session.object_key,
            )
        except StorageError as exc:
            logger.error(
                "upload_expiry_abort_failed",
                extra={"event": "upload_expiry_abort_failed", "upload_session_id": session.id},
            )
            raise HTTPException(status_code=502, detail="Unable to clean up expired upload") from exc
    db.query(UploadPart).filter(
        UploadPart.upload_session_id == session.id,
    ).delete(synchronize_session=False)
    session.status = "expired"
    db.commit()


def _require_active(db: Session, session: UploadSession) -> None:
    if session.status == "active" and _utc(session.expires_at) <= datetime.now(timezone.utc):
        _expire_session(db, session)
        raise HTTPException(status_code=410, detail="Upload session has expired")
    if session.status == "expired":
        raise HTTPException(status_code=410, detail="Upload session has expired")
    if session.status == "aborted":
        raise HTTPException(status_code=410, detail="Upload session was aborted")
    if session.status != "active":
        raise HTTPException(status_code=409, detail="Upload session is not active")


def _part_state(db: Session, session: UploadSession) -> list[dict]:
    records = db.query(UploadPart).filter(
        UploadPart.upload_session_id == session.id,
    ).order_by(UploadPart.part_number).all()
    try:
        provider_parts = get_storage(session.storage_provider).list_multipart_parts(
            session.provider_upload_id,
            session.object_key,
            session.id,
            session.expected_size,
        )
    except MultipartUploadAlreadyCompleted:
        return [
            {
                "part_number": part.part_number,
                "size_bytes": part.size_bytes,
                "checksum_sha256": part.checksum_sha256,
            }
            for part in records
        ]
    provider_by_number = {part["PartNumber"]: part for part in provider_parts}
    return [
        {
            "part_number": part.part_number,
            "size_bytes": part.size_bytes,
            "checksum_sha256": part.checksum_sha256,
        }
        for part in records
        if part.part_number in provider_by_number
        and provider_by_number[part.part_number].get("Size") == part.size_bytes
        and provider_by_number[part.part_number].get("ETag") == part.provider_etag
    ]


def _session_payload(session: UploadSession, parts: list[dict]) -> dict:
    return {
        "id": session.id,
        "episode_id": session.episode_id,
        "asset_type": session.asset_type,
        "original_filename": session.original_filename,
        "mime_type": session.mime_type,
        "expected_size": session.expected_size,
        "chunk_size": session.chunk_size,
        "expected_parts": ceil(session.expected_size / session.chunk_size),
        "scene_id": session.scene_id,
        "status": session.status,
        "expires_at": _utc(session.expires_at).isoformat(),
        "parts": parts,
    }


def _session_response(db: Session, session: UploadSession) -> dict:
    try:
        if session.status == "active":
            parts = _part_state(db, session)
        elif session.status == "committed":
            parts = [
                {
                    "part_number": part.part_number,
                    "size_bytes": part.size_bytes,
                    "checksum_sha256": part.checksum_sha256,
                }
                for part in db.query(UploadPart).filter(
                    UploadPart.upload_session_id == session.id,
                ).order_by(UploadPart.part_number).all()
            ]
        else:
            parts = []
    except StorageError as exc:
        raise HTTPException(status_code=502, detail="Unable to inspect upload session") from exc
    return _session_payload(session, parts)


@router.post("", status_code=201)
def create_upload_session(
    payload: CreateUploadSession,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    user: dict = Depends(require_roles("owner", "editor")),
    membership=Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    idempotency_key = validate_idempotency_key(idempotency_key)
    if payload.expected_size > min(settings.max_upload_size_bytes, MAX_ASSET_SIZE_BYTES):
        raise HTTPException(status_code=413, detail="File exceeds upload size limit")
    if ceil(payload.expected_size / settings.upload_chunk_size_bytes) > MAX_MULTIPART_PARTS:
        raise HTTPException(status_code=413, detail="File exceeds multipart part-count limit")
    safe_name = safe_filename(payload.original_filename)
    validate_upload(safe_name, payload.mime_type, payload.asset_type)
    episode = db.query(Episode).filter(Episode.id == payload.episode_id, Episode.organization_id == membership.organization_id).with_for_update().first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    if payload.scene_id is not None:
        scene = db.query(Scene).join(Episode, Scene.episode_id == Episode.id).filter(Scene.id == payload.scene_id, Episode.organization_id == membership.organization_id).first()
        if not scene or scene.episode_id != episode.id:
            raise HTTPException(status_code=422, detail="Scene does not belong to this episode")

    claim_or_response = begin_idempotency(
        db,
        actor_id=user["id"],
        key=idempotency_key,
        method=request.method,
        target=request.url.path,
        fingerprint=request_fingerprint(request.method, request.url.path, payload.model_dump(mode="json")),
        resource_type="upload_session",
    )
    if isinstance(claim_or_response, StoredResponse):
        return claim_or_response.response()
    if isinstance(claim_or_response, IdempotencyClaim) and not claim_or_response.created:
        raise HTTPException(status_code=409, detail="Upload session request is still processing")
    claim = claim_or_response if isinstance(claim_or_response, IdempotencyClaim) else None

    asset_version = db.query(func.max(Asset.version)).filter(Asset.episode_id == episode.id).scalar() or 0
    session_version = db.query(func.max(UploadSession.reserved_version)).filter(
        UploadSession.episode_id == episode.id,
    ).scalar() or 0
    version = max(asset_version, session_version) + 1
    session_id = claim.record.resource_id if claim else str(uuid4())
    object_key = build_object_key(
        episode.id,
        version,
        f"{uuid4().hex}_{safe_name}",
        payload.asset_type,
    )
    try:
        selected_provider = storage_provider_for_asset(payload.asset_type, payload.expected_size, payload.mime_type)
        storage = get_storage(selected_provider)
    except StorageError as exc:
        raise HTTPException(status_code=502, detail="Unable to initialize upload storage") from exc
    provider_upload_id = None
    upload = UploadSession(
        id=session_id,
        owner_id=user["id"],
        episode_id=episode.id,
        reserved_version=version,
        asset_type=payload.asset_type,
        scene_id=payload.scene_id,
        original_filename=safe_name,
        mime_type=payload.mime_type,
        expected_size=payload.expected_size,
        chunk_size=settings.upload_chunk_size_bytes,
        copyright_status=payload.copyright_status,
        storage_provider=storage.name,
        object_key=object_key,
        status="active",
        created_at=datetime.now(timezone.utc),
        last_activity_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=settings.upload_session_ttl_seconds),
    )
    try:
        db.add(upload)
        db.flush()
        provider_upload_id = storage.initiate_multipart_upload(
            object_key,
            payload.mime_type,
            session_id,
        )
        upload.provider_upload_id = provider_upload_id
        db.flush()
        response_data = _session_payload(upload, [])
        stored_response = complete_idempotency(claim, response_data, status_code=201)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        if provider_upload_id:
            try:
                storage.abort_multipart_upload(provider_upload_id, object_key)
            except StorageError:
                logger.exception("upload_session_reservation_cleanup_failed")
        raise HTTPException(status_code=409, detail="Unable to reserve an asset version") from exc
    except StorageError as exc:
        db.rollback()
        if provider_upload_id:
            try:
                storage.abort_multipart_upload(provider_upload_id, object_key)
            except StorageError:
                logger.exception("upload_session_creation_cleanup_failed")
        raise HTTPException(status_code=502, detail="Unable to initialize upload session") from exc
    except Exception:
        db.rollback()
        if provider_upload_id:
            try:
                storage.abort_multipart_upload(provider_upload_id, object_key)
            except StorageError:
                logger.exception("upload_session_creation_cleanup_failed")
        raise
    return stored_response.response() if stored_response else response_data


@router.get("/{upload_id}")
def get_upload_session(
    upload_id: str,
    user: dict = Depends(require_roles("owner", "editor")),
    db: Session = Depends(get_db),
):
    session = _owned_session(db, upload_id, user["id"], membership.organization_id, lock=True)
    if session.status == "active":
        _require_active(db, session)
    elif session.status == "expired":
        raise HTTPException(status_code=410, detail="Upload session has expired")
    elif session.status == "aborted":
        raise HTTPException(status_code=410, detail="Upload session was aborted")
    response = _session_response(db, session)
    if session.status == "committed":
        response["asset"] = _asset_for_session(db, session)
    return response


@router.put("/{upload_id}/chunks")
async def upload_chunk(
    upload_id: str,
    request: Request,
    part_number: int = Query(ge=1, le=MAX_MULTIPART_PARTS),
    offset: int = Query(ge=0),
    user: dict = Depends(require_roles("owner", "editor")),
    db: Session = Depends(get_db),
):
    session = _owned_session(db, upload_id, user["id"], lock=True)
    _require_active(db, session)
    if not session.provider_upload_id:
        raise HTTPException(status_code=500, detail="Upload session storage state is incomplete")
    expected_parts = ceil(session.expected_size / session.chunk_size)
    expected_offset = (part_number - 1) * session.chunk_size
    if part_number > expected_parts or offset != expected_offset:
        raise HTTPException(status_code=422, detail="Chunk number and offset do not match the upload session")
    expected_size = min(session.chunk_size, session.expected_size - offset)
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            declared_size = int(content_length)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid Content-Length") from exc
        if declared_size != expected_size:
            raise HTTPException(status_code=400, detail="Chunk size does not match its offset")

    body = bytearray()
    async for incoming in request.stream():
        if len(body) + len(incoming) > expected_size:
            raise HTTPException(status_code=413, detail="Chunk exceeds its permitted size")
        body.extend(incoming)
    if len(body) != expected_size:
        raise HTTPException(status_code=400, detail="Chunk size does not match its offset")
    checksum = hashlib.sha256(body).hexdigest()
    part = db.query(UploadPart).filter(
        UploadPart.upload_session_id == session.id,
        UploadPart.part_number == part_number,
    ).first()

    try:
        storage = get_storage(session.storage_provider)
        if part and part.size_bytes == len(body) and part.checksum_sha256 == checksum:
            remote_parts = storage.list_multipart_parts(
                session.provider_upload_id,
                session.object_key,
                session.id,
                session.expected_size,
            )
            remote_match = next((item for item in remote_parts if item["PartNumber"] == part_number), None)
            if remote_match and remote_match.get("ETag") == part.provider_etag and remote_match.get("Size") == part.size_bytes:
                session.last_activity_at = datetime.now(timezone.utc)
                db.commit()
                return {
                    "part_number": part_number,
                    "offset": offset,
                    "size_bytes": len(body),
                    "checksum_sha256": checksum,
                }
        etag = await asyncio.to_thread(
            storage.upload_part,
            session.provider_upload_id,
            session.object_key,
            part_number,
            bytes(body),
            part_number == expected_parts,
        )
    except StorageError as exc:
        db.rollback()
        raise HTTPException(status_code=502, detail="Unable to store upload chunk") from exc

    if part:
        part.size_bytes = len(body)
        part.checksum_sha256 = checksum
        part.provider_etag = etag
        part.created_at = datetime.now(timezone.utc)
    else:
        db.add(UploadPart(
            upload_session_id=session.id,
            part_number=part_number,
            size_bytes=len(body),
            checksum_sha256=checksum,
            provider_etag=etag,
        ))
    session.last_activity_at = datetime.now(timezone.utc)
    db.commit()
    return {
        "part_number": part_number,
        "offset": offset,
        "size_bytes": len(body),
        "checksum_sha256": checksum,
    }


@router.post("/{upload_id}/commit")
def commit_upload(
    upload_id: str,
    user: dict = Depends(require_roles("owner", "editor")),
    db: Session = Depends(get_db),
):
    session = _owned_session(db, upload_id, user["id"], lock=True)
    if session.status == "committed":
        return _asset_for_session(db, session)
    _require_active(db, session)
    if not session.provider_upload_id:
        raise HTTPException(status_code=500, detail="Upload session storage state is incomplete")
    expected_parts = ceil(session.expected_size / session.chunk_size)
    records = db.query(UploadPart).filter(
        UploadPart.upload_session_id == session.id,
    ).order_by(UploadPart.part_number).all()
    if (
        len(records) != expected_parts
        or [part.part_number for part in records] != list(range(1, expected_parts + 1))
        or any(
            record.size_bytes != (
                session.chunk_size
                if record.part_number < expected_parts
                else session.expected_size - session.chunk_size * (expected_parts - 1)
            )
            for record in records
        )
    ):
        raise HTTPException(status_code=409, detail="Upload is missing one or more valid chunks")

    try:
        storage = get_storage(session.storage_provider)
        stored = storage.complete_multipart_upload(
            session.provider_upload_id,
            session.object_key,
            [
                {
                    "PartNumber": part.part_number,
                    "Size": part.size_bytes,
                    "ETag": part.provider_etag,
                }
                for part in records
            ],
            session.expected_size,
            session.chunk_size,
            session.id,
        )
    except StorageError as exc:
        db.rollback()
        raise HTTPException(status_code=502, detail="Unable to finalize upload") from exc

    existing = db.query(Asset).filter(
        Asset.checksum_sha256 == stored.checksum_sha256,
        Asset.asset_type == session.asset_type,
        Asset.status != "deleted",
    ).order_by(Asset.created_at.asc()).first()

    if existing:
        if existing.episode_id == session.episode_id:
            try:
                if stored.object_key != existing.object_key:
                    storage.delete(stored.object_key)
            except StorageError:
                logger.exception("checksum_dedupe_cleanup_failed")
            else:
                session.status = "committed"
                session.last_activity_at = datetime.now(timezone.utc)
                db.commit()
                return existing

        if existing.episode_id != session.episode_id:
            try:
                if stored.object_key != existing.object_key:
                    storage.delete(stored.object_key)
            except StorageError:
                logger.exception("checksum_dedupe_cross_episode_cleanup_failed")
            else:
                asset = Asset(
                    episode_id=session.episode_id,
                    scene_id=session.scene_id,
                    asset_type=session.asset_type,
                    original_filename=session.original_filename,
                    storage_provider=existing.storage_provider,
                    local_path=existing.local_path,
                    object_key=existing.object_key,
                    checksum_sha256=existing.checksum_sha256,
                    mime_type=session.mime_type,
                    file_size_bytes=existing.file_size_bytes,
                    version=session.reserved_version,
                    copyright_status=session.copyright_status,
                    status="uploaded",
                )
                session.status = "committed"
                session.last_activity_at = datetime.now(timezone.utc)
                db.add(asset)
                db.commit()
                db.refresh(asset)
                return asset

    asset = Asset(
        episode_id=session.episode_id,
        scene_id=session.scene_id,
        asset_type=session.asset_type,
        original_filename=session.original_filename,
        storage_provider=stored.provider,
        local_path=stored.local_path,
        object_key=stored.object_key,
        checksum_sha256=stored.checksum_sha256,
        mime_type=session.mime_type,
        file_size_bytes=stored.size_bytes,
        version=session.reserved_version,
        copyright_status=session.copyright_status,
        status="uploaded",
    )
    session.status = "committed"
    session.last_activity_at = datetime.now(timezone.utc)
    db.add(asset)
    db.commit()
    db.refresh(asset)
    if settings.storage_replica_enabled and settings.storage_replica_provider:
        try:
            celery = get_celery(allow_missing=True)
            if celery is not None:
                enqueue_asset_replica(celery, asset.id)
        except Exception:
            logger.exception("storage_replica_enqueue_failed", extra={"asset_id": asset.id})
    return asset


@router.delete("/{upload_id}")
def abort_upload(
    upload_id: str,
    user: dict = Depends(require_roles("owner", "editor")),
    db: Session = Depends(get_db),
):
    session = _owned_session(db, upload_id, user["id"], lock=True)
    if session.status == "aborted":
        return {"id": session.id, "status": session.status}
    if session.status == "committed":
        raise HTTPException(status_code=409, detail="Committed upload cannot be aborted")
    _require_active(db, session)
    if not session.provider_upload_id:
        raise HTTPException(status_code=500, detail="Upload session storage state is incomplete")
    try:
        get_storage(session.storage_provider).abort_multipart_upload(
            session.provider_upload_id,
            session.object_key,
        )
    except StorageError as exc:
        db.rollback()
        raise HTTPException(status_code=502, detail="Unable to abort upload session") from exc
    db.query(UploadPart).filter(
        UploadPart.upload_session_id == session.id,
    ).delete(synchronize_session=False)
    session.status = "aborted"
    session.last_activity_at = datetime.now(timezone.utc)
    db.commit()
    return {"id": session.id, "status": session.status}
