# EarthTrace challenge-alignment — release and rollback

This is an **upgrade candidate** built from the user's Phase 7 submitted repository. It has NOT been deployed to the existing public URLs by this package alone. Keep the original submitted snapshot and team submission confirmation as immutable archive records.

## Deploy order

1. Back up current GitHub branch and local folder. Unzip upgraded package over a copy (do not delete `.venv`, `.env` or `no-push` data files).
2. Run Windows backend tests and frontend tests/build according to the two working guides inside `backend/no-push` and `frontend/no-push`.
3. Verify original MERRA-2 preloaded sample still yields 301 observations, 25 complete years and p≈0.2554, and that restoring the sample after an upload works.
4. Stage the changed files using `git add .`; inspect `git status --short`, confirm `no-push` content and secrets are excluded, and commit with a descriptive message.
5. Redeploy Render first, retaining `APP_ENV=production` and HTTPS `CORS_ORIGINS=https://earth-trend-explorer-tech-innovator.vercel.app`. Check `/api/ready`, `/api/variables` and `/docs`.
6. Redeploy Vercel next, retaining `VITE_API_URL=https://earth-trend-explorer-tech-innovators.onrender.com`. Visit the public site from a non-logged-in browser.
7. Test NASA Giovanni raw CSV upload with real downloaded CSV, inspect the p-value and provenance disclosure, check small screens and light/dark mode.
8. If any issue occurs, roll back both deployments to the known working Phase 7 commit before making another release.

## Acceptance gates

- Backend automated tests all pass; frontend Node tests all pass; Vite production build succeeds on Windows.
- No auth is required for reading preloaded data or running the transient analysis.
- Invalid JSON / data, source domain, wrong unit, duplicates, negative rainfall, insufficient years, oversized body and invalid CSV are rejected without exposing an internal error.
- The curated dataset is unchanged and publicly available.
- Unverified uploaded data are marked as visitor-supplied, never stored, and cannot overwrite the curated dataset.
- Temperature, rainfall and soil-moisture analysis can accept genuinely sourced monthly CSVs, not fabricated observation examples.
- Browser UI works at 320, 390, 768, 1366 and 1920 CSS px; both themes; keyboard navigation and export.
- Live CORS preflight for `POST /api/explore` is accepted from the configured Vercel origin and rejected from unrelated origins.
- Submission page and public README descriptions are updated **only if event rules allow changes** and should be worded consistently with real functionality.
