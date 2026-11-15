# Increment 4 — authentic NASA source validation and geographic extraction

## Status and evidence boundary

This is **an executable offline import-and-validation workflow**, not a claim that fresh NASA IMERG/GLDAS observations are bundled. The only actual curated scientific time-series retained from previous releases is the original NASA Giovanni MERRA-2 selected-area observation series. Test fixtures are synthetic, exclusively for automated verification.

Verified external NASA product references:

- GPM IMERG Final L3 monthly 0.1° V07: `GPM_3IMERGM_07`, science product `GPM_3IMERGM`, monthly precipitation rate (`mm/hr`): https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGM_07/summary and https://gpm.nasa.gov/data/directory
- GLDAS Noah L4 monthly 0.25° V2.1: `GLDAS_NOAH025_M_2.1`, `SoilMoi0_10cm_inst` (`kg m-2`): https://disc.gsfc.nasa.gov/datasets/GLDAS_NOAH025_M_2.1/summary and https://ldas.gsfc.nasa.gov/gldas/dataset

## Obtaining authentic observations

1. Log into NASA Earthdata, if requested by GES DISC, and open one of the exact product landing pages above.
2. Select a month or a documented temporal subset, desired product variable, and a **gridded** NetCDF download. A Giovanni *area-averaged time-series NetCDF* cannot be used as gridded spatial source.
3. Save source files in `backend/no-push/nasa-original/` and record exact origin/download date. Never commit Earthdata credentials.
4. Run `services.extract_nasa_batch_cli` with `--files` for one or several monthly `.nc` files, with a bundled country polygon or WGS84 custom geometry.
5. Inspect recorded checksums, source URL claims, missing months, and valid-region-weight fraction before approving any derived dataset for publication.

Note: The backend does not automatically authenticate or retrieve Earthdata files; providing a NASA-like filename or attributes is **not proof of origin**. The source URLs are user-reported and require independent verification with NASA's download records.

## Scientific data transformations

- Monthly IMERG Final precipitation rate in `mm/hr` is converted to monthly accumulated precipitation in `mm/month` by multiplying by the calendar month's actual hours (including leap years), **after** area-weighting the monthly rate.
- GLDAS Noah `SoilMoi0_10cm_inst` remains an 0–10 cm soil water equivalent layer in `kg m-2`; it is not re-labelled as percent or root-zone moisture.
- Geospatial weighting uses the existing rectilinear WGS84 fractional grid-cell area approximation; source grid edges are inferred from centers. Antimeridian-crossing polygons, CF non-Gregorian calendars, rotated grids, and polar edge cases are not supported.
- Individual monthly files may contain gaps; outputs preserve and enumerate all missing months instead of filling them. All-empty intersection months fail closed, and duplicates fail closed.
- Gridded file contents may be subsetted by NASA data-service tooling. A supplied subset must cover the entire intended geometry for legitimate area-mean interpretation.

## Increment acceptance scope

This increment adds offline per-file structural validation and multi-file temporal merging, retains the Increment 3 country boundaries, and does not claim that a live NASA integration or nationwide time series is deployed. Version 1 and Version 2 requirements remain in progress. Section 31 future enhancements are deferred.
