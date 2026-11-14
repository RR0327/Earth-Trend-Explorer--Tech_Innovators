"""Natural Earth reference country polygons; no inference of available NASA observations."""
import json
from pathlib import Path
from functools import lru_cache
from shapely.geometry import shape

FILE = Path(__file__).resolve().parent.parent / 'reference_data' / 'natural_earth_countries_110m.geojson'

@lru_cache(maxsize=1)
def _features():
    raw=json.loads(FILE.read_text(encoding='utf-8'))
    return {f['properties']['id']: f for f in raw['features']}

def list_boundaries(q='', limit=40):
    needle=str(q).strip().casefold()[:100]
    matches=[]
    for code, f in _features().items():
        p=f['properties']
        if needle and not any(needle in str(p[k]).casefold() for k in ('name','id','continent')): continue
        bounds=[round(float(v),4) for v in shape(f['geometry']).bounds]
        matches.append({'id':code, 'name':p['name'], 'continent':p['continent'], 'bbox':bounds,
                        'boundary_type':'natural_earth_generalized_polygon', 'has_verified_nasa_observations':False})
    return matches[:min(max(int(limit),1),250)]

def get_boundary(code):
    f=_features().get(str(code).upper())
    if f is None: raise KeyError('Country boundary not included in installed Natural Earth snapshot')
    return f
