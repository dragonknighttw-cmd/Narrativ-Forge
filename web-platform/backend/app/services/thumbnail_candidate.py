from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any
from sqlalchemy.orm import Session

from ..models import Asset, Episode, ReviewRecord


@dataclass(frozen=True)
class ThumbnailCandidateItem:
    id: str
    visual_prompt: str
    overlay_text: str
    composition_style: str
    color_mood: str
    score: float
    reason: str


THUMBNAIL_PRESETS = [
    {
        "id": "tc_01",
        "style": "close_up_reaction",
        "prompt": "Cinematic intense close-up of a Burmese creator expressing deep shock, dramatic rim light, shallow depth of field, 8k resolution.",
        "overlay": "တကယ်ပဲလား?!",
        "color": "high_contrast_yellow_dark",
        "score": 96.5,
        "reason": "မျက်နှာအမူအရာ အနီးကပ်ပြသခြင်းဖြင့် ပရိသတ်၏ ချက်ချင်းဆွဲဆောင်မှုကို ရရှိစေသည်။",
    },
    {
        "id": "tc_02",
        "style": "split_contrast",
        "prompt": "Split screen comparison showing expectation vs reality, left side dim monochrome, right side vivid hyper-detailed colors.",
        "overlay": "အမှန် vs အထင်",
        "color": "contrast_blue_gold",
        "score": 94.0,
        "reason": "ဆန့်ကျင်ဘက် အချက်နှစ်ခုကို ယှဉ်တွဲပြသပြီး စူးစမ်းလိုစိတ်ကို မြှင့်တင်ပေးသည်။",
    },
    {
        "id": "tc_03",
        "style": "warning_danger",
        "prompt": "Vibrant warning barrier with glowing hazard signs, moody dark atmosphere with high contrast yellow and black caution marks.",
        "overlay": "လုံးဝ မလုပ်ပါနဲ့!",
        "color": "dramatic_warning_yellow",
        "score": 92.5,
        "reason": "သတိပေးချက် သင်္ကေတများဖြင့် ဆုံးရှုံးမှု ရှောင်ရှားလိုသည့် စိတ်ကို လှုံ့ဆော်သည်။",
    },
    {
        "id": "tc_04",
        "style": "mystery_silhouette",
        "prompt": "Mysterious back-lit silhouette in front of an ancient Burmese temple archway, volumetric fog, dramatic sunbeams.",
        "overlay": "ဖုံးကွယ်ထားသော လျှို့ဝှက်ချက်",
        "color": "deep_shadow_gold_beam",
        "score": 91.0,
        "reason": "လျှို့ဝှက်ဆန်းကြယ်မှု ပုံရိပ်ဖြင့် ဗီဒီယိုကို နှိပ်ကြည့်ချင်လာအောင် ဆွဲဆောင်သည်။",
    },
    {
        "id": "tc_05",
        "style": "bold_text_focal",
        "prompt": "Clean studio backdrop with prominent central subject and massive 3D bold typography floating in perspective.",
        "overlay": "အရေးကြီးဆုံး အချက် ၃ ချက်",
        "color": "neon_accent_slate",
        "score": 89.5,
        "reason": "စာသား အဓိက အလေးပေးမှုဖြင့် အချက်အလက် တိကျမှုကို ချက်ချင်း ပေးစွမ်းသည်။",
    },
    {
        "id": "tc_06",
        "style": "intrigue_puzzle",
        "prompt": "Hand holding a glowing magnifying glass over old historical parchment map of Myanmar, magical ambient glow.",
        "overlay": "ဘယ်သူမှ မပြောပြတဲ့ အမှန်",
        "color": "warm_antique_amber",
        "score": 87.0,
        "reason": "စူးစမ်းရှာဖွေမှု အငွေ့အသက်ဖြင့် သမိုင်းနှင့် ဗဟုသုတကို စိတ်ဝင်စားသူများကို ဖမ်းစားသည်။",
    },
    {
        "id": "tc_07",
        "style": "cinematic_action",
        "prompt": "Dynamic dynamic camera angle showing motion blur and rapid action, cinematic lens flare, vivid cinematic grade.",
        "overlay": "ဒီလို ဖြစ်သွားတယ်!",
        "color": "action_orange_teal",
        "score": 85.5,
        "reason": "လှုပ်ရှားမှုနှင့် အရှိန်အဟုန်ကို ဖော်ပြပြီး စိတ်လှုပ်ရှားမှုကို မြှင့်တင်သည်။",
    },
    {
        "id": "tc_08",
        "style": "hero_character",
        "prompt": "Confident protagonist facing camera directly, soft professional studio lighting, authentic Burmese style modern aesthetic.",
        "overlay": "ကျွန်တော့် ကိုယ်တွေ့ အဖြစ်အပျက်",
        "color": "natural_warm_studio",
        "score": 84.0,
        "reason": "ကိုယ်တွေ့ ဇာတ်လမ်း ပုံစံဖြင့် ရင်းနှီးကျွမ်းဝင်မှုနှင့် ယုံကြည်စိတ်ကို တည်ဆောက်သည်။",
    },
    {
        "id": "tc_09",
        "style": "curiosity_peek",
        "prompt": "Subject peeking through a slightly opened wooden door with dazzling bright light spilling out from inside.",
        "overlay": "တံခါးဖွင့်ကြည့်လိုက်တော့…",
        "color": "dark_room_spill_light",
        "score": 82.0,
        "reason": "ချောင်းကြည့်ချင်သော စိတ်သဘောထားကို အသုံးချ၍ Click-Through-Rate ကို တက်စေသည်။",
    },
    {
        "id": "tc_10",
        "style": "documentary_evidence",
        "prompt": "Collage of forensic documents, red pinned yarn connecting clues on a dark pinboard, noir atmosphere.",
        "overlay": "ခိုင်လုံသော သက်သေများ",
        "color": "noir_red_string_dark",
        "score": 80.5,
        "reason": "သက်သေအထောက်အထား ခိုင်မာမှုကို ပြသပြီး အချက်အလက် ခိုင်လုံမှုဖြင့် ဆွဲဆောင်သည်။",
    },
]


def generate_thumbnail_candidates(
    title: str,
    hook: str | None = None,
    category: str | None = None,
) -> list[ThumbnailCandidateItem]:
    topic = " ".join(title.split()).strip()
    candidates: list[ThumbnailCandidateItem] = []
    for preset in THUMBNAIL_PRESETS:
        prompt = f"{preset['prompt']} Context: {topic[:100]}"
        candidates.append(
            ThumbnailCandidateItem(
                id=preset["id"],
                visual_prompt=prompt,
                overlay_text=preset["overlay"],
                composition_style=preset["style"],
                color_mood=preset["color"],
                score=float(preset["score"]),
                reason=preset["reason"],
            )
        )
    return candidates


def shortlist_thumbnail_candidates(
    candidates: list[ThumbnailCandidateItem],
    count: int = 5,
) -> list[ThumbnailCandidateItem]:
    return sorted(candidates, key=lambda c: -c.score)[:count]


def approve_thumbnail_candidate(
    db: Session,
    episode_id: str,
    candidate_id: str,
    visual_prompt: str,
    overlay_text: str,
    notes: str = "",
) -> dict[str, Any]:
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not episode:
        raise ValueError("Episode not found")

    # Find or create review record
    record = db.query(ReviewRecord).filter(ReviewRecord.episode_id == episode_id).first()
    if not record:
        record = ReviewRecord(episode_id=episode_id)
        db.add(record)

    # Update checklist JSON to set thumbnail_present: True
    checklist = json.loads(record.checklist_json or "{}") if record.checklist_json else {}
    checklist["thumbnail_present"] = True
    record.checklist_json = json.dumps(checklist)

    # Store approved thumbnail metadata in review record
    approved_data = {
        "candidate_id": candidate_id,
        "visual_prompt": visual_prompt,
        "overlay_text": overlay_text,
        "notes": notes,
        "approved_at": datetime.now(timezone.utc).isoformat(),
        "status": "approved",
    }
    record.notes = (record.notes or "") + f"\n[Thumbnail Approved: {candidate_id} - '{overlay_text}']"
    record.updated_at = datetime.now(timezone.utc)

    # Ensure a thumbnail Asset exists so _review_assets recognizes it
    thumbnail_asset = (
        db.query(Asset)
        .filter(Asset.episode_id == episode_id, Asset.asset_type == "thumbnail")
        .first()
    )
    if not thumbnail_asset:
        thumbnail_asset = Asset(
            episode_id=episode_id,
            asset_type="thumbnail",
            original_filename=f"thumbnail_{candidate_id}.png",
            storage_provider="local",
            mime_type="image/png",
            file_size_bytes=1024,
            version=1,
            is_final=True,
            status="uploaded",
        )
        db.add(thumbnail_asset)
    else:
        thumbnail_asset.is_final = True
        thumbnail_asset.status = "uploaded"

    db.commit()
    db.refresh(record)
    return {
        "episode_id": episode_id,
        "approved_thumbnail": approved_data,
        "thumbnail_present": True,
        "message": f"Thumbnail candidate '{candidate_id}' approved successfully.",
    }
