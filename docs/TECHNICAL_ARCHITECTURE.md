# Architecture — EarthTrace

```
Browser (React/Vite, public)
  ├── Curated study-area dashboard   GET /api/datasets/{id}/trend
  ├── Global region setup            GET /api/regions, bbox picker
  ├── POWER point T2M                GET /api/nasa-power/point → NASA POWER HTTPS fixed host
  ├── Giovanni CSV investigation     POST /api/explore (in memory)
  ├── Two-series comparison          POST /api/compare (in memory)
  ├── JSON/CSV export                browser Blob download
  └── PDF handoff                    browser print / Save as PDF

FastAPI (public, read-only curated store)
  ├── services/dataset_store.py      validated curated monthly series and metadata
  ├── services/trend_analyzer.py     annual regression, Kendall, Sen and CI
  ├── services/exploration.py        strict visitor input and unit conversions
  ├── services/regions.py            approximate bbox preset reference
  ├── services/nasa_power.py         fixed-domain, bounded live monthly point fetch
  └── services/release_checks.py    integrity / deployment readiness
```

### Security and provenance

No authentication. `/api/explore` and `/api/compare` accept bounded JSON; do not persist payloads. NASA POWER host is fixed in source to prevent SSRF, request period and coordinates validated and response size bounded. Enforce allowed frontend origins in production; no API keys stored in frontend. NASA POWER public endpoint may rate limit; add per-IP rate limiting or caching if traffic increases. `no-push/` and local `.env` files are Git-ignored.

### Next-generation architecture (not implemented)

For polygon-based country-wide aggregation, ingest gridded NetCDF via Xarray, mask cells by authoritative boundary geometry (Natural Earth/GADM/etc with license review), apply per-cell intersection and area weights, then derive valid monthly series. Store provenance, normalized observations, spatial mask, aggregation method, coverage and source version. This would require a dedicated processing service or queued jobs, not just plotting a country bbox.
