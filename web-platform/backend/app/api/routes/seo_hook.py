"""
SEO Hook Generator — Narrativ Forge brain feature.

Generates 5 viral hook/title variants from a story plot using LLM.
Falls back to extractive templates if LLM is unavailable.

Endpoints:
  POST /brain/seo/generate-hooks  — generate 5 hook variants
  GET  /brain/seo/hook-styles     — list available styles
"""
from __future__ import annotations

import json as _json
import logging

import httpx
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...db import get_db
from ...core.config import settings

log = logging.getLogger("narrativ.seo_hook")
router = APIRouter(prefix="/brain/seo", tags=["seo-hook"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class HookVariant(BaseModel):
    style: str         # curiosity | suspense | trending | question | bold
    hook_text: str
    score: float       # 0.0–1.0 estimated engagement score
    reasoning: str


class HookRequest(BaseModel):
    story_title: str
    plot_summary: str
    genre: str = "general"
    target_audience: str = "general readers"


class HookResponse(BaseModel):
    story_title: str
    hooks: list[HookVariant]
    best_hook: str
    seo_keywords: list[str]


# ---------------------------------------------------------------------------
# Internal LLM helper — uses OpenRouter free tier via httpx (same as ai_adapter)
# ---------------------------------------------------------------------------

def _get_openrouter_key() -> str:
    return (
        getattr(settings, "OPENROUTER_API_KEY", "")
        or getattr(settings, "ADMIN_OPENROUTER_API_KEY", "")
        or ""
    )


def _get_free_model() -> str:
    return getattr(
        settings,
        "DEFAULT_FREE_MODEL",
        "meta-llama/llama-3.1-8b-instruct:free",
    )


def _call_openrouter_sync(system: str, user: str) -> str:
    """Synchronous httpx call to OpenRouter — consistent with ai_adapter pattern."""
    api_key = _get_openrouter_key()
    if not api_key:
        return ""
    try:
        resp = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": _get_free_model(),
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0.7,
            },
            timeout=getattr(settings, "ai_provider_timeout_seconds", 30.0),
        )
        resp.raise_for_status()
        choices = resp.json().get("choices") or []
        return ((choices[0] if choices else {}).get("message") or {}).get("content", "")
    except Exception as exc:
        log.warning(f"OpenRouter SEO hook call failed: {exc}")
        return ""


# ---------------------------------------------------------------------------
# Fallback template hooks
# ---------------------------------------------------------------------------

def _fallback_hooks(title: str, genre: str, audience: str) -> tuple[list[dict], str, list[str]]:
    hooks = [
        {"style": "curiosity",  "hook_text": f"What really happens in {title}?",               "score": 0.60, "reasoning": "Curiosity gap drives clicks"},
        {"style": "suspense",   "hook_text": f"The untold truth behind {title}",                "score": 0.55, "reasoning": "Mystery builds anticipation"},
        {"style": "bold",       "hook_text": f"{title} — a story that changes everything",      "score": 0.50, "reasoning": "Bold claim demands attention"},
        {"style": "question",   "hook_text": f"Could {title} happen to you?",                   "score": 0.50, "reasoning": "Personal identification"},
        {"style": "trending",   "hook_text": f"Why everyone is talking about {title} right now", "score": 0.45, "reasoning": "Social proof signal"},
    ]
    best = hooks[0]["hook_text"]
    keywords = [genre.lower(), title.lower(), audience.lower()]
    return hooks, best, keywords


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/generate-hooks", response_model=HookResponse, status_code=status.HTTP_200_OK)
def generate_seo_hooks(
    payload: HookRequest,
    db: Session = Depends(get_db),
):
    """
    Generate 5 SEO hook variants for a story.

    Uses LLM (OpenRouter free tier) with an extractive fallback.
    No extra API key needed — reuses OPENROUTER_API_KEY.
    """
    system_prompt = (
        "You are an expert content strategist specialising in story hooks and SEO. "
        "Generate exactly 5 hook variants for the given story. "
        "Each hook must be under 20 words and maximise engagement. "
        "Styles must be: curiosity, suspense, trending, question, bold. "
        'Respond ONLY in JSON: {"hooks":[{"style":"curiosity","hook_text":"...","score":0.85,'
        '"reasoning":"..."},...], "best_hook":"...", "seo_keywords":["...","...","..."]}'
    )
    user_prompt = (
        f"Story Title: {payload.story_title}\n"
        f"Genre: {payload.genre}\n"
        f"Target Audience: {payload.target_audience}\n"
        f"Plot Summary: {payload.plot_summary[:1500]}"
    )

    raw = _call_openrouter_sync(system_prompt, user_prompt)

    hooks_data: list[dict] = []
    best_hook = ""
    seo_keywords: list[str] = []

    if raw:
        # Strip markdown fences if present
        text = raw.strip()
        if text.startswith("```"):
            lines = text.splitlines()[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        try:
            parsed = _json.loads(text)
            hooks_data = parsed.get("hooks", [])
            best_hook = parsed.get("best_hook", "")
            seo_keywords = parsed.get("seo_keywords", [])
        except Exception:
            log.warning("SEO hook LLM response was not valid JSON; using fallback")

    if not hooks_data:
        hooks_data, best_hook, seo_keywords = _fallback_hooks(
            payload.story_title, payload.genre, payload.target_audience
        )

    return HookResponse(
        story_title=payload.story_title,
        hooks=[HookVariant(**h) for h in hooks_data],
        best_hook=best_hook or (hooks_data[0]["hook_text"] if hooks_data else ""),
        seo_keywords=seo_keywords,
    )


@router.get("/hook-styles")
def list_hook_styles():
    """List available hook styles with descriptions."""
    return {
        "styles": [
            {"name": "curiosity",  "description": "Creates a knowledge gap the reader wants to fill"},
            {"name": "suspense",   "description": "Builds tension and mystery around the story"},
            {"name": "trending",   "description": "Uses social proof and trend signals"},
            {"name": "question",   "description": "Direct question that makes reader self-identify"},
            {"name": "bold",       "description": "Confident direct statement that commands attention"},
        ]
    }
