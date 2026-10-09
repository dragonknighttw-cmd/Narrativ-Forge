[CmdletBinding()]
param([string]$Root = $PSScriptRoot)
$ErrorActionPreference = "Continue"
$Root = (Resolve-Path $Root).Path
$Runtime = Join-Path $Root ".runtime"
$expectedApiPython = [System.IO.Path]::GetFullPath((Join-Path $Root "backend/.venv/Scripts/python.exe")).Replace("/", "\\")
$expectedFrontendServer = [System.IO.Path]::GetFullPath((Join-Path $Root "frontend/server.js")).Replace("/", "\\")
foreach ($name in @("web.pid", "api.pid")) {
    $pidFile = Join-Path $Runtime $name
    if (-not (Test-Path $pidFile)) { continue }
    $processId = 0
    [void][int]::TryParse((Get-Content $pidFile -Raw).Trim(), [ref]$processId)
    if ($processId -gt 0) {
        $proc = Get-CimInstance Win32_Process -Filter "ProcessId = $processId" -ErrorAction SilentlyContinue
        if ($proc) {
            $commandLine = [string]$proc.CommandLine
            $isExpected = $false
            if ($name -eq "api.pid") {
                $isExpected = ($proc.Name -ieq "python.exe") -and
                    ($commandLine.IndexOf($expectedApiPython, [StringComparison]::OrdinalIgnoreCase) -ge 0) -and
                    ($commandLine -match "uvicorn\\s+app\\.main:app")
            } else {
                $isExpected = ($proc.Name -ieq "node.exe") -and
                    ($commandLine.IndexOf($expectedFrontendServer, [StringComparison]::OrdinalIgnoreCase) -ge 0)
            }
            if ($isExpected) {
                Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
                try { Wait-Process -Id $processId -Timeout 10 -ErrorAction SilentlyContinue } catch {}
            } else {
                Write-Warning "PID $processId no longer matches this Narrativ Forge runtime; refusing to terminate an unrelated process."
            }
        }
    }
    Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
}
Write-Host "Narrativ Forge runtime stop completed. User data was preserved."
