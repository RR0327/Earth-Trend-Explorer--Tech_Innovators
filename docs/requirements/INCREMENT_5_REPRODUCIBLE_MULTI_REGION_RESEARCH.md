# Increment 5 — Reproducible multi-region scientific research

## Scope and relationship to the master specification

Increment 5 extends the verified Increment 4, without migrating the FastAPI application, changing its public interface, or altering the curated MERRA-2 monthly observations. It strengthens core Version 1 and Version 2 scientific requirements: multi-region extraction, geographic coverage checks, reproducible comparison, persistent research records, data provenance, and traceable results.

**Section 31 Future Enhancements is explicitly deferred.** No account system, automated updating, or advanced climate anomaly or drought claims are introduced here.

## New local, auditable research workflow

`backend/services/research_workspace.py` processes one set of researcher-provided trusted NASA NetCDF files for between 1 and 8 geographically distinct regions. For each study area it:

1. Validates the provided GeoJSON polygon or Natural Earth country boundary.
2. Verifies the *entire* study polygon is inside the supplied rectilinear grid's inferred center-derived edge envelope. Partial geographic input fails rather than silently reporting a national mean.
3. Invokes the existing product-aware batch validator: dataset identity, expected variable and units, month uniqueness, missing month audit, and SHA256 for each source file.
4. Enforces a configurable minimum monthly valid-cell area fraction (default 95%). The difference between sufficient valid-data grid coverage and actual grid geographic extent is explicitly documented.
5. Computes existing annual trend statistics only when there are at least eight complete calendar years. Insufficient-data studies retain observations but do **not** fabricate a trend.
6. Fits descriptive Sen slopes on the **intersection of complete years** across all comparable regions. This does not claim statistical significance of the difference between region slopes.
7. Generates a deterministic SHA256 `research_id` for the canonical full research result (including observations, configured regions, source hashes, methods, limitations).
8. Persists the immutable research result, indexed study summaries, and per-source provenance records into a local SQLite database. Re-running identical input is idempotent. Loaded records are verified against their original content hash.
9. Exports full JSON research snapshots for audit. Real NASA observations or research results are never fabricated or quietly interpolated.

## Important limitations

- This is a **trusted local-only** scientific processing CLI, not a public arbitrary-NetCDF upload. The API remains read-only with no unauthenticated admin or research write endpoints.
- NASA IMERG and GLDAS product definitions and file parsing are implemented; no newly uploaded authentic NASA IMERG/GLDAS source files were available to this incremental build environment. Unit and grid tests use deliberately synthetic fixtures. The user's earlier local verification is reported by the user but is not a source artifact included in this repository.
- Grid-envelope containment does not establish independent NASA authenticity, the requested region's exact geodesic area, area coverage at boundaries beyond the resolution of the product, or the absence of source-side cropping elsewhere.
- Country boundaries are generalized Natural Earth 110m reference polygons. Areas spanning the antimeridian require a future dedicated implementation; they must fail under existing longitude constraints.
- The underlying grid extraction weights are approximate for rectilinear WGS84 grid centers. Ocean/land masks, product-specific native grid bounds and scientifically precise geodesic cell areas require independent validation before publication.
- Annual Kendall/Mann-Kendall-style p-values are not autocorrelation adjusted. No cross-region p-value for the difference in Sen slopes is calculated. A difference in slopes is descriptive.
- The SQLite database is durable **only at the chosen local or mounted persistent path**. Render's ephemeral filesystem must not be presented as durable storage. No production research database or workflow API is deployed in this increment.

## Preserved behavior

- Authenticated NASA observations from the curated Giovanni MERRA-2 monthly file are not modified or re-labeled.
- The separate NASA Space Apps submitted snapshot remains unchanged.
- The desktop top navbar, hamburger mobile menu, animated Earth, light/dark theme, footer and all existing study workflows are unchanged.
- Both `backend/no-push/` and `frontend/no-push/` are excluded by root `.gitignore`.

## Traceability

New source: `backend/services/research_workspace.py`, `backend/services/research_workspace_cli.py`.

New automated scientific tests: `backend/tests/test_research_workspace.py`.

Updated ignored operational guides and complete source copies: `backend/no-push/INCREMENT_5_*` and `frontend/no-push/INCREMENT_5_*`.

## Next core implementation priorities (not claimed complete)

Validate the user's authentic IMERG and GLDAS NetCDF files on their Windows environment using this research CLI, with recorded Earthdata file source locations. Then pursue production-safe persistent metadata/storage with access policy, full polygon/map UX, multi-region visualizations, and reproducible server-side PDF reporting. AI interpretation must be separately grounded and validated. Section 31 remains deferred.
