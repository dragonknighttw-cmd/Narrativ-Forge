# AI / RAG

> Owner: AI/platform maintainers  
> Update when: providers, prompts, retrieval, quotas, or AI safety gates change  
> Last Updated: 2026-10-11  
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


## Free-first multi-provider content planning

The content-plan route tries exact-allowlisted OpenRouter free chat models first. If OpenRouter returns HTTP 401/403/429, it skips the remaining models sharing that key and moves to the next configured provider. Model-specific failures, transient errors, and invalid/empty JSON can advance to another candidate. If all providers fail, deterministic Mock content is returned; that is a safe fallback, not proof of live AI success.

The supported chat chain is OpenRouter → Groq → Cloudflare Workers AI → Gemini → Mistral → Cohere → NVIDIA, but non-OpenRouter providers are skipped unless their API key and matching `*_FREE_TIER_ENABLED=true` opt-in are both configured. The flags default to false because account-specific quotas and billing behavior vary. A key or a free-tier flag does not guarantee that all future calls are free; confirm dashboard limits and model terms before enabling each provider. OpenAI credentials are intentionally not used by this route.

Cloudflare Workers AI chat requires a separate Cloudflare Account ID and Workers AI API token. It must not reuse `CLOUDFLARE_WHISPER_SHARED_SECRET`, which only authenticates the separate Whisper Worker. Voyage is an embedding provider, not a chat fallback. Provider keys are sent only to canonical HTTPS API hosts; model IDs and API responses are validated, and logs avoid keys/prompts/generated text.

Use chat-capable text models for script generation. Do not use embedding, reranking, content-safety, audio-generation, or decision-only endpoints as chat models. Free/trial providers may log prompts/outputs under their own terms, so do not send confidential data until retention and training policies are accepted. See [OPENROUTER_FREE_MODEL_AUDIT.md](OPENROUTER_FREE_MODEL_AUDIT.md).


## Provider acceptance and free-model evidence

The owner-run [AI Provider Status Report](master_result%20all) records a dated live API smoke test. Treat it as historical endpoint evidence only: it does not prove that each provider is wired into the application route, that the current model ID still exists, or that Burmese content quality, persistence, and production reliability are accepted.

The canonical integration/security decisions and remaining work are tracked in [AI Provider Acceptance Matrix](AI_PROVIDER_ACCEPTANCE_MATRIX.md). OpenRouter is first and is restricted to an exact allowlist of free chat models. Other chat providers require both a configured key and an explicit free-tier opt-in; see the multi-provider section above. The dynamic openrouter/free router and models flagged for unsuitable prompt privacy/retention risk remain excluded.

A manually dispatched [OpenRouter free-model evidence workflow](../.github/workflows/openrouter-free-model-evidence.yml) sends one synthetic test request to one selected allowlisted model. It is opt-in, consumes one free-tier request, never logs response text or credentials, and is not run automatically by CI. Only run it after configuring OPENROUTER_API_KEY in GitHub Actions secrets. Current limits are dynamic; the official [OpenRouter pricing page](https://openrouter.ai/pricing/) currently lists 50 requests/day for the free tier, but account eligibility and endpoint availability can differ.
