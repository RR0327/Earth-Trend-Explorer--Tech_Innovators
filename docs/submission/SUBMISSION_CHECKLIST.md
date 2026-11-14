# Final NASA Space Apps 2026 Submission Verification

**Official submission window:** November 14, 2026 at 9:00 AM through **November 15, 2026 at 11:59 PM local time**, per the official 2026 Space Apps site. Verify any earlier local-event deadline with your organizers. The team lead should submit through the **Project tab of the registered team's page**, then confirm submission status.

## Required human checks

- [ ] Confirm correct registered local event, team and all member names on Space Apps.
- [ ] Open Space Apps **Team > Project** tab, populate project title, challenge and narrative.
- [ ] Paste reviewed short and long descriptions from `PROJECT_SUBMISSION.md`.
- [ ] Add public frontend URL: https://earth-trend-explorer-tech-innovator.vercel.app/
- [ ] Add backend API URL (if useful): https://earth-trend-explorer-tech-innovators.onrender.com/
- [ ] Add the **actual public GitHub repository URL**; do not use a placeholder.
- [ ] Record an actual demo; add the publicly viewable video URL and test it in incognito.
- [ ] Add actual team credits, real software responsibilities and truthful AI-assistance disclosures.
- [ ] Cite NASA Giovanni MERRA-2 T2M and clearly distinguish the selected area from all of Bangladesh.
- [ ] Verify annual trend statistics and the **not statistically significant** conclusion on the deployed frontend.
- [ ] Test the deployed site on at least one phone and one desktop; verify navbar, footer, theme toggler and no-login operation.
- [ ] Confirm HTTPS, backend readiness, chart data, and JSON export.
- [ ] Confirm `no-push/`, `.venv/`, `.env` and any secrets are NOT tracked in GitHub.
- [ ] Confirm curated CSV/JSON **are** tracked and accessible to Render.
- [ ] Save changes and formally **Submit** in the Space Apps Project tab (saving drafts alone is insufficient).
- [ ] Reopen the team project page and verify a visible submission confirmation/status before the deadline; keep evidence.
- [ ] Check whether the selected local event requires a **separate local judging form, presentation or earlier pitch deadline**.

## Windows 11 deployment smoke test

```powershell
cd D:\Hackathon\Nasa\Bangladesh-Earth-Trend-Explorer\backend
.\.venv\Scripts\python.exe scripts\smoke_check.py https://earth-trend-explorer-tech-innovators.onrender.com
```

Expected: `RELEASE SMOKE PASS` if all public endpoints are reachable. If it fails, do not claim the live backend has passed. Verify visual behavior manually with browser DevTools and real devices.

## Open items (replace before final submission)
- GitHub: `[INSERT REAL PUBLIC GITHUB URL]`
- Demo video: `[INSERT REAL PUBLIC VIDEO URL]`
- Team registered name and actual participants: `[CONFIRM]`
- Selected local event and any local submission deadline: `[CONFIRM]`
- Final project page URL and submission confirmation: `[CAPTURE]`

**Avoid overclaiming:** The dashboard currently integrates *temperature only*, for *one selected sampled area*. No global maps, countrywide means, live NASA API, significant warming conclusion or AI forecasting feature is claimed.
