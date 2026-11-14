"""Read-only API exposing imported NASA-data records; no climate claims are generated."""
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.dataset_store import list_datasets, load_dataset
from services.deployment_config import allowed_origins, is_production
from services.release_checks import dataset_readiness

app = FastAPI(title="Bangladesh Earth Trend Explorer", version="0.6.0")
origins = allowed_origins()
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET"], allow_headers=["*"])
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
