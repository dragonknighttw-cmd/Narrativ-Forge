# Current vs Target

**DONE** = implementation evidence exists.  
**VERIFY** = foundation/code exists; real integration or production verification remains.  
**TODO** = target not sufficiently complete.  
**RESERVE** = intentionally deferred.

| Area | Current | Status |
|---|---|---|
| Ideas / Series / Seasons / Episodes | Implemented | DONE |
| Scripts / versions / autosave | Implemented | DONE |
| Scenes / assets / upload safety | Implemented | DONE |
| Processing / Celery | Foundation + real-job code; live runtime proof remains | VERIFY |
| Burmese subtitle studio | Foundation implemented | DONE |
| Review / approval | Foundation implemented | DONE |
| B2 / Supabase / Cloudinary | Routing/foundation; real lifecycle tests remain | VERIFY |
| Cloudflare Whisper | Worker + signed usage/guardrails/VTT path | VERIFY |
| Google Drive | OAuth/export foundation | VERIFY |
| Stripe | Billing foundation | VERIFY |
| Tenant isolation | Foundation | VERIFY |
| Backup/restore | Runbook exists; drill remains | VERIFY |
| Core workflow UI | Implemented | DONE |
| Full UI state audit | Open | TODO |
| Mobile/tablet audit | Open | TODO |
| WCAG audit | Open | TODO |
| Final UI polish | Open | TODO |
| Episode/scene/content-extension version targets | Need explicit verification | TODO/VERIFY |
| Selective scene regeneration | Target behavior; explicit end-to-end verification remains | TODO/VERIFY |
| Content extensions | Target behavior; explicit end-to-end verification remains | TODO/VERIFY |
| Character / LoRA | Target/reserve capability | RESERVE |
| Legal docs | Not complete | TODO |

## Versioning policy

> **ပြန်ပြင်တာ ပိုကောင်းတယ်။ ဖျက်ပစ်တာ မကောင်းဘူး။**

Preserve useful history instead of destructively overwriting production content.

### Storage policy
- **v1 (Original)** — သိမ်း
- **v2 (Modified)** — သိမ်း
- **v3 (Final)** — သိမ်း
- **v4–v10** — အကောင်းဆုံး ၁ ခုပဲ သိမ်း၊ ကျန်ကို cleanup/delete policy နဲ့ဖယ်နိုင်

### AI request efficiency target

| Method | AI Requests |
|---|---:|
| Delete and regenerate | 20–30 |
| Modify existing result | 7 |

The objective is to reduce unnecessary regeneration and preserve reusable work.

### Data model target

```
episode_versions
scene_regenerations
content_extensions
```

### Selective regeneration

When only Scene 3 needs regeneration:
- Regenerate Scene 3 only.
- Scene 1, 2, 4, 5 remain untouched.
- Rebuild only the dependent output where necessary.

This is a target behavior and must be verified end-to-end before being marked DONE.

## Conclusion

Narrativ Forge is **not starting from zero**. Most core workflow code is already present. Immediate work is to turn implementation into verified production capability, then close only target gaps that matter.


## Expanded requirements — current status

All items below are **TODO** unless separately proven by repository/runtime evidence:

- Story ingestion + AI episode splitter — TODO
- Hook engineering + hook library + 3-candidate A/B flow — TODO
- SEO metadata generation — TODO
- Retention/pacing/emotional-arc analysis — TODO
- Thumbnail auto-generation/selection — TODO
- Sound design/BGM matching — TODO
- Series Bible + continuity checker — TODO
- Trending-topic adapter — TODO
- Cross-platform export preparation — TODO
- Engagement triggers — TODO
- Series trailer — TODO
- Batch generation — TODO
- Subtitle translation — RESERVE / later
- Series calendar — TODO
- Title/hook/thumbnail A/B testing — TODO
- Voice profiles — TODO
- Video-generation provider adapter/fallback — TODO
- Watermark policy check — TODO

### Provider note
The proposed Agnes/Kling/Magic Hour stack is a candidate, not a verified production integration. Free limits, API access, commercial terms, watermark behavior, quality and failure semantics must be verified live before marking it DONE.

### Expanded data targets
The new tables listed in `docs/09-auto-production-expansion.md` are target schema, not completion evidence.

### UI baseline change
The original 26-screen count is no longer the final target. The new screens in 09 must be deduplicated into standalone screens vs tabs/panels, then a new baseline count established.


## CI / Actions health (2026-10-06)

- CodeQL/Security/CI were previously green on the repaired code path, but the current docs-only HEAD is not a fresh code-triggered verification run.
- Docs-only commits intentionally do not trigger CI/CodeQL/Security under the current workflow path.
- Treat the last verified code SHA as the evidence baseline; re-run the full suite on the next code-changing release SHA.

Therefore repository health is currently **code-path previously verified; next release SHA requires fresh CI/security verification**.


## Explicit remaining requirements — capacity, performance, and UI

The following items are intentionally kept explicit so they are not lost during feature expansion:

| Requirement | Target / baseline | Status |
|---|---|---|
| **Agnes daily-limit calculation** | 500 sec/day ÷ ~25 sec/video = **20 videos/day** theoretical capacity | TODO/VERIFY |
| **Processing target** | **15–30 min/video** MVP target on the real worker path | TODO/VERIFY |
| **Groq daily-limit tracking** | **1,000 req/day** conservative planning baseline; live account/model limit must be verified | TODO/VERIFY |
| **Design System** | Colors, Typography, Spacing + semantic/responsive/accessibility rules implemented and audited | TODO/VERIFY |
| **Component Library** | **33 components** implemented with required variants/states and accessibility coverage | TODO/VERIFY |

These are not considered DONE merely because the numbers/specification are written in documentation. Real implementation, runtime measurement, or UI audit is required as applicable.


## Runtime / storage strategy status

| Area | Current decision | Status |
|---|---|---|
| Free local worker | One/two Windows PCs running the repository worker | PLAN / VERIFY |
| Paid worker | Render Background Worker or paid VPS reserved for later | RESERVE |
| Worker migration | Same Celery/Redis/DB/storage contract | PLAN |
| Storage cleanup | Reference-safe retention strategy defined | PLAN / TODO |
| Storage monitoring | 80/90/95% thresholds defined; implementation/verification remains | TODO |
| Local/B2/Cloudinary cleanup | Retention and safety rules defined; real jobs/tests remain | TODO/VERIFY |

The detailed single source for these items is `docs/10-runtime-and-storage-lifecycle-plan.md`.

The previous idea of maintaining a separate copied `worker/` application is superseded: local workers must run the repository's actual `web-platform/backend` worker code so local and future paid runtimes do not drift.


## Coding progress — post-infrastructure freeze

The live Local Worker gate is intentionally **paused** and remains VERIFY/TODO until the user can run the Home/Office worker test later.

Meanwhile, non-worker-dependent foundations have been advanced:

| Capability | Code status | Verification status |
|---|---|---|
| Hook library documented types | Number hook added to API validation | Unit test added; CI verification pending |
| Evidence-backed hook recommendations | Recommendation endpoint with minimum 5 published samples and multi-signal score | Unit/API verification pending |
| Provider quota budgeting | Agnes 500 sec/day + Groq 1,000 req/day planning budgets, idempotent reservations, warning/fallback thresholds | Unit test added; live provider limits still VERIFY |
| Storage lifecycle | Retention/GC foundation exists | Real cleanup/emergency drill remains VERIFY |

Important: these coding additions do **not** mark Agnes/Groq production integrations or Local Worker runtime as DONE. Live provider limits and real worker execution remain separate verification gates.


## Coding-First Progress — Phases 7–9

- Design system foundation: **DONE (coding foundation)** — semantic color/type/spacing/radius/shadow tokens, reusable primitives, visible focus states, touch targets, reduced-motion support.
- Full 33-component audit: **TODO/VERIFY** — foundation exists, but every component and state still needs screen-level QA.
- Production hardening: **VERIFY/TODO** — security, rate limits, idempotency, tenant isolation, retry/DLQ, observability, performance and backup/restore remain release gates.
- Release readiness: **VERIFY** — CI/security must be green on the final release SHA and all external/live gates must be explicitly signed off.


## Remaining work ownership — 2026-10-07

### USER / LIVE-ENVIRONMENT GATES

These require the user's machine, credentials, provider console, or explicit account approval and are intentionally not marked DONE by code alone:

1. **Local Worker runtime:** run the repository worker on Home/Office Windows PC(s) with real FFmpeg and the shared Upstash Redis queue.
2. **Worker E2E:** prove Queue → Worker → FFmpeg → DB → Storage → Retry/DLQ → Failover with a real job.
3. **Production auth E2E:** run the real production login/session flow and verify cross-tenant isolation.
4. **Google Drive:** provide/authorize OAuth callback credentials and run real export, idempotent re-export, and partial-upload recovery.
5. **SMTP:** provide production SMTP credentials and prove invitation/magic-link delivery to a real mailbox.
6. **Stripe:** provide production/test credentials + webhook endpoint and run API/webhook lifecycle verification.
7. **Sentry:** provide DSN/config and prove a real production event + alert path.
8. **Backup/restore:** execute the provider-supported backup/restore drill where provider tooling/account permissions are required.
9. **Live AI quotas:** verify actual Agnes/Groq account/model limits and approve the provider usage policy.
10. **Performance:** run the representative 15–30 min/video benchmark on the real worker/media path.

### ASSISTANT / CODE + DOCS TRACK

The assistant can continue without waiting for those live gates:

- Finish and harden provider adapters, quota guards, fallback/error semantics, and tests.
- Complete selective regeneration/versioning tests and content-extension behavior where code paths are available.
- Finish storage lifecycle cleanup/monitoring code, safety checks, and test coverage.
- Complete magic-link/auth implementation tests and production-safe error handling.
- Audit security, tenant isolation, idempotency, retry/DLQ, and observability code paths.
- Expand the design system into the 33-component audit and screen-level accessibility/responsive states.
- Build Auto Production foundations in schema → API/service → worker job → UI → tests order, without claiming live worker DONE.
- Maintain docs/04, docs/05, docs/10, and docs/11 as the status/runbook source of truth.
- Re-run/fix CI after every code-changing batch and only promote status from TODO/VERIFY when evidence exists.

### RELEASE BLOCKERS

Production Ready remains blocked by the live gates above. Code completeness is not a substitute for worker runtime, external credentials, recovery drills, or production E2E evidence.


## Coding track completion update — 2026-10-07

The following additional code-level work has now been applied while the real-worker gate remains paused:

- Auto Mode episode lookup is organization-scoped through the current membership.
- Owner user listing is organization-scoped; cross-tenant users are excluded.
- Cross-tenant user-listing regression coverage was added.
- Provider quota reservation/idempotency coverage exists for the planning budgets.
- Design-system primitives were expanded with Select, Textarea, Checkbox, Switch, Spinner, Progress, Skeleton, EmptyState, and visually-hidden accessibility support.
- Reduced-motion and keyboard/focus behavior remain part of the design-system foundation.

These are **coding-track completions**, not live production verification. Screen-level UI wiring, full automated CI evidence for the newest SHA, real worker runtime, and external credential gates remain separate.


## Coding-track update — 2026-10-07 (continued)

Completed in the current coding pass:
- Auto Mode now normalizes provider output to the episode target duration (bounded 150–210 seconds) and preserves scene sequencing.
- Selective scene regeneration reuses the same duration normalization and is organization-scoped.
- Added deterministic Auto Production foundations for SEO metadata, thumbnails, sound/BGM policy, platform export preparation, batch scheduling, and A/B variants.
- Added eight-family hook engineering foundation.
- Added provider fallback execution semantics with retryable/non-retryable classification.
- Added storage threshold classification and final/approved/only-copy deletion protection.
- Added magic-link security/failure-path tests and broader production-foundation tests.
- Fixed UI primitive token references and explicit input prop typing.

These remain coding-track completions only. Real provider limits, worker runtime, external delivery, recovery drills, and production E2E remain VERIFY/live gates.
