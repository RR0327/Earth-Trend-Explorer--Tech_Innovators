# Increment 6 - Secure Research Publication, History, Comparison Evidence, and PDF Reports

## Scope and security model

This increment extends the authentic NASA NetCDF-to-SQLite research workflow from Increment 5. It does **not** introduce a public upload or write API. The backend still requires an administrator to acquire trusted NASA files, run the validated batch CLI, and explicitly select a previously vetted SQLite archive for publication. This limits anonymous visitors to read-only research access and preserves the no-authentication architecture.

- `EARTH_TREND_RESEARCH_PUBLIC=1` is required for publication; absent or zero means the endpoints return `503`.
- `EARTH_TREND_RESEARCH_DB` is the absolute path of the reviewed, durable SQLite database. The service uses SQLite read-only mode.
- The public API never executes NetCDF ingestion or writes to the database. It does not accept arbitrary source paths.
- A loaded record is verified against its content-addressed SHA256 ID; corrupt or modified records are refused.
- `GET /api/research/history?limit=20&offset=0`: paginated list of vetted research records. Maximum page size 50.
- `GET /api/research/{64-character-sha256}`: complete validated research JSON, including source-file hashes and limitations.
- `GET /api/research/{64-character-sha256}/report.pdf`: dynamically generated scientific PDF from the immutable record.

## Methodological honesty

The report contains recorded product, region, observation coverage, annual regression/Mann-Kendall/Sen statistics where calculable, a vector annual observation plot, evidence hashes, reproducibility identifier, limitations, and caveats on inferred causation. It does not add a new climate observation or infer national means from point data. Reports are generated only from records saved by the trusted local workflow.

The browser comparison chart plots two series over the *actual shared complete years* returned by the comparison API. A visual difference between slopes is not an inferential test of between-region difference.

## Privacy and publication policy

The public database must be reviewed *before* publication: archived records include region descriptions and declared source filenames, URLs and science provenance. Never publish private paths, team credentials, or personal datasets. Anonymous users can read approved records but cannot create or alter them via the website. Administrators continue to manage the research archive using Windows/local CLI access.

## Production persistence

SQLite files are excluded from Git. A database stored on an ephemeral Render filesystem is not durable. Mount an appropriate persistent disk (where supported by your hosting plan), backup the archive independently, and configure `EARTH_TREND_RESEARCH_DB` to its absolute mounted path. On Vercel, the public frontend only calls the backend API. Do not add database secrets to `VITE_` variables.

If durable storage is not configured, leave research publication disabled; the rest of EarthTrend Detective continues to operate. No promise of production persistence is made by this code alone.

## Deferred master-specification requirements

This increment does not yet implement a public job submission queue, authentication-based administrator UI, PostGIS/managed PostgreSQL, actual country-wide autonomous NASA extraction, map raster layers, external AI inference, collaborative projects, or all Version 2 report formats. The official Section 31 future enhancements remain deferred.
