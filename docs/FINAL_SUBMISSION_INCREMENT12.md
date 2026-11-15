# EarthTrend Detective — Increment 12: deadline-safe submission handoff

## Verified from the user's local logs (not independently rerun with their data)
- 300 IMERG monthly NetCDF files and 300 GLDAS monthly NetCDF files are present.
- Both products passed local scientific preflight and generated separate content-hashed SQLite research records.
- SQLite integrity and backup passed with **2** research records.
- Frontend 61 Node tests passed; Vite production build previously passed after the CSS `@import` fix.
- Previous research APIs returned HTTP 200 when Uvicorn was running.

## Correct the reported connection refused error
The API was stopped with Ctrl+C. It cannot respond until Uvicorn runs. From the repository root in PowerShell:

```powershell
.\scripts\start-research-api.ps1
```
Leave that terminal running. In another terminal:

```powershell
.\scripts\verify-release.ps1
```

The launcher verifies a real, existing SQLite file before opting into publication. It never creates synthetic studies or modifies the database. This script is for local development **only**; it binds to 127.0.0.1.

## Backend and frontend acceptance

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
cd ..\frontend
npm test
npm run build
npm audit
```

If the audit flags Vite/esbuild, do not run `npm audit fix --force` before submission. Review the specific advisory and test a major-version upgrade on a separate branch. Never expose a Vite development server to the public Internet. The published Vercel frontend is a static production build, not a Vite development server.

## Source-control safeguards
- Keep `backend/no-push/`, `frontend/no-push/`, `*.sqlite3`, `.env`, `.netrc`, and downloaded NASA files private.
- Keep original NASA MERRA-2 observations, metadata and submitted NASA Space Apps snapshot immutable.
- Verify with `git status --short` and `git check-ignore backend/no-push/research/earthtrend.sqlite3`.
- Research SQLite is **not** in GitHub. A Render deployment built from GitHub will not automatically contain the two local studies.

## Production deployment is a separate acceptance gate
- A clean Vercel static build and Render FastAPI deployment can serve existing curated MERRA-2 content with appropriate environment variables.
- To serve saved IMERG/GLDAS records on Render, provision durable storage, securely copy the approved SQLite (or migrate to a managed database), set `EARTH_TREND_RESEARCH_DB` to its absolute **server-side** mount path and `EARTH_TREND_RESEARCH_PUBLIC=1`, validate integrity, and confirm the APIs.
- Never copy or assume local Windows paths work on Render.
- Public live extraction also requires independently mounted, operator-approved gridded NASA files; do not claim live geographic extraction when approved datasets are absent on the server.
- Review CORS_ORIGINS and VITE_API_BASE_URL before deploying. Protect downloaded source data from Git and static web routes.
- Keep Section 31 deferred. Do not modify the immutable submitted snapshot.

## Scientific reproducibility
The local 300-month IMERG and GLDAS studies were confirmed by the user's Windows logs. The packaged repository does not include their multi-gigabyte raw data or private SQLite database. Data authenticity claims remain limited to what source manifests and product validation support.
