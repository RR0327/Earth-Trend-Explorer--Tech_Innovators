# Increment 2 — Exact NASA products and local geospatial extraction

**Scope:** Master specification: data product identity, product metadata, partial area weighting, monthly temporal conversions, scientific validation, read-only capability endpoint. **Section 31 Future Enhancements remains deferred.**

## Verified NASA product definitions
- IMERG Final V07 monthly GPM_3IMERGM_07; variable `precipitation`, unit `mm/hr`, 0.1° grid; NASA DOI `10.5067/GPM/IMERG/3B-MONTH/07` (verified against NASA dataset catalog and GPM documentation).
- GLDAS-2.1 Noah monthly GLDAS_NOAH025_M_2.1, `SoilMoi0_10cm_inst` water equivalent mass per area `kg m-2`, 0.25° grid; soil depth 0–10 cm (verified against NASA GLDAS README and dataset specifications).
- Original MERRA-2 selected-region temperature series remains intact; it is not a complete Bangladesh-country series.

## Current extraction capability
`backend/services/grid_extraction.py` supports valid polygon/bounding-box intersections against downloaded *gridded* rectilinear monthly NASA NetCDF. It calculates weighted averages using fractional grid-cell areas, masks missing values, records quality coverage, applies product-specific conversion, and preserves SHA256 provenance metadata. It does NOT fetch NASA products, verify Earthdata credentials, or provide a public NetCDF upload.

`GET /api/geospatial/capabilities` publishes the actual supported input products and scientific limitations.

## What remains open
- Independently retrieve and validate real IMERG/GLDAS gridded datasets before claiming complete product integration.
- Implement real country, admin and watershed boundary datasets with license records; currently only approximate boxes.
- Implement robust large-file asynchronous extraction, non-Gregorian calendars, dateline handling and geodesic polygon area validation for research-grade global processing.
- Implement production persistence, interactive map polygon editing, full comparison, AI service and server-side PDF reporting as required by Version 2.

No synthetic observation is packaged as NASA data. Synthetic fixtures are created by tests in temporary directories and never stored in the product catalogue.

## NASA documentation
- https://data.nasa.gov/dataset/gpm-imerg-final-precipitation-l3-1-month-0-1-degree-x-0-1-degree-v07-gpm-3imergm-at-ges-di-75e72
- https://gpm.nasa.gov/data/directory
- https://disc.gsfc.nasa.gov/datasets/GLDAS_NOAH025_M_2.1/summary
- https://hydro1.gesdisc.eosdis.nasa.gov/data/GLDAS/GLDAS_NOAH025_M.2.1/doc/README_GLDAS2.pdf
