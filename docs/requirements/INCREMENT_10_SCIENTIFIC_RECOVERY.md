# EarthTrend Detective — Increment 10 NASA Scientific Processing Recovery

## Root causes confirmed against `NASA.zip`
1. PowerShell expansion of 300 130+-character filenames exceeds Windows process-command-line limits. Use `--directory`.
2. IMERG Harmony precipitation is stored in `/Grid/precipitation`, with `time,lon,lat` order. Opening only the NetCDF root produces an empty `xarray.Dataset`.
3. GLDAS Noah soil moisture is a root variable `SoilMoi0_10cm_inst`, with `time,lat,lon` order. Do not incorrectly open GLDAS `/Grid`.
4. SQLite, backups and research API publication depend on successful source validation and research build; don't create a dummy database.

## Archive evidence (read-only scientific structure audit)
Prior user-provided `NASA.zip` contains **300 IMERG** and **300 GLDAS** `.nc4` files, January 2000–December 2024, with unique monthly filename IDs. HDF5 structural inspection of all 600 detected no unreadable containers. For IMERG, all 300 precipitation arrays have shape (1,51,70), and for GLDAS, all 300 soil-moisture arrays have shape (1,28,20). Example source coordinates: IMERG lat ~20.05–26.95, lon ~88.05–93.05; GLDAS lat 20.125–26.875, lon 88.125–92.875. These are *subset* grids, not proof of complete geographical coverage or quantitative correctness. This audit is not an independent NASA origin attestation or a completed xarray numeric extraction.

## Windows 11 PowerShell — execute from `backend`
```powershell
cd D:\Hackathon\Nasa\Bangladesh-Earth-Trend-Explorer\backend
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
$i = 'cc68af0e-8e65-48a7-a405-7add8a0eeba7'
$g = 'f8efd328-b615-43e9-8a35-a7308d407000'
$imerg = ".\no-push\nasa-downloads\IMERG\$i"
$gldas = ".\no-push\nasa-downloads\GLDAS\$g"
@($imerg,$gldas) | ForEach-Object { if (!(Test-Path $_)) { throw "Missing NASA source directory: $_" } }
.\.venv\Scripts\python.exe -m services.nasa_preflight_cli --directory $imerg --product gpm_3imergm_07_final --country BGD --limit 12
.\.venv\Scripts\python.exe -m services.nasa_preflight_cli --directory $gldas --product gldas_noah025_m_2_1_soil0_10 --country BGD --limit 12
.\.venv\Scripts\python.exe -m services.nasa_preflight_cli --directory $imerg --product gpm_3imergm_07_final --country BGD
.\.venv\Scripts\python.exe -m services.nasa_preflight_cli --directory $gldas --product gldas_noah025_m_2_1_soil0_10 --country BGD
New-Item -ItemType Directory -Force '.\no-push\research' | Out-Null
.\.venv\Scripts\python.exe -m services.research_workspace_cli build --directory $imerg --product gpm_3imergm_07_final --countries BGD --database '.\no-push\research\earthtrend.sqlite3' --export-json '.\no-push\research\imerg_bgd.json'
.\.venv\Scripts\python.exe -m services.research_workspace_cli build --directory $gldas --product gldas_noah025_m_2_1_soil0_10 --countries BGD --database '.\no-push\research\earthtrend.sqlite3' --export-json '.\no-push\research\gldas_bgd.json'
.\.venv\Scripts\python.exe -m services.research_storage --database '.\no-push\research\earthtrend.sqlite3' --backup '.\no-push\research\earthtrend_backup_increment10.sqlite3'
$db=(Resolve-Path '.\no-push\research\earthtrend.sqlite3' -ErrorAction Stop).Path
$env:EARTH_TREND_RESEARCH_DB=$db
$env:EARTH_TREND_RESEARCH_PUBLIC='1'
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```
In a **second** PowerShell terminal:
```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/api/research/status'
Invoke-RestMethod 'http://127.0.0.1:8000/api/research/history?limit=10'
Invoke-RestMethod 'http://127.0.0.1:8000/api/research/available-regions'
```

## Important precautions
- Verify actual `.nc4` downloads are under the job-ID directories, **not** `verified-2026` unless you deliberately created that name.
- `--directory` is local/offline and will enumerate at most 500 files; it does not bypass scientific coverage/units/duplicate-month requirements.
- Full processing may fail if NASA subset excludes a portion of the requested country. Correct the study geometry or acquire a complete source. Never disable the coverage check.
- Preserve all original observations, original NASA download files, four manifests/scripts, original immutable hackathon submission ZIP and existing frontend. Section 31 remains deferred.
- On Render, an approved persistent research DB and source-data mount must be provisioned explicitly. Do not publish NASA credentials, raw NetCDF, or local SQLite through GitHub.
- The environment that prepared this increment lacked netCDF4/h5netcdf to execute full xarray extraction on the authentic NetCDF4 files. Windows extraction and report acceptance must still be performed, despite the structural evidence and synthetic automated tests.
