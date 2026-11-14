"""Geographic search presets: approximate bounding boxes, NOT administrative polygons.

Selecting a preset does not retrieve Earth observations or certify their coverage.
Bboxes use W,S,E,N in WGS84; antimeridian-crossing boxes are intentionally unsupported.
"""
import math

REGIONS = [
    ('BGD','Bangladesh','Asia',[88.0,20.5,92.7,26.7]),
    ('IND','India','Asia',[68.1,6.5,97.5,35.5]),
    ('BRA','Brazil','South America',[-73.99,-33.75,-34.79,5.27]),
    ('USA','United States','North America',[-124.8,24.4,-66.9,49.4]),
    ('CAN','Canada','North America',[-141.0,41.7,-52.6,83.1]),
    ('AUS','Australia','Oceania',[112.9,-43.8,153.7,-10.7]),
    ('ZAF','South Africa','Africa',[16.3,-34.9,32.9,-22.1]),
    ('KEN','Kenya','Africa',[33.9,-4.7,41.9,5.1]),
    ('DEU','Germany','Europe',[5.9,47.2,15.1,55.1]),
    ('JPN','Japan','Asia',[122.9,24.0,145.9,45.6]),
    ('IDN','Indonesia','Asia',[95.0,-11.1,141.0,6.1]),
    ('EGY','Egypt','Africa',[24.7,21.7,36.9,31.7]),
    ('ARG','Argentina','South America',[-73.6,-55.1,-53.6,-21.8]),
    ('FRA','France (metropolitan)','Europe',[-5.2,41.3,9.7,51.1]),
    ('GBR','United Kingdom','Europe',[-8.7,49.9,2.1,59.0]),
    ('CHN','China','Asia',[73.5,18.2,134.8,53.6]),
]

def listing(query='',limit=30):
    q=query.strip().casefold()
    return [{'id':code,'name':name,'continent':continent,'bbox':bbox,
             'boundary_type':'approximate_bbox','data_available':False} for code,name,continent,bbox in REGIONS
            if not q or q in name.casefold() or q in code.casefold() or q in continent.casefold()][:limit]

class RegionError(ValueError):
    pass

def validate_bbox(coords):
    if not isinstance(coords,list) or len(coords)!=4 or any(type(v) not in (int,float) or not math.isfinite(v) for v in coords):
        raise RegionError('Bounding box must be four finite numbers [west,south,east,north]')
    west,south,east,north=coords
    if not (-180<=west<east<=180 and -90<=south<north<=90):
        raise RegionError('Invalid bounding box coordinates or ordering')
    return [float(v) for v in coords]
