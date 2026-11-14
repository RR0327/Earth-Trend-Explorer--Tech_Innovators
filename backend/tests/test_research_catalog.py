from fastapi.testclient import TestClient
import main
from services.research_catalog import preview, products, PreviewError
import pytest

client = TestClient(main.app)

def test_catalog_declares_not_invented_data():
    catalog=client.get('/api/catalog/products')
    assert catalog.status_code==200
    items=catalog.json()['products']
    assert {x['family'] for x in items} == {'MERRA-2','GPM IMERG','GLDAS'}
    assert next(x for x in items if x['family']=='GPM IMERG')['available_curated_series']==0
    assert all(x['has_live_area_extraction'] is False for x in items)

def test_real_data_preview():
    answer=client.post('/api/data/preview',json={'dataset_id':'merra2_selected_area_temperature_2000_2025','start_year':2000,'end_year':2024})
    assert answer.status_code==200
    result=answer.json()
    assert result['observation_count']==300
    assert result['missing_month_count']==0
    assert len(result['complete_years'])==25
    assert result['analysis_available']
    assert 'NOT Bangladesh national average' in result['source_region']

def test_preview_cannot_spoof_region():
    result=client.post('/api/data/preview',json={'dataset_id':'merra2_selected_area_temperature_2000_2025','region':'Brazil'}).json()
    assert result['requested_region']=='Brazil'
    assert not result['requested_region_matches_source']
    assert 'Bangladesh' in result['source_region']

def test_incomplete_2025_year_excluded():
    result=client.post('/api/data/preview',json={'dataset_id':'merra2_selected_area_temperature_2000_2025'}).json()
    assert result['observation_count']==301
    assert 2025 not in result['complete_years']
    assert result['missing_month_count']==11

def test_invalid_or_unavailable_preview():
    for body in ({'dataset_id':'nonexistent'}, {'dataset_id':'../secret'}, {'dataset_id':'merra2_selected_area_temperature_2000_2025','start_year':1990}, {'dataset_id':'merra2_selected_area_temperature_2000_2025','start_year':2024,'end_year':2000}):
        assert client.post('/api/data/preview',json=body).status_code==422
    assert client.post('/api/data/preview',data='not-json',headers={'content-type':'application/json'}).status_code==400
    assert client.post('/api/data/preview',data='x',headers={'content-type':'text/plain'}).status_code==415

def test_region_detail_remains_approximate():
    response=client.get('/api/regions/BRA')
    assert response.status_code==200
    assert response.json()['boundary_type']=='approximate_bbox'
    assert client.get('/api/regions/invalid').status_code==404

def test_empty_local_dataset_catalog(tmp_path):
    assert all(x['available_curated_series']==0 for x in products(tmp_path)['products'])
    with pytest.raises(PreviewError):
        preview(tmp_path, {'dataset_id':'merra2_selected_area_temperature_2000_2025'})
