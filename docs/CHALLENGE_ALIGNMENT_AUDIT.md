# EarthTrace — 2026 Earth System Trend Detective alignment audit

**Source:** User-provided 2026 NASA Space Apps challenge text, “Be An Earth System Trend Detective!” The original reference page is https://www.spaceappschallenge.org/2026/challenges/earth-system-trend-detective/?tab=details . This is an independent project, not an official NASA product.

## What the official challenge asks

1. Identify Earth science variables that might exhibit trends.
2. Acquire data for a specific region, not necessarily the whole Earth or nation.
3. Plot a sufficiently long time series with scientifically accurate units.
4. Quantify its rate of change and test significance (for example using a Mann-Kendall test or a confidence interval).

## What the upgraded project actually implements

| Challenge objective | Implementation | Evidence / limitation |
| --- | --- | --- |
| Select variables | Select temperature (MERRA-2), precipitation (GPM IMERG), or soil moisture (GLDAS) | These are **available analysis paths**, not three preloaded NASA datasets. |
| Select geographic region | Describe actual NASA Giovanni sampled area/grid and include a source URL | No interactive map raster extraction; the user obtains the time series in Giovanni; arbitrary region names are not automatically mapped to observations. |
| Acquire NASA mission/model data | One curated MERRA-2 region/variable from original NASA Giovanni files; new CSV upload workflow for other data | No live NASA data API, no assertion of independent source authentication for visitor uploads. |
| Visualize time series | Responsive monthly chart plus annual mean/total and fitted regression | Full calendar years only for annual analysis; missing years are excluded. |
| Quantify change | OLS slope + R²; Sen's slope and 95% confidence interval | Units shown with monthly vs annual distinction. |
| Test significance | Annual Kendall rank trend test (Mann-Kendall-style) with p-value; threshold 0.05 | No correction for serial autocorrelation or spatial sampling uncertainty. |
| Explain findings | Detective report: WHAT, WHERE, HOW MUCH, SIGNIFICANT? | Results are statistical associations, not causal attribution. |
| Audience | Definitions, guided process, instructions for NASA Giovanni, curated example | One curated demonstration only; no fabricated demo data. |

## Public user workflow

1. Open **New investigation**. Choose a variable and appropriate corresponding mission/model product.
2. In NASA Giovanni, produce an **area-averaged monthly time series** and export its CSV; check `Data Bounding Box` in the CSV metadata.
3. Select the actual **unit** from the export. Never assume rate vs total. Enter an accurate sampled study area description and NASA HTTPS source URL.
4. Upload the raw NASA Giovanni CSV (`time, mean_...`) or normalized `date,value` file. Only files with 24–1000 records and under 110 KB are accepted by browser validation.
5. Select start/end years; a minimum of eight **complete calendar years** must be available within the selection to analyze a trend.
6. Click **Analyze this investigation**. Review monthly observations, annual statistical results, confidence interval, the four-question report and coverage caveats. Save JSON results if desired.
7. Restore the curated example to return to its independently preserved MERRA-2 analysis.

## Scientific integrity

- The real curated dataset contains 301 monthly observations (January 2000–January 2025), with 25 complete calendar years in annual trend analysis.
- The original sampled grid is **not** a Bangladesh national average. The requested area and the data grid are documented separately in source metadata.
- The original outcome is a modest upward annual temperature slope, but the annual Kendall test is not statistically significant at p < 0.05 (p about 0.2554).
- A new upload is **visitor-supplied and not independently verified**. The system never persists it, writes it into the curated public data directory or asserts its NASA authenticity.
- Statistical tests are exploratory and do not resolve causal drivers, nonlinear effects, seasonality or autocorrelation-adjusted confidence claims.
- Region comparison, automatic NASA discovery/download, satellite raster processing and causal reasoning are **not implemented**. They should not appear as completed features in the final project submission.

## Submission amendment policy

The submitted Phase 7 snapshot should remain immutable. This upgraded version is a **post-submission revision candidate**: publish or modify a submitted project only if the event rules and submission interface explicitly permit updates. Record the actual deploy revision and update public descriptions to match verifiable behavior.
