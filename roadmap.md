# Narrativ Forge — Master Roadmap

> **Single Source of Truth** — Project Overview, Tools, Roadmap, UI, Manual Guide, Future Reserve
>
> **Last updated:** 2026-10-06

---

## 📌 အပိုင်း ၀: Project Overview

### ၀.၁ Narrativ Forge ဆိုတာ ဘာလဲ?

**Narrativ Forge** သည်—

- Private
- Invite-only
- Standalone
- Burmese Short-Form Video Production System
- Manual + Auto Mode နှစ်မျိုးပါ
- Human Review + Approval ပါ
- Google Drive Export လုပ်နိုင်

### ၀.၂ အဓိက သဘောတရား

> **Manual က production data ထုတ်ပေးမယ်။ Auto က အဲဒီ data နဲ့ workflow ကို မြန်အောင်လုပ်မယ်။ Human က quality ကို အတည်ပြုမယ်။ Google Drive က approved output ကို သိမ်းမယ်။**

### ၀.၃ Primary Output

```text
Vertical short-form video
Target: 3 minutes
Aspect ratio: 9:16
Target resolution: 1080 × 1920
Language: Burmese
Subtitle: Burmese
Output package: Video + subtitles + transcript + script + metadata + thumbnail
၀.၄ Audience
Burmese-speaking viewers

Psychology / Life lessons / Motivation

TikTok / Shorts / Reels users

၀.၅ Business Direction
Brand deals

Affiliate marketing

Later: AI-assisted video production service

၀.၆ မပါဝင်သည့်အရာများ (Strict Boundaries)
❌ Logixa Flow integration

❌ Aether Bridge integration

❌ Public registration

❌ Public profiles

❌ Public video browsing

❌ Public comments

❌ TikTok/YouTube/Facebook တိုက်ရိုက် publish

❌ External downstream delivery

❌ Google Drive ကို workflow database အဖြစ် သုံးခြင်း

📌 အပိုင်း ၁: Constraints (မသုံးတဲ့အရာ)
၁.၁ Constraint ရဲ့ အကြောင်းရင်း
Constraint	အကြောင်းရင်း
No R2	Card လိုတယ်
No AWS S3	Card လိုတယ်
No Docker	Local Space မရှိ
No WSL	Local Space မရှိ
No Ollama	Local Space မရှိ
No LM Studio	Local Space မရှိ
No Paid Services	ပိုက်ဆံ မကုန်ရ
၁.၂ အစားထိုး နည်းလမ်း
မသုံးတာ	အစားထိုး
Cloudflare R2	Backblaze B2 + Supabase
Docker	GitHub Codespaces
WSL	GitHub Codespaces
Ollama	Groq API / Cloudflare Workers AI
LM Studio	Groq API
📌 အပိုင်း ၂: Tools Stack အပြည့်အစုံ
Legend
သင်္ကေတ	အဓိပ္ပာယ်
✅	သုံးနေပြီ
🔄	သုံးမယ် (planned)
🟢	အရံ (reserve)
❌	မသုံး (Constraint)
⚠️	စစ်ရမယ်
၂.၁ Development Tools
Tool	Status	ဘာအတွက်	မှတ်ချက်
GitHub	✅	Code Storage	—
VS Code	✅	Code Editor	Local ရှိပြီး
Git	✅	Version Control	—
GitHub Codespaces	🔄	Cloud Dev Env	Docker အစားထိုး
Gitpod	🟢	Cloud Dev Env	Alternative
Postman / Insomnia	🟢	API Test	—
Continue.dev	🟢	AI Coding	—
❌ Docker	❌	—	Space မရှိ
❌ WSL	❌	—	Space မရှိ
၂.၂ Frontend
Tool	Status	ဘာအတွက်
Next.js	✅	Framework
React	✅	UI Library
Tailwind CSS	✅	Styling
TypeScript	✅	Type Safety
shadcn/ui	🔄	Component Library
Radix UI	🟢	Accessible Components
TanStack Query	🔄	Data Fetching
Zustand	🟢	State Management
Framer Motion	🟢	Animation
၂.၃ Frontend Hosting
Tool	Status	ဘာအတွက်
Netlify	✅	Hosting
Vercel	🟢	Alternative
Cloudflare Pages	🟢	Alternative
၂.၄ Backend
Tool	Status	ဘာအတွက်
FastAPI	✅	API Framework
SQLAlchemy	✅	ORM
Alembic	✅	Migrations
Pydantic	✅	Validation
Uvicorn	✅	ASGI Server
Celery	✅	Task Queue
Redis	✅	Queue / Cache
၂.၅ Backend Hosting
Tool	Status	ဘာအတွက်
Render (Web Service)	✅	API Hosting
Render (Worker)	⚠️	Free/Paid စစ်ရမယ်
Fly.io	🟢	Alternative
Cloud Run	🟢	Alternative
၂.၆ Database
Tool	Status	ဘာအတွက်
Neon PostgreSQL	✅	Production DB
SQLite	✅	Local Dev
Redis	✅	Cache / Queue
Supabase (PostgreSQL)	🟢	Alternative
၂.၇ Storage
Tool	Status	ဘာအတွက်	Size Limit
Cloudinary	✅	Images / Preview	≤ 10 MB
Supabase Storage	✅	SRT / Manifest	≤ 50 MB
Backblaze B2	✅	Raw Video / Audio	Unlimited
Google Drive	✅	Final Export	15 GB Free
❌ Cloudflare R2	❌	—	Card လိုတယ်
❌ AWS S3	❌	—	Card လိုတယ်
၂.၈ Export
Tool	Status	ဘာအတွက်
Google Drive API	✅	File Upload
Google OAuth 2.0	✅	Auth
Scope: drive.file	✅	Narrow Scope
၂.၉ Edge / AI
Tool	Status	ဘာအတွက်
Cloudflare Worker	✅	Edge Compute
Cloudflare WAF	✅	Security
Cloudflare Workers AI	✅	Whisper + LLM
Cloudflare D1	🟢	Edge DB
Cloudflare KV	🟢	Edge Storage
၂.၁၀ AI / LLM (Cloud Only)
Tool	Status	Free Tier	Card
Groq	🔄	14,400 req/day	❌
Cloudflare Workers AI	✅	10,000 neurons/day	❌
Google AI Studio (Gemini)	🔄	Free Tier	❌
OpenRouter	🟢	Free Models	❌
Mistral	🟢	Free Mode	❌
NVIDIA NIM	🟢	40 RPM	❌
Hugging Face	🟢	~1000 req/month	❌
❌ Ollama	❌	—	Space လိုတယ်
❌ LM Studio	❌	—	Space လိုတယ်
❌ Together AI	❌	—	Free Tier မရှိ
၂.၁၁ AI / ML (Manual Mode)
Tool	Status	ဘာအတွက်
ChatGPT	🔄	Script
Claude	🔄	Script
Fliki	🔄	TTS
Edge-TTS	✅	TTS Fallback
Pollinations	🔄	Image
Leonardo.Ai	🟢	Image Alternative
Suno	🟢	BGM
Udio	🟢	BGM Alternative
၂.၁၂ Video Processing
Tool	Status	ဘာအတွက်
ffmpeg.wasm	✅	Client-side
FFmpeg (Server)	✅	Fallback
ffprobe	✅	Media Info
CapCut	🔄	Manual Edit
၂.၁၃ Queue / Job
Tool	Status	ဘာအတွက်
Celery	✅	Task Queue
Redis	✅	Broker
Upstash Redis	🟢	Alternative
၂.၁၄ Monitoring
Tool	Status	ဘာအတွက်	Priority
Sentry	✅	Error Tracking	🔴 လိုတယ်
UptimeRobot	✅	Uptime	🔴 လိုတယ်
Umami Cloud	🟢	Web Analytics	🟡 နောက်မှ
Pydantic Logfire	🟢	FastAPI Monitor	🟡 နောက်မှ
Axiom	🟢	Log Aggregation	🟡 နောက်မှ
PostHog	🟢	Product Analytics	🟡 နောက်မှ
Rule: ၅ ခု → ၂ ခုပဲ (Sentry + UptimeRobot)

၂.၁၅ Email
Tool	Status	ဘာအတွက်
Resend	✅	Transactional Email
SendGrid	🟢	Alternative
၂.၁၆ Payment
Tool	Status	ဘာအတွက်
Stripe	🔄	Subscription
Paddle	🟢	Alternative
၂.၁၇ CI/CD
Tool	Status	ဘာအတွက်
GitHub Actions	✅	CI/CD
Netlify CI	✅	Frontend Deploy
Render CI	✅	Backend Deploy
၂.၁၈ Security
Tool	Status	ဘာအတွက်
CodeQL	✅	Static Analysis
Trivy	✅	Container Scan
pip-audit	✅	Python Deps
npm audit	✅	Node Deps
Dependabot	🟢	Auto Updates
၂.၁၉ Testing
Tool	Status	ဘာအတွက်
Playwright	✅	E2E Test
pytest	✅	Backend Test
Vitest	🟢	Frontend Test
၂.၂၀ Design
Tool	Status	ဘာအတွက်
Figma	🔄	UI Design
Excalidraw	🟢	Wireframe
၂.၂၁ Local Dev (Docker မပါ)
Tool	Status	ဘာအတွက်
GitHub Codespaces	🔄	Primary Dev
Gitpod	🟢	Alternative
Python venv	✅	Backend
nvm (Node.js)	✅	Frontend
PostgreSQL (Local)	🟢	DB
📌 အပိုင်း ၃: Manual Mode Guide
၃.၁ Workflow (၆ ဆင့်)
text
1. Idea (၅ မိနစ်)
2. Script (၃၀ မိနစ်)
3. Voice (၁၅ မိနစ်)
4. Images (၃၀ မိနစ်)
5. Video (၄၅ မိနစ်)
6. Publish (၁၅ မိနစ်)
၃.၂ Step 1: Idea
Topic ရွေး

Category သတ်မှတ်

Hook ရေး

Audience သတ်မှတ်

Emotion သတ်မှတ်

Quality Gate:

Title ရှိလား?

Category သတ်မှတ်ပြီးလား?

One-line concept ရှိလား?

၃.၃ Step 2: Script (ChatGPT/Claude)
Prompt:

"မြန်မာ TikTok အတွက် ၃ မိနစ်စာ Mini Series ဇာတ်ညွှန်း ရေးပါ။ Dark Psychology အကြောင်း။ ပထမ ၅ စက္ကန့် Hook။ အဆုံး Cliffhanger။"

လုပ်ရမှာ:

Scene ၅ ခု ခွဲ

Scene တစ်ခုစီ Prompt ရေး

Quality Gate:

Hook ရှိလား?

၃ မိနစ်အတွင်း?

Cliffhanger ရှိလား?

၃.၄ Step 3: Voice (Fliki/Edge-TTS)
Text paste

Voice ရွေး (Nilar/Thiha)

MP3 download

Quality Gate:

Voice duration ကိုက်လား?

Commercial Use ရလား?

၃.၅ Step 4: Images (Pollinations)
Scene တိုင်း Prompt

9:16 (1080x1920) ထုတ်

ဇာတ်ကောင် တစ်သမတ်တည်း

Quality Gate:

Scene တိုင်းမှာ ရုပ်ပုံရှိလား?

Aspect ratio မှန်လား?

၃.၆ Step 5: Video (CapCut)
Import MP3 + Images

Auto-Captions → Burmese ပြင်

BGM ထည့်

1080p, 9:16 Export

Quality Gate:

Duration မှန်လား?

Audio sync?

Subtitle overlap?

၃.၇ Step 6: Publish
TikTok တင်

Caption + Hashtag

Log ဖြည့်

၃.၈ Production Log (Google Sheets)
Column	ဘာဖြည့်မလဲ
video_id	NAR_001
topic	Dark Psychology
category	Psychology
hook	"မင်းသိထားသင့်တယ်..."
hook_type	Warning
script_length	450 words
duration	180 sec
scene_count	5
voice_tool	Fliki
image_tool	Pollinations
video_tool	CapCut
subtitle_style	Burmese Default
production_time	135 min
errors	Subtitle timing
quality_score	8/10
published	Yes
platform	TikTok
views	5000
completion_rate	45%
notes	Hook ကောင်း
၃.၉ Manual Mode Exit Gate
□ ဗီဒီယို ၁၅-၂၀ ခု ထုတ်ပြီး
□ Production Log ဖြည့်ပြီး
□ Hook types ၃ မျိုး စမ်းပြီး
□ Subtitle styles ၂ မျိုး စမ်းပြီး
□ Production time တိုင်းပြီး
□ Commercial-use risk စစ်ပြီး
📌 အပိုင်း ၄: Auto Mode Architecture
၄.၁ High-Level Architecture
text
Next.js Frontend
        ↓
FastAPI Backend
        ↓
PostgreSQL (Neon)
        ↓
Job Queue (Redis)
        ↓
Worker (Celery)
  ├── FFmpeg
  ├── Whisper
  ├── Cloud LLM (Groq)
  └── Drive Export
        ↓
Google Drive
၄.၂ Responsibility Boundaries
Layer	တာဝန်
Next.js	UI, editor, player, review
FastAPI	Auth, CRUD, validation, permissions
PostgreSQL	Workflow state
Worker	Heavy processing
FFmpeg	Media extraction/assembly
Whisper	Transcript
Google Drive	Approved export
৪.၃ Workflow (၈ ဆင့်)
text
1. Idea
2. Structure
3. Script
4. Assets
5. Processing
6. Subtitle
7. Review
8. Output
၄.၄ Status Model
text
idea → planned → script_draft → script_review
→ assets_needed → in_production → processing
→ subtitle_review → needs_approval → approved
→ exporting → exported
၄.၅ Revision Transitions
text
script_review → script_draft
subtitle_review → in_production
needs_approval → in_production
exporting → failed → processing
📌 အပိုင်း ၅: Data Model
၅.၁ Core Tables
text
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
drive_exports
publishing_states
manual_production_logs
hook_library
subtitle_presets
app_analytics
social_analytics
activity_logs
episode_versions          ← အသစ်
scene_regenerations       ← အသစ်
content_extensions        ← အသစ်
characters                ← အသစ်
၅.၂ Versioning System (အရေးကြီး)
text
episode_versions
- id
- episode_id
- version_number (v1, v2, v3)
- script_id
- voice_asset_id
- video_asset_id
- subtitle_id
- duration_seconds
- status (draft/final)
- notes
- created_at

scene_regenerations
- id
- episode_id
- scene_id
- old_asset_id
- new_asset_id
- reason
- created_at

content_extensions
- id
- episode_id
- extension_type (scene/voice/script)
- added_content
- created_at
၅.၃ Characters (LoRA)
text
characters
- id
- name
- type (main/side/background)
- lora_url (main ဆိုရင် ပဲ)
- lora_file_id (B2)
- rank (16/32)
- prompt_template (side ဆိုရင်)
- trained_at
- status (active/inactive)
- created_at
Rule:

Main Character (၃ ယောက်) → LoRA လိုတယ်

ဖြတ်လျှောက် → Prompt ပဲ

📌 အပိုင်း ၆: UI Plan
၆.၁ Design Principles (၅ ခု)
Production-first (not consumer social)

Keyboard-friendly

Responsive (Desktop/Tablet/Mobile)

Accessible (WCAG AA)

State-complete (Empty/Loading/Error)

၆.၂ Screen List (၂၆ ခု)
Auth (၂)
#	Screen	Priority
1	Login	🔴 P0
2	Logout	🔴 P0
Dashboard (၁)
#	Screen	Priority
3	Dashboard	🔴 P0
Content (၅)
#	Screen	Priority
4	Ideas	🔴 P0
5	All Series	🔴 P0
6	Series Detail	🔴 P0
7	Episodes	🔴 P0
8	Episode Detail	🔴 P0
Production (၆)
#	Screen	Priority
9	Script Studio	🔴 P0
10	Scene Breakdown	🔴 P0
11	Asset Library	🔴 P0
12	Video Project	🔴 P0
13	Subtitle Studio	🔴 P0
14	Thumbnail Studio	🟡 P1
Processing (၁)
#	Screen	Priority
15	Processing Queue	🔴 P0
Review (၂)
#	Screen	Priority
16	Review Center	🔴 P0
17	Approval Detail	🔴 P0
Export (၂)
#	Screen	Priority
18	Drive Export	🔴 P0
19	Publishing Preparation	🟡 P1
Intelligence (၄)
#	Screen	Priority
20	Hook Library	🟡 P1
21	Manual Production Log	🟡 P1
22	App Analytics	🟡 P1
23	Social Analytics	🟡 P1
System (၃)
#	Screen	Priority
24	Settings	🟡 P1
25	Usage & Limits	🟢 P2
26	Activity Log	🟢 P2
၆.၃ Most Important Screens (၃ ခု)
1. Episode Detail
Workflow control center

Status timeline

Quick actions

2. Subtitle Studio
Transcript pane

Subtitle editor

Timing ruler

Warning panel

Preset selector

3. Review & Export
Video player

Checklist

Critical issue blocking

Approve/Reject buttons

📌 အပိုင်း ၇: Design System
၇.၁ Colors
text
Primary:    Blue (#3B82F6)
Secondary:  Gray (#6B7280)
Success:    Green (#10B981)
Warning:    Yellow (#F59E0B)
Error:      Red (#EF4444)
Background: White / Dark
၇.၂ Typography
text
Font:  Inter / Noto Sans Myanmar
Sizes: 12, 14, 16, 18, 20, 24, 32, 48
၇.၃ Spacing
text
4, 8, 12, 16, 24, 32, 48, 64
၇.၄ States
text
Default / Hover / Focus / Disabled / Loading / Error
📌 အပိုင်း ၈: Component Library (၃၃ ခု)
၈.၁ Layout (၄)
AppShell

Sidebar

TopBar

Breadcrumb

၈.၂ Forms (၈)
TextInput

TextArea

Select

Checkbox

Radio

FileUpload

DatePicker

FormError

၈.၃ Data Display (၆)
Table

Card

Badge

StatusPill

ProgressBar

Timeline

၈.၄ Media (၅)
VideoPlayer

AudioPlayer

ImagePreview

SubtitleEditor

Timeline

၈.၅ Feedback (၅)
Toast

Modal

Drawer

Alert

ConfirmDialog

၈.၆ States (၅)
EmptyState

LoadingState

ErrorState

OfflineState

PermissionDeniedState

📌 အပိုင်း ၉: Versioning & Modification System
၉.၁ Rule (အရေးကြီးဆုံး)
ပြန်ပြင်တာ ပိုကောင်းတယ်။ ဖျက်ပစ်တာ မကောင်းဘူး။

၉.၂ Selective Regeneration
text
EP 2 မှာ Scene 3 မကြိုက်ဘူး
    ↓
Scene 3 ပဲ ရွေး → "Regenerate"
    ↓
AI က Scene 3 ရုပ်ပုံ အသစ် ၃ ပုံ ထုတ်
    ↓
မင်း ကြိုက်တာ ရွေး
    ↓
Video ပြန် ပေါင်း
    ↓
ပြီး။ Scene 1, 2, 4, 5 မထိဘူး။
၉.၃ Version Storage Policy
text
သိမ်းထားရမယ့် Version:
├── v1 (Original) — သိမ်း
├── v2 (Modified) — သိမ်း
├── v3 (Final) — သိမ်း
└── v4-v10 — အကောင်းဆုံး ၁ ခုပဲ သိမ်း၊ ကျန် ဖျက်

Rule:
- Final Version — အမြဲ သိမ်း
- Last 3 Versions — သိမ်း
- ကျန် — ဖျက်
၉.၄ ဖျက်သင့်တဲ့ အခြေအနေ
အခြေအနေ	ဖျက်သင့်လား?
Concept လုံးဝ မှား	✅ ဖျက်
Version ၁၀ ခုအထက်	✅ အကောင်းဆုံး ၃ ခုပဲ ထား
Storage ပြည့်	✅ အကောင်းဆုံးပဲ ထား
Scene တစ်ခုပဲ မကြိုက်	❌ မဖျက်ရ — ပြန် Generate
၉.၅ AI Request နှိုင်းယှဉ်
နည်း	AI Request
ဖျက်ပြီး ပြန်လုပ်	၂၀-၃၀
ပြန်ပြင်	၇
၉.၆ LoRA Strategy
ဇာတ်ကောင်	LoRA	Space
Main Character (၃)	✅	၆၀၀ MB
ဖြတ်လျှောက် (၂၀+)	❌ Prompt ပဲ	၀ MB
Training:

Platform: Kaggle (Free 30 hrs/week) / Google Colab

Tool: Kohya's GUI

Time: ၁-၂ နာရီ/LoRA

Storage: B2 (Primary) + Google Drive (Backup)

📌 အပိုင်း ၁၀: Roadmap
၁၀.၁ Track 0: Setup
□ GitHub Codespaces ဖွင့်
□ VS Code (Browser) setup
□ Python venv
□ Node.js (nvm)
□ Git config
□ roadmap.md ရေး
၁၀.၂ Track 1: Manual Production (🔴 P0)
□ ChatGPT/Claude နဲ့ ဇာတ်ညွှန်း
□ Fliki/Edge-TTS နဲ့ အသံ
□ Pollinations နဲ့ ရုပ်ပုံ
□ CapCut နဲ့ ဗီဒီယို
□ TikTok တင်
□ Google Sheets Log
□ Hook Types ၃ မျိုး
□ Subtitle Styles ၂ မျိုး
Exit Gate:

□ ဗီဒီယို ၁၅-၂၀ ခု
□ Manual Log ရှိ
□ Hook Library အစ
၁၀.၃ Track 2: Backend Verification (🔴 P0)
Real Storage Tests:

□ B2 upload/download/delete
□ Supabase Storage test
□ Cloudinary test
□ Hybrid routing E2E
Real AI Tests:

□ Cloudflare Whisper → VTT → Subtitle Studio
□ Celery fallback on quota-exhaustion
□ Groq API → Script
Real Drive Tests:

□ Google OAuth callback
□ Real Drive export
□ Idempotent retry test
Worker Tests:

□ Full processing worker smoke test
□ Retry/DLQ verification
□ Duplicate-dispatch verification
Business Tests:

□ Stripe webhook lifecycle
□ SMTP invitation delivery
□ Sentry production event
Security Tests:

□ Cross-tenant isolation E2E
□ Full E2E auth flow
□ Backup/restore drill
၁၀.၄ Track 3: Frontend / UI (🔴 P0)
Phase 1: Foundation

□ Next.js app structure
□ Tailwind setup
□ shadcn/ui setup
□ API client
□ Auth screens
Phase 2: Core Screens

□ Dashboard
□ Ideas
□ Series / Seasons / Episodes
□ Episode Detail
□ Script Studio
□ Scene Breakdown
Phase 3: Media Screens

□ Asset Library
□ Video Project
□ Subtitle Studio
□ Processing Queue
□ Thumbnail Studio
Phase 4: Review & Export

□ Review Center
□ Approval Detail
□ Drive Export
□ Publishing Preparation
Phase 5: Intelligence

□ Hook Library
□ Manual Production Log
□ App Analytics
□ Social Analytics
Phase 6: Settings

□ Settings
□ Usage & Limits
□ Activity Log
□ Billing
UI States (အားလုံး လိုတယ်):

□ Empty
□ Loading
□ Uploading
□ Processing
□ Completed
□ Failed
□ Retrying
□ Rejected
□ Offline/Read-only
□ Permission denied
□ Session expired
□ Drive disconnected
□ Drive export failed
□ Storage warning
□ Unsupported file
□ Critical quality issue
၁၀.၅ Track 4: Production Hardening (🟡 P1)
Security:

□ Final dependency scan
□ Docker image scan
□ Penetration test
□ Security review
Reliability:

□ Flaky-network upload test
□ Backup/restore drill
□ Load test
UX:

□ Empty/loading states audit
□ Mobile/tablet responsive
□ WCAG accessibility
□ UI polish
၁၀.၆ Track 5: Business / Legal (🟡 P1)
□ Terms of Service
□ Privacy Policy
□ DPA documentation
□ DMCA process
□ Stripe production
□ Business review
၁၀.၇ Track 6: Future / Reserve (🟢 P2)
Mobile:

React Native

Expo

Flutter

Advanced AI:

GPT-4 API

Claude 3.5 API

Gemini API

Stable Diffusion Local

ComfyUI

LoRA Training (Cloud GPU)

Advanced Video:

DaVinci Resolve

Adobe Premiere

Blender

Advanced Storage:

AWS S3

Cloudflare R2

Wasabi

MinIO

Advanced Queue:

RabbitMQ

Kafka

AWS SQS

Temporal

Advanced Monitoring:

Grafana

Prometheus

Datadog

New Relic

ELK Stack

Advanced Security:

Vault

AWS KMS

Auth0

Clerk

Business:

Stripe Connect

Paddle

Lemon Squeezy

PayPal

Marketing:

Mailchimp

ConvertKit

Buffer

Analytics:

Mixpanel

Amplitude

Segment

PostHog

Infrastructure:

Kubernetes

Terraform

Ansible

Pulumi

Database:

MongoDB

Cassandra

DynamoDB

ClickHouse

Search:

Elasticsearch

Meilisearch

Typesense

Algolia

Feature Flags:

LaunchDarkly

Unleash

Flagsmith

A/B Testing:

Optimizely

VWO

GrowthBook

Communication:

Slack API

Discord API

Telegram Bot

Design:

Figma

Penpot

Sketch

Documentation:

Docusaurus

MkDocs

GitBook

📌 အပိုင်း ၁၁: Quality Gates
၁၁.၁ Script Gate
□ Hook ရှိရမယ်
□ Target duration ကိုက်ရမယ်
□ Scene တိုင်းမှာ purpose ရှိရမယ်
□ Cliffhanger/resolution ရှိရမယ်
၁၁.၂ Asset Gate
□ Scene တိုင်းမှာ asset ရှိရမယ်
□ Aspect ratio မှန်ရမယ်
□ Voice duration ကိုက်ရမယ်
□ Commercial-use status သိရမယ်
၁၁.၃ Processing Gate
□ Render successful
□ 9:16 resolution
□ Audio track ရှိ
□ No corrupted output
၁၁.၄ Subtitle Gate
□ No overlap
□ Missing text မရှိ
□ Start < End
□ Min 1s, Max 7s
□ Burmese text valid
□ Reading speed warning
၁၁.၅ Review Gate
□ Video playback complete
□ Audio clear
□ Subtitle readable
□ Thumbnail selected
□ Critical issues = 0
၁၁.၆ Export Gate
□ Status = approved
□ Required files complete
□ Metadata schema valid
□ Drive connected
📌 အပိုင်း ၁၂: Google Drive Export
၁၂.၁ Folder Structure
text
/narrativ-forge/
└── YYYY-MM-DD/
    └── content-id/
        ├── video.mp4
        ├── subtitles.srt
        ├── subtitles.vtt
        ├── transcript.txt
        ├── script.md
        ├── metadata.json
        ├── thumbnail.jpg
        └── export-manifest.json
၁၂.၂ Export Rules
Approved content သာ export

Same episode ကို ပြန် export ရင် duplicate folder မဖန်တီး

Existing export ကို versioned update

Export failure → failed → retry

Partial upload → manifest မပြီးမချင်း complete မသတ်မှတ်

Drive file IDs အားလုံး database မှာ သိမ်း

OAuth token frontend မှာ မထား

📌 အပိုင်း ၁၃: Security
၁၃.၁ Security Rules
☑ Invite-only access
☑ Backend-side RBAC
☑ OAuth tokens server-side only
☑ No secrets in Git
☑ No tokens in localStorage
☑ Narrow Google Drive scopes
☑ MIME and extension validation
☑ File size limit
☑ Filename sanitization
☑ Path traversal protection
☑ CORS whitelist
☑ Auth/upload rate limits
☑ No secrets in logs
☑ Audit approval/export actions
☑ Idempotent Drive export
☑ Retry without duplicate files
☑ Preserve failed jobs
☑ Never delete source asset automatically
☑ Soft-delete content
☑ Database backup
☑ Export manifest checksum
၁၃.၂ Reliability Rule
Original uploaded files ကို processing output နဲ့ overwrite မလုပ်ပါ။ Original, draft, preview, final ကို သီးခြား version တွေအဖြစ် သိမ်းရမယ်။

📌 အပိုင်း ၁၄: Development
၁၄.၁ Frontend
bash
cd web-platform/frontend
npm install
npm run dev
၁၄.၂ Backend
bash
cd web-platform/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
၁၄.၃ Checks
bash
npm run typecheck
npm run build
npm run e2e
pytest
၁၄.၄ GitHub Codespaces
text
1. github.com ဖွင့်
2. Repo → Code → Codespaces → New
3. Terminal ဖွင့်
4. pip install / npm install
5. Run
📌 အပိုင်း ၁၅: Environment Variables
text
APP_ENV=production
SESSION_SECRET=<secret>
SESSION_COOKIE_SECURE=true
CORS_ORIGINS=<frontend-origin>
TRUSTED_HOSTS=<backend-host>

DATABASE_URL=<postgres>
REDIS_URL=<redis>

CLOUDINARY_CLOUD_NAME=<secret>
CLOUDINARY_API_KEY=<secret>
CLOUDINARY_API_SECRET=<secret>

B2_APPLICATION_KEY_ID=<secret>
B2_APPLICATION_KEY=<secret>
B2_BUCKET_NAME=<bucket>
B2_REGION=<region>

SUPABASE_URL=<project-url>
SUPABASE_SERVICE_ROLE_KEY=<secret>
SUPABASE_STORAGE_BUCKET=narrativ-forge

GOOGLE_CLIENT_ID=<secret>
GOOGLE_CLIENT_SECRET=<secret>
GOOGLE_REDIRECT_URI=<backend-callback>
OAUTH_ENCRYPTION_KEY=<secret>

SENTRY_DSN=<secret>

CLOUDFLARE_WHISPER_WORKER_URL=<worker-url>
CLOUDFLARE_WHISPER_SHARED_SECRET=<secret>
CLOUDFLARE_WHISPER_TOKEN_TTL_SECONDS=300

GROQ_API_KEY=<secret>                    ← အသစ်

STRIPE_SECRET_KEY=<secret>
STRIPE_WEBHOOK_SECRET=<secret>
STRIPE_PRICE_PRO=<price-id>
STRIPE_PRICE_BUSINESS=<price-id>
📌 အပိုင်း ၁၆: Daily Limit & Processing Targets
၁၆.၁ Groq Free Tier
အချက်	တန်ဖိုး
Limit	1,000 requests/day (model တစ်ခုချင်း)
တစ်ပုဒ် (ပြင်ဆင်မှု အပါ)	6-10 requests
Practical Max	5-10 ပုဒ်/ရက်
၁၆.၂ Cloudflare Workers AI
အချက်	တန်ဖိုး
Limit	10,000 neurons/day
Whisper	~243 audio min/day
၁၆.၃ Processing Targets
Operation	MVP Target	Optimized Target
Audio extraction	1-2 min	Under 1 min
Whisper transcription	5-10 min	2-3 min
Subtitle generation	1-2 min	Under 1 min
Thumbnail	1-2 min	Under 1 min
FFmpeg assembly	5-10 min	2-3 min
Drive export	2-5 min	1-2 min
Total	15-30 min	7-15 min
📌 အပိုင်း ၁၇: Final Definition of Done
၁၇.၁ Manual Mode
□ Video ၁၅-၂၀ ခု ထုတ်ပြီး
□ Production log ဖြည့်ပြီး
□ Hook types ၃ မျိုးအနည်းဆုံး
□ Subtitle styles ၂ မျိုးအနည်းဆုံး
□ Production time တိုင်းပြီး
□ Commercial-use risk စစ်ပြီး
၁၇.၂ Auto Mode
□ Standalone app
□ No Logixa Flow
□ No Aether Bridge
□ Invite-only login
□ Role-based access
□ Ideas → Series → Season → Episode
□ Script and scene workflow
□ Upload and asset versioning
□ Transcript generation
□ Timestamp alignment
□ Burmese subtitle editor
□ Quality gates
□ Human approval
□ Approved-only export
□ Google Drive package
□ Metadata and manifest
□ Category system
□ Social preparation
□ Manual publishing record
□ App analytics
□ Social analytics import
□ Hook library
□ Subtitle presets
□ Manual production log
□ Feedback loop
□ Empty/loading/error/offline states
□ Responsive UI
□ Unit/integration/E2E tests
□ Security audit
□ Deployment audit
□ Backup/restore test
📌 အပိုင်း ၁၈: Final Source of Truth
Narrativ Forge သည် Manual Mode နှင့် Auto Mode ပါဝင်သော standalone Burmese short-form video production system ဖြစ်သည်။ Manual Mode သည် Auto Mode ၏ specification နှင့် training data ဖြစ်ပြီး၊ Auto Mode သည် အတည်ပြုထားသော manual workflow ကို automate လုပ်ပေးသည်။

Workflow သည် Idea → Structure → Script → Assets → Processing → Subtitle → Review → Output ဖြစ်သည်။ Human approval မရှိပါက Google Drive export မဖြစ်ရ။

Google Drive သည် approved output ၏ final destination ဖြစ်ပြီး၊ application database သည် workflow state, version, subtitle, approval, analytics နှင့် audit data များ၏ source of truth ဖြစ်သည်။

📌 အပိုင်း ၁၉: Next Sequence
text
1. Verify production storage credentials
        ↓
2. Run real B2 / Supabase / Cloudinary verification
        ↓
3. Run real Cloudflare Whisper → VTT → Subtitle Studio
        ↓
4. Run real Groq API → Script
        ↓
5. Run a real Celery worker/runtime smoke test
        ↓
6. Verify Google Drive export + idempotent retry
        ↓
7. Verify Stripe + SMTP + Sentry + audit events
        ↓
8. Complete backup/restore, dependency, security audits
        ↓
9. Run the full integration/E2E suite
        ↓
10. Final production readiness decision
📌 အပိုင်း ၂၀: Documentation Index
Root Level
File	Status	ဘာအတွက်
README.md	✅	Project Overview
SECURITY.md	✅	Security Policy
roadmap.md	✅	This file
tools.md	🟢	Tool Stack (roadmap မှာ ပါပြီ)
manual-mode.md	🟢	Manual Guide (roadmap မှာ ပါပြီ)
ui-plan.md	🟢	UI Plan (roadmap မှာ ပါပြီ)
future-reserve.md	🟢	Future (roadmap မှာ ပါပြီ)
web-platform/docs/
File	ဘာအတွက်
architecture.md	System Architecture
data-contract.md	Data Model
processing-flow.md	Processing Pipeline
drive-export.md	Google Drive Export
deployment.md	Deployment Guide
web-platform/docs/runbooks/
File	ဘာအတွက်
stuck_job.md	Stuck Job Recovery
rotate_secrets.md	Secret Rotation
restore.md	Database Restore
UI Docs
File	ဘာအတွက်
ui-states.md	State Management
ui-accessibility.md	A11y Guide
ui-responsive.md	Responsive Guide
ui-testing.md	UI Testing Guide
ဒီ roadmap.md သည် Narrativ Forge ရဲ့ Single Source of Truth ဖြစ်သည်။


---

## 📚 Reconciled Documentation

The master roadmap remains the **target/source of truth for what Narrativ Forge is intended to become**. The repository README remains the source for actual implementation/deployment state.

The reconciled documentation is now split under `docs/`:

- `docs/README.md` — documentation map
- `docs/01-product.md` — product definition and boundaries
- `docs/02-stack.md` — stack and constraints
- `docs/03-architecture.md` — architecture
- `docs/04-current-vs-target.md` — implementation vs target reconciliation
- `docs/05-execution-roadmap.md` — remaining work and release order
- `docs/06-future-reserve.md` — deferred scope

### Documentation rule

`roadmap.md` describes the **desired final system**.  
`README.md` describes the **actual repository state**.  
`docs/04-current-vs-target.md` reconciles the two.  
`docs/05-execution-roadmap.md` is the current execution queue.

Do not mark a feature production-ready merely because code exists; real integration, runtime, security, and recovery verification must pass.


---

## 📚 Add-On Reconciliation — 2026-10-06

The additional Auto Production requirements have been merged into the reconciled plan. Detailed specification: `docs/09-auto-production-expansion.md`.

### Newly added target areas
- Story Upload + AI Episode Splitter
- 8-type Hook Engineering + Hook Library + A/B flow
- SEO Optimization + Keyword/Trend adapters
- Retention, Pacing, Emotional Arc and Engagement systems
- Auto Thumbnail pipeline + Visual Variety
- Sound Design + emotion-based BGM matching
- Character/Voice consistency + Series Bible + Continuity Checker
- Cross-platform export preparation
- Batch Generation + Series Calendar
- Feedback Loop + Title/Hook/Thumbnail A/B testing
- Video Generation Provider Adapter + fallback + quota tracking
- Watermark/commercial-use policy checks
- Expanded data tables and production screens

### Important planning rule
The new provider numbers/free-tier claims are treated as **unverified candidate assumptions** until checked against live provider terms, API access, quotas, commercial-use rules, watermark behavior and quality.

### Revised execution principle
Do not jump directly into all new features. First make the repository green and complete real infrastructure verification. Then build the expanded Auto Production pipeline incrementally with schema → API/service → worker → UI → tests → real integration verification.

### Revised Source of Truth
`roadmap.md` = desired final system.
`README.md` = actual repository state.
`docs/04-current-vs-target.md` = current vs target status.
`docs/05-execution-roadmap.md` = current execution order.
`docs/09-auto-production-expansion.md` = detailed Add-On target specification.


## Master reconciliation — 2026-10-07

The repository roadmap, prior master/remediation plans, formal Phases 01–12, Expanded Auto Production 13–17, and Batches 18–36 are reconciled in **docs/21-master-completion-matrix.md**.

That matrix is the execution status map: code/foundation work may be completed autonomously, while real worker, credentials, provider accounts, production recovery, E2E, performance, accessibility, legal, and pen-test gates remain explicitly evidence-bound.
