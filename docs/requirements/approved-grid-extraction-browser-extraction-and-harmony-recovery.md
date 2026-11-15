# Increment 9 — approved grid browser research and NASA Harmony recovery

## Baseline and data integrity
- Built on Increment 8. Original curated MERRA-2 CSV and metadata are unchanged.
- Original NASA Space Apps submission snapshot is NOT modified, included as a separate immutable artifact if present in the prior package.
- This is an opt-in system. No NetCDF files, downloads, SQLite database, passwords, or local-only instructions are committed to GitHub.
- Section 31 future enhancements deferred.

## Implemented
- `/api/extraction/catalog` lists operator-approved local datasets, never arbitrary NASA URL claims.
- `/api/extraction/analyze` accepts a validated country ISO3 or bounded rectangle, loads only operator-approved files and returns observations, trends, coverage and limitations.
- `GridWorkspace.jsx` provides responsive browser UI for real extraction; navigation includes Grid Lab.
- Server extraction runs in an executor rather than blocking the ASGI event loop. Single extraction at a time; requests are currently synchronous from a visitor perspective.
- Research-history, reports and deterministic scientific interpretations remain read-only and available independently of this experimental on-demand extraction.
- Local-only Harmony manifest recovery utility validates existing files before attempting download and reports 404/expired-job limitations.

## Scientific and operational restrictions
- An approved NetCDF file must match the product and spatial/time extent requested. Geographic polygons are generalized Natural Earth country boundaries. Do not call a grid-cell point a national mean.
- Public extraction defaults OFF. Explicit operator approval is required for all source files.
- The current approved-grid engine has strict 120-file and 150MB limits, so a 300-month batch will NOT fit as a single request. Curate a smaller valid study subset or extend through a separately benchmarked asynchronous precomputation pipeline; never silently skip months.
- Not all Harmony URL manifests remain valid. NASA Harmony staged downloads typically expire after 30 days; a `Not Found` for job status needs new investigation/subset job. Direct URLs can also expire.
- `earthaccess.login(strategy='interactive')` is local only. Do not place credentials in Git or Vercel variables.
- SQLite publication requires an actual approved database on persistent Render disk. A mounted disk path must be independently configured in Render; simply setting env vars will not create records.
- No new live NASA observations are included. Source files from prior user local machine were NOT automatically copied into this ZIP.

## Production storage recommendation
1. Backup the approved research database and copy to secured persistent Render disk, such as `/var/data/research/earthtrend.sqlite3`, if supported by selected hosting plan.
2. Set `EARTH_TREND_RESEARCH_PUBLIC=1` and `EARTH_TREND_RESEARCH_DB` to the real mounted file path.
3. Set `EARTH_TREND_GRID_PUBLIC=1` only after placing an explicitly approved NetCDF subset into a persistent mount and creating a validated JSON manifest. `EARTH_TREND_GRID_ROOT` is the directory and `EARTH_TREND_GRID_MANIFEST` the approved registry.
4. Verify `/api/research/status`, `/api/research/history`, `/api/extraction/catalog` and `/api/ready` after deployment; check exact source coverage and avoid exposed filesystem paths.
5. Do not run Harmony download jobs during Vercel builds or ordinary Render web requests.
