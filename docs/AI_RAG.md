# AI / RAG

> Owner: AI/platform maintainers  
> Update when: providers, prompts, retrieval, quotas, or AI safety gates change  
> Last Updated: 2026-10-09  
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

**Deployment VERIFIED; authenticated live endpoint acceptance FAILED / UNVERIFIED.**

Cloudflare Worker `narrativ-forge-whisper` is deployed and the `NARRATIV_SHARED_SECRET` binding exists. However, live evidence run [#37895020420](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37895020420) failed before authenticated inference: the unauthenticated request returned HTTP 403 instead of the expected 401. Do not treat the shared-secret match or real transcription as verified yet.

The GitHub production secret `CLOUDFLARE_WHISPER_SHARED_SECRET`, Render API environment variable of the same name, and Cloudflare Worker secret `NARRATIV_SHARED_SECRET` must contain the same exact value. If the original value is lost, rotate the value consistently and manually run the protected Worker deployment workflow before the quota-consuming live evidence test.

Fallback policy:
1. Prefer Cloudflare Whisper when configured and within the budget threshold.
2. If cloud transcription is unavailable/over budget, use local Whisper in the media worker.
3. Persist the transcription source and final subtitle state.
4. Record failure/retry evidence.

A live authenticated audio → VTT → Subtitle Studio test is required before Gate 4 can become VERIFIED.


## Free-only OpenRouter content planning

The content-plan adapter now routes only through an explicit allowlist of vetted chat-capable free OpenRouter IDs from the owner’s list or the exact free-only router ID openrouter/free. Arbitrary IDs ending in :free are rejected. The production route intentionally ignores Groq/OpenAI credentials. If OpenRouter is not configured, the deterministic Mock adapter is used; it must not silently fall back to a paid provider.

Use chat-capable free text models for script generation. Do not use embedding, reranking, content-safety, audio-generation, or decision-only endpoints as chat models; they require different APIs or return non-prose outputs. The owner-maintained model inventory and privacy cautions are in [OPENROUTER_FREE_MODEL_AUDIT.md](OPENROUTER_FREE_MODEL_AUDIT.md). Free endpoints may log prompts/outputs under their respective provider terms, so exclude confidential data.
