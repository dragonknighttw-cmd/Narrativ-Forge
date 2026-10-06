# Stack & Constraints

## Constraints
No R2, AWS S3, Docker, WSL, Ollama, LM Studio, or paid dependency where a free alternative is viable.

## Selected stack
- GitHub
- Next.js + React + TypeScript + Tailwind
- FastAPI + SQLAlchemy + Alembic + Pydantic
- Neon PostgreSQL; SQLite local
- Celery + Redis
- Netlify frontend
- Render backend
- Backblaze B2 raw media
- Cloudinary images/previews
- Supabase Storage for SRT/manifest
- Google Drive API + OAuth 2.0
- Cloudflare Worker / Workers AI
- Groq / cloud LLM adapters
- Edge-TTS fallback
- ffmpeg.wasm + server FFmpeg
- Sentry + UptimeRobot
- Resend
- Stripe
- GitHub Actions
- CodeQL / Trivy / pip-audit / npm audit
- Playwright + pytest

## Cloud LLM API stack

| Tool | Free Tier | Card |
|---|---|---|
| Groq | 14,400 req/day | ❌ |
| Cloudflare Workers AI | 10,000 neurons/day | ❌ |
| Google AI Studio | Free Tier | ❌ |
| OpenRouter | Free Models | ❌ |
| Mistral | Free Mode | ❌ |

### Planning baseline

For conservative planning, use **1,000 requests/day** as the working baseline until the actual account/model limits are verified.

- One video: approximately 6–10 requests, including revisions.
- 1,000 req/day ÷ 10 = **100 videos/day in theory**.
- Practical planning target: **5–10 videos/day**, because review and human approval time are the real bottleneck.

Provider limits can change; verify live account limits before production capacity planning.

## Local model exclusions
- Ollama — not used.
- LM Studio — not used.

The current plan prefers cloud/free-tier APIs so the production machine does not need to reserve local model storage/compute.

## Important
The roadmap lists possible providers; the repository README decides actual implementation/deployment state. Real credentials and live tests are required before calling an integration production-ready.
