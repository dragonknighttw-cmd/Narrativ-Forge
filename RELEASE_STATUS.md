# Canonical Release Status: Narrativ Forge

> **Current Tracked Release SHA:** `db28753d331bc2c7a5e639fd64efd65d023cad6c`  
> **Target Branch:** `main`  
> **Audit Status:** Conditional Sign-Off (CI green; production worker and data durability gates remain)  
> **Last Verification Date:** 2026-11-09 14:42:00 +06:30  

---

## 1. Release Identification & Contracts
* **Project Name:** Narrativ Forge
* **Assigned Telegram Topic:** `Topic 6`
* **Primary Telegram Bot:** `@NarrativForgeBot`
* **Inbound Webhook Target:** `https://narrativ-forge.onrender.com/api/v1/telegram/webhook`
* **Test Suite Status:** Backend Telegram 14/14 Passed, SQLite & Single-User reproducible test env configured, Frontend Typecheck 0 Errors

---

## 2. Release Gates & Verification Matrix
- [X] Code & Architecture Scan
- [X] Local .env DATABASE_URL & SINGLE_USER_EMAIL restored
- [X] Live Telegram getMe & getWebhookInfo 100% healthy (last user-provided check; revalidate after topic-routing deployment)
- [X] CI E2E, backend unit/integration, frontend, CodeQL, SAST, dependency, container, Windows runtime and portable-package gates (main SHA `db28753`)
- [X] Render API and frontend deployed successfully from main SHA `db28753`; API readiness observed returning HTTP 200 in Render logs
- [ ] Dedicated persistent background worker for FFmpeg & Whisper
- [ ] Staging database migration rehearsal
- [ ] Verify live multi-topic Telegram routing and callback isolation
- [ ] Move Character Studio registry from ephemeral local JSON to durable database storage

---

## 3. Policy & Unconditional Production Criteria
This repository must NOT be tagged as `Unconditional Production Ready` until all remaining unchecked gates are signed off with live production evidence.
