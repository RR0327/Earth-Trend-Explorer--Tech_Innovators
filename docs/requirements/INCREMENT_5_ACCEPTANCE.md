# Increment 5 — Acceptance and next core requirements

## Automated acceptance
- [ ] Existing backend tests plus new research suite pass (`102 passed` in build environment).
- [ ] Existing frontend tests pass (`44 passed` in build environment).
- [ ] Frontend production build passes on Windows 11.
- [ ] Real NASA IMERG V07 file(s) are obtained with independent acquisition/provenance evidence.
- [ ] IMERG extraction over two fully covered real country polygons passes and outputs SHA256/audit results.
- [ ] Real NASA GLDAS Noah V2.1 file(s) are obtained with independent provenance evidence.
- [ ] GLDAS extraction over two fully covered real country polygons passes.
- [ ] A batch with less than 95% valid weighted coverage is rejected (not silently imputed).
- [ ] Partial source-grid extent fails before claiming national results.
- [ ] A research run is saved to local SQLite and re-opened with verified research ID.
- [ ] Compare studies only on shared complete calendar years; no untested between-region statistical significance claims.
- [ ] Existing curated MERRA-2 hashes remain unchanged and source provenance is preserved.
- [ ] Professional footer, responsive UI, no-auth public API and `no-push` rules still work.
- [ ] NASA Space Apps original submitted project ZIP remains archived separately and unchanged.

## Explicitly not delivered in this increment

Full NASA online data retrieval; verified newly acquired IMERG or GLDAS binaries in this ZIP; precise geodesic area weighting; untrusted public NetCDF uploads; frontend research history; production persistent database; region comparison p-value; AI explanations and PDF reporting; Section 31 Future Enhancements.
