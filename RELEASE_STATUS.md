# Canonical Release Status: Narrativ Forge

> **Current Tracked Release SHA:** `eaa29c73e968a64601ef0ed4134da494a202289b`  
> **Target Branch:** `main`  
> **Audit Status:** Conditional Sign-Off (Telegram topic/tenant fixes deployed; worker and Character Studio durability gates remain)  
> **Last Verification Date:** 2026-11-09 UTC  

---

## 1. Release Identification & Contracts
* **Project Name:** Narrativ Forge
* **Assigned Telegram Topic:** `Topic 6`
* **Primary Telegram Bot:** `@NarrativForgeBot`
* **Inbound Webhook Target:** `https://narrativ-forge.onrender.com/api/v1/telegram/webhook`
* **Test Suite Status:** PR #119: backend 332 passed/3 skipped, integration 77 passed/1 skipped, browser E2E passed, Real Worker Evidence passed; main SHA re-run still has Real Worker E2E and Repository Gate pending at checkpoint time.

---

## 2. Release Gates & Verification Matrix
- [X] Code & Architecture Scan
- [X] Local .env DATABASE_URL & SINGLE_USER_EMAIL restored
- [X] Live Telegram getMe & getWebhookInfo 100% healthy (last user-provided check; revalidate after topic-routing deployment)
- [X] PR #118 CI E2E, backend, frontend, CodeQL, security, Windows runtime and portable-package gates
- [X] PR #119 five-topic Telegram routing and tenant-isolation tests; merged to main as `eaa29c7`
- [X] Render API and frontend deployed live from main SHA `eaa29c7`; API readiness returned HTTP 200 after rollout
- [ ] Exact-main Real Worker E2E and Repository Gate completion
- [ ] Dedicated persistent background worker for FFmpeg & Whisper
- [ ] Staging database migration rehearsal
- [ ] Owner-side Telegram smoke test in all five forum topics
- [ ] Apply Alembic `0024_character_registry` only after legacy Character Studio data preservation is confirmed

---

## 3. Policy & Unconditional Production Criteria
This repository must NOT be tagged as `Unconditional Production Ready` until all remaining unchecked gates are signed off with live production evidence.
