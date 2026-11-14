# EarthTrace Presentation Outline — 8 Slides

**Audience:** NASA Space Apps local and global judges. Use real screenshots from the deployed site, not invented charts. If your local event requires a different slide count or pitch duration, adapt accordingly.

1. **Cover — EarthTrace:** title, tagline, team name, 2026 Space Apps challenge, website QR/link. Visual: actual live EarthTrace landing screenshot.
2. **Why trend detection matters:** large seasonal fluctuations can be mistaken for long-term change; central question: “Is the direction statistically meaningful?” Include the challenge's four questions.
3. **The study area and NASA source:** NASA Giovanni MERRA-2 T2M; sampled 91.25°E, 23–23.5°N; monthly 2000–2025 Jan; explicit “Not a Bangladesh national average.” Visual: actual Giovanni graph or source screenshot with caption.
4. **Product walkthrough:** public React dashboard, monthly→annual chart, fitted line, accessible and responsive UI, light/dark theme, JSON export. Visual: 2–3 actual UI screenshots.
5. **Statistical engine:** 301 months, 25 complete years; Celsius conversion; regression, Kendall/MK-style p-value, Theil–Sen slope; exclusion of incomplete 2025. Visual: simple pipeline, not fabricated data.
6. **Key result:** +0.009723 °C/year regression; +0.012989 °C/year Sen; p=0.255372; R²=0.066665; **not significant at 0.05**. Explain direction ≠ significance. Visual: real annual chart.
7. **System design, integrity and limits:** React/Vercel ↔ FastAPI/Render ↔ versioned curated MERRA-2 CSV/metadata. No auth, no public data mutation. Acknowledge sampled-area limits, serial autocorrelation not corrected, and no causal attribution.
8. **Impact, next steps and demo:** benefit for learners and evidence-based exploration; future possibilities (additional validated datasets and regions, more rigorous statistics) explicitly marked future work. Finish with live website, source/GitHub/demo links and team credits.

## Pitch structure (approximately 3 minutes)
0:00–0:25 problem, 0:25–0:50 data and scope, 0:50–1:35 live product, 1:35–2:15 method/result, 2:15–2:40 value/limitations, 2:40–3:00 call-to-action and team.

## Likely judges' questions
- **Why is it called Bangladesh Earth Trend Explorer?** It is a Bangladesh-focused prototype that currently demonstrates only one selected area; we deliberately disclose the narrower spatial coverage.
- **Is the positive trend significant?** No. Kendall/MK-style p=0.255372 at threshold 0.05; we must not claim otherwise.
- **Is it live NASA API data?** No. The versioned dataset was curated from a genuine Giovanni export; the app does not call NASA dynamically.
- **Why no AI prediction?** The challenge rewards defensible trend investigation. We prioritized genuine data, transparent statistics and reproducibility over unvalidated forecasts.
- **What could improve the science?** Serial-correlation-aware significance, area-representative processing, seasonal anomalies, uncertainty quantification, and further sourced variables.
