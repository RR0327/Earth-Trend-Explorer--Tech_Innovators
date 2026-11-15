"""Opt-in bounded extraction of administrator-approved, local scientific NetCDF grids.

Public callers select only a registered product and supported geometry. They never
supply filenames, URLs, or arbitrary GeoJSON. No source files are written/uploaded.
This synchronous route is intended for small approved subsets, not large GIS jobs.
"""
from __future__ import annotations
import json
import os
import re
import threading
from pathlib import Path
from shapely.geometry import box, Polygon
from services.country_boundaries import get_boundary
from services.grid_extraction import PRODUCTS
from services.research_workspace import build_workspace, ResearchValidationError

_LOCK = threading.BoundedSemaphore(value=1)
_PRODUCT = re.compile(r'^[a-z][a-z0-9_]{4,70}$')
MAX_FILES=120
MAX_TOTAL_BYTES=150_000_000

class ApprovedExtractionError(ValueError):
    pass


def _manifest():
    """Load operator-approved paths only, constrained under a configured data root."""
    root_text=os.environ.get('EARTH_TREND_GRID_ROOT','').strip()
    manifest_text=os.environ.get('EARTH_TREND_GRID_MANIFEST','').strip()
    if os.environ.get('EARTH_TREND_GRID_PUBLIC','')!='1' or not root_text or not manifest_text:
        return None
    root=Path(root_text).expanduser().resolve()
    manifest=Path(manifest_text).expanduser().resolve()
    if not root.is_dir() or not manifest.is_file():
        raise ApprovedExtractionError('Approved grid configuration unavailable')
    try:
        registry=json.loads(manifest.read_text(encoding='utf-8'))
    except (ValueError,OSError) as exc:
        raise ApprovedExtractionError('Invalid approved grid manifest') from exc
    if not isinstance(registry,dict) or registry.get('schema_version')!=1 or not isinstance(registry.get('products'),dict):
        raise ApprovedExtractionError('Approved grid manifest schema invalid')
    approved={}
    for product, entry in registry['products'].items():
        if product not in PRODUCTS or not isinstance(entry,dict):
            raise ApprovedExtractionError('Unexpected product in approved grid manifest')
        rels=entry.get('files')
        if not isinstance(rels,list) or not 1<=len(rels)<=MAX_FILES or len(set(rels))!=len(rels):
            raise ApprovedExtractionError('Approved file count invalid or duplicated')
        files=[];total=0
        for rel in rels:
            if not isinstance(rel,str) or not rel or Path(rel).is_absolute() or '\\' in rel:
                raise ApprovedExtractionError('Approved files must be relative paths')
            p=(root/rel).resolve()
            if not p.is_relative_to(root) or p.suffix.lower() not in ('.nc','.nc4') or not p.is_file():
                raise ApprovedExtractionError('Approved file missing or outside configured data root')
            total+=p.stat().st_size
            if total>MAX_TOTAL_BYTES: raise ApprovedExtractionError('Approved file set exceeds public processing budget')
            files.append(p)
        approved[product]={'files':files,'file_count':len(files),'total_bytes':total,
                           'label':str(entry.get('label') or product)[:120]}
    return approved


def catalog():
    approved=_manifest()
    if approved is None:
        return {'enabled':False,'products':[],'note':'Administrator-approved gridded extraction is disabled. Published research remains available.'}
    return {'enabled':True,'products':[{'product_id':key,'label':value['label'],
              'file_count':value['file_count'],'product_version':PRODUCTS[key]['version'],
              'variable':PRODUCTS[key]['variable'],'unit':PRODUCTS[key]['out_unit']}
              for key,value in approved.items()],
            'note':'Datasets are trusted operator-selected local files, not an automatically authenticated NASA service.'}


def extract(request):
    if not isinstance(request,dict): raise ApprovedExtractionError('JSON object required')
    if set(request)-{'product_id','country_code','bbox','polygon'}:
        raise ApprovedExtractionError('Unexpected request fields')
    product=request.get('product_id')
    if not isinstance(product,str) or not _PRODUCT.fullmatch(product):
        raise ApprovedExtractionError('Valid product_id required')
    approved=_manifest()
    if approved is None: raise ApprovedExtractionError('Public grid extraction disabled')
    if product not in approved: raise ApprovedExtractionError('Product not included in approved public grid catalogue')
    if sum(key in request for key in ('country_code','bbox','polygon'))!=1:
        raise ApprovedExtractionError('Choose exactly one country_code, bbox or polygon')
    if 'country_code' in request:
        code=request['country_code']
        if not isinstance(code,str) or not re.fullmatch('[A-Z]{3}',code):
            raise ApprovedExtractionError('Country must use three-letter uppercase code')
        try: feature=get_boundary(code)
        except KeyError as exc: raise ApprovedExtractionError('Unknown country boundary') from exc
        geometry=feature['geometry'];name=str(feature['properties']['name']);region_id=code
    elif 'polygon' in request:
        coords=request['polygon']
        if (not isinstance(coords,list) or not 4<=len(coords)<=26 or
            any(not isinstance(pt,list) or len(pt)!=2 or any(type(value) not in (int,float) for value in pt) for pt in coords)):
            raise ApprovedExtractionError('Polygon must have 3–25 WGS84 vertices and a closing point')
        import math
        if not all(math.isfinite(value) and -180<=pt[0]<=180 and -90<=pt[1]<=90 for pt in coords for value in pt):
            raise ApprovedExtractionError('Polygon has invalid WGS84 coordinates')
        if coords[0]!=coords[-1] or len({tuple(pt) for pt in coords[:-1]})<3:
            raise ApprovedExtractionError('Polygon must be closed with at least three distinct vertices')
        west=min(pt[0] for pt in coords);east=max(pt[0] for pt in coords)
        south=min(pt[1] for pt in coords);north=max(pt[1] for pt in coords)
        if east-west>25 or north-south>25 or west==east or south==north:
            raise ApprovedExtractionError('Polygon must be bounded to 25 degrees per axis')
        area=Polygon(coords)
        if area.is_empty or not area.is_valid or area.area<=1e-9:
            raise ApprovedExtractionError('Polygon must be simple, non-self-intersecting and nonzero area')
        geometry=area.__geo_interface__
        region_id='CUSTOM_POLYGON';name='User-drawn bounded polygon'
    else:
        coords=request['bbox']
        if not isinstance(coords,list) or len(coords)!=4 or any(type(v) not in (int,float) for v in coords):
            raise ApprovedExtractionError('bbox must be [west,south,east,north] numeric coordinates')
        import math
        west,south,east,north=coords
        if not all(math.isfinite(v) for v in coords) or not (-180<=west<east<=180 and -90<=south<north<=90):
            raise ApprovedExtractionError('Invalid WGS84 bounding box')
        if east-west>25 or north-south>25:
            raise ApprovedExtractionError('Public custom rectangle limited to 25 degrees per axis')
        geometry=box(west,south,east,north).__geo_interface__
        region_id='CUSTOM';name='User-selected bounded rectangular area'
    if not _LOCK.acquire(blocking=False):
        raise ApprovedExtractionError('Research extraction is busy; retry after the current request')
    try:
        try:
            result=build_workspace(approved[product]['files'],product,
                                   [{'id':region_id,'name':name,'geometry':geometry}])
        except (ResearchValidationError,ValueError,OSError) as exc:
            raise ApprovedExtractionError('Scientific extraction rejected: '+str(exc)) from exc
    finally:
        _LOCK.release()
    study=result['studies'][0]
    return {'data_status':'computed_from_operator_approved_local_grids',
            'not_persisted':True,'research_id':result['research_id'], 'product_id':product,
            'region_id':region_id,'region_name':name,'geometry':geometry,
            'observation_count':len(study['observations']),
            'observations':study['observations'],'trend':study['trend'],
            'trend_status':study['trend_status'],
            'coverage_checks':study['coverage_checks'],
            'metadata':study['metadata'], 'limitations':result['limitations']}
