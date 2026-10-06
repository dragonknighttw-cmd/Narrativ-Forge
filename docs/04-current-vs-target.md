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
| Episode/scene/content extension version targets | Need explicit verification | TODO/VERIFY |
| Characters / LoRA | Future/reserve capability | RESERVE |
| Legal docs | Not complete | TODO |

## Conclusion
Narrativ Forge is **not starting from zero**. Most core workflow code is already present. Immediate work is to turn implementation into verified production capability, then close only target gaps that matter.