# EarthTrace Global Release — Features and Scientific Limits

## Source-of-truth distinction

1. **Curated NASA Giovanni study-area example:** imported 301 monthly observations of MERRA-2 T2M, with documented sampled bounds in original NASA export. This is an eastern Bangladesh selected-area series, not a national mean.
2. **Visitor-uploaded Giovanni time series:** variable/region/product/date/source URL and measurements are user supplied and not independently verified by the backend. Uploads are ephemeral; analysis only if at least eight complete years.
3. **Live NASA POWER T2M at point:** requests monthly NASA POWER point values at center coordinates. POWER is a different service and spatial aggregation from Giovanni's area mean. External service may be unavailable. No data is manufactured as fallback.
4. **Global map:** SVG schematic for setting an approximate rectangular bbox only, not a geospatial raster, NASA layer, verified administrative boundary, or zonal aggregation.
5. **Regional comparison:** two uploaded real time-series use compatible variable/product/units and shared complete years; reporting a difference of slopes does not establish a statistically significant difference of slopes.

## Statistical rules

- Temperature annual mean uses average of twelve monthly observations (each month equally weighted, not day-weighted).
- Monthly rainfall rate `mm/day` is multiplied by calendar days to monthly depth `mm/month`, and annual totals sum the twelve monthly depths. Slope of annual total has units `mm/year²` (calendar-year rate of change of annual precipitation total).
- Soil moisture annual mean is derived from declared layer and unit; layer-to-layer comparisons are not valid without metadata.
- Kendall's tau with annual year, two-sided p-value; Sen's slope with 95% interval and a separate least-squares line. P-values uncorrected for autocorrelation. Partial years excluded.
- `p < 0.05` is statistically significant **under these assumptions**. A non-significant positive slope cannot be described as proof of warming.

## Official challenge mapping

| Objective | Evidence |
|---|---|
| Select variable | Temperature/rainfall/soil moisture catalogue and visitor upload |
| Select region | 16 approximate country boxes, custom W/S/E/N, actual source-region declaration |
| Obtain NASA data | Curated Giovanni source; POWER live *point* T2M; manual Giovanni exports for other sources |
| Time series | Monthly and annual plots, seasonal chart |
| Trends and significance | Regression, Sen's slope/CI, Kendall rank p-value, transparent interpretation |
| Compare geographic trends | Two compatible uploaded time series, matched complete years |
| Public research | No auth, JSON/CSV and browser Print-to-PDF |

## Not represented as complete

True country polygons, geographic masks, global raster heatmaps, direct gridded NetCDF area extraction, automatic GLDAS and IMERG retrieval, true polygon regional comparison, machine-learning-driven variable discovery, and AI-generated reports are not in this package. This transparency is required for scientific credibility.
