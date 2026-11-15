# Increment 11 — Local NASA Acceptance and CSS Build Hotfix

## Scope
Fix the test that assumed downloaded NASA datasets were missing; add isolated tests covering absent, partial, zero-byte, and complete file sets. Correct stylesheet import ordering; add frontend regression test. No NASA observations, boundaries, footer, backend API behavior, database schema, or original submitted snapshot are changed. Section 31 deferred.

## Verified in the build environment
- `cd backend && python -m pytest -q`: **136 passed, 8 warnings**.
- `cd frontend && npm test`: **61 passed**.
- Frontend Vite production build was NOT run here: `node_modules` are absent. The user's Windows `npm run build` previously completed successfully despite the warning. The import order fix should remove the CSS warning but must be verified locally.

## Windows commands — IMPORTANT: reset variables in every new PowerShell session
```powershell
cd D:\Hackathon\Nasa\Bangladesh-Earth-Trend-Explorer\backend
$i = "cc68af0e-8e65-48a7-a405-7add8a0eeba7"
$g = "f8efd328-b615-43e9-8a35-a7308d407000"
$imerg = ".\no-push\nasa-downloads\IMERG\$i"
$gldas = ".\no-push\nasa-downloads\GLDAS\$g"
foreach ($dir in @($imerg,$gldas)) {
  if (-not (Test-Path -LiteralPath $dir -PathType Container)) { throw "Missing directory: $dir" }
  $count = @(Get-ChildItem -LiteralPath $dir -Filter *.nc4 -File).Count
  Write-Host "$dir : $count files"
  if ($count -ne 300) { throw "Expected 300 files, found $count in $dir" }
}
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m services.nasa_preflight_cli --directory $imerg --product gpm_3imergm_07_final --country BGD
.\.venv\Scripts\python.exe -m services.nasa_preflight_cli --directory $gldas --product gldas_noah025_m_2_1_soil0_10 --country BGD
```

## Create the second verified research record (only if missing)
```powershell
# Run from backend directory in the same PowerShell where $imerg and $gldas were set.
.\.venv\Scripts\python.exe -m services.research_workspace_cli build `
 --directory $imerg `
 --product gpm_3imergm_07_final `
 --countries BGD `
 --database .\no-push\research\earthtrend.sqlite3 `
 --export-json .\no-push\research\imerg_bgd.json

.\.venv\Scripts\python.exe -m services.research_storage `
 --database .\no-push\research\earthtrend.sqlite3 `
 --backup .\no-push\research\earthtrend_backup_increment11.sqlite3
```
The original GLDAS study already exists according to the user's Windows output. Do not overwrite the database or delete that study. Do not publish unreviewed records.

## Frontend
```powershell
cd D:\Hackathon\Nasa\Bangladesh-Earth-Trend-Explorer\frontend
npm test
npm run build
npm audit --omit=dev
```
Check the audit's advisory details before updating dependencies; never run `npm audit fix --force` blindly. Vite's 500-kB JS bundle warning is a performance issue, not a build failure; code-splitting should be evaluated as a separate change.

## API verification
In the backend terminal with an approved existing database:
```powershell
$db = (Resolve-Path '.\no-push\research\earthtrend.sqlite3' -ErrorAction Stop).Path
$env:EARTH_TREND_RESEARCH_DB = $db
$env:EARTH_TREND_RESEARCH_PUBLIC = '1'
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```
In another terminal:
```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/api/research/status'
Invoke-RestMethod 'http://127.0.0.1:8000/api/research/history?limit=10'
```
Expected two records only after IMERG is successfully built and approved.

## Scientific caveat
The input's monthly file presence is distinct from NetCDF validation, source provenance verification, region extent, and research record content. These existing verification stages remain mandatory.
