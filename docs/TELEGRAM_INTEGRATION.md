# Telegram Integration Guide: Narrativ-Forge

> **Project:** Narrativ-Forge (Private Burmese Short-Form Video Production Workspace)  
> **Directory:** `dragonknight.tw@gmail.com\Narrativ-Forge`  
> **Runtime / Stack:** FastAPI (Python), Docker, Render  
> **Primary Topic:** `🎬 Narrativ-Forge`

---

## 1. Overview & Topic Role

Narrativ-Forge uses the Telegram Supergroup to alert producers and review leads about the lifecycle of short-form video episodes:
* Script approval queue
* Video rendering progress and preview links
* Automated Google Drive export status
* Processing queue bottlenecks or pipeline errors

Producers can review and approve scripts or videos directly from Telegram via **Inline Keyboard buttons**.

---

## 2. Topic Configuration

* **Suggested Topic Name:** `🎬 Narrativ-Forge`
* **Suggested Topic ID:** `1` (or your assigned `message_thread_id`)
* **Color / Icon:** 🎬 Film Slate / Video Production

---

## 3. Environment Variables

Configure these variables in your local `.env` or in the Render Dashboard under **Environment**:

| Key | Type | Default | Description |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | String (Secret) | `""` | Bot token provided by `@BotFather` |
| `TELEGRAM_CHAT_ID` | String | `""` | Supergroup ID (e.g. `-100xxxxxxxxxx`) |
| `TELEGRAM_TOPIC_ID` | Integer | `None` | Thread ID for `#Narrativ-Forge` topic |
| `TELEGRAM_ENABLED` | Boolean | `false` | Master toggle (`true` to enable delivery) |

---

## 4. Code Architecture

* **Service Module:** `apps/web-platform/backend/app/services/telegram.py`
* **Configuration:** `apps/web-platform/backend/app/core/config.py` (`Settings.telegram_*`)
* **Template:** `apps/web-platform/backend/.env.example`

---

## 5. Available Action Hooks & API

### (1) Script Review Notification
```python
from app.services.telegram import notify_script_review

await notify_script_review(
    script_id="sc_12345",
    title="Episode 1: The Dragon's Awakening",
    author="Thuwon"
)
```
* **Actions included:**
  - `[✅ Approve Script]` (`nf_script_appr:sc_12345`)
  - `[❌ Reject]` (`nf_script_rej:sc_12345`)

### (2) Video Render Completed
```python
from app.services.telegram import notify_video_ready

await notify_video_ready(
    video_id="vid_9876",
    title="Episode 1 (Final Render)",
    preview_url="https://your-preview-link.example/vid_9876"
)
```
* **Actions included:**
  - `[▶️ Preview]` (Direct URL link)
  - `[👍 Approve Video]` (`nf_video_appr:vid_9876`)
  - `[🔄 Re-render]` (`nf_video_rerun:vid_9876`)

### (3) Google Drive Export Completed
```python
from app.services.telegram import notify_export_complete

await notify_export_complete(
    title="Episode 1 - 4K Master Export",
    gdrive_url="https://drive.google.com/file/d/xxxxx/view"
)
```

### (4) Pipeline Error Alert
```python
from app.services.telegram import notify_pipeline_error

await notify_pipeline_error(
    stage="Subtitle Sync",
    error_message="Audio timestamp misalignment at 00:42",
    project_id="vid_9876"
)
```

---

## 6. Cloud Deployment Checklist (Render)

1. Open Render dashboard -> `narrativ-forge-api` service.
2. Go to **Environment** tab.
3. Add `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `TELEGRAM_TOPIC_ID`, and set `TELEGRAM_ENABLED=true`.
4. Save Changes (Render will auto-deploy).

---

## 7. Inbound Action Handler API

This project includes a dedicated inbound endpoint to receive callbacks from the Central Cloudflare Gateway:
* **Endpoint:** `POST /api/v1/telegram/action`
* **Supported Actions:**
  * `nf_script_appr:<id>` -> Approves script and notifies topic
  * `nf_script_rej:<id>` -> Rejects script and requests revision
  * `nf_video_appr:<id>` -> Approves video and triggers Google Drive upload
  * `nf_video_rerun:<id>` -> Queues fresh render task to Celery/workers
  * `nf_idea_capture` -> Saves message text as a new script draft in Studio

---

## 8. AI Provider & API Keys Configuration

| Provider | Environment Key | Primary Role in Narrativ-Forge | Free / Paid Notes |
|---|---|---|---|
| **Gemini** | `GEMINI_API_KEY` | Burmese Script Studio & Dialogue Generation | Needs VPN in MM; excellent Burmese fluency |
| **OpenRouter** | `OPENROUTER_API_KEY` | Free AI fallback (50 req/day) | Vetted free models: `liquid/lfm-2.5`, `nvidia/nemotron` |
| **Groq** | `GROQ_API_KEY` | Ultra-fast scene breakdown & hooks | `qwen/qwen3.8-27b` (14,400 req/day free) |
| **Mistral** | `MISTRAL_API_KEY` | JSON scene structure generation | `codestral-latest` / `ministral-8b` |
| **Cohere** | `COHERE_API_KEY` | Asset library tagging & narrative continuity | `command-a-03-2025` |
| **Cloudflare** | `CLOUDFLARE_API_TOKEN`<br>`CLOUDFLARE_ACCOUNT_ID` | Thumbnail generation (Flux) & Speech Whisper | 100k free req/day on Workers AI |
| **Voyage** | `VOYAGE_API_KEY` | Multimodal video asset embeddings | `voyage-3-lite` (512-dim) |
| **Hugging Face** | `HUGGINGFACE_API_KEY` | Burmese NLP models (`bert-myanmar`) | Inference API disabled (Oct 8); Hub/Spaces only |

---

## 9. Tuned Fallback Chains & AI Monitoring

### 💬 Chat / Scriptwriting Chain
1. 🥇 **Gemini 2.5/3.5-flash** — Primary for native Burmese fluency & creative dialogue.
2. 🥈 **Groq (`qwen/qwen3.8-27b`)** — Ultra-fast fallback (14,400 req/day free).
3. 🥉 **Cloudflare Workers AI (`llama-3.1-8b`)** — Free serverless tier.
4. 4️⃣ **Cohere (`command-a-03-2025`)** — High quality creative reasoning.
5. 5️⃣ **OpenRouter (Free models)** — Emergency quota fallback (50 req/day).

### 🎙️ Speech-to-Text (STT / Subtitles) Chain
1. 🥇 **Cloudflare Whisper (`@cf/openai/whisper`)** — Direct token offload via `/cloud-processing/whisper-token`.
2. 🥈 **Groq Whisper (`whisper-large-v3`)** — Ultra-fast fallback via `/cloud-processing/groq-transcribe` (2 hrs/day free).
3. 🥉 **Local Celery Worker** — Offline FFmpeg + OpenAI Whisper CLI (`tiny`/`small`).

### 📚 RAG & Semantic Asset Search
1. 🥇 **Voyage AI (`voyage-3-lite`, 512-D)**
2. 🥈 **Cohere (`embed-v4.0`, 512-D)**
3. 🥉 **Deterministic Hash Fallback (512-D)**

### 📊 Real-Time AI Usage & Health API
* **Endpoint:** `GET /api/v1/ai/usage`
* **Telegram Command:** Send `/ai_status` or click `[🔄 Refresh Usage]` in Telegram to inspect real-time call counts, error rates, and quota exhaustion across all providers.


