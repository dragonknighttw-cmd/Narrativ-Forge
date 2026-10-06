from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import Episode, Scene, Script
from .ai_adapter import get_ai_adapter


def regenerate_scene(
    db: Session,
    episode: Episode,
    scene_number: int,
    instruction: str,
) -> tuple[Script, list[Scene]]:
    if scene_number < 1:
        raise ValueError("scene_number must be >= 1")
    instruction = instruction.strip()
    if not instruction:
        raise ValueError("instruction is required")

    current_script = (
        db.query(Script)
        .filter(Script.episode_id == episode.id, Script.is_current.is_(True))
        .first()
    )
    if current_script is None:
        raise ValueError("Current script not found")

    current_scenes = (
        db.query(Scene)
        .filter(Scene.script_id == current_script.id)
        .order_by(Scene.scene_number.asc())
        .all()
    )
    target = next((scene for scene in current_scenes if scene.scene_number == scene_number), None)
    if target is None:
        raise ValueError("Scene not found")

    plan = get_ai_adapter().create_content_plan(
        idea=f"{target.description or target.dialogue or target.purpose}\n\nRewrite instruction: {instruction}",
        category="selective_regeneration",
    )

    replacement = plan.scenes[0] if plan.scenes else {
        "purpose": target.purpose,
        "description": target.description,
        "dialogue": target.dialogue,
        "duration_seconds": target.duration_seconds,
    }

    db.query(Script).filter(
        Script.episode_id == episode.id,
        Script.is_current.is_(True),
    ).update({Script.is_current: False})

    new_version = (current_script.version or 0) + 1
    new_script = Script(
        episode_id=episode.id,
        version=new_version,
        title=current_script.title,
        content=current_script.content,
        status="draft",
        is_current=True,
    )
    db.add(new_script)
    db.flush()

    new_scenes: list[Scene] = []
    for scene in current_scenes:
        data = replacement if scene.scene_number == scene_number else {
            "purpose": scene.purpose,
            "description": scene.description,
            "dialogue": scene.dialogue,
            "duration_seconds": scene.duration_seconds,
        }
        item = Scene(
            episode_id=episode.id,
            script_id=new_script.id,
            scene_number=scene.scene_number,
            purpose=data.get("purpose") or scene.purpose,
            description=data.get("description"),
            dialogue=data.get("dialogue"),
            duration_seconds=data.get("duration_seconds"),
        )
        db.add(item)
        new_scenes.append(item)

    episode.current_step = "review"
    episode.status = "script_review"
    db.commit()
    db.refresh(new_script)
    for scene in new_scenes:
        db.refresh(scene)
    return new_script, new_scenes
