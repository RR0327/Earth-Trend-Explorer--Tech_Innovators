# API Reference

Default local base URL: `http://127.0.0.1:8000`.

| Method | Route | Description |
|---|---|---|
| GET | `/api/health` | API health |
| GET | `/api/ready` | Curated-source readiness |
| GET | `/api/datasets` | Available curated datasets |
| GET | `/api/datasets/{id}` | Curated observations and metadata |
| GET | `/api/datasets/{id}/trend` | Validated trend calculations |
| GET | `/api/geography/countries` | Generalized country catalogue |
| GET | `/api/geography/countries/{code}` | Country GeoJSON boundary |
| GET | `/api/geography/world` | Natural Earth GeoJSON FeatureCollection |
| GET | `/api/research/status` | Research publication configuration and state |
| GET | `/api/research/history` | Published read-only research records (when enabled) |
| GET | `/api/research/available-regions` | Study regions backed by published evidence |
| GET | `/api/extraction/catalog` | Approved gridded datasets, when configured |
| POST | `/api/extraction/analyze` | Bounded geographic analysis from approved sources |

Refer to FastAPI interactive OpenAPI documentation at `/docs` for request/response schemas. The research database and approved grid extraction are separately configured and may be unavailable on a fresh installation.
