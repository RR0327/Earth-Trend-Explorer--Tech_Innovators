# EarthTrace — Bangladesh Earth Trend Explorer

**Phase 4: NASA Space Apps 2026 Earth System Trend Detective dashboard.** Independent team-built hackathon project, not a NASA website.

The Phase 4 dashboard preserves the Phase 3 FastAPI API, curated genuine Giovanni MERRA-2 monthly observations, annual trend engine, and scientific caveats. It adds a responsive investigation workspace, chart-period toggle, detective report, source/methodology details and JSON result export. It does not add unsupported observations, national averages or forecasts.

## Local setup (Windows 11)

In `D:\Hackathon\Nasa\Bangladesh-Earth-Trend-Explorer\backend`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

In a second terminal at `D:\Hackathon\Nasa\Bangladesh-Earth-Trend-Explorer\frontend`:

```powershell
npm install
npm run test
npm run build
npm run dev
```

Navigate to http://127.0.0.1:5173. API documentation: http://127.0.0.1:8000/docs.

Set `VITE_API_URL` to a deployed API origin when deploying the frontend and set `CORS_ORIGINS` on the API to the deployed frontend URL. The Vite build will contain the value of the variable present **at build time**.

## Ethical and scientific safeguards

- The included MERRA-2 T2M data cover a **selected eastern Bangladesh study area**, not Bangladesh as a whole.
- Original Giovanni exports and operational phase guides live in `backend/no-push` and `frontend/no-push` and are ignored by Git.
- The specifically approved, curated CSV and JSON in `backend/data` are tracked by `.gitignore` exceptions.
- The 2000–2024 trend excludes partial 2025. A positive fitted slope is **not statistically significant** (Mann-Kendall p > 0.05).
- Source metadata were user supplied. The application does not independently authenticate data downloads.
- Statistical trend tests remain exploratory and do not correct for all temporal dependence or other climate-model uncertainties.

## Development-only reference files

- `backend/no-push/PHASE_3_BACKEND_GUIDE.md`
- `backend/no-push/PHASE_3_FULL_REPLACEMENT_FILES.md`
- `frontend/no-push/PHASE_4_FRONTEND_GUIDE.md`
- `backend/no-push/PHASE_4_VERIFICATION_GUIDE.md`

## Original challenge

[NASA Space Apps 2026: Be An Earth System Trend Detective!](https://www.spaceappschallenge.org/2026/challenges/earth-system-trend-detective/)


## Phase 5 — Public, responsive interface and regression hardening

EarthTrace is a **public, read-only** scientific dashboard. No authentication, account, or payment is required; the API intentionally exposes only `GET` endpoints. Users can select authentic, curated NASA datasets and view evidence-derived statistics. Editing/importing observations is an offline operator workflow, not a public HTTP endpoint.

The frontend now offers a persistent dark/light appearance toggle (respecting device preference on first visit), keyboard skip navigation, a responsive mission navbar, a research-focused footer, and readable research caveats. `src/theme.mjs` never changes NASA observations or statistical output.

Scientific limitations remain: a small selected MERRA-2 grid region is **not Bangladesh's national mean**; January 2025 is excluded from complete-year analysis; a Mann-Kendall p-value greater than 0.05 **does not establish significance**. See `backend/no-push/PHASE_5_BACKEND_GUIDE.md` and `frontend/no-push/PHASE_5_FRONTEND_GUIDE.md` for local-only Windows commands and manual device checks.


## Phase 6 — release architecture

**Public website:** React/Vite on Vercel (`frontend/`), no authentication or personal data collection. **Public read-only API:** FastAPI on Render (`backend/`). **Curated scientific data:** reviewed `backend/data/merra2_selected_area_temperature_2000_2025.{csv,json}` included in version control. Raw Giovanni exports and development documentation remain under ignored `no-push/` folders.

### Production configuration

* Backend: `APP_ENV=production`, `CORS_ORIGINS=https://your-actual-frontend.vercel.app` (required), and Render start command `uvicorn main:app --host 0.0.0.0 --port $PORT`.
* Frontend: `VITE_API_URL=https://your-actual-backend.onrender.com` (required for real production API calls). Vite exposes this public URL in the compiled frontend; do not put secrets in `VITE_` variables.
* Readiness endpoint: `GET /api/ready` returns HTTP 200 only if the reviewed 301-observation dataset is present and parseable. Deploy health check should point to `/api/ready`.
* API smoke test: from the `backend` directory run `python scripts/smoke_check.py https://your-actual-backend.onrender.com`.
* Windows 11 operation details: `backend/no-push/PHASE_6_BACKEND_GUIDE.md` and `frontend/no-push/PHASE_6_FRONTEND_GUIDE.md`.

The analysis applies **only to the narrowly sampled eastern Bangladesh study area** (not national Bangladesh). Mann-Kendall significance is exploratory; serial autocorrelation is not corrected. Partial-year 2025 is excluded. No runtime NASA API lookup occurs; data are approved curated observations. Deployment and live cloud uptime must be verified separately.
