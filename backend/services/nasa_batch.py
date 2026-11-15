"""Reproducible offline validation and extraction of user-obtained NASA gridded files.

No network access or product authenticity is inferred from a filename. The caller
must document actual Earthdata/GES DISC retrieval independently.
"""
import csv
import hashlib
import json
from datetime import date
from pathlib import Path

import xarray as xr

from services.grid_extraction import PRODUCTS, GridExtractionError, extract_gridded_series, open_product_dataset


class BatchValidationError(ValueError):
    pass


def _hash(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()


def validate_source_file(path, product_id):
    """Check scientific structure + local SHA256; not proof of NASA provenance."""
    if product_id not in PRODUCTS:
        raise BatchValidationError('Unsupported product identifier')
    p=Path(path)
    if not p.is_file() or p.suffix.lower() not in ('.nc','.nc4'):
        raise BatchValidationError('Local NetCDF .nc/.nc4 required')
    if p.stat().st_size > 1_000_000_000:
        raise BatchValidationError('NetCDF exceeds 1 GB safe local extraction limit')
    spec=PRODUCTS[product_id]
    try:
        with open_product_dataset(p, product_id, decode_times=True) as ds:
            var=ds.get(spec['variable'])
            if var is None:
                raise BatchValidationError('Missing expected variable '+spec['variable'])
            if set(var.dims)!={'time','lat','lon'} or var.ndim!=3:
                raise BatchValidationError('Expected 3-D time,lat,lon gridded variable')
            unit=str(var.attrs.get('units',''))
            unit_norm=unit.lower().replace(' ','').replace('**','^').replace('²','2')
            allowed={'mm/hr':{'mm/hr','mmh-1','mmhour-1'},'K':{'k','kelvin'},'kg m-2':{'kgm-2','kg/m2','kgm^-2'}}[spec['unit']]
            if unit_norm not in allowed:
                raise BatchValidationError('Unexpected native units: '+repr(unit))
            given=str(ds.attrs.get('product_short_name',''))
            if given and given!=spec['short_name']:
                raise BatchValidationError('Embedded product conflicts with expected NASA product')
            for attr in ('version','product_version','VersionID','Version'):
                if attr in ds.attrs:
                    v=str(ds.attrs[attr]).strip()
                    if v and not (v.startswith(spec['version']) or v.startswith('V'+spec['version'])):
                        raise BatchValidationError('Embedded product version differs from selected product: '+v)
            months=[]
            for t in ds.time.values:
                month=str(__import__('numpy').datetime64(t,'M'))
                if len(month)!=7 or not month[:4].isdigit() or not month[5:7].isdigit():
                    raise BatchValidationError('Unsupported monthly timestamp')
                months.append(month)
            if not months:
                raise BatchValidationError('File contains no time observations')
            if len(months)!=len(set(months)):
                raise BatchValidationError('Duplicate months inside source file')
            return {'file':p.name,'sha256':_hash(p),'bytes':p.stat().st_size,'months':months,
                    'native_unit':unit,'variable':spec['variable'],'product_id':product_id,
                    'product_short_name':spec['short_name'],'version':spec['version'],
                    'coordinate_range':{'lat':[float(ds.lat.min()),float(ds.lat.max())],
                                        'lon':[float(ds.lon.min()),float(ds.lon.max())]},
                    'local_validation':'passed','nasa_authenticity':'not_independently_verified'}
    except BatchValidationError:
        raise
    except (OSError,ValueError,KeyError,TypeError) as exc:
        raise BatchValidationError('Cannot validate scientific NetCDF: '+str(exc)) from exc


def extract_batch(files,product_id,geometry,region_name,source_urls=None):
    paths=[Path(p) for p in files]
    if not paths:
        raise BatchValidationError('At least one real NetCDF file is required')
    if len(paths)>500:
        raise BatchValidationError('Limit batch to 500 source files')
    if source_urls is not None and len(source_urls)!=len(paths):
        raise BatchValidationError('One source URL per NetCDF file is required')
    records={}; sources=[]
    for i,p in enumerate(paths):
        validated=validate_source_file(p,product_id)
        if source_urls:
            url=source_urls[i]
            if not (isinstance(url,str) and url.startswith('https://') and len(url)<=2048):
                raise BatchValidationError('Source URL must be a recorded HTTPS download link')
            validated['declared_source_url']=url
        try:
            result=extract_gridded_series(p,product_id,geometry,region_name,validated['sha256'])
        except GridExtractionError as exc:
            raise BatchValidationError(p.name+': '+str(exc)) from exc
        if len(result['observations'])!=len(validated['months']):
            raise BatchValidationError('Missing all-valid-grid coverage for one or more months in '+p.name+'; do not silently drop months')
        for obs in result['observations']:
            month=obs['date']
            if month in records:
                raise BatchValidationError('Duplicate month across NetCDF files: '+month)
            records[month]=obs
        sources.append(validated)
    ordered=[records[k] for k in sorted(records)]
    start,end=ordered[0]['date'],ordered[-1]['date']
    sy,sm=map(int,start.split('-'));ey,em=map(int,end.split('-'))
    expected=[f'{y:04d}-{m:02d}' for y in range(sy,ey+1) for m in range(1,13)
              if (y>sy or m>=sm) and (y<ey or m<=em)]
    gaps=[month for month in expected if month not in records]
    meta={'product_id':product_id,'product_short_name':PRODUCTS[product_id]['short_name'],
          'product_version':PRODUCTS[product_id]['version'],'variable_id':PRODUCTS[product_id]['variable'],
          'unit':PRODUCTS[product_id]['out_unit'],'region':region_name,'geometry':geometry,
          'spatial_method':'fractional_grid_area_weighted_mean',
          'time_span':{'first':start,'last':end},'observation_count':len(ordered),
          'missing_months':gaps,'missing_month_count':len(gaps),'sources':sources,
          'provenance_statement':'Source URLs are user-recorded claims; local validation and checksums do not authenticate NASA provenance.',
          'scientific_limitations':'Only grid cells available in supplied files; coordinate and product checks do not establish representativeness beyond sampled extent.'}
    return {'metadata':meta,'observations':ordered}


def write_batch_result(result,prefix):
    prefix=Path(prefix)
    prefix.parent.mkdir(parents=True,exist_ok=True)
    csv_path=prefix.with_suffix('.csv');json_path=prefix.with_suffix('.json')
    with csv_path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['date','value','quality_flag','valid_region_weight_fraction'])
        w.writeheader();w.writerows(result['observations'])
    json_path.write_text(json.dumps(result['metadata'],indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return csv_path,json_path
