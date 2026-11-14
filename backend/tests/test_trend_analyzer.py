"""All synthetic input below is testing-only, not NASA observations."""
import pytest
from fastapi.testclient import TestClient
from services.trend_analyzer import analyze_dataset, TrendValidationError

def dataset(years=10, direction=1, variable="temperature", unit="degC", drop=()):
    obs = [{"date":f"{y}-{m:02d}","value":25+direction*(y-2000)*0.5 + m*0.01} for y in range(2000, 2000+years) for m in range(1,13) if (y,m) not in drop]
    return {"metadata":{"id":"synthetic_test","variable":variable,"normalized_unit":unit,"region":"TEST region", "source_url":"https://giovanni.gsfc.nasa.gov/giovanni/"},"observations":obs}

def test_increasing_trend():
    out=analyze_dataset(dataset());assert out['mann_kendall']['significant_at_0_05'];assert out['sen_slope']['slope_per_year']==pytest.approx(0.5);assert out['linear_regression']['r_squared']==pytest.approx(1)

def test_decreasing_trend():
    out=analyze_dataset(dataset(direction=-1));assert out['sen_slope']['slope_per_year']<0;assert out['mann_kendall']['significant_at_0_05']

def test_partial_calendar_year_excluded():
    out=analyze_dataset(dataset(years=9,drop={(2008,12)}));assert out['included_years']==8;assert out['excluded_years'][0]['year']==2008

def test_partial_year_cannot_enter_analysis():
    with pytest.raises(TrendValidationError,match='complete calendar years'):analyze_dataset(dataset(years=8,drop={(2007,12)}))

def test_insufficient_years():
    with pytest.raises(TrendValidationError):analyze_dataset(dataset(years=7))

def test_rainfall_annual_total():
    d=dataset(variable='rainfall',unit='mm/month');d['observations']=[{**v,'value':10.0 + (int(v['date'][:4])-2000)*0.1} for v in d['observations']]
    o=analyze_dataset(d);assert o['annual_series'][0]['value']==120;assert o['unit']=='mm/year'

def test_wrong_rainfall_units():
    with pytest.raises(TrendValidationError):analyze_dataset(dataset(variable='rainfall'))

def test_non_finite_rejected():
    d=dataset();d['observations'][0]['value']=float('nan')
    with pytest.raises(TrendValidationError):analyze_dataset(d)

def test_duplicate_rejected():
    d=dataset();d['observations'].append(dict(d['observations'][0]))
    with pytest.raises(TrendValidationError):analyze_dataset(d)

def test_api_integration(tmp_path,monkeypatch):
    import main
    from services.dataset_store import ingest
    import csv,json
    d=dataset();source=tmp_path/'s.csv';meta=tmp_path/'s.json'
    with source.open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['date','value']);w.writerows((p['date'],p['value']+273.15) for p in d['observations'])
    meta.write_text(json.dumps({'id':'synthetic_test','variable':'temperature','product':'MERRA-2','source_url':'https://giovanni.gsfc.nasa.gov/giovanni/','region':'TEST region','spatial_method':'area_mean','temporal_resolution':'monthly','unit':'K','retrieved_at':'2026-11-14'}))
    ingest(source,meta,tmp_path/'data');monkeypatch.setattr(main,'DATA_DIR',tmp_path/'data')
    client=TestClient(main.app)
    r=client.get('/api/datasets/synthetic_test/trend');assert r.status_code==200;assert r.json()['included_years']==10
    assert client.get('/api/datasets/missing/trend').status_code==404


def test_constant_annual_values_rejected():
    d=dataset()
    for p in d['observations']:
        p['value']=25.0
    with pytest.raises(TrendValidationError,match='constant'):
        analyze_dataset(d)
