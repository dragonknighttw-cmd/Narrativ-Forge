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
- Drive: approved export

## Status
`idea → planned → script_draft → script_review → assets_needed → in_production → processing → subtitle_review → needs_approval → approved → exporting → exported`

## Current implementation
README reports the core content workflow, scripts/scenes/assets, processing/Celery foundation, subtitles, review/approval, storage routing, Drive foundation, analytics/log foundations, billing foundation, tenant scope, webhooks, and security hardening implemented.

The remaining gap is primarily **real integration/runtime verification**, plus explicit UI/data/business gaps listed in current-vs-target.