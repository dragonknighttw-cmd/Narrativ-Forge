from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import Episode, Scene, Script
from .ai_adapter import ContentPlan, get_ai_adapter


TARGET_MIN_SECONDS = 150
TARGET_MAX_SECONDS = 210


def normalize_content_plan(plan: ContentPlan, target_duration_seconds: int = 180) -> ContentPlan:
    """Make provider output safe for the short-form target without inventing a new provider."""
    target = max(TARGET_MIN_SECONDS, min(TARGET_MAX_SECONDS, int(target_duration_seconds or 180)))
    source_scenes = list(plan.scenes)
    if not source_scenes:
        source_scenes = [{
            "scene_number": 1,
            "purpose": "body",
            "description": plan.script[:500],
            "dialogue": plan.script,
            "duration_seconds": target,
        }]

    # Preserve provider scenes, then add deterministic bridge scenes so the
    # local/mock adapter also exercises the production-sized scene pipeline.
    scenes: list[dict] = []
    remaining = target
    for index, item in enumerate(source_scenes, start=1):
        if remaining <= 0:
            break
        duration = max(3, min(45, int(item.get("duration_seconds") or 10)))
        duration = min(duration, remaining)
        scenes.append({
            "scene_number": index,
            "purpose": item.get("purpose") or ("hook" if index == 1 else "body"),
            "description": item.get("description") or item.get("dialogue") or "",
            "dialogue": item.get("dialogue") or item.get("description") or "",
            "duration_seconds": duration,
        })
        remaining -= duration

    bridge_index = len(scenes) + 1
    bridge_texts = [
        ("context", "အကြောင်းအရာရဲ့ နောက်ခံအချက်ကို ရှင်းပြပြီး အဓိကပြဿနာကို ဖော်ပြမယ်။"),
        ("detail", "အရေးကြီးတဲ့အချက်တွေကို တစ်ချက်ချင်း ဆက်စပ်ရှင်းပြမယ်။"),
        ("example", "လက်တွေ့ဥပမာတစ်ခုနဲ့ ကြည့်ရှုသူ နားလည်လွယ်အောင် ချိတ်ဆက်မယ်။"),
        ("payoff", "အဓိက takeaway ကို စုစည်းပြီး ကြည့်ရှုသူအတွက် အသုံးဝင်တဲ့အဆုံးသတ်ကို ပေးမယ်။"),
    ]
    cursor = 0
    while remaining > 0:
        purpose, text = bridge_texts[min(cursor, len(bridge_texts) - 1)]
        duration = min(30 if purpose != "payoff" else 20, remaining)
        if duration < 3:
            if scenes:
                scenes[-1]["duration_seconds"] += remaining
            break
        scenes.append({
            "scene_number": bridge_index,
            "purpose": purpose,
            "description": text,
            "dialogue": text,
            "duration_seconds": duration,
        })
        remaining -= duration
        bridge_index += 1
        cursor += 1

    # Re-number after normalization and guarantee exact target duration.
    total = sum(int(scene["duration_seconds"]) for scene in scenes)
    if scenes and total != target:
        scenes[-1]["duration_seconds"] += target - total

    return ContentPlan(
        hook=plan.hook,
        script=plan.script,
        scenes=scenes,
    )


def create_auto_plan(
    db: Session,
    episode: Episode,
    idea: str,
    category: str | None = None,
) -> tuple[Script, list[Scene]]:
    plan = _normalize_content_plan(
        get_ai_adapter().create_content_plan(idea=idea, category=category),
        episode.target_duration_seconds,
    )

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
