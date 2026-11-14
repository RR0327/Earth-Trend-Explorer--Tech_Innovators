# Scientific Methodology and Reproducibility

## Question and boundaries
This is an exploratory investigation of **monthly, area-averaged 2-meter air temperature (T2M)** in one selected sampled area of eastern Bangladesh. It is not a national estimate or a causal climate assessment.

## Source and coverage
- NASA Giovanni, MERRA-2 monthly `M2TMNXSLV_5_12_4_T2M`, original Kelvin values.
- Requested bounding box (longitude, latitude): **90.6444°E, 22.9127°N to 91.3915°E, 23.5279°N**.
- Sampled grid limits represented by the Giovanni result: **91.25°E, 23°N to 91.25°E, 23.5°N**. The sampled region is narrower than the requested box.
- 301 monthly records from **2000-01 through 2025-01**, without detected monthly gaps.
- Source and original-file hashes are retained in `backend/data/merra2_selected_area_temperature_2000_2025.json`; raw `.csv`, `.nc`, and PNG remain under the ignored `backend/no-push/nasa-original/` on the team's working copy.
- Data provenance is based on supplied NASA Giovanni exports; the application does not independently fetch or cryptographically authenticate NASA services.

## Preprocessing and units
1. Parse monthly dates and numeric observations, rejecting malformed dates, duplicates, non-finite numbers and unsupported metadata.
2. Convert temperatures by `T(°C) = T(K) − 273.15`.
3. Retain original monthly series as supplied; group monthly observations by calendar year.
4. Include a year only if all 12 months are present, then compute the arithmetic mean of that year's 12 monthly values.
5. **2000–2024:** 25 complete years. **2025:** only January present, excluded. Annual mean weights months equally, rather than day weighting; document this approximation.

## Trend statistics
For annual series `(year, annual mean temperature)`:
- **Ordinary least-squares regression:** `scipy.stats.linregress`, returning slope (°C/year), R², regression p-value and standard error. The fitted annual line is plotted alongside observations.
- **Mann-Kendall-style rank trend test:** `scipy.stats.kendalltau(year, annual temperature)` with a two-sided p-value. This is Kendall's rank trend test on annual values, described as MK-style; it is not seasonal MK or a serial-autocorrelation-corrected MK.
- **Theil–Sen slope:** `scipy.stats.theilslopes(annual temperature, year, alpha=0.95)` reporting the robust estimated slope and its 95% slope interval.
- **Significance threshold:** `p < 0.05` for the two-sided Kendall/MK-style test. The code evaluates significance and slope direction separately.

## Reproduced result from Phase 6 source

| Statistic | Result |
|---|---:|
| Annual values | 25 (2000–2024) |
| Regression slope | +0.0097234513 °C/year |
| Regression R² | 0.0666649377 |
| Regression p-value | 0.2127109403 |
| Kendall tau | +0.1666666667 |
| Kendall/MK-style p-value | 0.2553720923 |
| Sen slope | +0.0129893902 °C/year |
| Sen 95% interval | [−0.0052808000, +0.0326482500] °C/year |
| Significant at α=0.05? | **No** |

**Interpretation:** Estimated trend direction is slightly positive; the two-sided rank test is not significant at 0.05. The confidence interval for Sen slope includes zero. This result neither establishes significant warming nor proves temperatures are unchanged.

## Statistical limitations
- Annual averages reduce but do not eliminate potential temporal dependence; p-values and intervals are **not adjusted for serial autocorrelation**.
- Equal weighting of monthly averages is a simplification; no area-weight or uncertainty propagation across grid cells is estimated.
- Spatial representation is limited to the selected sampled grid, not Bangladesh as a whole.
- Seasonal anomalies, changepoints, nonlinear trends, uncertainty in model reanalysis and attribution are outside current scope.
- Multiple series or regions are not evaluated in this release; temperature is the only integrated demonstration dataset.
- Observational/model reanalysis data are not a direct causal demonstration of climate drivers.

## Reproduction (Windows 11 backend folder)

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -c "from services.dataset_store import load_dataset; from services.trend_analyzer import analyze_dataset; from pprint import pprint; pprint(analyze_dataset(load_dataset('data','merra2_selected_area_temperature_2000_2025')))"
```

The public API returns the trend result at `https://earth-trend-explorer-tech-innovators.onrender.com/api/datasets/merra2_selected_area_temperature_2000_2025/trend` (verify directly in a browser or PowerShell).
