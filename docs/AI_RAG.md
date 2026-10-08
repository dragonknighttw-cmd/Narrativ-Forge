# AI / RAG

> Owner: AI/platform maintainers  
> Update when: providers, prompts, retrieval, quotas, or AI safety gates change  
> Last Updated: 2026-10-08  
> Do NOT put here: provider secrets

## Provider architecture

Text generation is adapter-based:
- Groq: configured provider path.
- OpenAI-compatible provider: configured provider path.
- Mock: deterministic fallback for tests/development.

Cloudflare Workers AI Whisper is a separate transcription adapter/path.

Provider code/configuration does not prove provider health. Live limits, terms, latency, quality, and commercial use require live verification.

## Live Whisper evidence

**VERIFIED — 2026-10-08:** Cloudflare Worker `narrativ-forge-whisper` is present in the connected Cloudflare account, has a live 100% deployment version created 2026-10-07, has the required `NARRATIV_SHARED_SECRET` binding, and is reachable at:

https://narrativ-forge-whisper.narrativ-forge.workers.dev

This verifies deployment/configuration only. It does **not** verify authenticated real-audio transcription, VTT output correctness, Subtitle Studio integration, quota/fallback behavior, or production quality.

## AI gates

- Backend AI gate is authoritative.
- Public AI is disabled by default where configured.
- AI secrets stay server-side.
- Human approval remains mandatory before publication/export.
- Legacy agents remain separate from the canonical workflow engine.

## Auto Production AI

AI foundations cover:
- story analysis and episode splitting;
- eight hook families;
- first-10-second hook structure;
- SEO/title/caption/hashtag/keyword assistance;
- retention/emotional-arc/pacing analysis;
- thumbnail/sound/BGM planning;
- Series Bible and continuity;
- platform preparation;
- batch/calendar planning;
- A/B/feedback foundations.

AI recommendations must not silently modify approved content.

## RAG / learning limitations

Feedback and recommendation data may be process-local or foundation-level depending on the implementation. Do not claim durable RAG learning, A/B learning, or provider ranking is production-persistent until the relevant persistence and live evaluation evidence exists.

## Provider policy

Agnes/Kling/Magic Hour and similar candidates remain candidate/planning providers unless live access, limits, commercial terms, watermark behavior, quality, and retry semantics are verified.

## Whisper close-out status

**Deployment VERIFIED; real transcription E2E BLOCKED.**

Cloudflare Whisper is deployed and reachable, but no authenticated representative audio has been processed through the production worker path.

Fallback policy:
1. Prefer Cloudflare Whisper when configured and within the budget threshold.
2. If cloud transcription is unavailable/over budget, use local Whisper in the media worker.
3. Persist the transcription source and final subtitle state.
4. Record failure/retry evidence.

A live authenticated audio → VTT → Subtitle Studio test is required before Gate 4 can become VERIFIED.
