# EarthTrend Detective

### Explore Earth. Investigate environmental change. Follow the evidence.

**EarthTrend Detective** is an open, web-based environmental research application that turns NASA Earth science observations into transparent, reproducible trend investigations. It combines a responsive geographic exploration interface with scientific time-series analysis, regional comparison, source provenance, and a searchable library of approved research studies.

Built as an independent **NASA Space Apps Challenge** project, EarthTrend Detective helps students, researchers, educators, and interested citizens investigate **what is changing, where it is changing, how large the change is, and what statistical evidence supports the result**.

> **Independent project:** EarthTrend Detective is not an official NASA website or NASA-endorsed service. Data product names and attributions identify their scientific sources. Statistical associations should not be interpreted as proof of causation.

## Live application

| Service              | URL                                                            |
| -------------------- | -------------------------------------------------------------- |
| **Website (Vercel)** | **https://earth-trend-explorer-tech-innovator.vercel.app/**    |
| API documentation    | https://earth-trend-explorer-tech-innovators.onrender.com/docs |

The website URL is the published project address. Availability of the Render service, saved research history, and live extraction depends on the active deployment and its configured data storage. Some research capabilities described below are available in a properly configured local installation but are not automatically enabled on the hosted application.

## Why EarthTrend Detective?

Environmental datasets are often distributed as technical files, complex gridded products, or time series that are difficult for non-specialists to interpret. A chart alone cannot establish whether a region is represented accurately, whether units have been converted correctly, or whether the underlying trend is statistically meaningful.

EarthTrend Detective bridges this gap through a traceable workflow:

1. **Choose a dataset and study area.** Explore supported country boundaries, enter a bounded geographic rectangle, or select a curated study.
2. **Access real observations.** Use the included reviewed MERRA-2 example, inspect approved published research, upload a supported monthly time-series export, retrieve an available NASA POWER point series, or analyze administrator-approved local NetCDF grids.
3. **Validate the inputs.** Check product identity, variables, native units, observation dates, coverage, and the requested geography as applicable.
4. **Calculate trends.** Aggregate valid monthly records into complete years and apply documented trend statistics.
5. **Explore the evidence.** Review time-series charts, regional comparisons, observations, statistical summaries, limitations, and provenance metadata.
6. **Share reproducible results.** Export data and analysis results, access approved research history, and generate PDF reports for published studies.

The application does **not** fill missing observations with invented values or present a point measurement as a country-wide average.

## Features

### Environmental data exploration

- Responsive dashboard for desktop, tablet, and mobile, with accessible navigation and light/dark themes.
- Curated **NASA MERRA-2** near-surface air temperature series for a specifically bounded study area in Bangladesh.
- **NASA GPM IMERG** precipitation and **NASA GLDAS** soil-moisture analysis using downloaded gridded NetCDF files.
- Supported monthly NASA Giovanni-style time-series import for exploratory analysis, with clear distinctions between imported, curated, and operator-reviewed datasets.
- Optional live **NASA POWER** temperature investigation for a geographic **point**; results depend on NASA POWER availability.
- Interactive country boundaries derived from bundled Natural Earth geometry and user-selected bounded study areas.

### Scientific analysis and visualization

- Monthly observations, annual summaries, long-term trend plots, and monthly climatology.
- Linear regression, Sen's slope with confidence interval, and Kendall/Mann–Kendall-style trend evidence.
- Regional time-series comparison aligned by **actual common years**, not chart array position.
- Product-aware NetCDF reading, including IMERG's nested `Grid` group and GLDAS's root-level variables.
- Geographic coverage checks, gridded study-area extraction, source metadata, and explicit limitations.
- Transparent, evidence-grounded explanations of approved stored research statistics, rather than invented measurements.
- JSON/CSV export, printable browser output, and server-generated PDF reports for published studies.

### Research library and data safeguards

- Reproducible, content-addressed research records stored in SQLite by a trusted local research workflow.
- Optional **read-only** publication of reviewed studies through the FastAPI backend.
- Research history, study details, geographic availability, explanations, and downloadable reports.
- Browser-driven extraction restricted to **administrator-approved NetCDF collections**. Visitors cannot submit arbitrary server paths or permanently write research records through the public API.
- Resource limits and scientific coverage validation for public extraction. The complete 25-year, 300-file product collections should be processed using the **offline research CLI**; the bounded public extraction endpoint is designed for smaller approved file sets.

## Scientific data sources

| NASA product        | Environmental variable                       | How the application uses it                                                                                       |
| ------------------- | -------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **MERRA-2**         | Near-surface air temperature (`T2M`)         | Included curated selected-area Giovanni demonstration; can also be processed from supported local gridded sources |
| **GPM IMERG V07**   | Precipitation (`precipitation`)              | Validated monthly NetCDF-based research and regional precipitation trends                                         |
| **GLDAS Noah V2.1** | 0–10 cm soil moisture (`SoilMoi0_10cm_inst`) | Validated monthly NetCDF-based research and regional soil-moisture trends                                         |
| **NASA POWER**      | Point-based near-surface temperature         | Optional live HTTPS query; not a polygon-based national average                                                   |
| **Natural Earth**   | Country boundary geometry                    | Country identification and geographic selection; not an observation dataset                                       |

The repository contains a curated MERRA-2 sample. The full downloaded IMERG and GLDAS NetCDF collections, research database, and personal acquisition files are deliberately **not committed to GitHub**. A fresh clone can run the dashboard and included sample without them. To reproduce extended research results locally, obtain and validate the appropriate source datasets using your own NASA Earthdata access.

**Scientific limitations:** Gridded coverage depends on the actual source subset; a Bangladesh subset cannot support an unsupported global analysis. Monthly files must have compatible product metadata, valid temporal coverage, and suitable spatial resolution. Significance tests are descriptive evidence and do not automatically correct for serial autocorrelation or establish a causal mechanism. External dataset authenticity requires reviewing the original acquisition evidence in addition to local NetCDF structural validation.

## Technology stack

| Layer                 | Technologies                                                    |
| --------------------- | --------------------------------------------------------------- |
| Frontend              | React 18, Vite, JavaScript, CSS, Recharts, Lucide icons         |
| Backend               | Python, FastAPI, Uvicorn                                        |
| Scientific processing | NumPy, SciPy, xarray, netCDF4, Shapely                          |
| Research persistence  | SQLite with integrity checking and backup tooling               |
| Report generation     | ReportLab                                                       |
| Quality assurance     | pytest, Node.js built-in test runner, production frontend build |
| Hosting               | Vercel (frontend), Render (backend)                             |

## System architecture

```text
                         ┌──────────────────────────────┐
                         │ Browser / React + Vite       │
                         │ Dashboard · Explore Earth    │
                         │ Grid Lab · Research Library  │
                         └──────────────┬───────────────┘
                                        │ HTTPS / JSON
                         ┌──────────────▼───────────────┐
                         │ Python FastAPI               │
                         │ Read-only data/catalog APIs  │
                         │ Trend & scientific validation│
                         └───┬──────────┬──────────┬────┘
                             │          │          │
                  ┌──────────▼──┐  ┌────▼─────┐  ┌─▼────────────────┐
                  │ Curated      │  │ NASA     │  │ Approved local   │
                  │ MERRA-2 data │  │ POWER    │  │ NetCDF source    │
                  └──────────────┘  └──────────┘  └──────┬───────────┘
                                                          │
                                                Validated extraction
                                                          │
                                                ┌─────────▼─────────┐
                                                │ Research workflow │
                                                │ SQLite + PDF      │
                                                │ approved records  │
                                                └───────────────────┘
```

The trusted **offline research workflow** handles larger NetCDF collections and persists reviewed records. Public publication serves approved database records without allowing anonymous database writes. Bounded live grid extraction, when explicitly enabled and supplied with approved datasets, returns computed results without persisting them.

## Repository structure

```text
Bangladesh-Earth-Trend-Explorer/
├── backend/
│   ├── main.py                    # FastAPI application and API routes
│   ├── requirements.txt           # Python dependencies
│   ├── services/                  # Trend analysis, validation, research services
│   ├── reference_data/            # Bundled geographic reference boundaries
│   ├── data/                      # Reviewed curated MERRA-2 example
│   ├── tests/                     # Backend regression and scientific tests
│   └── no-push/                   # Local NASA downloads, SQLite, private files
├── frontend/
│   ├── src/                       # React UI, visualizations, client-side tests
│   ├── package.json
│   ├── vite.config.js
│   └── .env.example
├── scripts/
│   ├── start-research-api.ps1      # Local reviewed-database launcher
│   └── verify-release.ps1         # Local API and research smoke test
├── docs/                         # Architecture and scientific documentation
├── render.yaml                    # Render configuration
└── README.md
```

`no-push/`, local `.env` files, virtual environments, build artifacts, raw downloads, and SQLite databases are excluded by `.gitignore`. Do not force-add them to Git.

## Requirements

- **Python 3** with support for the versions specified in `backend/requirements.txt` (a current supported Python 3 release is recommended).
- **Node.js and npm** compatible with the repository's React/Vite version.
- Git and an internet connection to install dependencies.
- Windows PowerShell for the provided convenience scripts; the Python backend and Vite frontend can also be started manually on macOS or Linux.
- Optional: NASA Earthdata Login and validated NetCDF files for reproducing large-scale IMERG/GLDAS research.

## Run locally

### 1. Obtain the repository

Clone your published repository, or extract the supplied project archive. From the project directory:

```powershell
cd Bangladesh-Earth-Trend-Explorer
```

> Use the actual location of the checked-out repository. This README intentionally does not assume a particular GitHub repository owner or clone URL.

### 2. Set up the backend

Open **PowerShell terminal A**:

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

On macOS/Linux, replace the Python executable with `.venv/bin/python` after creating the environment with `python3 -m venv .venv`.

The API will be available at:

- http://127.0.0.1:8000/api/health
- http://127.0.0.1:8000/api/ready
- http://127.0.0.1:8000/docs

**This default setup serves the curated dataset and standard public APIs.** An approved research database is optional and is not created automatically.

### 3. Set up the frontend

Open **PowerShell terminal B**, from the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open **http://127.0.0.1:5173/** in a browser. Local development automatically uses `http://127.0.0.1:8000` when `VITE_API_URL` is not set.

### 4. Run the tests

From `backend/`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

From `frontend/`:

```powershell
npm test
npm run build
```

`npm run build` produces deployable static frontend files in `frontend/dist/`. Review `npm audit` findings before upgrading major build-tool versions; avoid exposing the Vite development server publicly.

## Reproduce and publish local NASA research (optional)

Use this workflow only if you have obtained suitable NASA monthly `.nc` or `.nc4` products and preserved their original acquisition information. The commands below assume you are in `backend/` and the two dataset folders already contain validated, monthly downloads.

### 1. Validate the data

```powershell
$imerg = ".\no-push\nasa-downloads\IMERG\<your-IMERG-data-folder>"
$gldas = ".\no-push\nasa-downloads\GLDAS\<your-GLDAS-data-folder>"

.\.venv\Scripts\python.exe -m services.nasa_preflight_cli `
  --directory $imerg `
  --product gpm_3imergm_07_final `
  --country BGD

.\.venv\Scripts\python.exe -m services.nasa_preflight_cli `
  --directory $gldas `
  --product gldas_noah025_m_2_1_soil0_10 `
  --country BGD
```

Replace the placeholder folder names with the actual local directories. Use a country supported by the source grid; a request whose spatial coverage does not match the data will be rejected.

### 2. Build reproducible research records

```powershell
New-Item -ItemType Directory -Force ".\no-push\research" | Out-Null

.\.venv\Scripts\python.exe -m services.research_workspace_cli build `
  --directory $imerg `
  --product gpm_3imergm_07_final `
  --countries BGD `
  --database ".\no-push\research\earthtrend.sqlite3" `
  --export-json ".\no-push\research\imerg_bgd.json"

.\.venv\Scripts\python.exe -m services.research_workspace_cli build `
  --directory $gldas `
  --product gldas_noah025_m_2_1_soil0_10 `
  --countries BGD `
  --database ".\no-push\research\earthtrend.sqlite3" `
  --export-json ".\no-push\research\gldas_bgd.json"
```

These commands process the actual scientific datasets, generate study observations and trends, and store content-addressed records. If a record already exists, the storage layer handles its digest rather than manufacturing duplicates.

### 3. Check SQLite integrity and create a backup

```powershell
.\.venv\Scripts\python.exe -m services.research_storage `
  --database ".\no-push\research\earthtrend.sqlite3" `
  --backup ".\no-push\research\earthtrend_verified_backup.sqlite3"
```

Use a new filename for each subsequent backup. Store backups outside the public Git repository and verify that a restore is possible.

### 4. Start the backend with approved research history

In a **new terminal**, from the project root:

```powershell
.\scripts\start-research-api.ps1
```

The launcher checks that the database already exists and passes integrity verification; it does **not** create the scientific records. If local PowerShell policy blocks scripts, inspect and trust the file before using a **process-scoped** execution policy, or start Uvicorn directly with `EARTH_TREND_RESEARCH_DB` and `EARTH_TREND_RESEARCH_PUBLIC=1` set in that same terminal.

In another terminal, from the project root:

```powershell
.\scripts\verify-release.ps1
```

The provided smoke test is tailored to installations with **both** reviewed IMERG and GLDAS study records; it is not required for a clean sample-only checkout.

## API reference

The interactive OpenAPI documentation is available at **`/docs`**. Key endpoints include:

| Method | Endpoint                                  | Purpose                                               |
| ------ | ----------------------------------------- | ----------------------------------------------------- |
| GET    | `/api/health`                             | API health                                            |
| GET    | `/api/ready`                              | Curated dataset readiness                             |
| GET    | `/api/datasets`                           | Available curated datasets                            |
| GET    | `/api/datasets/{dataset_id}`              | Curated monthly observations and metadata             |
| GET    | `/api/datasets/{dataset_id}/trend`        | Trend analysis of a curated dataset                   |
| GET    | `/api/catalog/products`                   | Supported NASA product information                    |
| GET    | `/api/geography/countries`                | Country list and boundary references                  |
| GET    | `/api/geography/countries/{country_code}` | Boundary geometry for an ISO3 country                 |
| GET    | `/api/nasa-power/point`                   | Available NASA POWER point temperature series         |
| POST   | `/api/explore`                            | Ephemeral visitor-supplied series analysis            |
| POST   | `/api/compare`                            | Compare compatible observation series                 |
| GET    | `/api/extraction/catalog`                 | Public availability of operator-approved grids        |
| POST   | `/api/extraction/analyze`                 | Bounded extraction against approved grids, if enabled |
| GET    | `/api/research/status`                    | Published research library availability               |
| GET    | `/api/research/history`                   | Approved saved research records                       |
| GET    | `/api/research/available-regions`         | Regions supported by published studies                |
| GET    | `/api/research/{research_id}`             | Detailed approved study record                        |
| GET    | `/api/research/{research_id}/explanation` | Grounded interpretation of stored results             |
| GET    | `/api/research/{research_id}/report.pdf`  | PDF research report                                   |

Public research-library and approved-grid endpoints are **optional**, and their availability reflects configured, reviewed server-side data. No public endpoint accepts arbitrary filesystem paths or writes directly into the research database.

## Deployment

The application uses separate hosting services for the frontend and backend.

### Backend — Render

Configure the Render service for the `backend` directory:

| Setting        | Value                                                    |
| -------------- | -------------------------------------------------------- |
| Root directory | `backend`                                                |
| Build command  | `pip install -r requirements.txt`                        |
| Start command  | `uvicorn main:app --host 0.0.0.0 --port $PORT`           |
| Health check   | `/api/ready`                                             |
| `APP_ENV`      | `production`                                             |
| `CORS_ORIGINS` | `https://earth-trend-explorer-tech-innovator.vercel.app` |

For published research history, additionally provision and back up a **durable server-side database volume**. Securely transfer the reviewed SQLite database to that volume and configure:

```text
EARTH_TREND_RESEARCH_PUBLIC=1
EARTH_TREND_RESEARCH_DB=/absolute/server/path/to/earthtrend.sqlite3
```

These environment variables should only be set once the database is available and verified on Render. Paths from a local Windows PC will not exist in the Render environment. SQLite on ephemeral storage is not suitable for durable records.

Browser-based grid extraction also needs a separate, approved, server-side NetCDF data root and manifest, enabled explicitly through `EARTH_TREND_GRID_PUBLIC`, `EARTH_TREND_GRID_ROOT`, and `EARTH_TREND_GRID_MANIFEST`. Do not enable this feature without the necessary data, resource budget, and storage access controls.

### Frontend — Vercel

| Setting          | Value                                                       |
| ---------------- | ----------------------------------------------------------- |
| Root directory   | `frontend`                                                  |
| Framework        | Vite                                                        |
| Build command    | `npm run build`                                             |
| Output directory | `dist`                                                      |
| `VITE_API_URL`   | `https://earth-trend-explorer-tech-innovators.onrender.com` |

Set `VITE_API_URL` in the Vercel project environment before running the production build. The frontend intentionally does **not** fall back to a visitor's localhost API in production. Do not put secrets in variables beginning with `VITE_`.

After deployment, verify the real website, backend `/api/health` and `/api/ready`, CORS, supported dataset routes, and the availability of any optional research storage. A working local SQLite library does not imply it is present on the hosted backend.

## Security and data governance

- **Public, no-account design:** Core public features do not require user registration. Public analysis inputs are bounded and transient.
- **Read-only publication:** Administrative research creation and curation occur offline; visitors cannot write approved studies.
- **Data quality:** Unsupported sources, inconsistent units, inadequate spatial coverage, malformed records, and incomplete trend periods are rejected or explicitly qualified.
- **Source traceability:** Reports and study records identify product/version, study area, supported temporal coverage, methodology, and limitations.
- **Filesystem protection:** Private NASA downloads, Earthdata credentials, original manifests, research databases, exports, and backups remain outside source control.
- **Frontend safety:** Build only with public API URLs; do not expose `npm run dev` to the Internet.
- **Operational responsibility:** Production operators must provide durable storage, backup/restore verification, access controls for approved source files, and monitoring appropriate to traffic.

## Documentation

Further technical and scientific details are available in `docs/`, in the source-code docstrings, and through the FastAPI OpenAPI documentation at `/docs`.

## Acknowledgments

EarthTrend Detective uses data and reference materials from **NASA Earth science programs**, NASA Giovanni, NASA POWER, and **Natural Earth** geographic boundaries. The project was developed independently for the NASA Space Apps Challenge. Data remain subject to their respective source acknowledgments, terms, quality notes, and citations.


## Super Intelligence (SI) Use Disclosure

Team Tech_Innovators used ChatGPT and AI-assisted tools for project ideation, technical research, software development, debugging, automated testing, interface design, documentation, and presentation preparation.

The environmental observations used in EarthTrend Detective originate from NASA MERRA-2, GPM IMERG, and GLDAS datasets. The team used Python-based scientific processing methods for statistical analysis rather than generating artificial environmental measurements.

AI-assisted code and content were incorporated into the project's development workflow. The demonstration presentation is visibly identified as SI-assisted. The team retains responsibility for the accuracy, review, attribution, and originality of the submitted work.
---

**EarthTrend Detective** — _From satellite-informed observations to transparent environmental insight._
