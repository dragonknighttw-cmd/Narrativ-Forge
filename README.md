# Narrativ Forge

Private, invite-only Burmese short-form video production workspace.

## Repository layout

- `web-platform/frontend` — Next.js web application
- `web-platform/backend` — FastAPI API and domain foundation
- `web-platform/docs` — architecture and implementation documentation
- `mobile` — reserved mobile application workspace

The application follows the Narrativ Forge Final Master Plan v4.0.

## Development

Frontend:
```bash
cd web-platform/frontend
npm install
npm run dev
```

Backend:
```bash
cd web-platform/backend
python -m venv .venv
# activate the environment
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The first implementation is mock-first. Heavy media processing, Whisper, FFmpeg, Google Drive OAuth, and cloud deployment are integration phases after the foundation is verified.
