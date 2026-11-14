from fastapi.testclient import TestClient
from main import app
from services.regions import listing,validate_bbox,RegionError
from test_exploration import payload
import pytest

client=TestClient(app)

def test_region_catalog_public_and_not_claiming_data():
    response=client.get('/api/regions?q=Brazil')
    assert response.status_code==200
    entry=response.json()['regions'][0]
    assert entry['id']=='BRA' and entry['data_available'] is False
    assert 'not actual' not in response.text.lower() or 'approximate' in response.text.lower()
    assert len(listing())>=12

def test_bbox_validation():
    assert validate_bbox([-60,-20,-50,10])==[-60.,-20.,-50.,10.]
    for bad in ([30,20,0,10],[-200,0,0,10],[0,-95,10,12]):
        with pytest.raises(RegionError):validate_bbox(bad)

def test_visitor_bbox_roundtrip_and_invalid_rejected():
    p=payload();p['requested_bbox']=[88,20,93,27]
    r=client.post('/api/explore',json=p)
    assert r.status_code==200,r.text
    assert r.json()['dataset']['metadata']['requested_bbox']==[88,20,93,27]
    p['requested_bbox']=[100,20,80,30]
    assert client.post('/api/explore',json=p).status_code==422

def test_compare_two_distinct_regions_and_shared_years():
    a=payload();b=payload();b['region']='Brazil sampled NASA grid';b['observations']=b['observations'][:-12]
    for v in b['observations']:v['value']+=1.5
    r=client.post('/api/compare',json={'studies':[a,b]})
    assert r.status_code==200,r.text
    d=r.json();assert d['shared_first_year']==2000 and d['shared_last_year']==2023 and d['shared_year_count']==24
    assert len(d['studies'])==2

def test_compare_rejects_incompatible_and_duplicate_regions():
    a=payload();b=payload()
    assert client.post('/api/compare',json={'studies':[a,b]}).status_code==422
    b['region']='Other area';b['variable']='rainfall';b['product']='GPM IMERG';b['unit']='mm/day'
    assert client.post('/api/compare',json={'studies':[a,b]}).status_code==422

def test_compare_rejects_payload_errors():
    assert client.post('/api/compare',json={'studies':[]}).status_code==422
    assert client.post('/api/compare',data='bad',headers={'Content-Type':'text/plain'}).status_code==415
    assert client.post('/api/compare',data='x'*240001,headers={'Content-Type':'application/json'}).status_code==413
