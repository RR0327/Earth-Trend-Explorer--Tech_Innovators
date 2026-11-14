# EarthTrend Detective — Master Requirements Alignment

**Specification:** user-provided EarthTrend Detective requirements (33 numbered sections, November 2026).  
**Foundation:** EarthTrace Global Investigation Complete Upgrade, preserved and extended.  
**Release scope:** Core Version 1 and Version 2 defined in Sections 4, 28, and 32. **Section 31 is explicitly deferred** until core acceptance criteria are verified.

## Meaning of the status labels

- **Implemented and locally tested:** source and automated test evidence in this repository.
- **Partial:** there is a limited workflow; do not claim the specification's full capability.
- **Not implemented:** not represented as complete or enabled in a public interface.
- **Externally unverified:** feature has local tests but depends on a NASA external response or actual browser deployment.

## Scientific ground rules

1. Actual NASA observations are never fabricated, extrapolated across unmeasured areas, or renamed to imply a different region.
2. MERRA-2 source observations originally supplied by the user cover only the selected eastern Bangladesh study area, not Bangladesh nationally. Their normalized CSV and metadata have not changed in this increment.
3. NASA POWER monthly temperature uses a point, not a national-area average.
4. A visitor supplied CSV and NASA URL are **not independently authenticated** just because the domain is a NASA domain.
5. Monthly precipitation rates must only be converted to monthly accumulated amounts with explicit documented rate conventions and proper calendar length; IMERG product/version must be checked before enabling a new product connector.
6. GLDAS soil-moisture depths/layers must not be merged without tracking layer name, depth and product units.
7. Annual Kendall/Mann–Kendall significance tests on climate series may be sensitive to serial dependence; non-significance is not proof of no change.

## Major specification workstreams and implementation evidence

| Spec area | Current status | Evidence / next acceptance gate |
|---|---|---|
| §§1–4 Objectives, scopes, research questions | Defined | This requirements alignment; website four-question detective report |
| §5 FR-01 region selection | Partial | Approximate presets and custom bbox exist; polygon geometry and real administrative boundaries not yet integrated |
| §5 FR-02/03 dataset catalogue | Partial, improved in this increment | `/api/catalog/products` distinguishes installed observations from documented NASA products |
| §5 FR-04/05 date selection and extraction | Partial | `/api/data/preview` validates period from installed data; global geospatial extraction not yet implemented |
| §5 FR-06 monthly series | Implemented for CSV sources | importer tests, `/api/explore`, curated Giovanni data |
| §5 FR-07 stats | Partial | annual regression, Sen slope and MK-like tests implemented; seasonal MK and autocorrelation corrections not yet complete |
| §5 FR-08/09 visualization and interpretation | Implemented for supported series | monthly/annual/seasonal charts, evidence-based caveats |
| §5 FR-10 exports | Partial | CSV/JSON and browser print available; reproducible backend PDF and PNG export remain |
| §5 FR-11 comparisons | Partial | two supplied compatible series and shared complete years; stronger geospatial cross-checks remain |
| §5 FR-12/13 AI/report | Not implemented | no hosted generative service, no backend-generated research PDF |
| §§6–7 NFR, public access | Partial | no-login, responsive frontend, strict CORS, tests; needs production load and monitoring tests |
| §§8–9 NASA products | Partial | real MERRA-2 curated example; IMERG/GLDAS visitor-import only, exact product version for those not independently verified |
| §10 spatial analysis | Not complete | no production-ready true boundary masking, partial cell weights, polygon extraction |
| §11 normalization | Partial | normalized monthly CSV and metadata, checksums; no generalized NetCDF grid extractor |
| §12 statistical methodology | Partial | complete-year annual statistics; more independent scientific validation required |
| §§13–14 modular architecture & stack | Partial | React, FastAPI, scipy; PostGIS, Xarray/GeoPandas processing, jobs and object storage not integrated |
| §§15–16 frontend/backend APIs | Partial | functioning interface and existing APIs; source availability browser panel and new preview endpoints |
| §17 geospatial engine | Not implemented | true CRS handling, polygon masks, area weights, coastal boundaries |
| §18 persisted database | Not implemented | file-backed curated metadata only; database design and migrations remain |
| §19 API contract | Partial | health/catalog/regions/explore/compare plus new products/preview; no persisted analysis IDs or reports API |
| §20 visualization | Partial | charts and source metrics; missing-value visualization and downloadable PNG remain |
| §§21–22 AI/reporting (Version 2) | Not implemented | must be driven by calculated statistics, source metadata and uncertainty; never invent data |
| §§23–25 security, errors, testing | Partial | robust basic validation, test suites; production throttling and NetCDF safeguards remain |
| §26 deployment | Partial | Vercel/Render existing; persistent storage, monitoring and backups remain |
| §§27–30 architecture/roadmap/docs | Defined | keep existing deployed structure, implement modular services incrementally, do not break source imports |
| §31 future enhancements | **Deferred** | climate indices, drought, heatwaves, extended products, user accounts, research sharing |
| §32–33 acceptance criteria / completion | Not yet complete | follow acceptance requirements, do not mark all checked without explicit evidence |

## Delivered in the current increment

1. `GET /api/catalog/products`: three NASA product-family entries with clear status (preloaded vs visitor CSV), links and source caveats.
2. `POST /api/data/preview`: existing dataset coverage, real month counts, complete years, missing months, source region, product and units. The requested region never overwrites true sample coverage.
3. `GET /api/regions/{region_id}`: confirms preset boxes are approximate, not polygon boundaries.
4. Frontend product-catalogue cards and sample-data source preview with loading/error and responsive styles.
5. Regression tests for missing source, dates, incomplete years, spoofed region labels and catalogue status.
6. API root and health response now use EarthTrend Detective identity, removing obsolete `phase: 3` label.

## Next implementation sequence: core requirements first, Section 31 last

1. **Data verification and exact product mapping:** product IDs, units, quality flags and source files for IMERG and GLDAS; no fabricated test observations from NASA.
2. **Geographic extraction:** reliable GeoJSON country and subnational boundaries (licensed), geometry validation, NetCDF cell selection and weighted-area aggregation, polygon/map selection.
3. **Statistical correctness:** independent test benchmarks, monthly seasonal MK, serial-dependence diagnostics, missing-data and outlier handling.
4. **Persistence and API contract:** reproducible analysis records, stable results IDs, data previews, meaningful errors, storage strategy for deployed hosting.
5. **Advanced research UI:** integrated map and comparative charts with correct location/data provenance; accessible polished design maintained.
6. **Grounded interpretation/reporting:** model-assisted explanations constrained by backend values; PDF/PNG exports with citations and reproducibility metadata.
7. **Security/QA/deployment:** upload and request size controls, caching, rate limits, monitoring, migration strategy, browser E2E tests and source-validation evidence.
8. **Only after those acceptance gates:** Section 31 future enhancements, which are a separate backlog and not part of the initial complete release.

## Why the app is not claimed complete yet

A public map and region selector are not proof of gridded regional extraction. An IMERG or GLDAS entry in the product catalogue is not proof of live ingestion. A successful test using mocked NASA POWER is not independent live service verification. These distinctions are explicit requirements of the supplied specification and should be defended in research reviews.
