from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ...db import get_db
from ...models import Episode, Idea, Script, Series
from ..dependencies import get_current_membership

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
def global_search(
    q: str = Query(min_length=1, max_length=200),
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    membership=Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    term = q.strip()
    if not term:
        return {"query": q, "limit": limit, "offset": offset, "total": 0, "results": []}

    pattern = f"%{term}%"
    results = []

    candidate_limit = min(limit + offset, 200)

    idea_query = db.query(Idea).filter(Idea.organization_id == membership.organization_id,
        or_(Idea.title.ilike(pattern), Idea.concept.ilike(pattern), Idea.hook.ilike(pattern))
    )
    for item in idea_query.order_by(Idea.created_at.desc()).limit(candidate_limit).all():
        results.append({
            "type": "idea",
            "id": item.id,
            "title": item.title,
            "status": item.status,
            "snippet": item.concept or item.hook or "",
            "created_at": item.created_at,
        })

    series_query = db.query(Series).filter(Series.organization_id == membership.organization_id,
        or_(Series.title.ilike(pattern), Series.description.ilike(pattern))
    )
    for item in series_query.order_by(Series.updated_at.desc()).offset(offset).limit(limit).all():
        results.append({
            "type": "series",
            "id": item.id,
            "title": item.title,
            "status": item.status,
            "snippet": item.description or "",
            "created_at": item.created_at,
        })

    episode_query = db.query(Episode).filter(Episode.organization_id == membership.organization_id,
        or_(Episode.title.ilike(pattern), Episode.synopsis.ilike(pattern), Episode.category.ilike(pattern))
    )
    for item in episode_query.order_by(Episode.updated_at.desc()).offset(offset).limit(limit).all():
        results.append({
            "type": "episode",
            "id": item.id,
            "title": item.title,
            "status": item.status,
            "snippet": item.synopsis or "",
            "created_at": item.created_at,
        })

    script_query = db.query(Script).join(Episode, Script.episode_id == Episode.id).filter(Episode.organization_id == membership.organization_id,
        or_(Script.title.ilike(pattern), Script.content.ilike(pattern))
    )
    for item in script_query.order_by(Script.updated_at.desc()).offset(offset).limit(limit).all():
        results.append({
            "type": "script",
            "id": item.id,
            "episode_id": item.episode_id,
            "title": item.title or "Untitled",
            "status": item.status,
            "version": item.version,
            "snippet": (item.content or "")[:240],
            "created_at": item.created_at,
        })

    results.sort(key=lambda item: item["created_at"], reverse=True)
    total = idea_query.count() + series_query.count() + episode_query.count() + script_query.count()
    page = results[offset:offset + limit]
    return {
        "query": term,
        "limit": limit,
        "offset": offset,
        "total": total,
        "results": page,
    }
