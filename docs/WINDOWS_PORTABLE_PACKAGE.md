# Windows Portable Package

This document describes how to build and run the Narrativ Forge Windows portable package
(a self-contained `.zip` that bundles the Next.js standalone output + FastAPI backend + SQLite).

## Prerequisites

- Windows 10/11 (x64)
- Node.js 20 LTS (for the build step)
- Python 3.11+ (bundled in the package after build)

## Build

```powershell
# From repo root
.\scripts\windows-portable\build.ps1
```

This produces `dist/narrativ-forge-windows-portable-<version>.zip`.

## Run

```powershell
# Extract the zip, then:
cd narrativ-forge-windows-portable
.\start.bat
```

The start script launches:
1. FastAPI backend on `http://localhost:8000`
2. Next.js standalone server on `http://localhost:3000`

Open `http://localhost:3000` in your browser.

## Environment

Copy `.env.example` to `.env` and fill in your values before running.
The portable package reads `.env` from its own directory.

## CI

The `windows-portable-package.yml` workflow builds and smoke-tests this package
on every push that touches frontend, backend, scripts, or this doc file.
