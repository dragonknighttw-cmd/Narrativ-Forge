# OpenRouter free-model audit — 2026-10-09

Scope: model IDs supplied by the owner. OpenRouter prices and availability are dynamic; the table records intended use and risks, not a permanent price guarantee. Check the linked official listing before changing production configuration.

## Safe default chat-generation shortlist

These are the supplied free IDs that are suitable candidates for ordinary text/chat-completion script generation:

| Model ID | Intended use | Decision |
|---|---|---|
| google/gemma-4-31b-it:free | General multilingual text/reasoning | Keep as primary candidate |
| google/gemma-4-26b-a4b-it:free | General text/reasoning, lower active compute | Keep as fallback candidate |
| cohere/north-mini-code:free | Code and agentic tasks; supports chat completions | Keep as technical fallback |
| nvidia/nemotron-3-super-120b-a12b:free | General reasoning/planning | Keep as fallback candidate |
| nvidia/nemotron-3-ultra-550b-a55b:free | General reasoning/agent orchestration | Optional; use only with the exact :free suffix |
| nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free | Text plus audio/image/video inputs | Optional multimodal candidate |
| nvidia/nemotron-3.5-lightning:free | High-throughput agentic text tasks | Optional candidate; the un-suffixed model is paid |
| liquid/lfm-2.5-2.6b:free | Lightweight extraction/RAG; not ideal for knowledge-heavy or coding work | Optional low-priority fallback |
| apodex/apodex-1.1-mini:free | Research/reasoning and tool workflows | Optional; validate JSON reliability before production |
| poolside/laguna-s-2.1:free | Coding/agentic coding | Not a default script writer; avoid confidential prompts because provider may use free-tier inputs/outputs to improve models |
| thinkingmachines/inkling:free | General reasoning, coding and agent use | Not a default; free endpoint is intended for agentic harnesses and prompts/outputs may be logged for model improvement |
| thinkingmachines/inkling-small:free | Small-model/agentic use | Optional only for agentic harnesses; prompts/outputs are logged for model improvement, so do not send confidential data |
| openrouter/free | OpenRouter's free-only model router | Safe as a final free-only fallback, but output model can vary and quality is less deterministic |

Official listings: [Gemma 4 31B free](https://openrouter.ai/google/gemma-4-31b-it%3Afree), [Gemma 4 26B A4B free](https://openrouter.ai/google/gemma-4-26b-a4b-it%3Afree), [North Mini Code free](https://openrouter.ai/cohere/north-mini-code%3Afree), [Nemotron 3 Super free](https://openrouter.ai/nvidia/nemotron-3-super-120b-a12b%3Afree), [Nemotron 3 Ultra free](https://openrouter.ai/nvidia/nemotron-3-ultra-550b-a55b%3Afree), [Nemotron 3 Nano Omni free](https://openrouter.ai/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning%3Afree), [Nemotron 3.5 Lightning free](https://openrouter.ai/nvidia/nemotron-3.5-lightning%3Afree), [LFM 2.5 2.6B free](https://openrouter.ai/liquid/lfm-2.5-2.6b%3Afree), [Apodex 1.1 Mini free](https://openrouter.ai/apodex/apodex-1.1-mini%3Afree), [Laguna S 2.1 free](https://openrouter.ai/poolside/laguna-s-2.1%3Afree), [Inkling free](https://openrouter.ai/thinkingmachines/inkling%3Afree), [OpenRouter free collection](https://openrouter.ai/collections/free-models).

## Free but not general chat-generation models

| Model ID | Actual purpose | Decision |
|---|---|---|
| inception/mercury-decide:free | Structured decision endpoint; uses a dedicated System One API, not ordinary chat completions | Do not use for script generation |
| respan/span-01-lite:free | Behavior scoring/classification via Decisions API; not prose generation | Do not use for script generation |
| liquid/lfm-2.5-embedding-350m:free | Text embeddings for semantic search; inputs may be retained for training | Use only for an embeddings pipeline |
| nvidia/llama-nemotron-embed-vl-1b-v2:free | Multimodal embedding vectors; free endpoint warns against sensitive data and production/business-critical use | Do not use for chat; avoid sensitive data |
| nvidia/llama-nemotron-rerank-vl-1b-v2:free | Reranking text/image documents | Use only for reranking |
| nvidia/nemotron-3.5-content-safety:free | Safe/unsafe moderation and safety categories | Use only for moderation |

## Specialized audio / sunset entries

| Model ID | Actual purpose / issue | Decision |
|---|---|---|
| fish-audio/s2.1-pro-free:free | Text-to-speech/audio generation, not ordinary text chat; no production latency or availability guarantees | Do not put in script-generation fallback; use only for low-volume testing/prototyping after checking current terms |
| dots-studio/dots-3-note-preview:free | It was listed as free, but OpenRouter's listing says it was going away on September 30, 2026 | Remove from any active configuration; do not rely on it |

## Billing guardrails

- A model ID ending in :free is the free variant; a similarly named ID without that suffix can be paid. Example: nvidia/nemotron-3-ultra-550b-a55b is listed at paid token rates, while nvidia/nemotron-3-ultra-550b-a55b:free is listed free.
- The application enforces a last-line exact allowlist of vetted chat-capable free IDs from the owner's list, plus the exact openrouter/free router. Arbitrary IDs are rejected even if they end in :free. The default fallback chain contains only allowlisted forms.
- This prevents accidental paid-model calls from this content-plan route, but it does not prevent rate limits, provider outages, changes to model availability, or disclosure of prompts to providers.
- Do not send API keys, private customer data, unpublished confidential scripts, or personal data to trial/free models unless their data terms are acceptable.
- Free endpoints are currently listed at $0 per token by OpenRouter, but free availability and rate limits can change. Never remove the suffix to “fix” an unavailable model.
- OPENROUTER_API_KEY usability is not verified until one authenticated production request succeeds. Never print the key or send it in chat.
