# NASA Data Sources, Provenance and Attribution

## Data actually integrated
**NASA Giovanni portal:** https://giovanni.gsfc.nasa.gov/giovanni/

**Product:** MERRA-2 Monthly Time-Averaged 2D Data, `M2TMNXSLV v5.12.4`, variable `T2M` (2-meter air temperature).

**Requested bounding box:** 90.6444°E, 22.9127°N to 91.3915°E, 23.5279°N.

**Actual sampled region reported by Giovanni:** 91.25°E, 23°N–23.5°N.

**Period:** January 2000–January 2025 (301 months); trend uses complete years 2000–2024.

**Unit processing:** Kelvin to °C by subtraction of 273.15.

**Original source exports:** Giovanni `.csv`, `.nc` and visualization `.png`, maintained in the team's `backend/no-push/nasa-original/` working directory (not Git tracked).

**Published curated research files:** `backend/data/merra2_selected_area_temperature_2000_2025.csv` and `backend/data/merra2_selected_area_temperature_2000_2025.json`.

**Giovanni reproduction link:** https://giovanni.gsfc.nasa.gov/giovanni/#service=ArAvTs&starttime=2000-01-01T00:00:00Z&endtime=2025-01-31T23:59:59Z&bbox=90.6444,22.9127,91.3915,23.5279&data=M2TMNXSLV_5_12_4_T2M&portal=GIOVANNI&format=json

**Raw CSV SHA-256 (recorded in team-provided metadata):** `da1bfe00504a5a4b1aba43a8c2b1f4fe4643d995d1bbe9c6e8b5229c67ca0912`

**Raw NetCDF SHA-256 (recorded in team-provided metadata):** `31b1caef542cffe3da4b521d0129381821a5bd7b7a30ec2f1fc1543cf16b3626`

**Dataset verification note:** The original exports were supplied by the project team. The application validates data structure, units and metadata but does not independently verify the upstream NASA provenance with an authenticated NASA service.

## Suggested attribution for the website and submission
“EarthTrace uses a user-provided NASA Giovanni export of MERRA-2 M2TMNXSLV v5.12.4 T2M monthly 2-meter air temperature data. The present analysis represents a narrow sampled region in eastern Bangladesh, not a national mean. NASA data access: https://giovanni.gsfc.nasa.gov/giovanni/. EarthTrace is an independent hackathon project and is not endorsed by NASA.”

## Sources not implemented
GPM IMERG rainfall and GLDAS soil moisture are possible future integrations. **Do not list them as currently integrated datasets** or pretend regional selection has full coverage.

## AI-assistance disclosure template — verify before using
“Our team used AI-assisted tools to help plan architecture, draft or revise code and documentation, and generate testing guidance. Team members reviewed the code, tested functionality, curated the NASA data and accepted responsibility for the submitted project.”

Edit this to reflect the tools and actual use by your team; do not copy it as a claim if inaccurate.

## Other external assets
Use only appropriately licensed or original images/icons/music. Credit any non-project artwork used in slides/videos. Do not imply NASA endorsement or use the NASA logo as if EarthTrace were a NASA-operated service.
