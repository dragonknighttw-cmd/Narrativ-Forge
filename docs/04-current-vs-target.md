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
