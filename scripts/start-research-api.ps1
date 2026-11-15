# EarthTrend Detective: local read-only research API launcher.
# Run from the repository root. It DOES NOT create or alter research records.
param([string]$Database = "backend/no-push/research/earthtrend.sqlite3", [int]$Port = 8000)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$backend = Join-Path $repo 'backend'
$python = Join-Path $backend '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw "Python virtual environment missing: $python" }
$selected = if ([IO.Path]::IsPathRooted($Database)) { $Database } else { Join-Path $repo $Database }
if (-not (Test-Path -LiteralPath $selected -PathType Leaf)) { throw "Reviewed research database is missing: $selected. Run real NASA research extraction first." }
$db = (Resolve-Path -LiteralPath $selected -ErrorAction Stop).Path
Push-Location $backend
try {
  & $python -m services.research_storage --database $db
  if ($LASTEXITCODE -ne 0) { throw 'Research SQLite integrity verification failed. Refusing to publish.' }
  $env:EARTH_TREND_RESEARCH_DB = $db
  $env:EARTH_TREND_RESEARCH_PUBLIC = '1'
  Write-Host "Starting read-only EarthTrend research API on http://127.0.0.1:$Port"
  & $python -m uvicorn main:app --host 127.0.0.1 --port $Port
  if ($LASTEXITCODE -ne 0) { throw "Uvicorn exited with code $LASTEXITCODE" }
} finally { Pop-Location }
