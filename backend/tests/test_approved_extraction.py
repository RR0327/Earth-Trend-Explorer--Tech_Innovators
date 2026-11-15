"""Public extraction security and synthetic scientific-fixture regression tests."""
import json
import pytest
from fastapi.testclient import TestClient
from main import app
from services.approved_extraction import extract, catalog, ApprovedExtractionError
from tests.test_research_workspace import grid, PRODUCT

client=TestClient(app)


def configured(tmp_path,monkeypatch,years=8):
    source=grid(tmp_path,years=years)
    manifest=tmp_path/'approved.json'
    manifest.write_text(json.dumps({'schema_version':1,'products':{
      PRODUCT:{'label':'Fixture precipitation','files':[source.name]}
    }}))
    monkeypatch.setenv('EARTH_TREND_GRID_PUBLIC','1')
    monkeypatch.setenv('EARTH_TREND_GRID_ROOT',str(tmp_path))
    monkeypatch.setenv('EARTH_TREND_GRID_MANIFEST',str(manifest))
    return manifest


def test_disabled_by_default(monkeypatch):
    monkeypatch.delenv('EARTH_TREND_GRID_PUBLIC',raising=False)
    assert catalog()['enabled'] is False
    r=client.post('/api/extraction/analyze',json={'product_id':PRODUCT,'country_code':'BGD'})
    assert r.status_code==503


def test_catalog_and_real_finite_grid_extraction(tmp_path,monkeypatch):
    configured(tmp_path,monkeypatch)
    c=client.get('/api/extraction/catalog')
    assert c.status_code==200 and c.json()['products'][0]['file_count']==1
    r=client.post('/api/extraction/analyze',json={'product_id':PRODUCT,'bbox':[19.5,9.5,20.5,11.5]})
    assert r.status_code==200,r.text
    j=r.json()
    assert j['observation_count']==96 and j['trend']['included_years']==8
    assert j['not_persisted'] and j['data_status']=='computed_from_operator_approved_local_grids'
    assert j['metadata']['sources'][0]['sha256']


def test_refuse_arbitrary_paths_and_geometry(tmp_path,monkeypatch):
    configured(tmp_path,monkeypatch)
    for data in ({'product_id':PRODUCT,'file':'secrets.nc'},
                 {'product_id':PRODUCT,'bbox':[19,10,20,11],'country_code':'BGD'},
                 {'product_id':PRODUCT,'bbox':[0,0,100,30]},
                 {'product_id':PRODUCT,'bbox':[19,'10',20,11]},
                 {'product_id':PRODUCT,'country_code':'../../etc/passwd'}):
        assert client.post('/api/extraction/analyze',json=data).status_code==422


def test_manifest_rejects_traversal_and_duplicate_paths(tmp_path,monkeypatch):
    m=configured(tmp_path,monkeypatch)
    for files in (['../secret.nc'], ['synthetic.nc','synthetic.nc'], ['/etc/passwd']):
        m.write_text(json.dumps({'schema_version':1,'products':{PRODUCT:{'files':files}}}))
        with pytest.raises(ApprovedExtractionError):catalog()


def test_reject_source_without_spatial_coverage(tmp_path,monkeypatch):
    configured(tmp_path,monkeypatch)
    r=client.post('/api/extraction/analyze',json={'product_id':PRODUCT,'bbox':[50,30,51,31]})
    assert r.status_code==422
    assert 'fully cover' in r.json()['detail']


def test_reject_large_payload_and_wrong_media_type(tmp_path,monkeypatch):
    configured(tmp_path,monkeypatch)
    assert client.post('/api/extraction/analyze',data='x'*2100,headers={'content-type':'application/json'}).status_code==413
    assert client.post('/api/extraction/analyze',data='x',headers={'content-type':'text/plain'}).status_code==415
