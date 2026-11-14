# Country boundaries provenance

- Original geometry: Natural Earth **low-resolution, 1:110m administrative country polygons** packaged as the `naturalearth_lowres` test fixture with `pyogrio` / GeoPandas ecosystem.
- Source documentation: https://www.naturalearthdata.com/downloads/110m-cultural-vectors/
- Terms of use: https://www.naturalearthdata.com/about/terms-of-use/ — **public domain**.
- The bundled test fixture is a historic snapshot, **not guaranteed to reflect current legal borders or all territories**.
- Geometry exported to WGS84 GeoJSON, retaining ISO A3 code, common name, and continent. No new boundary vertices were fabricated.
- Feature count: 172.
- File SHA256: `1435df317ddf18610e66c26f208a606e17566a205e8aef0104df427dee0f52c8`.
- **Important:** These are generalized visualization/research boundaries, not administrative/legal determinations. Countries that span the antimeridian or whose data spans longitude conventions must use explicit geometry handling; the current NetCDF extractor rejects antimeridian-crossing areas.
