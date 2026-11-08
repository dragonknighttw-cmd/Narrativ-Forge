"""Manga & Webtoon Generation Engine for Narrativ Forge.

Supports:
- Multi-panel layout generation (Webtoon Vertical, 4-Koma, Classic 3x2 Manga Grid, Cinematic Splash)
- Speech Bubble placement & tail pointer vectors (speech, shout, thought, whisper)
- Onomatopoeia / Action Sound Effects (Japanese ドドド/ゴゴゴ and Burmese ဒုန်း/ဝုန်း)
- Monochrome Screentone & Halftone visual effects
- Motion Comic Camera keyframing (Pan, Zoom, Shake, Transitions) for Manga-to-Video conversion
"""

from __future__ import annotations

import math
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .storyboard_generator import StoryboardGeneratorService


class LayoutType(str, Enum):
    WEBTOON_VERTICAL = "webtoon_vertical"
    YONKOMA_4KOMA = "4koma"
    MANGA_GRID_3X2 = "manga_grid_3x2"
    CINEMATIC_SPLASH = "cinematic_splash"


class BubbleType(str, Enum):
    SPEECH = "speech"
    SHOUT = "shout"
    THOUGHT = "thought"
    WHISPER = "whisper"


class VisualEffectType(str, Enum):
    SCREENTONE_DOTS = "screentone_dots"
    SPEED_LINES = "speed_lines"
    RADIAL_EXPLOSION = "radial_explosion"
    DARK_AURA = "dark_aura"
    SPARKLE_SHOUJO = "sparkle_shoujo"


# Pre-curated Manga Sound Effects / Onomatopoeia
MANGA_SFX_CATALOG = [
    {"romaji": "DODODO", "japanese": "ドドド", "burmese": "ဒုတ်ဒုတ်ဒုတ်", "meaning": "Heavy rumble / approaching danger", "style": "action"},
    {"romaji": "GOGOGO", "japanese": "ゴゴゴ", "burmese": "ဝေါင်းဝေါင်း", "meaning": "Menacing presence / rising tension", "style": "aura"},
    {"romaji": "BAAAN", "japanese": "バーン", "burmese": "ဒုန်း!", "meaning": "Loud boom / dramatic revelation", "style": "impact"},
    {"romaji": "SHUT", "japanese": "シュッ", "burmese": "ဖျတ်ခနဲ", "meaning": "Swift dash / ninja speed line", "style": "speed"},
    {"romaji": "GAAN", "japanese": "ガーン", "burmese": "ဟာ!", "meaning": "Shock / dismay / betrayal", "style": "emotion"},
    {"romaji": "DOKI DOKI", "japanese": "ドキドキ", "burmese": "ဒိတ်ဒိတ်", "meaning": "Heartbeat / romantic suspense", "style": "emotion"},
]


@dataclass
class SpeechBubble:
    id: str
    text: str
    speaker: str
    bubble_type: BubbleType = BubbleType.SPEECH
    x_percent: float = 50.0  # Percentage position within panel
    y_percent: float = 20.0
    width_percent: float = 40.0
    tail_direction: str = "bottom-left"  # "bottom-left", "bottom-right", "top", "none"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "speaker": self.speaker,
            "bubble_type": self.bubble_type.value,
            "x_percent": self.x_percent,
            "y_percent": self.y_percent,
            "width_percent": self.width_percent,
            "tail_direction": self.tail_direction,
        }


@dataclass
class MangaPanel:
    panel_index: int
    title: str
    visual_prompt: str
    aspect_ratio: str
    width_ratio: float
    height_ratio: float
    image_url: Optional[str] = None
    bubbles: List[SpeechBubble] = field(default_factory=list)
    sfx: Optional[Dict[str, str]] = None
    effect: Optional[VisualEffectType] = None
    camera_cue: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "panel_index": self.panel_index,
            "title": self.title,
            "visual_prompt": self.visual_prompt,
            "aspect_ratio": self.aspect_ratio,
            "width_ratio": self.width_ratio,
            "height_ratio": self.height_ratio,
            "image_url": self.image_url,
            "bubbles": [b.to_dict() for b in self.bubbles],
            "sfx": self.sfx,
            "effect": self.effect.value if self.effect else None,
            "camera_cue": self.camera_cue,
        }


class MangaEngine:
    """Core generator and motion comic compiler for Manga & Webtoons."""

    @classmethod
    def _build_panel_image_url(cls, prompt: str, aspect_ratio: str = "4:3") -> str:
        ratio = "16:9" if aspect_ratio == "16:9" else ("1:1" if aspect_ratio == "1:1" else "9:16")
        return StoryboardGeneratorService.build_storyboard_url(
            prompt=prompt,
            aspect_ratio=ratio,
            model="flux",
            enhance=True,
        )

    @classmethod
    def get_layout_templates(cls) -> List[Dict[str, Any]]:
        return [
            {
                "id": LayoutType.WEBTOON_VERTICAL.value,
                "name": "Vertical Webtoon Strip",
                "orientation": "vertical",
                "panel_count": 4,
                "aspect_ratio": "9:16",
                "description": "Infinite-scroll mobile format with dynamic vertical pacing and gutters.",
            },
            {
                "id": LayoutType.YONKOMA_4KOMA.value,
                "name": "Classic 4-Koma Comic Strip",
                "orientation": "vertical_strip",
                "panel_count": 4,
                "aspect_ratio": "4:3",
                "description": "Japanese 4-panel structure: Ki (Intro), Shō (Development), Ten (Climax), Ketsu (Punchline).",
            },
            {
                "id": LayoutType.MANGA_GRID_3X2.value,
                "name": "Manga Page 6-Grid",
                "orientation": "page",
                "panel_count": 6,
                "aspect_ratio": "3:4",
                "description": "Traditional printed tankobon page layout with reading flow from right to left.",
            },
            {
                "id": LayoutType.CINEMATIC_SPLASH.value,
                "name": "Cinematic Splash Spread",
                "orientation": "widescreen",
                "panel_count": 3,
                "aspect_ratio": "16:9",
                "description": "Dominant full-bleed hero panel with 2 dynamic action cutaways.",
            },
        ]

    @classmethod
    def generate_manga_page(
        cls,
        title: str,
        story_synopsis: str,
        layout_type: LayoutType = LayoutType.WEBTOON_VERTICAL,
        anime_style_prompt: str = "anime style, makoto shinkai aesthetic, high contrast manga inks, crisp lineart",
        character_names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate panel breakdown, visual prompts, and speech bubble layouts for a story scene."""
        characters = character_names or ["Protagonist", "Rival"]
        panels: List[MangaPanel] = []

        if layout_type == LayoutType.YONKOMA_4KOMA:
            stages = [
                ("1. Ki (起 - Introduction)", "Normal peaceful setting, character introduced", 0),
                ("2. Shō (承 - Development)", "An unexpected event or challenge begins to unfold", 1),
                ("3. Ten (転 - The Twist)", "Sudden comedic or high-stakes turn of events", 2),
                ("4. Ketsu (結 - Punchline)", "Final resolution, punchline reaction or dramatic cliffhanger", 3),
            ]
            for idx, (stage_name, stage_desc, step) in enumerate(stages):
                prompt = (
                    f"{stage_desc}, {story_synopsis}, {anime_style_prompt}, panel {idx + 1}"
                )
                bubble_text = f"Dialog for step {idx + 1}: {stage_name}"
                bubbles = [
                    SpeechBubble(
                        id=f"bubble_{idx}_1",
                        text=bubble_text,
                        speaker=characters[idx % len(characters)],
                        bubble_type=BubbleType.SHOUT if step == 2 else BubbleType.SPEECH,
                        x_percent=25.0 if idx % 2 == 0 else 55.0,
                        y_percent=20.0,
                        tail_direction="bottom-left" if idx % 2 == 0 else "bottom-right",
                    )
                ]
                sfx_item = MANGA_SFX_CATALOG[idx % len(MANGA_SFX_CATALOG)]
                panels.append(
                    MangaPanel(
                        panel_index=idx + 1,
                        title=stage_name,
                        visual_prompt=prompt,
                        aspect_ratio="4:3",
                        width_ratio=1.0,
                        height_ratio=0.25,
                        image_url=cls._build_panel_image_url(prompt, aspect_ratio="4:3"),
                        bubbles=bubbles,
                        sfx=sfx_item,
                        effect=VisualEffectType.SPEED_LINES if step == 2 else None,
                        camera_cue={
                            "action": "zoom_in" if step == 2 else "pan_right",
                            "duration_seconds": 3.0,
                            "zoom_scale": 1.25 if step == 2 else 1.05,
                        },
                    )
                )

        elif layout_type == LayoutType.CINEMATIC_SPLASH:
            # 3 Panels: 1 Huge Hero Panel + 2 Action Insets
            p1_prompt = f"Grand heroic battle scene, {story_synopsis}, {anime_style_prompt}, masterpiece widescreen"
            panels.append(
                MangaPanel(
                    panel_index=1,
                    title="Main Hero Splash",
                    visual_prompt=p1_prompt,
                    aspect_ratio="16:9",
                    width_ratio=1.0,
                    height_ratio=0.65,
                    image_url=cls._build_panel_image_url(p1_prompt, aspect_ratio="16:9"),
                    bubbles=[
                        SpeechBubble(
                            id="splash_bubble_1",
                            text="This ends now!",
                            speaker=characters[0],
                            bubble_type=BubbleType.SHOUT,
                            x_percent=60.0,
                            y_percent=25.0,
                            tail_direction="bottom-right",
                        )
                    ],
                    sfx=MANGA_SFX_CATALOG[2],  # BAAAN
                    effect=VisualEffectType.RADIAL_EXPLOSION,
                    camera_cue={"action": "camera_shake_and_zoom", "duration_seconds": 4.0, "zoom_scale": 1.3},
                )
            )
            p2_prompt = f"Intense eye close up, {story_synopsis}, {anime_style_prompt}"
            panels.append(
                MangaPanel(
                    panel_index=2,
                    title="Close-Up Reaction",
                    visual_prompt=p2_prompt,
                    aspect_ratio="1:1",
                    width_ratio=0.5,
                    height_ratio=0.35,
                    image_url=cls._build_panel_image_url(p2_prompt, aspect_ratio="1:1"),
                    bubbles=[
                        SpeechBubble(
                            id="splash_bubble_2",
                            text="Impossible... such raw power!",
                            speaker=characters[-1],
                            bubble_type=BubbleType.THOUGHT,
                            x_percent=30.0,
                            y_percent=30.0,
                        )
                    ],
                    sfx=MANGA_SFX_CATALOG[4],  # GAAN
                    effect=VisualEffectType.DARK_AURA,
                    camera_cue={"action": "slow_pan_left", "duration_seconds": 2.5, "zoom_scale": 1.1},
                )
            )
            p3_prompt = f"Energy clash spark lines, high contrast manga ink, {anime_style_prompt}"
            panels.append(
                MangaPanel(
                    panel_index=3,
                    title="Weapon Impact Clash",
                    visual_prompt=p3_prompt,
                    aspect_ratio="1:1",
                    width_ratio=0.5,
                    height_ratio=0.35,
                    image_url=cls._build_panel_image_url(p3_prompt, aspect_ratio="1:1"),
                    bubbles=[],
                    sfx=MANGA_SFX_CATALOG[0],  # DODODO
                    effect=VisualEffectType.SPEED_LINES,
                    camera_cue={"action": "quick_zoom", "duration_seconds": 2.0, "zoom_scale": 1.2},
                )
            )

        else:
            # Default: Webtoon Vertical (4 dynamic panels)
            panel_titles = [
                "Establishing Scene - The Horizon",
                "Encounter - Two Destinies Collide",
                "Climactic Flash - Spark of Battle",
                "Aftermath & Turning Point",
            ]
            for i, ptitle in enumerate(panel_titles):
                is_climax = i == 2
                wb_prompt = f"{ptitle}, {story_synopsis}, {anime_style_prompt}, vertical webtoon composition"
                panels.append(
                    MangaPanel(
                        panel_index=i + 1,
                        title=ptitle,
                        visual_prompt=wb_prompt,
                        aspect_ratio="9:16",
                        width_ratio=1.0,
                        height_ratio=1.0,
                        image_url=cls._build_panel_image_url(wb_prompt, aspect_ratio="9:16"),
                        bubbles=[
                            SpeechBubble(
                                id=f"webtoon_bubble_{i}",
                                text=f"Panel dialogue: {ptitle}",
                                speaker=characters[i % len(characters)],
                                bubble_type=BubbleType.SHOUT if is_climax else BubbleType.SPEECH,
                                x_percent=35.0,
                                y_percent=22.0 + (i * 5),
                            )
                        ],
                        sfx=MANGA_SFX_CATALOG[i % len(MANGA_SFX_CATALOG)],
                        effect=VisualEffectType.SPEED_LINES if is_climax else None,
                        camera_cue={
                            "action": "vertical_scroll_down",
                            "duration_seconds": 3.5,
                            "zoom_scale": 1.15 if is_climax else 1.05,
                        },
                    )
                )

        return {
            "page_id": f"manga_page_{uuid.uuid4().hex[:8]}",
            "title": title,
            "layout_type": layout_type.value,
            "total_panels": len(panels),
            "panels": [p.to_dict() for p in panels],
            "motion_comic_ready": True,
            "estimated_video_duration_seconds": sum(
                p.camera_cue.get("duration_seconds", 3.0) for p in panels
            ),
        }

    @classmethod
    def compile_motion_comic_timeline(
        cls,
        manga_page: Dict[str, Any],
        bgm_track: Optional[str] = "anime_cinematic_bgm.mp3",
    ) -> Dict[str, Any]:
        """Convert a static manga page layout into a playable Motion Comic video timeline."""
        panels = manga_page.get("panels", [])
        timeline_cues = []
        current_time = 0.0

        for panel in panels:
            cue = panel.get("camera_cue", {})
            duration = cue.get("duration_seconds", 3.0)
            timeline_cues.append({
                "panel_index": panel.get("panel_index"),
                "title": panel.get("title"),
                "start_time_seconds": round(current_time, 2),
                "end_time_seconds": round(current_time + duration, 2),
                "duration_seconds": duration,
                "camera_action": cue.get("action", "pan_right"),
                "zoom_scale": cue.get("zoom_scale", 1.1),
                "sfx_overlay": panel.get("sfx"),
                "bubbles": panel.get("bubbles", []),
            })
            current_time += duration

        return {
            "motion_comic_id": f"motion_{uuid.uuid4().hex[:8]}",
            "title": f"Motion Comic - {manga_page.get('title', 'Manga Scene')}",
            "total_duration_seconds": round(current_time, 2),
            "total_panels": len(panels),
            "bgm_track": bgm_track,
            "timeline_cues": timeline_cues,
            "export_formats": ["mp4_9_16_tiktok", "mp4_16_9_youtube"],
        }
