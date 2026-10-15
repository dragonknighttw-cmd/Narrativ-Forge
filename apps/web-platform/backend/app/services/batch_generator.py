from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any
from sqlalchemy.orm import Session

from ..models import Episode, Scene, Script, Series
from .hook_engineering import CANONICAL_HOOK_TEMPLATES


@dataclass(frozen=True)
class BatchEpisodeOutline:
    episode_number: int
    title: str
    hook: str
    hook_family: str
    synopsis: str
    target_duration_seconds: int
    cliffhanger: str
    scenes: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class BatchSeriesPlan:
    theme: str
    category: str
    episodes: list[BatchEpisodeOutline]

    def to_dict(self) -> dict[str, Any]:
        return {
            "theme": self.theme,
            "category": self.category,
            "episodes": [
                {
                    "episode_number": ep.episode_number,
                    "title": ep.title,
                    "hook": ep.hook,
                    "hook_family": ep.hook_family,
                    "synopsis": ep.synopsis,
                    "target_duration_seconds": ep.target_duration_seconds,
                    "cliffhanger": ep.cliffhanger,
                    "scenes": ep.scenes,
                }
                for ep in self.episodes
            ],
        }


EPISODE_ARCS = [
    {
        "role": "hook_setup",
        "hook_family": "mystery",
        "title_prefix": "အပိုင်း ၁ — လျှို့ဝှက်ဆန်းကြယ်မှု အစပျိုးခြင်း",
        "synopsis_template": "ဒီအပိုင်းမှာ {theme} နဲ့ပတ်သက်ပြီး လူအများ သတိမထားမိသေးတဲ့ လျှို့ဝှက်ဆန်းကြယ်မှုနဲ့ စတင်မိတ်ဆက်ပေးပါတယ်။ အဓိကပြဿနာနဲ့ မေးခွန်းကို ချပြပါတယ်။",
        "cliffhanger": "ဒါပေမဲ့ အဖြစ်အပျက်ရဲ့ နောက်ကွယ်မှာ ဘယ်သူမှ မထင်ထားတဲ့ အမှန်တရားတစ်ခု ရှိနေသေးတယ်… နောက်အပိုင်းမှာ ဆက်ကြည့်ပါ။",
    },
    {
        "role": "deepening_conflict",
        "hook_family": "shock",
        "title_prefix": "အပိုင်း ၂ — မထင်မှတ်ထားသော အဖြစ်အပျက်",
        "synopsis_template": "{theme} ရဲ့ အဓိက အချက်အလက်တွေကို ပိုမိုနက်ရှိုင်းစွာ တူးဖော်ပြီး ကြည့်ရှုသူကို အံ့သြသွားစေမယ့် ထိတ်လန့်ဖွယ် သက်သေအထောက်အထားတွေကို ဖော်ပြပါတယ်။",
        "cliffhanger": "ဒီအချက်ကို သိလိုက်ရတဲ့အချိန်မှာ အားလုံးဟာ ထင်ထားတာထက် ပိုရှုပ်ထွေးသွားပါပြီ… အပိုင်း ၃ မှာ အဖြေရှိပါတယ်။",
    },
    {
        "role": "turning_point",
        "hook_family": "warning",
        "title_prefix": "အပိုင်း ၃ — အရေးကြီးသော သတိပေးချက်နှင့် အလှည့်အပြောင်း",
        "synopsis_template": "{theme} နဲ့ပတ်သက်တဲ့ အဓိက အန္တရာယ်နဲ့ အလွဲတွေကို ရှင်းလင်းပြသပြီး ဇာတ်လမ်းရဲ့ အထွတ်အထိပ် အလှည့်အပြောင်းကို ရောက်ရှိစေပါတယ်။",
        "cliffhanger": "ဒါဟာ ရိုးရိုးရှင်းရှင်း အမှားတစ်ခု မဟုတ်ပါဘူး။ တကယ်တမ်း ဘာကြောင့် ဖြစ်ပျက်ခဲ့ရတာလဲ?",
    },
    {
        "role": "twist_revelation",
        "hook_family": "contrarian",
        "title_prefix": "အပိုင်း ၄ — ဆန့်ကျင်ဘက် အမှန်တရားနှင့် ဖော်ထုတ်ချက်",
        "synopsis_template": "လူအများ လက်ခံထားကြတဲ့ အယူအဆတွေကို ချေဖျက်ပြီး {theme} ရဲ့ တကယ့်အရှိတရားနဲ့ ဆန့်ကျင်ဘက် အမြင်သစ်ကို သက်သေပြပါတယ်။",
        "cliffhanger": "အခုဆိုရင် အရာအားလုံးရဲ့ အဓိက သော့ချက်ကို ရရှိသွားပါပြီ။ ဇာတ်သိမ်းပိုင်းမှာ အဆုံးသတ် အဖြေကို တွေ့ရမှာပါ။",
    },
    {
        "role": "resolution_payoff",
        "hook_family": "number",
        "title_prefix": "အပိုင်း ၅ — နိဂုံးချုပ်နှင့် အဓိက သင်ခန်းစာ ၃ ချက်",
        "synopsis_template": "{theme} စီးရီးတစ်ခုလုံးရဲ့ အဓိက အနှစ်ချုပ်၊ လက်တွေ့အသုံးချနိုင်မယ့် သင်ခန်းစာ ၃ ချက်နဲ့ ကြည့်ရှုသူအတွက် အရေးကြီးဆုံး takeaway ကို ပေးပြီး နိဂုံးချုပ်ပါတယ်။",
        "cliffhanger": "ဒီစီးရီးကနေ အဓိက အကျိုးကျေးဇူးကို ရရှိခဲ့ရင် နောက်ထပ် စိတ်ဝင်စားဖွယ် စီးရီးသစ်များအတွက် Subscribe / Follow လုပ်ထားပေးပါ။",
    },
]


def generate_5_episode_batch(
    theme: str,
    category: str = "general",
    target_duration_seconds: int = 180,
) -> BatchSeriesPlan:
    theme = " ".join(theme.split()).strip()
    if not theme:
        raise ValueError("theme is required")
    target_duration = max(60, min(300, int(target_duration_seconds or 180)))

    outlines: list[BatchEpisodeOutline] = []
    for idx, arc in enumerate(EPISODE_ARCS, start=1):
        hook_fam = arc["hook_family"]
        template = CANONICAL_HOOK_TEMPLATES.get(hook_fam, "ဒီအကြောင်းကို သိထားသင့်တာက…")
        hook_text = f"{template} {theme}"
        title = f"{arc['title_prefix']}: {theme}"
        synopsis = arc["synopsis_template"].format(theme=theme)
        cliffhanger = arc["cliffhanger"]

        scene_duration = target_duration // 3
        scenes = [
            {
                "scene_number": 1,
                "purpose": "hook",
                "description": f"မျက်စိဖမ်းစားမယ့် Opening Hook — {hook_fam.upper()} ပုံစံဖြင့် စတင်ခြင်း",
                "dialogue": hook_text,
                "duration_seconds": min(15, scene_duration),
            },
            {
                "scene_number": 2,
                "purpose": "body",
                "description": f"အဓိက အကြောင်းအရာ ရှင်းလင်းချက် — {theme}",
                "dialogue": synopsis,
                "duration_seconds": target_duration - min(15, scene_duration) - 15,
            },
            {
                "scene_number": 3,
                "purpose": "payoff",
                "description": "နိဂုံးချုပ်နှင့် နောက်အပိုင်းသို့ ဆက်စပ်ပေးသော Cliffhanger",
                "dialogue": cliffhanger,
                "duration_seconds": 15,
            },
        ]

        outlines.append(
            BatchEpisodeOutline(
                episode_number=idx,
                title=title,
                hook=hook_text,
                hook_family=hook_fam,
                synopsis=synopsis,
                target_duration_seconds=target_duration,
                cliffhanger=cliffhanger,
                scenes=scenes,
            )
        )

    return BatchSeriesPlan(
        theme=theme,
        category=category or "general",
        episodes=outlines,
    )


def _generate_public_id(db: Session) -> str:
    prefix = date.today().strftime("nar_%Y%m%d_")
    count = db.query(Episode).filter(Episode.public_id.like(prefix + "%")).count()
    return f"{prefix}{count + 1:04d}"


def commit_batch_episodes(
    db: Session,
    organization_id: str,
    plan: BatchSeriesPlan,
    series_id: str | None = None,
) -> tuple[Series, list[Episode]]:
    series: Series | None = None
    if series_id:
        series = db.query(Series).filter(Series.id == series_id, Series.organization_id == organization_id).first()
    if not series:
        series = Series(
            organization_id=organization_id,
            title=f"{plan.theme} (၅ ပိုင်းတွဲ စီးရီး)",
            description=f"Automated 5-Episode Batch Production for '{plan.theme}' ({plan.category})",
        )
        db.add(series)
        db.flush()

    episodes: list[Episode] = []
    for outline in plan.episodes:
        pub_id = _generate_public_id(db)
        ep = Episode(
            organization_id=organization_id,
            public_id=pub_id,
            series_id=series.id,
            episode_number=outline.episode_number,
            title=outline.title,
            category=plan.category,
            synopsis=outline.synopsis,
            target_duration_seconds=outline.target_duration_seconds,
            status="planned",
            current_step="structure",
        )
        db.add(ep)
        db.flush()

        script_content = f"HOOK:\n{outline.hook}\n\nSYNOPSIS:\n{outline.synopsis}\n\nCLIFFHANGER:\n{outline.cliffhanger}"
        script = Script(
            episode_id=ep.id,
            version=1,
            title=outline.title,
            content=script_content,
            is_current=True,
            status="draft",
        )
        db.add(script)
        db.flush()

        for s in outline.scenes:
            scene = Scene(
                episode_id=ep.id,
                script_id=script.id,
                scene_number=s["scene_number"],
                purpose=s["purpose"],
                description=s["description"],
                dialogue=s["dialogue"],
                duration_seconds=s["duration_seconds"],
            )
            db.add(scene)

        episodes.append(ep)

    db.commit()
    for ep in episodes:
        db.refresh(ep)
    db.refresh(series)
    return series, episodes
