# Auto Production Expansion Requirements

This document reconciles the new Auto Production requirements with the original roadmap. It expands the target system and does not replace Manual Mode, human approval, storage policy, or strict product boundaries.

## 1. Story ingestion and episode planning
User can upload a full story or story idea. AI proposes episode count, duration, scenes, characters, emotional arc, cliffhangers, and a proposed publish schedule. The plan must be shown for user approval/modification before generation.

## 2. Hook engineering
Required hook types: Question, Shock, Mystery, Warning, Personal Story, Contrarian, Cliffhanger, Number.

Hook library target fields: hook_text, hook_type, topic, emotion, used_count, views_average, completion_average, shares_average, performance_score, is_default.

A/B target: generate 3 hook candidates, user selects, measure after a defined window, promote winners into the library.

First-10-seconds target:
- 0:00–0:03 Hook
- 0:03–0:05 Pattern Interrupt
- 0:05–0:10 Context
- 0:10+ Content

## 3. SEO and discovery
Target title optimization, keyword-aware title/caption generation, hashtag groups, caption structure, keyword research adapters, and posting-time recommendations. External research providers must be verified before production use.

## 4. Retention and engagement
Target cliffhangers, episode recap, question/poll/follow/share/save triggers, pacing analysis, and emotional arc analysis.

Target emotional pattern: Curious → Tense → Satisfied + Curious.

AI should warn about likely drop-off/pacing problems rather than silently changing approved content.

## 5. Thumbnail and visual variety
Thumbnail target: choose 10 candidate frames, create 5 candidates, user selects.

Visual variety target: close-up, wide shot, text overlay, stock footage, animation.

## 6. Sound and subtitle styling
Sound target: logo intro, hook impact, transition whoosh, climax/tension music, soft outro, and emotion-based BGM recommendation.

Subtitle style target: bold yellow hook, clean white normal, red important highlight, animation for emphasis.

## 7. Character and voice consistency
Main characters (target: 3) use LoRA-backed visual consistency and stable voice profiles. Side/background characters use prompt templates and a voice pool.

LoRA is a target capability and is not DONE until training → storage → generation → consistency is verified.

## 8. Series Bible and continuity
Target series_bible fields: series_id, title, genre, characters, world_setting, tone, visual_style, continuity_rules.

Continuity checker: character consistency, timeline, location, props.

## 9. Trending topics and cross-platform preparation
Target trend ingestion adapter, relevance matching, and optional trend-aware suggestions.

Cross-platform preparation:
- TikTok: 9:16, target 3 min
- YouTube Shorts: 9:16, target 60 sec
- Facebook Reels: 9:16, target 90 sec
- Instagram Reels: 9:16, target 90 sec

Direct platform publishing remains out of scope.

## 10. Batch generation and calendar
Batch target: plan 5 episodes → user approval → daily-limit-aware generation → weekly queue.

Calendar target: episode schedule, dates/times, calendar view, scheduling metadata.

Auto scheduling means preparing a schedule; it does not authorize direct platform publishing.

## 11. Translation
Optional later target: Burmese → English / Thai / Chinese. Not a Burmese-first release blocker.

## 12. Feedback and experimentation
Feedback loop:
Manual Data → Hook Library → Auto Defaults → Human Approve → Performance Data → Rule Refinement.

Do not change defaults from one video. Require at least 5–10 content pieces and compare multiple signals.

A/B target: title, hook, thumbnail. Manual analytics import remains acceptable under current product boundaries.

## 13. Video generation provider layer
The add-on provider list is a candidate configuration, not a verified production fact.

Target architecture:
VideoGenerationAdapter → Provider → Job → Asset → Quality/Watermark Check

Candidate providers:
- Agnes AI — primary candidate
- Kling AI — secondary candidate
- Magic Hour — tertiary candidate

Before production use, verify current free limits, API/auth, commercial-use terms, watermark behavior, quality, rate limits, and failure/retry semantics.

Do not implement watermark removal as a bypass for provider terms. If final-output policy requires no watermark, reject or route away from disallowed output.

## 14. Additional data model targets
- hook_library
- seo_metadata
- thumbnails
- ab_tests
- series_bible
- continuity_checks
- trending_topics
- engagement_triggers
- sound_design
- emotional_arcs
- pacing_analysis
- cross_platform_exports
- series_calendar
- voice_profiles
- music_library
- story_ingestion_jobs
- episode_split_plans
- video_generation_jobs
- provider_fallback_logs

A migration alone does not make a table DONE; the workflow using it must be verified.

## 15. Additional screens
- Story Upload
- Episode Split Review
- Hook Library
- SEO Optimization
- Thumbnail Selection
- A/B Test
- Series Bible
- Continuity Check
- Trending Topics
- Sound Design
- Emotional Arc
- Pacing Analysis
- Cross-Platform Export
- Series Calendar
- Voice Profile
- Music Library
- Video Generation Queue
- Provider Status
- Watermark Check
- Batch Generation

These expand the original 26-screen target. Final count must be re-baselined after duplicate concepts are merged and panels/tabs are distinguished from standalone screens.

## 16. Expanded end-to-end workflow
Story Upload → AI Analysis → Episode Split/Character/Emotion/Cliffhanger → User Approve/Modify → Script → Voice → Image → Video → Subtitle → Hook → SEO → Thumbnail → User Review/Selective Modify → Final Approval → Google Drive Export → Analytics.

Human approval remains mandatory before final export.

## 17. Expanded Definition of Done
Release target includes Story ingestion, Episode splitter, Hook library, SEO generation, Thumbnail generation, A/B testing, Series Bible, Continuity checker, Trend integration, Cross-platform preparation/export, Feedback loop, Provider fallback, Watermark policy check, Batch generation, and Series calendar.

All must pass applicable security, quota, failure/retry, audit, and human-approval requirements or be explicitly moved to reserve.


## Explicit capacity and performance requirements

### Agnes daily-limit calculation
- Planning baseline: **500 seconds/day**.
- MVP generated video assumption: **~25 seconds/video**.
- Theoretical capacity: **20 videos/day**.
- This is a planning baseline only. Verify current provider/account limits, API access, commercial-use terms, watermark behavior, rate limits, and retry semantics before production.
- Daily-limit-aware generation must reserve/consume quota, track used/remaining seconds, account for failed/retried jobs, and pause/reschedule when the verified limit is exhausted.

### Groq daily-limit tracking
- Conservative planning baseline: **1,000 requests/day**.
- Track requests used, remaining budget, retries, reset time, and fallback activation.
- Verify the live account/model limit before production; 1,000 is not a permanent provider guarantee.

### Processing target
- MVP target: **15–30 minutes per video** from processing dispatch to production-ready output.
- Verify this on the real Celery/worker + media-processing path with representative inputs and realistic load.

### Design System
- Explicit completion target: Colors, Typography, Spacing, semantic states, responsive rules, and accessibility rules implemented in actual UI code and audited.

### Component Library
- Explicit completion target: **33 reusable components** from docs/07-ui-design.md, including required variants and applicable loading/empty/error/success/disabled/permission/responsive/accessibility states.
- Documentation of the 33-component target does not count as implementation completion.
