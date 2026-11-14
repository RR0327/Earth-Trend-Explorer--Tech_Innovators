"""Read-only API exposing imported NASA-data records; no climate claims are generated."""
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from services.dataset_store import list_datasets, load_dataset
from services.deployment_config import allowed_origins, is_production
from services.release_checks import dataset_readiness

app = FastAPI(title="EarthTrend Detective API", version="1.0.0")
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
    return {"name": "EarthTrend Detective API", "status": "running"}

@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "earthtrend-detective"}

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


@app.get("/api/regions")
def supported_regions(q: str = ""):
    """Search approximate country bounding-box presets, not actual gridded NASA data."""
    from services.regions import listing
    return {"regions":listing(q[:100]),"note":"Presets are approximate geographic boxes for preparing a Giovanni export; they are not measured coverage, true country boundaries, or available analyses."}


@app.post("/api/compare")
async def compare_regions(request: Request):
    """Compare two independent real uploaded series; refuse incompatible observations."""
    from services.exploration import investigate, ExplorationValidationError
    from services.regions import RegionError
    from fastapi.responses import JSONResponse
    if request.headers.get('content-type','').split(';')[0].lower()!='application/json':
        raise HTTPException(415, 'Content-Type must be application/json')
    body=await request.body()
    if len(body)>240_000: raise HTTPException(413,'Payload exceeds 240 KB')
    import json
    try: payload=json.loads(body)
    except (ValueError,UnicodeDecodeError): raise HTTPException(400,'Invalid JSON')
    if not isinstance(payload,dict) or not isinstance(payload.get('studies'),list) or len(payload['studies'])!=2:
        raise HTTPException(422,'Exactly two study series are required')
    try:
        a,b=[investigate(x) for x in payload['studies']]
    except (ExplorationValidationError,RegionError) as exc:
        raise HTTPException(422,str(exc))
    am,bm=a['dataset']['metadata'],b['dataset']['metadata'];at,bt=a['trend'],b['trend']
    if am['variable']!=bm['variable'] or am['product']!=bm['product'] or am['normalized_unit']!=bm['normalized_unit']:
        raise HTTPException(422,'Both series must share variable, NASA product, and normalized unit')
    if am['region'].casefold()==bm['region'].casefold():
        raise HTTPException(422,'Provide two distinct study-area descriptions')
    ay={v['year']:v['value'] for v in at['annual_series']}; by={v['year']:v['value'] for v in bt['annual_series']}
    shared=sorted(set(ay)&set(by))
    if len(shared)<8: raise HTTPException(422,'At least eight common complete annual observations are required')
    # Refit on exactly the same years; do not compare incompatible spans.
    from scipy.stats import kendalltau,theilslopes,linregress
    x=list(shared); results=[]
    for original, values in ((a,ay),(b,by)):
        y=[values[year] for year in x]
        if len(set(y))<2: raise HTTPException(422,'One shared-year series is constant')
        linear=linregress(x,y);sen=theilslopes(y,x);tau,p=kendalltau(x,y)
        results.append({'region':original['dataset']['metadata']['region'],
                        'sen_slope_per_year':float(sen.slope), 'linear_slope_per_year':float(linear.slope),
                        'kendall_tau':float(tau),'p_value':float(p),'significant_at_0_05':bool(p<.05),
                        'annual_series':[{'year':year,'value':values[year]} for year in shared]})
    return {'comparison_status':'visitor_supplied_not_independently_authenticated',
            'product':am['product'],'variable':am['variable'], 'annual_unit':at['unit'],
            'shared_first_year':shared[0],'shared_last_year':shared[-1],'shared_year_count':len(shared),
            'studies':results,'difference_sen_slope_per_year':results[0]['sen_slope_per_year']-results[1]['sen_slope_per_year'],
            'limitations':['Both uploaded series must represent the stated areas; coverage is not verified by URL alone.',
                           'Approximate country bounding boxes are not national-boundary means.',
                           'Annual Kendall tests are not corrected for serial dependence; comparisons do not prove causation.']}

@app.get('/api/nasa-power/point')
async def nasa_power_point(latitude: float, longitude: float, start_year: int = 2001, end_year: int = 2024):
    """Opt-in global T2M data at ONE point. Never claim a country aggregate."""
    from services.nasa_power import retrieve,PowerError
    try:return await retrieve(latitude,longitude,start_year,end_year)
    except PowerError as exc:raise HTTPException(422,str(exc))


@app.get('/api/catalog/products')
def research_product_catalog():
    from services.research_catalog import products
    return products(DATA_DIR)


@app.post('/api/data/preview')
async def research_data_preview(request: Request):
    from services.research_catalog import preview, PreviewError
    if request.headers.get('content-type', '').split(';')[0].lower() != 'application/json':
        raise HTTPException(status_code=415, detail='Content-Type must be application/json')
    payload = await request.body()
    if len(payload) > 8192:
        raise HTTPException(status_code=413, detail='Preview payload exceeds 8 KB')
    import json
    try:
        parameters = json.loads(payload)
    except (UnicodeDecodeError, ValueError):
        raise HTTPException(status_code=400, detail='Invalid JSON')
    try:
        return preview(DATA_DIR, parameters)
    except PreviewError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@app.get('/api/regions/{region_id}')
def region_detail(region_id: str):
    from services.regions import listing
    matches = [r for r in listing() if r['id'].casefold() == region_id.casefold()]
    if not matches:
        raise HTTPException(status_code=404, detail='Unknown region preset')
    return {**matches[0], 'note':'Approximate preset only. Not a surveyed boundary, national mean, or guaranteed NASA coverage.'}


@app.get('/api/geospatial/capabilities')
def geospatial_capabilities():
    """Declare exactly what regional NetCDF extraction currently supports."""
    from services.grid_extraction import PRODUCTS
    return {
        'input':'trusted local NetCDF with time/lat/lon rectilinear grid',
        'geometry':'GeoJSON Polygon or MultiPolygon EPSG:4326, no antimeridian crossing',
        'method':'fractional_grid_area_weighted_mean',
        'products':[{'id':pid, **spec} for pid,spec in PRODUCTS.items()],
        'runtime_mode':'local_cli_only',
        'public_upload_enabled':False,
        'limitations':[
            'No country/admin boundary catalogue or automatic NASA download is implied.',
            'Only genuine gridded source files can be spatially aggregated; Giovanni area-average time series cannot be remasked.',
            'NetCDF metadata and file hashes are retained; independent NASA source authenticity requires provenance review.',
            'The area-weighting transformation approximates irregular polygon edges; results require scientific validation for high-precision studies.'
        ]
    }
