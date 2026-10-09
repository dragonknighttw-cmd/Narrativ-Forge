[CmdletBinding()]
param([string]$Root = $PSScriptRoot)
$ErrorActionPreference = "Continue"
$Root = (Resolve-Path $Root).Path
$Runtime = Join-Path $Root ".runtime"
foreach ($name in @("web.pid", "api.pid")) {
    $pidFile = Join-Path $Runtime $name
    if (-not (Test-Path $pidFile)) { continue }
    $processId = 0
    [void][int]::TryParse((Get-Content $pidFile -Raw).Trim(), [ref]$processId)
    if ($processId -gt 0) {
        $proc = Get-Process -Id $processId -ErrorAction SilentlyContinue
        if ($proc) {
            Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
            try { Wait-Process -Id $processId -Timeout 10 -ErrorAction SilentlyContinue } catch {}
        }
    }
    Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
}
Write-Host "Narrativ Forge runtime processes stopped. User data was preserved."
