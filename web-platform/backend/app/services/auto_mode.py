from sqlalchemy.orm import Session

from ..models import Episode, Scene, Script
from .ai_adapter import get_ai_adapter


def create_auto_plan(db: Session, episode: Episode, idea: str, category: str | None = None) -> tuple[Script, list[Scene]]:
    plan = get_ai_adapter().create_content_plan(idea=idea, category=category)

    current_version = (
        db.query(Script.version)
        .filter(Script.episode_id == episode.id)
        .order_by(Script.version.desc())
        .first()
    )
    version = (current_version[0] if current_version else 0) + 1
    db.query(Script).filter(Script.episode_id == episode.id, Script.is_current.is_(True)).update(
        {Script.is_current: False}
    )

    script = Script(
        episode_id=episode.id,
        version=version,
        title=episode.title,
        content=plan.script,
        status="draft",
        is_current=True,
    )
    db.add(script)
    db.flush()

    scenes = []
    for item in plan.scenes:
        scene = Scene(
            episode_id=episode.id,
            script_id=script.id,
            scene_number=item["scene_number"],
            purpose=item["purpose"],
            description=item.get("description"),
            dialogue=item.get("dialogue"),
            duration_seconds=item.get("duration_seconds"),
        )
        db.add(scene)
        scenes.append(scene)

    episode.current_step = "assets"
    episode.status = "in_production"
    db.commit()
    db.refresh(script)
    for scene in scenes:
        db.refresh(scene)
    return script, scenes
