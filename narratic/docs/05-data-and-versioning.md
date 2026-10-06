# Narrativ Forge — Data & Versioning

## Core entities

```
users
ideas
series
seasons
episodes
scripts
scenes
assets
subtitle_cues
processing_jobs
approvals
drive_exports / export_records
publishing_states
manual_production_logs
hook_library
subtitle_presets
app_analytics
social_analytics
activity_logs
```

The roadmap additionally reserves:
- episode_versions
- scene_regenerations
- content_extensions
- characters

## Versioning principle

> ပြန်ပြင်တာ ပိုကောင်းတယ်။ ဖျက်ပစ်တာ မကောင်းဘူး။

Original uploaded files must never be overwritten by processing outputs.

## Episode version

Target fields include:
- episode_id
- version_number
- script_id
- voice_asset_id
- video_asset_id
- subtitle_id
- duration_seconds
- status
- notes
- created_at

## Selective regeneration

If Scene 3 is wrong, regenerate Scene 3 only. Keep Scenes 1, 2, 4, 5 unchanged, then rebuild the video from the selected asset versions.

## Storage policy target

- Final version: always keep
- Last 3 versions: keep
- Older disposable versions: garbage-collect when policy allows
- Never automatically delete source assets merely because a derivative version is replaced

## Characters / LoRA

Target:
- main characters may use LoRA
- background/transient characters use prompt templates
- LoRA training/storage remains future/reserve until the current production workflow is stable
