# EarthTrace — Bangladesh Earth Trend Explorer

**NASA Space Apps Challenge 2026 | Be An Earth System Trend Detective!**

EarthTrace is an independent, public, read-only Earth-science investigation website built for the 2026 NASA Space Apps Challenge. It transforms a curated NASA Giovanni MERRA-2 2-meter air temperature time series into transparent visualizations and exploratory annual trend statistics for a **narrow selected study area in eastern Bangladesh**. It is not an official NASA website and does not show Bangladesh-wide averages.

## Public demo

- **Website:** https://earth-trend-explorer-tech-innovator.vercel.app/
- **Backend API:** https://earth-trend-explorer-tech-innovators.onrender.com/
- **API docs:** https://earth-trend-explorer-tech-innovators.onrender.com/docs
- **Challenge:** https://www.spaceappschallenge.org/2026/challenges/earth-system-trend-detective/

Live deployment URLs were supplied by the team. The public backend root responded during submission preparation; verify the complete live end-to-end experience before final judging.

## What it does

- Displays authentic, curated monthly observations from a user-supplied NASA Giovanni export.
- Switches between the monthly temperature series and annual values with a fitted regression line.
- Calculates annual linear regression, Kendall rank/Mann-Kendall-style significance, and Theil–Sen slope with a 95% slope interval.
- Answers four questions: what is changing, where, how much, and is the trend statistically significant?
- Explains data source, selected-area coverage, excluded incomplete years, and uncertainty.
- Offers light/dark theme persistence, a responsive navbar/footer, keyboard navigation and JSON result export.
- Requires no account; the public HTTP interface is read-only.

## Demonstration dataset and findings

| Field | Verified project value |
|---|---|
| Source | NASA Giovanni, MERRA-2 M2TMNXSLV v5.12.4, T2M |
| Measure | Monthly area-averaged 2-meter air temperature |
| Original unit | Kelvin (K) |
| Curated unit | degrees Celsius (°C) |
| Monthly records | 301 (January 2000–January 2025) |
| Complete analysis years | 25 (2000–2024) |
| Excluded | 2025: only January supplied |
| Spatial extent | Requested: 90.6444–91.3915°E, 22.9127–23.5279°N; sampled grid 91.25°E, 23–23.5°N |
| Linear regression slope | +0.009723 °C/year |
| R² | 0.066665 |
| Sen slope | +0.012989 °C/year |
| Sen slope 95% interval | −0.005281 to +0.032648 °C/year |
| Kendall/MK-style p-value | 0.255372; **not statistically significant** at α=0.05 |

**Interpretation:** The fitted annual temperature direction is slightly positive within this limited sample, but evidence is insufficient to conclude a statistically significant monotonic trend at the 5% threshold. These results do not demonstrate national temperature change, identify a cause, or prove absence of change.

## Technology

- Frontend: React, Vite, Recharts, CSS, Lucide icons.
- Backend: Python, FastAPI, Pandas-free strict CSV normalization, SciPy statistical analysis.
- Hosting: Vercel (website) and Render (API).
- Data storage: small curated, version-controlled CSV and JSON files. No database or user-authentication service.

## Local execution (Windows 11)

Backend (from `backend/`):

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Frontend (from `frontend/`):

```powershell
npm install
npm test
npm run build
npm run dev
```

Development frontend: `http://127.0.0.1:5173`; backend: `http://127.0.0.1:8000`. Configure `VITE_API_URL` for Vercel and `APP_ENV=production`, `CORS_ORIGINS=<actual Vercel origin>` for Render. Do not put secrets in Vite `VITE_` environment values.

## Scientific methods and limitations

See [Scientific Methodology](docs/submission/SCIENTIFIC_METHODOLOGY.md) and [Data and Attribution](docs/submission/DATA_SOURCES_AND_ATTRIBUTION.md). The Kendall test uses the two-sided `scipy.stats.kendalltau` result (Mann-Kendall-style on annual values), **without serial-autocorrelation adjustment**, seasonality modeling, geographic weighting uncertainty, or causal attribution. The source files and provenance supplied by the project team are recorded; the application itself cannot authenticate the upstream download.

## Submission and demonstration material

- [Project submission text](docs/submission/PROJECT_SUBMISSION.md)
- [2-minute demo script and recording plan](docs/submission/DEMO_VIDEO_SCRIPT.md)
- [Presentation outline](docs/submission/PRESENTATION_OUTLINE.md)
- [Final submission and link verification](docs/submission/SUBMISSION_CHECKLIST.md)
- [Scientific methodology](docs/submission/SCIENTIFIC_METHODOLOGY.md)
- [Attribution and AI-use disclosure template](docs/submission/DATA_SOURCES_AND_ATTRIBUTION.md)

## Repository hygiene

Operational phase guides, raw NASA downloads, temporary commands and logs are kept in `backend/no-push/` and `frontend/no-push/` and excluded by `.gitignore`. The reviewed curated dataset files under `backend/data/` are explicitly allowed. No public route supports data modification.

## Ownership and acknowledgment

Developed as an independent hackathon submission by the project team. Replace the team name and member credits in the submission portal with the registered team information. NASA, Giovanni and MERRA-2 are data-source acknowledgments, **not claims of NASA endorsement**. See the attribution document for exact data details and disclosure guidance.
