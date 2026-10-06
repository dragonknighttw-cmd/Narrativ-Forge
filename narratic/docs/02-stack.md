# Narrativ Forge — Stack & Constraints

## Hard constraints

- No paid services as a dependency where a free alternative is viable
- No R2
- No AWS S3
- No Docker
- No WSL
- No Ollama
- No LM Studio
- Local-space limitations are the stated reason for local-heavy tooling constraints

## Selected stack

| Area | Current / target choice |
|---|---|
| Source | GitHub |
| Frontend | Next.js + React + TypeScript + Tailwind |
| UI | shadcn/ui planned |
| Backend | FastAPI + SQLAlchemy + Alembic + Pydantic |
| Database | Neon PostgreSQL production; SQLite local |
| Queue | Celery + Redis |
| Frontend hosting | Netlify |
| Backend hosting | Render free |
| Raw media | Backblaze B2 |
| Images/previews | Cloudinary |
| SRT/manifest | Supabase Storage |
| Final export | Google Drive API + OAuth 2.0 |
| Edge/AI | Cloudflare Worker / Workers AI |
| Script LLM | Groq / other cloud adapters |
| TTS | Edge-TTS fallback; Fliki manual |
| Images | Pollinations manual |
| Video | ffmpeg.wasm + server FFmpeg fallback |
| Monitoring | Sentry + UptimeRobot |
| Email | Resend |
| Billing | Stripe |
| CI/CD | GitHub Actions + Netlify/Render CI |
| Security | CodeQL, Trivy, pip-audit, npm audit |
| E2E/backend tests | Playwright + pytest |

## Important implementation distinction

The roadmap lists several providers as possible or planned. The repository README is the authority for what is actually implemented and deployed. Provider availability must be verified with real credentials before declaring production readiness.

## Deployment shape

GitHub main → Netlify frontend + Render API. Processing must stay behind a worker boundary; free-only deployment may require a dedicated worker decision before production.
