<p align="center"><img src="https://raw.githubusercontent.com/narrativforge/Narrativ-Forge/main/docs/assets/narrativ-forge-banner.svg" alt="Narrativ Forge — AI-Powered Creative Studio" width="100%" /></p>

# 🎬 Narrativ Forge
> **Autonomous AI Multimedia Narrative Studio & Generative Production Engine**

[![Next.js](https://img.shields.io/badge/Next.js-16-black?style=flat-square&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Python_3.12-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Supabase](https://img.shields.io/badge/Supabase-Database_&_Auth-3ECF8E?style=flat-square&logo=supabase)](https://supabase.com/)
[![Gemini 2.0](https://img.shields.io/badge/Gemini-2.0_Flash-4285F4?style=flat-square&logo=google)](https://deepmind.google/technologies/gemini/)
[![Kling AI](https://img.shields.io/badge/Kling_AI-Generative_Video-6366F1?style=flat-square)](https://klingai.com/)
[![Cloudinary](https://img.shields.io/badge/Cloudinary-Media_CDN-3448C5?style=flat-square&logo=cloudinary)](https://cloudinary.com/)
[![Render](https://img.shields.io/badge/Render-Backend_Live-46E3B7?style=flat-square&logo=render)](https://narrativ-forge.onrender.com)
[![Telegram](https://img.shields.io/badge/Telegram_Bot-Topic_%236-26A5E4?style=flat-square&logo=telegram)](https://github.com/narrativforge/Narrativ-Forge)

---

## 🌟 Overview

**Narrativ Forge** is a generative media production studio that automates end-to-end creative narrative pipelines: from scriptwriting and character design to neural voice generation, AI video synthesis, and timeline rendering.

Equipped with free-first tiered LLMs, multilingual speech generation (including Burmese Whisper/Edge-TTS), and integrated with Kling AI, AionLabs, and Z-AI video synthesis.

---

## 🚀 Key Features

* **✍️ Generative Scriptwriting**: Multi-scene storyboard scripting, character emotional arcs, and cinematic direction via Gemini 2.0.
* **🎥 Multi-Engine Video Generation**: Seamless orchestrations with Kling AI, AionLabs, and background GPU renderers.
* **🎙️ Multilingual Neural Voice**: Voice synthesis with Edge-TTS, Whisper transcription, and emotional speech timing.
* **🎞️ Timeline & Storyboard Studio**: Interactive web-based canvas for scene arranging, caption sync, and transition effects.
* **☁️ Cloud & Local Portable Runtime**: Runs on cloud infrastructure (Render backend) or packaged as a Windows Portable Studio.
* **📲 Telegram Studio Dispatcher**: Trigger video renders, receive preview clips, and monitor render pipelines via Telegram Bot (Topic `#6`).

---

## 🏗️ System Architecture

```
             Story Concept / Prompt / Telegram Dispatch
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                    Story & Direction Engine                   │
│   • Gemini 2.0 Flash Scriptwriter • Character Architect       │
│   • Storyboard Scene Splitter & Audio Prompt Synthesizer      │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                 Multimedia Synthesis Pipeline                 │
│   • Video Engines: Kling AI / AionLabs / Z-AI                │
│   • Audio Engines: Edge-TTS / Cloudflare Whisper              │
│   • Asset Delivery: Cloudinary Media CDN & Supabase Vault     │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                 Review & Production Deployment                │
│   • Next.js 16 Production Studio (Web Canvas)                │
│   • Render FastAPI Backend & Background Celery Workers        │
│   • Telegram Channel Dispatcher (Topic #6)                    │
└───────────────────────────────────────────────────────────────┘
```

---

## ⚡ Quickstart

```bash
# 1. Backend Server
cd apps/web-platform/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.lock
uvicorn app.main:app --reload --port 8000

# 2. Frontend Studio
cd ../frontend
pnpm install
pnpm dev
```

---

## 📜 License

Private Creative Suite License. All Rights Reserved.
