# Increment 4 Acceptance and outstanding work

## Automated verification

- Backend: 89 passed.
- Frontend: 44 passed.
- Full ZIP integrity and preserved source-data SHA256 validated during packaging.
- Local frontend production build was not executed because Vite/node_modules are unavailable in the packaging environment.

## Acceptance gates

1. Backend tests 89 passed.
2. Frontend tests 44 passed and Windows Vite production build passed.
3. Existing selected-area MERRA-2 analysis unchanged.
4. New NetCDF source validation rejects mismatched native units, product IDs, and embedded versions.
5. Multi-file batch correctly rejects duplicate months and reports missing months.
6. Country geometry extraction remains operational.
7. Both `no-push` directories remain Git-ignored.
8. At least one *authentic downloaded* IMERG file is processed after recording provenance (**pending without actual NASA file**).
9. At least one *authentic downloaded* GLDAS file is processed after recording provenance (**pending without actual NASA file**).

## Scientific blockers

NASA Earthdata source files must actually be acquired and independently checked before marking authentic IMERG/GLDAS validation complete. Current tests use synthetic fixtures; they are not real NASA observations. Do not claim full area-average retrieval or public live-data availability.

Section 31 enhancements remain deferred; original submitted snapshot is immutable.
