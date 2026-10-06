# Narrativ Forge — Auto Architecture

## High-level

```
Next.js Frontend
      ↓
FastAPI Backend
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

## Responsibility boundaries

| Layer | Responsibility |
|---|---|
| Next.js | UI, editors, player, review |
| FastAPI | auth, CRUD, validation, permissions |
| PostgreSQL | workflow state |
| Worker | heavy processing |
| FFmpeg | media extraction/assembly |
| Whisper | transcript |
| Google Drive | approved export |

## Status model

`idea → planned → script_draft → script_review → assets_needed → in_production → processing → subtitle_review → needs_approval → approved → exporting → exported`

Revision paths:
- script_review → script_draft
- subtitle_review → in_production
- needs_approval → in_production
- exporting → failed → processing

## Current implementation reality

The repository already contains the application foundation, content workflow, script/scene/assets, processing-job/Celery foundation, subtitle foundation, review/approval foundation, storage routing, Drive foundation, analytics/log foundations, billing foundation, tenant foundation, and security hardening.

The important remaining gap is not simply “build the feature”; it is proving the real integrations and production runtime end-to-end.
