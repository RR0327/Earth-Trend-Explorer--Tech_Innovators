# EarthTrend Detective — Increment 3

## Delivered
- Versioned, generalized Natural Earth country polygons (172 included, public domain) with source provenance and SHA256.
- Read-only country-boundary search and full GeoJSON detail APIs.
- Existing trusted-local NetCDF extraction CLI now accepts `--country BGD` instead of GeoJSON path, deriving geometry from installed country boundaries.
- Professional React footer extracted as a modular component with real anchors, NASA resources, legal/independence disclaimer, source limitations, mobile/tablet layouts and keyboard focus styling.
- No modification to the NASA observations, previous trend calculations, or archived submitted snapshot.

## Scientific and product limitations
- Natural Earth boundaries are generalized and historic; not authoritative for disputed borders or administrative subdivisions. Some shapes, islands, and regions require additional geospatial precision.
- Country selection alone **does not fetch observations**. The CLI needs a real downloaded gridded NetCDF covering the area.
- IMERG Final V07 and GLDAS Noah V2.1 integration has been implemented for trusted local files; authentic new NASA sample files have **not** been acquired or independently validated in this increment.
- WGS84, regular rectilinear grids; antimeridian crossing is not supported.
- Section 31 future enhancements remain explicitly deferred.

## Trusted-source CLI example (requires user-supplied real gridded NetCDF)
`python -m services.extract_grid_cli --nc .\no-push\nasa-original\YOUR_REAL_GRID.nc4 --product gldas_noah025_m_2_1_soil0_10 --country BGD --region Bangladesh --output-prefix .\no-push\extraction\bangladesh_soil_moisture`

## Source and license
- Natural Earth: https://www.naturalearthdata.com/downloads/110m-cultural-vectors/
- Terms: https://www.naturalearthdata.com/about/terms-of-use/
- Boundary GeoJSON SHA256: `1435df317ddf18610e66c26f208a606e17566a205e8aef0104df427dee0f52c8`

## Frontend display
The country selector now loads the packaged boundary catalogue from `/api/geography/countries?limit=250` and retrieves each selected country's GeoJSON on demand. The map highlights the real generalized country polygon over a schematic locator. Custom box drawing and point-temperature workflows remain intact. Missing API connectivity falls back to the original approximate presets with an explicit warning.

## Footer
Three fully authored navigation columns: Explore; Data & Science; Project & Resources. This includes live anchor targets, NASA Giovanni, GES DISC, NASA POWER, the Space Apps challenge, Natural Earth, and Earthdata Search. It includes an independent-project disclaimer, open-access/no-login statement, geography/provenance qualification, responsive and keyboard-accessible markup. No invented repository URL, email address, staff names, or NASA endorsement.
