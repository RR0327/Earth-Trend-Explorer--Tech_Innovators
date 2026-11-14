import pytest
from shapely.geometry import shape
from fastapi.testclient import TestClient
from main import app
from services.country_boundaries import get_boundary, list_boundaries
from services.grid_extraction import spatial_weights

client=TestClient(app)

def test_bangladesh_and_brazil_have_real_nonrectangular_geometries():
    for code in ('BGD','BRA'):
        feature=get_boundary(code)
        polygon=shape(feature['geometry'])
        assert polygon.is_valid and polygon.area>0
        bounds=polygon.bounds
        assert polygon.area < (bounds[2]-bounds[0])*(bounds[3]-bounds[1])

def test_country_search_and_api():
    results=list_boundaries('Bangla')
    assert len(results)==1 and results[0]['id']=='BGD'
    assert results[0]['boundary_type']=='natural_earth_generalized_polygon'
    listing=client.get('/api/geography/countries?q=Brazil')
    assert listing.status_code==200 and listing.json()['regions'][0]['id']=='BRA'
    detail=client.get('/api/geography/countries/BGD')
    assert detail.status_code==200 and detail.json()['type']=='Feature'
    assert client.get('/api/geography/countries/ZZZ').status_code==404

def test_country_polygon_works_with_grid_cell_weights():
    feature=get_boundary('BGD')
    weights=spatial_weights([21,23,25,27],[88,90,92,94],feature['geometry'])
    assert weights.sum()>0
    assert (weights==0).any()
