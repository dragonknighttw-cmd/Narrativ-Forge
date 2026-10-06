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

- CodeQL latest run for repaired commit: **GREEN**.
- Security latest run for repaired commit: **GREEN**.
- CI latest run for repaired commit: **QUEUED**, blocked behind historical in-progress CI runs.
- Historical stale runs are being cancelled by the new concurrency policy where GitHub applies it; older pre-policy runs may still need manual cancellation.

Therefore repository health is currently **CodeQL GREEN / Security GREEN / CI verification pending**.


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
