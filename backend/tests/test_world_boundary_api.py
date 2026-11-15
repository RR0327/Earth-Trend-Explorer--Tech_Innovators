from fastapi.testclient import TestClient
from main import app
from services.country_boundaries import world_boundaries

def test_world_boundary_endpoint():
    response=TestClient(app).get('/api/geography/world')
    assert response.status_code==200
    data=response.json()
    assert data['type']=='FeatureCollection'
    assert len(data['features'])>=150
    assert all(f.get('geometry') for f in data['features'])

def test_world_boundary_matches_bundled_snapshot():
    assert world_boundaries()['type']=='FeatureCollection'
    assert len(world_boundaries()['features'])>=150
