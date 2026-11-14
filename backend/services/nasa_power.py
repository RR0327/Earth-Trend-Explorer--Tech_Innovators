"""Live global NASA POWER monthly *point* temperature data.

NASA POWER's MERRA-2-derived T2M point series is not the same dataset or
spatial aggregation as the curated NASA Giovanni MERRA-2 area-average CSV.
Only fixed public NASA POWER HTTPS host is contacted, never user-provided URLs.
"""
import hashlib
import json
import math
from datetime import date
import httpx
from services.trend_analyzer import analyze_dataset, TrendValidationError

API_URL = 'https://power.larc.nasa.gov/api/temporal/monthly/point'

class PowerError(ValueError):
    pass


def check_params(lat, lon, start, end):
    if not all(isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x) for x in (lat,lon)):
        raise PowerError('Latitude and longitude must be finite numbers')
    if not (-90<=lat<=90 and -180<=lon<=180): raise PowerError('Coordinates outside Earth latitude or longitude range')
    if not (isinstance(start,int) and isinstance(end,int) and 1981<=start<=end<=date.today().year-1):
        raise PowerError('Use valid complete years from 1981 to the previous calendar year')
    if end-start+1>45 or end-start+1<8:
        raise PowerError('An investigation needs 8–45 calendar years')


def power_to_series(response, lat, lon, start, end):
    """Strictly consume NASA POWER's JSON parameter.T2M month keys YYYYMM."""
    if not isinstance(response,dict): raise PowerError('NASA POWER returned an invalid object')
    parameter=response.get('properties',{}).get('parameter',{})
    monthly=parameter.get('T2M') if isinstance(parameter,dict) else None
    if not isinstance(monthly,dict): raise PowerError('NASA POWER did not return T2M monthly observations')
    observations=[]
    for key,value in monthly.items():
        if not isinstance(key,str) or len(key)!=6 or not key.isdigit():continue
        year,month=int(key[:4]),int(key[4:])
        if not (start<=year<=end and 1<=month<=12):continue
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<=-990 or value>75 or value<-100:
            continue
        observations.append({'date':f'{year:04d}-{month:02d}','value':round(float(value),9)})
    observations.sort(key=lambda p:p['date'])
    if len(observations)<96:raise PowerError('NASA POWER supplied insufficient valid monthly values (need >=96)')
    source=(f'{API_URL}?parameters=T2M&community=RE&longitude={lon:.4f}'
            f'&latitude={lat:.4f}&format=JSON&start={start}&end={end}')
    raw=json.dumps(response,sort_keys=True,separators=(',',':')).encode('utf-8')
    metadata={'id':'nasa_power_point_t2m','variable':'temperature','product':'NASA POWER / MERRA-2-derived T2M',
              'dataset_variable':'T2M', 'region':f'Point at {lat:.4f}° latitude, {lon:.4f}° longitude',
              'normalized_unit':'degC','unit':'degC','source_url':source,
              'first_month':observations[0]['date'],'last_month':observations[-1]['date'],
              'observation_count':len(observations),'temporal_resolution':'monthly',
              'spatial_method':'model_grid_point_not_country_average',
              'verification_status':'retrieved_live_from_nasa_power_api',
              'source_file_sha256':hashlib.sha256(raw).hexdigest(),
              'coverage_warning':'This is NASA POWER monthly temperature at a selected point, NOT a country or custom-region average. Source is derived from MERRA-2; differences from NASA Giovanni area averages are expected.'}
    return {'metadata':metadata,'observations':observations}


async def retrieve(lat,lon,start,end):
    check_params(lat,lon,start,end)
    params={'parameters':'T2M','community':'RE','longitude':round(lon,4),'latitude':round(lat,4),
            'format':'JSON','start':start,'end':end}
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(20,connect=8),follow_redirects=False) as client:
            r=await client.get(API_URL,params=params,headers={'User-Agent':'EarthTrace-EarthScience-Research/1.0'})
            r.raise_for_status()
            if len(r.content)>2_000_000:raise PowerError('NASA response too large')
            body=r.json()
    except (httpx.HTTPError,ValueError) as exc:
        raise PowerError('Unable to retrieve NASA POWER data. Retry later or use NASA Giovanni CSV upload.') from exc
    dataset=power_to_series(body,lat,lon,start,end)
    try:trend=analyze_dataset(dataset)
    except TrendValidationError as exc:raise PowerError(str(exc)) from exc
    return {'dataset':dataset,'trend':trend,'disclosure':'Data retrieved directly from NASA POWER, representing a point/grid value, not an area-weighted regional average.'}
