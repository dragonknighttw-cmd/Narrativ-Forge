[CmdletBinding()]
param(
    [string]$Root = $PSScriptRoot,
    [switch]$NoBrowser
)
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path $Root).Path
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$Data = Join-Path $Root "data"
$Runtime = Join-Path $Root ".runtime"
$VenvPython = Join-Path $Backend ".venv\Scripts\python.exe"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw "Python 3.12 is required on PATH." }
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { throw "Node.js 20 is required on PATH." }
$pythonVersion = (& python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')").Trim()
if ($pythonVersion -ne "3.12") { throw "Python 3.12 is required; found $pythonVersion." }
if (-not (Test-Path (Join-Path $Frontend "server.js"))) { throw "Portable frontend server.js is missing." }
New-Item -ItemType Directory -Force -Path $Data, (Join-Path $Data "uploads"), $Runtime | Out-Null

if (-not (Test-Path $VenvPython)) {
    & python -m venv (Join-Path $Backend ".venv")
    if ($LASTEXITCODE -ne 0) { throw "Could not create backend virtual environment." }
}
& $VenvPython -m pip install --disable-pip-version-check -r (Join-Path $Backend "requirements-windows-portable.txt")
if ($LASTEXITCODE -ne 0) { throw "Could not install portable API dependencies." }

$env:APP_ENV = "development"
$env:DATABASE_URL = "sqlite:///" + ((Join-Path $Data "narrativ_forge.db") -replace '\\', '/')
$env:STORAGE_PROVIDER = "local"
$env:UPLOAD_DIR = (Join-Path $Data "uploads")
$env:SESSION_SECRET = ([guid]::NewGuid().ToString("N") + [guid]::NewGuid().ToString("N"))
$env:SESSION_COOKIE_SECURE = "false"
$env:CORS_ORIGINS = "http://127.0.0.1:3000,http://localhost:3000"
$env:TRUSTED_HOSTS = "127.0.0.1,localhost"
$env:FRONTEND_BASE_URL = "http://127.0.0.1:3000"

Push-Location $Backend
try {
    & $VenvPython -m alembic upgrade head
    if ($LASTEXITCODE -ne 0) { throw "Database migration failed." }
} finally { Pop-Location }

$apiOut = Join-Path $Runtime "api.stdout.log"
$apiErr = Join-Path $Runtime "api.stderr.log"
$webOut = Join-Path $Runtime "web.stdout.log"
$webErr = Join-Path $Runtime "web.stderr.log"
$api = $null
$web = $null
try {
    $api = Start-Process -FilePath $VenvPython -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000") -WorkingDirectory $Backend -PassThru -RedirectStandardOutput $apiOut -RedirectStandardError $apiErr
    $api.Id | Set-Content -Encoding ascii (Join-Path $Runtime "api.pid")
    $apiReady = $false
    for ($i = 0; $i -lt 45; $i++) {
        if ($api.HasExited) { throw "API process exited early. See $apiErr" }
        try {
            $null = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8000/api/v1/health" -TimeoutSec 3
            $apiReady = $true
            break
        } catch { Start-Sleep -Seconds 2 }
    }
    if (-not $apiReady) { throw "API did not become healthy. See $apiOut and $apiErr" }

    $env:PORT = "3000"
    $env:HOSTNAME = "127.0.0.1"
    $web = Start-Process -FilePath (Get-Command node).Source -ArgumentList @((Join-Path $Frontend "server.js")) -WorkingDirectory $Frontend -PassThru -RedirectStandardOutput $webOut -RedirectStandardError $webErr
    $web.Id | Set-Content -Encoding ascii (Join-Path $Runtime "web.pid")
    $webReady = $false
    for ($i = 0; $i -lt 45; $i++) {
        if ($web.HasExited) { throw "Frontend process exited early. See $webErr" }
        try {
            $response = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:3000/login" -TimeoutSec 3
            if ($response.StatusCode -eq 200) { $webReady = $true; break }
        } catch { Start-Sleep -Seconds 2 }
    }
    if (-not $webReady) { throw "Frontend did not become healthy. See $webOut and $webErr" }
    [ordered]@{
        started_at = (Get-Date).ToUniversalTime().ToString("o")
        api_url = "http://127.0.0.1:8000"
        frontend_url = "http://127.0.0.1:3000"
        api_pid = $api.Id
        frontend_pid = $web.Id
        database = "SQLite"
        storage = $env:UPLOAD_DIR
        worker_included = $false
        offline_capable = $false
    } | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $Runtime "runtime-manifest.json")
    Write-Host "Narrativ Forge portable API/UI runtime is ready."
    Write-Host "API: http://127.0.0.1:8000"
    Write-Host "UI:  http://127.0.0.1:3000/login"
    if (-not $NoBrowser) { Start-Process "http://127.0.0.1:3000/login" }
} catch {
    if ($web -and -not $web.HasExited) { Stop-Process -Id $web.Id -Force -ErrorAction SilentlyContinue }
    if ($api -and -not $api.HasExited) { Stop-Process -Id $api.Id -Force -ErrorAction SilentlyContinue }
    throw
}
