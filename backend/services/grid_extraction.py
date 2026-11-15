"""Genuine finite-cell area aggregation of monthly gridded NASA exports.

Input is a TRUSTED, locally downloaded NetCDF, never an arbitrary public upload.
No boundary geometries or NASA observations are fabricated.
Supports rectilinear lat/lon cells on WGS84; excludes antimeridian-crossing regions.
"""
import calendar
from datetime import datetime
from math import radians, sin
from pathlib import Path
import hashlib
import numpy as np
import xarray as xr
from shapely.geometry import box, shape
from shapely.ops import transform
from shapely.validation import explain_validity

class GridExtractionError(ValueError):
    pass

PRODUCTS = {
    'gpm_3imergm_07_final': {'short_name':'GPM_3IMERGM','version':'07', 'variable':'precipitation', 'unit':'mm/hr', 'out_unit':'mm/month', 'family':'GPM IMERG'},
    'gldas_noah025_m_2_1_soil0_10': {'short_name':'GLDAS_NOAH025_M','version':'2.1','variable':'SoilMoi0_10cm_inst','unit':'kg m-2','out_unit':'kg m-2','family':'GLDAS'},
    'merra2_m2tmnxslv_t2m': {'short_name':'M2TMNXSLV','version':'5.12.4','variable':'T2M','unit':'K','out_unit':'degC','family':'MERRA-2'},
}

def _geometry(geometry):
    if not isinstance(geometry, dict):
        raise GridExtractionError('GeoJSON geometry object required')
    if geometry.get('type') not in ('Polygon','MultiPolygon'):
        raise GridExtractionError('Only Polygon/MultiPolygon geometries supported; use a rectangular Polygon for boxes')
    try:
        g=shape(geometry)
    except Exception as exc:
        raise GridExtractionError('Invalid GeoJSON coordinates') from exc
    if g.is_empty or not g.is_valid or g.area<=0:
        raise GridExtractionError('Invalid polygon: '+explain_validity(g))
    xmin,ymin,xmax,ymax=g.bounds
    if not (-180<=xmin<xmax<=180 and -90<=ymin<ymax<=90) or xmax-xmin>180:
        raise GridExtractionError('Region outside WGS84 or crossing the antimeridian is not supported')
    return g

def _bounds(coords):
    arr=np.asarray(coords,dtype=float)
    if arr.ndim!=1 or len(arr)<2 or not np.all(np.isfinite(arr)) or len(np.unique(arr))!=len(arr):
        raise GridExtractionError('Latitude/longitude axes must contain at least two distinct finite centers')
    dif=np.diff(arr)
    if not (np.all(dif>0) or np.all(dif<0)):
        raise GridExtractionError('Grid axes must be strictly monotonic')
    mid=(arr[:-1]+arr[1:])/2
    edges=np.concatenate(([arr[0]-(mid[0]-arr[0])],mid,[arr[-1]+(arr[-1]-mid[-1])]))
    return np.column_stack((np.minimum(edges[:-1],edges[1:]),np.maximum(edges[:-1],edges[1:])))

def _area_transform(x,y,z=None):
    # Equal area for lon-lat rectangles; polygon edges transformed approximately.
    # For high-precision regional geodesic intersections use an equal-area projection.
    if np.isscalar(x): return (radians(float(x)),sin(radians(float(y))))
    return ([radians(float(v)) for v in x],[sin(radians(float(v))) for v in y])

def spatial_weights(lat,lon,geometry):
    """Fractional cell area in longitude × sin(latitude) coordinates (up to Earth radius²)."""
    g=_geometry(geometry)
    yy=_bounds(lat);xx=_bounds(lon)
    if yy.min()<-90 or yy.max()>90 or xx.min()<-180 or xx.max()>180:
        raise GridExtractionError('Cells exceed WGS84 bounds / require longitude wrapping')
    transformed=transform(_area_transform,g)
    weights=np.zeros((len(yy),len(xx)),dtype=float)
    for i,(south,north) in enumerate(yy):
        for j,(west,east) in enumerate(xx):
            cell=box(radians(west),sin(radians(south)),radians(east),sin(radians(north)))
            if cell.intersects(transformed):
                weights[i,j]=cell.intersection(transformed).area
    if not weights.any():
        raise GridExtractionError('Selected polygon does not intersect any grid cells')
    return weights

def _normalize_unit(unit):
    return str(unit).lower().replace(' ','').replace('**','^').replace('−','-').replace('²','2')

def open_product_dataset(path, product_id, decode_times=True):
    """Open supported root-level products and Harmony's IMERG /Grid layout.

    Backward compatibility: legacy approved root-level IMERG fixtures are valid;
    real Harmony subset exports expose precipitation under /Grid.
    """
    if product_id not in PRODUCTS:
        raise GridExtractionError('Unsupported NASA product identifier')
    try:
        root = xr.open_dataset(path, decode_times=decode_times)
    except Exception as exc:
        raise GridExtractionError('Cannot decode NetCDF root (install netCDF4 for HDF5): '+str(exc)) from exc
    if product_id != 'gpm_3imergm_07_final' or PRODUCTS[product_id]['variable'] in root:
        return root
    root.close()
    try:
        return xr.open_dataset(path, group='Grid', decode_times=decode_times)
    except Exception as exc:
        raise GridExtractionError('Cannot decode IMERG /Grid group (install netCDF4): '+str(exc)) from exc

def extract_gridded_series(path,product_id,geometry,region_name,expected_source_file_sha256=None):
    if product_id not in PRODUCTS:raise GridExtractionError('Unsupported NASA product identifier')
    if not isinstance(region_name,str) or not 1<=len(region_name.strip())<=150:
        raise GridExtractionError('A descriptive region name is required')
    file=Path(path)
    if not file.is_file() or file.suffix.lower() not in ('.nc','.nc4'):
        raise GridExtractionError('Locally downloaded NetCDF source file required')
    if file.stat().st_size>1_000_000_000: raise GridExtractionError('Input exceeds 1 GB local processing limit')
    digest=hashlib.sha256(file.read_bytes()).hexdigest()
    if expected_source_file_sha256 and digest!=expected_source_file_sha256:
        raise GridExtractionError('Source checksum mismatch')
    specification=PRODUCTS[product_id]
    try:
        ds=open_product_dataset(file, product_id, decode_times=True)
    except Exception as exc:
        raise GridExtractionError('Cannot decode NetCDF input (install netCDF4 for NetCDF4/HDF5)') from exc
    try:
        var=specification['variable']
        if var not in ds:raise GridExtractionError('Required product variable '+var+' missing')
        for name in ('time','lat','lon'):
            if name not in ds.coords:raise GridExtractionError('Expected time/lat/lon coordinate missing')
        field=ds[var]
        if tuple(field.dims)!=('time','lat','lon'):
            try:field=field.transpose('time','lat','lon')
            except ValueError as exc:raise GridExtractionError('Expected single-layer time/lat/lon variable') from exc
        unit=str(field.attrs.get('units',''))
        allowed={ 'mm/hr':{'mm/hr','mmh-1','mmhour-1'}, 'K':{'k','kelvin'}, 'kg m-2':{'kgm-2','kg/m2','kgm^-2'}}[specification['unit']]
        if _normalize_unit(unit) not in allowed:
            raise GridExtractionError('Unexpected unit '+repr(unit)+'; expected '+specification['unit'])
        # NASA product identity must be supported by externally recorded provenance, not inferred from filename.
        metadata_short=str(ds.attrs.get('product_short_name',''))
        if metadata_short and metadata_short!=specification['short_name']:
            raise GridExtractionError('Embedded product identifier conflicts with selected product')
        weights=spatial_weights(ds.lat.values,ds.lon.values,geometry)
        times=ds.time.values
        observations=[]
        for index,t in enumerate(times):
            try:
                month=str(np.datetime64(t,'M'))
                year,mo=map(int,month.split('-'))
                if not (1<=mo<=12): raise ValueError
            except Exception as exc:
                raise GridExtractionError('Unsupported time calendar; use CF-compatible Gregorian months') from exc
            data=np.asarray(field.isel(time=index).values,dtype=float)
            valid=np.isfinite(data)
            weight=weights*valid
            if weight.sum()==0:continue
            value=float((np.where(valid,data,0)*weight).sum()/weight.sum())
            if specification['unit']=='K':value-=273.15
            elif specification['unit']=='mm/hr':value*=24*calendar.monthrange(year,mo)[1]
            observations.append({'date':month,'value':round(value,8),'quality_flag':'valid_area_weighted',
                                 'valid_region_weight_fraction':round(float(weight.sum()/weights.sum()),6)})
        if not observations:raise GridExtractionError('No valid grid observations intersect region')
        if len({o['date'] for o in observations})!=len(observations):
            raise GridExtractionError('Duplicate monthly timestamps in NetCDF input')
        observations.sort(key=lambda x:x['date'])
        return {'metadata':{'product':specification['family'],'product_short_name':specification['short_name'],
                            'product_version':specification['version'],'variable_id':var,
                            'variable':{'T2M':'temperature','precipitation':'rainfall','SoilMoi0_10cm_inst':'soil_moisture'}[var],
                            'original_unit':specification['unit'],'normalized_unit':specification['out_unit'],
                            'region':region_name,'geometry':geometry,'spatial_method':'fractional_grid_area_weighted_mean',
                            'weighting_notes':'Approximate equal-area spherical lon/sin(lat); regular rectilinear lat-lon grid; grid cell edges inferred from center coordinates',
                            'temporal_method':'monthly native product; precipitation rate converted to monthly amount using calendar month hours',
                            'source_file_sha256':digest,'source_filename':file.name,
                            'verification_status':'local_file_not_independently_authenticated',
                            'coverage_warning':'Only the supplied NetCDF grid and its valid cells; polygon must not be equated to an unverified national-average dataset.'},
                'observations':observations}
    finally:
        ds.close()
