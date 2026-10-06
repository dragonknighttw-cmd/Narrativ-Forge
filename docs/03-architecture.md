# Architecture

```
Next.js
  ↓
FastAPI
  ↓
PostgreSQL
  ↓
Redis / Celery
  ↓
Worker
 ├─ FFmpeg
 ├─ Whisper / Cloudflare Whisper
 ├─ Cloud LLM
 ├─ Character / LoRA assets
 └─ Drive Export
  ↓
Google Drive
```

## Responsibilities
- Next.js: UI, editor, player, review
- FastAPI: auth, CRUD, validation, permissions
- PostgreSQL: workflow state
- Worker: heavy processing
- FFmpeg: media processing
- Whisper: transcript
- Cloud LLM: script/structure/assistance
- Drive: approved export

## Status
`idea → planned → script_draft → script_review → assets_needed → in_production → processing → subtitle_review → needs_approval → approved → exporting → exported`

## Character / LoRA strategy

The current target strategy keeps LoRA usage narrow.

| Character | LoRA | Space |
|---|---|---:|
| Main Characters (3) | ✅ Required | ~600 MB |
| Walk-on / background (20+) | ❌ Prompt only | 0 MB |

### LoRA training
- Platform: Kaggle (free allocation) / Google Colab
- Tool: Kohya's GUI
- Time target: 1–2 hours per LoRA
- Storage: Backblaze B2 primary + Google Drive backup

### Database target

```
characters
- id
- name
- type (main / side / background)
- lora_url (main only)
- prompt_template (side/background)
```

LoRA is a **target/reserve capability**, not proof that the current repository already has the complete training and generation pipeline. See `04-current-vs-target.md`.

## Current implementation
README reports the core content workflow, scripts/scenes/assets, processing/Celery foundation, subtitles, review/approval, storage routing, Drive foundation, analytics/log foundations, billing foundation, tenant scope, webhooks, and security hardening implemented.

The remaining gap is primarily **real integration/runtime verification**, plus explicit UI/data/business gaps listed in current-vs-target.
