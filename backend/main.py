"""Read-only API exposing imported NASA-data records; no climate claims are generated."""
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from services.dataset_store import list_datasets, load_dataset
from services.deployment_config import allowed_origins, is_production
from services.release_checks import dataset_readiness

app = FastAPI(title="Bangladesh Earth Trend Explorer", version="0.6.0")
origins = allowed_origins()
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST"], allow_headers=["*"])
DATA_DIR = Path(os.getenv("BETE_DATA_DIR", str(Path(__file__).resolve().parent / "data")))

@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "DENY"
    if is_production():
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response

@app.get("/")
def root():
    return {"name": "Bangladesh Earth Trend Explorer API", "status": "running"}

@app.get("/api/health")
def health():
    return {"status": "healthy", "phase": 3}

@app.get("/api/ready")
def ready():
    report = dataset_readiness(DATA_DIR)
    if not report["ready"]:
        raise HTTPException(status_code=503, detail=report)
    return report

@app.get("/api/datasets")
def datasets():
    return {"datasets": list_datasets(DATA_DIR)}

@app.get("/api/datasets/{dataset_id}")
def dataset(dataset_id: str):
    try:
        return load_dataset(DATA_DIR, dataset_id)
    except (FileNotFoundError, ValueError):
        raise HTTPException(status_code=404, detail="Dataset not found or invalid")


@app.get("/api/datasets/{dataset_id}/trend")
def dataset_trend(dataset_id: str):
    from services.trend_analyzer import analyze_dataset, TrendValidationError
    try:
        data = load_dataset(DATA_DIR, dataset_id)
    except (FileNotFoundError, ValueError):
        raise HTTPException(status_code=404, detail="Dataset not found or invalid")
    try:
        return analyze_dataset(data)
    except TrendValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@app.get("/api/variables")
def variable_catalog():
    """Transparent capabilities, not claims of currently hosted observations."""
    from services.exploration import PRODUCTS
    return {"variables": [
        {"id":"temperature","name":"2-m air temperature","definition":"Near-surface air temperature measured or modeled two meters above ground.","product":"MERRA-2","units":sorted(PRODUCTS['temperature']['MERRA-2'])},
        {"id":"rainfall","name":"Precipitation","definition":"Water reaching the surface as precipitation; a rate and a monthly total have different units.","product":"GPM IMERG","units":sorted(PRODUCTS['rainfall']['GPM IMERG'])},
        {"id":"soil_moisture","name":"Soil moisture","definition":"Water held in soil, expressed as water-equivalent depth or mass per unit area.","product":"GLDAS","units":sorted(PRODUCTS['soil_moisture']['GLDAS'])},
    ], "note":"Only imported datasets are preloaded. Other variables require a visitor-provided monthly NASA export."}


@app.post("/api/explore")
async def explore(request: Request):
    """Analyze a small visitor-supplied NASA monthly series without saving it."""
    from services.exploration import investigate, ExplorationValidationError
    if request.headers.get('content-type', '').split(';')[0].lower() != 'application/json':
        raise HTTPException(status_code=415, detail='Content-Type must be application/json')
    body = await request.body()
    if len(body) > 120_000:
        raise HTTPException(status_code=413, detail='Payload exceeds 120 KB')
    import json
    try:
        payload = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        raise HTTPException(status_code=400, detail='Invalid JSON')
    try:
        return investigate(payload)
    except ExplorationValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
