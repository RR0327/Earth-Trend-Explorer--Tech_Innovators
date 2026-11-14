# EarthTrace — NASA Space Apps 2026 Project Submission

## Project title
EarthTrace — Bangladesh Earth Trend Explorer

## Tagline
Turn NASA Earth observations into transparent, testable local trend investigations.

## Short description
EarthTrace is a public Earth-science dashboard that turns NASA MERRA-2 temperature observations into time-series visualizations and statistically transparent trend findings for a selected study area in eastern Bangladesh.

## Challenge
Be An Earth System Trend Detective! — https://www.spaceappschallenge.org/2026/challenges/earth-system-trend-detective/

## Project story / longer description
Earth systems change through time, but interpreting a line chart is not the same as demonstrating a meaningful trend. EarthTrace helps visitors investigate observed environmental time series using a clear four-question workflow: **What is changing? Where? By how much? Is the change statistically significant?**

The current demonstrated investigation uses 301 genuine monthly temperature observations (January 2000–January 2025), obtained through NASA Giovanni from the MERRA-2 2-meter air temperature product. The sample is a **narrow selected eastern Bangladesh area**, not Bangladesh's national average. Our FastAPI backend validates and exposes a curated series, aggregates complete calendar years, and computes linear regression, a Kendall rank/Mann-Kendall-style trend test, and Theil–Sen slope. The React interface presents monthly and annual charts, fitted values, statistics, source coverage and limitations, with light/dark themes, responsive layout and accessibility controls. Anyone can explore it without creating an account.

The 2000–2024 complete-year analysis finds a small positive fitted slope (+0.0097 °C/year), but the rank-trend p-value (~0.255) is **not statistically significant at 0.05**. The result demonstrates why we distinguish the direction of an estimated trend from the evidence supporting it. January 2025 is excluded from annual analysis because it is incomplete. Serial autocorrelation is not corrected, so the analysis is exploratory rather than a definitive climate assessment.

EarthTrace makes NASA model-derived observations more approachable for students, educators and curious citizens while preserving the scientific context needed to avoid misleading conclusions. It provides a working example that can be extended to other validated datasets and regions in later releases; those future datasets are **not** claimed as implemented today.

## The four investigation answers

1. **What:** Monthly MERRA-2 2-meter air temperature, summarized annually.
2. **Where:** A selected sampled grid area in eastern Bangladesh, **not** the whole country.
3. **How much:** Linear +0.009723 °C/year; Sen +0.012989 °C/year.
4. **Significant?** No, two-sided Kendall/MK-style p=0.255372 (>0.05), without serial-correlation adjustment.

## Technology
React, Vite, Recharts, Python, FastAPI, SciPy, curated NASA Giovanni CSV/JSON, Vercel and Render.

## Links
- Working website: https://earth-trend-explorer-tech-innovator.vercel.app/
- Public API: https://earth-trend-explorer-tech-innovators.onrender.com/
- Challenge: https://www.spaceappschallenge.org/2026/challenges/earth-system-trend-detective/
- Source portal: https://giovanni.gsfc.nasa.gov/giovanni/
- **GitHub repository:** [INSERT REAL PUBLIC GITHUB URL BEFORE SUBMISSION]
- **Demo video:** [INSERT PUBLIC VIDEO LINK AFTER RECORDING]
- **Team:** [INSERT REGISTERED TEAM NAME AND MEMBERS]

## Honest scope and novelty
The distinct contribution is the public, accessible **explanation-first** investigation experience around a reproducible, provenance-aware local dataset. It is not a live global climate platform, not a national trend map and not a predictive AI system. The statistical analysis is not a causal attribution study.

## Team contributions
[Insert actual team members and their real contributions. Do not invent names or responsibilities.]

## AI tools disclosure (edit to match actual use)
AI assistance was used during project planning, code/documentation drafting and testing support; the team reviewed the generated material and ran its own local and deployment verification. **Confirm and edit this statement to reflect your exact tools and activities before submission.**
