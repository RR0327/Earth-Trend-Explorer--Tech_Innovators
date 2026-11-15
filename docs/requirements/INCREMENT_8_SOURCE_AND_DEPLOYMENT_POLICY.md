# Increment 8: Source and Deployment Policy

- Public FastAPI is read-only for saved research; no database writes or untrusted NetCDF uploads through the browser.
- Original NASA download scripts and URL manifests are retained in `backend/no-push/nasa-downloads`, not copied into GitHub/Render/Vercel. These are collection aids, not application dependencies.
- Existing curated MERRA-2 observations are unchanged and may be served from approved tracked files.
- Real IMERG/GLDAS research records are created from real validated NetCDF and published from reviewed persistent SQLite; research availability endpoints do not invent regions or observations.
- The new explanation function is deterministic and based on stored numerical results. This is not an LLM integration and must not be represented as one.
- Production persistence on Render requires an actual persistent disk and database migration/backup plan. GitHub is source control, not a database or a raw-data warehouse.
- Authentication failures must be corrected with a valid user-owned Earthdata Login, never by hardcoding credentials or bypassing access controls.
- Submitted NASA Space Apps snapshot and Section 31 backlog remain unchanged.
