# AI Provider Acceptance Matrix

Last reconciled: 2026-10-11 UTC
Release status: PENDING — NOT PRODUCTION READY
Source of truth: this matrix separates historical live endpoint probes, repository integration, and production acceptance. The owner-run report is preserved in [master_result all](master_result%20all).

## Status vocabulary

- LIVE-SMOKE — one or more authenticated test requests reportedly returned a response at the recorded date; not current availability certification.
- CODE-TESTED — application adapter behavior is covered by unit tests using mocks rather than a live provider.
- INTEGRATED — a real application path calls the provider adapter when configured.
- PRODUCTION-VERIFIED — live end-to-end evidence, persistence, failure recovery, quality acceptance, cost/terms, and environment are all checked. No provider below is production-verified solely from the report.
- BLOCKED — a known mismatch or missing E2E prevents acceptance.

## Provider and capability inventory

| Provider / model family | Historical live evidence from master_result all | Repository integration as inspected 2026-10-11 | Decision / next gate |
|---|---|---|---|
| OpenRouter free chat models | Four model IDs returned HTTP 200 in the report; a separate candidate audit lists Gemma 4, North Mini Code, Nemotron, Liquid and Apodex candidates | INTEGRATED for content planning through ai_adapter.py; exact free-ID allowlist, HTTPS host guard and mocked unit tests exist | Run the opt-in one-model live smoke workflow; then evaluate Burmese JSON validity, latency, fallback and data terms. No confidential content in smoke tests. |
| Groq | Reported successful chat/speech checks; gpt-oss outputs sometimes empty with low token limits | NOT integrated into current content-plan route; config keys exist but route intentionally ignores them | Future adapter candidate. Verify actual model ID, token behavior, terms, network requirements and retry handling before connecting. |
| Cloudflare Workers AI | Reported successful chat/embed/image/speech probes | Partially integrated by capability: Whisper has a separate transcription path; report chat/embed/image calls are not complete application integration | Keep transcription acceptance separate; add capability-specific adapters/tests before claiming chat/embedding/image integration. |
| Cohere | Reported successful chat and embedding probes | Not integrated into current content-plan route as a direct provider; North Mini Code is available through OpenRouter if configured | Verify direct Cohere adapter separately if required; do not equate OpenRouter-hosted Cohere model with direct Cohere API integration. |
| Gemini | Reported several HTTP 200 model probes; one latest alias returned 503 | Not integrated into current content-plan route | Validate current model IDs, regional/network constraints, quotas and Burmese quality before adapter work. |
| Mistral | Reported chat probes; one model rate-limited | Not integrated into current content-plan route | Candidate for coding/agent workloads; verify model ID, rate limits and cost guardrails. |
| Voyage AI | voyage-3-lite returned 512-dimension vectors | No verified full RAG integration evidence from inspected files | BLOCKED: inspect database vector dimension and migration strategy; test ingest → query → retrieval with same dimensions. Never mix vector dimensions in one index. |
| NVIDIA NIM | Several direct model probes succeeded; many account endpoints unavailable; one parse error | Not integrated into current content-plan route as a direct provider | Check access grants, exact model IDs, response shape and quota before enabling. |
| Hugging Face | Hub/Spaces/Datasets available; Inference API returned 402 in report | No remote inference integration established by this report | Use Hub/Datasets/Spaces/local weights only where appropriate; local model setup and license checks are separate tasks. |
| Cerebras | Chat returned 402 billing despite model listing | Not integrated | Keep disabled until billing/access is deliberately approved. |
| Canva | API returned 401 invalid token | Not integrated | OAuth/token/scope verification required before any integration claim. |

## Free-model routing decisions

The backend content-plan path must remain free-first and fail closed:

1. Allow only exact, reviewed chat-generation model IDs ending in :free.
2. Reject paid IDs, unknown IDs that merely end in :free, and unsafe base URLs before any network request.
3. Do not enable openrouter/free in the app route by default because it selects a changing model/provider at runtime, reducing reproducibility of quality and privacy decisions.
4. Exclude poolside/laguna-s-2.1:free from the application content route until provider retention/training terms are accepted for unpublished content.
5. Do not use embedding, reranking, moderation, decision-only, or audio-generation models for script generation.
6. Retry the next reviewed free model after transient HTTP failures or invalid/empty model output; do not cascade on 401/403 authentication/authorization errors.
7. Never remove the :free suffix to work around an outage. No paid fallback is allowed.

Current code-level guard and tests: apps/web-platform/backend/app/services/ai_adapter.py and apps/web-platform/backend/tests/test_ai_adapter.py.

## Manual live verification

Use the [OpenRouter free-model evidence workflow](../.github/workflows/openrouter-free-model-evidence.yml) only when intentionally spending one free-tier request. It requires OPENROUTER_API_KEY in GitHub Actions secrets, runs one synthetic request to one allowlisted model, and emits redacted metadata: model ID, HTTP/result status, latency, JSON validation, finish reason, response character count, token usage when supplied, structured provider error identifiers, and Retry-After seconds. It never stores prompt/response text, raw provider error messages, or the API key. HTTP 429 is not retried automatically. Standard CI does not call live providers.

The OpenRouter free plan currently advertises 50 requests/day, but limits and available model endpoints can change by account and model. Sources: [Free models collection](https://openrouter.ai/collections/free-models), [Pricing and limits](https://openrouter.ai/pricing/), [API request format](https://openrouter.ai/docs/api/api-reference/chat/send-chat-completion-request), and [provider data practices](https://openrouter.ai/docs/guides/privacy/provider-logging).

## Free-first multi-provider routing implementation

- OpenRouter remains first and only accepts the exact allowlisted free chat-model IDs.
- Groq, Gemini, Mistral, Cohere, and NVIDIA are subsequent OpenAI-compatible chat providers, but each is skipped by default until its API key is present and its `*_FREE_TIER_ENABLED` flag is explicitly enabled.
- HTTP 401/403/429 skips remaining model candidates sharing that provider family/key and continues to the next provider. Invalid output and model-specific/transient failures may advance to another candidate.
- Cloudflare Workers AI chat uses a separate account ID/API token and explicit opt-in; the Whisper Worker shared secret is not an AI API token. Voyage embeddings are not chat providers and must be tested on their own capability path.
- Unit tests cover cross-provider quota fallback and canonical endpoint validation. This code-level coverage is not live provider acceptance; each intended provider still needs a controlled live smoke test and quota/terms confirmation.

## Open blockers and future queue

### Current blockers

- [ ] Run one-model live smoke for each intended active OpenRouter free model, deliberately, with quota awareness. The latest Gemma 4 31B attempt returned HTTP 429; no candidate has passed this new content-plan JSON validation yet.
- [ ] Verify current OpenRouter model IDs/availability; retire or replace unavailable entries only after a new smoke test.
- [ ] Fix RAG vector dimension mismatch and run persisted ingest → retrieval E2E.
- [ ] Run Publishing E2E after provider output is persisted and human approval/permissions are checked.
- [ ] Collect representative Burmese prompts and evaluate factuality, JSON validity, script quality, and fallback correctness.
- [ ] Verify real provider terms, prompt retention/training flags, quota, regional availability and commercial use before sending unpublished or personal data.
- [ ] Rotate any API key that may have been exposed during prior testing; never put credentials in chat, repository files, logs, or artifacts.

### Future work (phased, not all required now)

- Phase 21 — AI quality evaluation/provider ranking: fixed Burmese test set, deterministic scoring, JSON/schema validity, latency, quota/cost and fallback metrics; provider ranking only from reproducible evidence.
- Phase 29 — quota-aware scheduling: provider-specific budgets, reservations, rate-limit fallback and idempotency.
- Phase 38 — cost governance: hard free-only enforcement, request budgets, budget alerts and evidence.
- Phase 43–44 — evaluation governance/provider change management: versioned benchmark data, model-ID drift detection, canary comparison and rollback rules.
- Phase 53/66 — Burmese localization quality operations: glossary/versioned corpus, subtitle/script QA thresholds and human acceptance.
- Phase 65 — provider adapter/marketplace seam: capability-based adapters for chat, embeddings, image, speech and moderation rather than treating every provider as interchangeable.
- Phase 68 — SLO/error-budget operations: production latency/error/availability targets after real telemetry exists.

Do not mark these future phases verified merely because a design or unit test exists. Each gate needs commit-linked evidence and, where applicable, live/manual acceptance.
## Additional free-tier provider smoke workflow

Use [Free-tier Provider Smoke Evidence](../.github/workflows/free-provider-smoke-evidence.yml) to test one selected non-OpenRouter provider at a time: Groq, Cloudflare Workers AI, Gemini, Mistral, Cohere, or NVIDIA. It requires the corresponding secret(s) in GitHub Actions, and the operator must explicitly check `confirm_free_tier`. Only the selected provider's secret(s) are passed into the request step. The workflow sends one synthetic prompt, performs no retries, does not log the generated text or raw provider error, and uploads redacted metadata for 30 days. It is manual-only; regular CI never contacts live providers.

Before dispatching, verify that the exact account, key, model and endpoint are eligible for a free tier and that billing cannot be triggered. The confirmation checkbox is an operator acknowledgement, not an automated guarantee that a provider will not charge. If any provider's free status is uncertain, leave it disabled and do not dispatch it. Add secrets only in GitHub repository Settings → Secrets and variables → Actions; never put key values in chat, workflow files, commits, logs or artifacts. Cloudflare Workers AI requires `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN`; these are separate from the Whisper Worker shared secret.

This workflow is a provider connectivity/output smoke test, not production acceptance. The returned model ID, availability, quota and terms must still be reviewed before enabling a provider in production.
