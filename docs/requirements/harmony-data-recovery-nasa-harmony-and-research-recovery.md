# Increment 7 — Scientific source handling and research-publication diagnostics

## Input evidence

The user supplied two NASA Harmony Python download helpers and two subset URL manifests. Each manifest enumerates 300 monthly `.nc4` subset results from January 2000 through December 2024. They identify GLDAS Noah V2.1 `SoilMoi0_10cm_inst` and IMERG V07 monthly precipitation. The supplied files contain **links and download instructions, not gridded observations**. Real NASA validation remains dependent on downloading the actual NetCDF files and inspecting their scientific contents.

The NASA-generated helpers and URL lists are retained unchanged, in separate Git-ignored GLDAS/IMERG folders. They must run in those folders because their outputs are relative to the working directory. They are not production web-app dependencies.

## Research history root cause

`Research database unavailable` means the configured local SQLite file does not exist, despite research publication being enabled. This is configuration/data availability, not a frontend or statistical bug. The new `/api/research/status` endpoint publishes non-sensitive readiness diagnostics. It does not expose a local path or enable anonymous writes. Real SQLite records must be created and verified by the local trusted research CLI, then explicitly approved.

## Safeguards

* Never fabricate NASA measurements or research records to clear the error.
* NASA NetCDF file presence is not proof of authenticity, spatial coverage or correct units.
* Preserve country-boundary full-coverage validation and monthly valid-cell requirements.
* Do not publish raw NASA data, download credentials, local research workspaces or temporary guides.
* The original submitted snapshot, MERRA-2 data, frontend design, and `.gitignore` protections are unchanged.
* Durable public research storage requires a deliberate infrastructure decision; local SQLite is not a production persistent database merely because it exists.
* Section 31 future enhancements remain deferred.
