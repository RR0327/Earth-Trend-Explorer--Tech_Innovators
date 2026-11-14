# EarthTrace | Earth System Trend Detective

**NASA-powered, public environmental trend investigation** — independent NASA Space Apps Challenge project, not an official NASA site.

EarthTrace uses authentic NASA Earth science observations to answer: **what is changing, where, by how much, and is the observed trend statistically significant?**

### What works

- Responsive React dashboard (desktop top navigation, mobile hamburger), persistent light/dark theme, reduced-motion-friendly animated Earth hero.
- NASA Giovanni MERRA-2 **selected-area** curated temperature demonstration: 301 monthly records, 2000–2024 complete annual years; January 2025 is stored but excluded from annual results.
- Global geographic bounding-box presets, numeric W/S/E/N editing, schematic box-drawing map; these are **not country polygons** and selecting a box does not produce a national average.
- **Live NASA POWER point temperature (T2M)** analysis at the selected box center (2001–2024). Returns a point/grid series, **not an area average**. Availability depends on the external NASA POWER service; no synthetic observations are substituted on failures.
- Visitor-uploaded NASA Giovanni monthly time-series files for temperature (MERRA-2), precipitation (GPM IMERG), or soil moisture (GLDAS), subject to real product and unit compatibility and actual source coverage. Visitor provenance is not independently authenticated, and uploads are not stored.
- Annual linear regression, Sen's slope and 95% CI, Kendall/Mann–Kendall-style two-sided rank p-value; full calendar years only and uncorrected for serial autocorrelation.
- Seasonal monthly climatology, annual and monthly charts, JSON/CSV export, browser Print → Save as PDF, and comparison of two uploaded compatible real series over shared complete years.
- No user accounts. Public read-only curated datasets; ephemeral visitor analysis.

### Scientific boundaries

**Not implemented:** country-boundary polygon extraction of raw gridded NASA datasets, unattended on-demand Giovanni/GLDAS/IMERG extraction for arbitrary shapes, true country-wide climate maps or layers, an autonomous AI interpretation service, stored history, GIS-grade global country polygons, or server-created research PDF files. The current map is a schematic region-selection canvas, not an Earth-observation raster. Selecting Brazil, for example, is a configuration step; for a region mean you must supply real Brazil observations from Giovanni. The live NASA POWER button instead retrieves an actual **point** record at the selected center.

Do not describe NASA POWER point readings as NASA Giovanni area averages, national means, or raw satellite measurements. Statistical tests establish trend evidence, not causation.

### Local Windows 11 installation

Backend PowerShell (`D:\Hackathon\Nasa\Bangladesh-Earth-Trend-Explorer\backend`):

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Frontend PowerShell (`D:\Hackathon\Nasa\Bangladesh-Earth-Trend-Explorer\frontend`):

```powershell
npm install
npm test
npm run build
npm run dev
```

Browser: http://127.0.0.1:5173 — API docs http://127.0.0.1:8000/docs.

### Deployment

- Backend: Render, root `backend`, build `pip install -r requirements.txt`, start `uvicorn main:app --host 0.0.0.0 --port $PORT`, health `/api/ready`.
- Frontend: Vercel, root `frontend`, build `npm run build`, output `dist`.
- Set `APP_ENV=production`, `CORS_ORIGINS=https://earth-trend-explorer-tech-innovator.vercel.app` on Render (edit when your frontend address changes).
- Set `VITE_API_URL=https://earth-trend-explorer-tech-innovators.onrender.com` on Vercel, then redeploy.
- The public NASA POWER request requires outbound HTTPS to `power.larc.nasa.gov`. Confirm actual data availability after deployment; tests use deterministic fixtures, not live internet.
- Push only reviewed curated `.csv/.json`; raw NASA downloads, logs, Markdown replacement guides, and temporary work remain in ignored `backend/no-push/` and `frontend/no-push/`.

Live website: https://earth-trend-explorer-tech-innovator.vercel.app/

### API

`GET /api/health`, `/api/ready`, `/api/variables`, `/api/datasets`, `/api/datasets/{id}`, `/api/datasets/{id}/trend`, `/api/regions?q=Brazil`, `/api/nasa-power/point?latitude=-15&longitude=-47&start_year=2001&end_year=2024`; `POST /api/explore` (JSON visitor observations); `POST /api/compare` (two compatible JSON series). Details in FastAPI `/docs`.

### Traceability

`docs/GLOBAL_RELEASE_SCOPE_AND_LIMITATIONS.md`, `docs/TECHNICAL_ARCHITECTURE.md`, and the ignored local verification/replacement instructions. The previous contest submission ZIP must remain unchanged and archived separately.
