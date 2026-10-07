# Architecture

> Owner: Backend/platform maintainers  
> Update when: service boundaries, durable workflow, queue/runtime, or provider architecture changes  
> Last Updated: 2026-10-08  
> Do NOT put here: live credentials or operational incident history

## Canonical workflow engine

`workflow.py` is the canonical workflow engine. PostgreSQL is the durable source of workflow state. Do not introduce a second workflow engine.

```
Next.js → FastAPI → PostgreSQL
                    ↓
              delivery/worker boundary
             ↙       ↓        ↘
          FFmpeg   Whisper    AI/export
                    ↓
          B2 / Supabase / Cloudinary
                    ↓
               Google Drive
```

## Responsibilities

- Next.js: UI, editing, player, review.
- FastAPI: auth, CRUD, validation, authorization, orchestration API.
- PostgreSQL: durable workflow/version/audit state.
- Worker: heavy media and asynchronous processing.
- FFmpeg: media transformation.
- Whisper/Cloudflare Whisper: transcription.
- AI adapters: script/structure/assistance.
- Storage adapters: provider routing.
- Drive adapter: approved-output export.

## Durable execution

Processing jobs are persisted in PostgreSQL and delivered through the configured queue/runtime. Redis/Celery code exists for worker execution. QStash durable delivery is part of the deployment strategy where enabled. `CELERY_ENABLED=false` is the documented free-first deployment default; Celery/Redis remains an optional worker path.

Do not infer that an available queue credential means a worker is healthy.

## Tenant/security boundary

The backend owns database access. The frontend must not use service-role credentials. RLS is defense-in-depth where configured; application authorization remains authoritative.

## Storage boundary

Storage is hybrid:
- B2 for raw/large media.
- Cloudinary for small images/previews.
- Supabase Storage for small workflow files such as SRT/manifests.
- local storage only for development/temporary work.
- Google Drive for approved final output.

## AI architecture

AI providers are adapter-based. Current text routing supports Groq/OpenAI-compatible providers with deterministic Mock fallback. Cloudflare Workers AI Whisper is a separate transcription path. Public AI is disabled by default where configured; backend AI gates are authoritative.

Legacy agents are kept separate from the canonical workflow engine.

## Architecture decisions

- No second workflow engine.
- Application DB remains workflow source of truth.
- Human approval is mandatory before final export.
- Heavy processing stays outside request/response paths.
- Direct social publishing is out of scope.
