# System Architecture

EarthTrend Detective uses a public React/Vite frontend and a Python FastAPI backend. The frontend consumes documented JSON endpoints; the backend provides validated NASA observations, read-only published research records, a Natural Earth boundary catalogue and optional approved-grid extraction.

## Components

- **Frontend:** React 18, Vite, Recharts, Lucide icons, CSS theme tokens and Natural Earth 110m map rendering. The bundled GeoJSON supports map rendering if the world-boundary API is temporarily unavailable.
- **Backend:** FastAPI service endpoints; country polygon reference data; product-aware xarray/NetCDF4 extraction; spatial validation, area-weighted observations and trend statistics.
- **Research storage:** SQLite persisted in an operator-controlled location; publication is read-only. A durable production mount and verified backups are required before enabling published research history on Render.
- **External sources:** NASA MERRA-2, IMERG, GLDAS and optional NASA POWER point observations; Natural Earth for generalized country boundaries.

## Data flow

1. A user selects a supported country or bounded study area.
2. The frontend requests country geometry or the bundled world map.
3. The backend serves existing curated studies or validates a configured approved extraction source.
4. Trend charts and explanations use returned observations and associated provenance.
5. Reviewed research runs may be published from the controlled local research database. Public visitors cannot write research records.

The Natural Earth geometry is reference geography, not proof of NASA data availability.
