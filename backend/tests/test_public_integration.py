"""Phase 5 integration tests: public read-only endpoints and unchanged authentic dataset."""
from pathlib import Path
from fastapi.testclient import TestClient
import main

client=TestClient(main.app)
DATASET_ID='merra2_selected_area_temperature_2000_2025'

def test_all_public_get_routes_work_without_authentication():
    for url in ('/','/api/health','/api/datasets',f'/api/datasets/{DATASET_ID}',f'/api/datasets/{DATASET_ID}/trend'):
        response=client.get(url)
        assert response.status_code == 200,(url,response.text)
        assert 'www-authenticate' not in response.headers

def test_no_auth_credential_routes_exposed():
    paths=set(main.app.openapi()['paths'])
    assert not any(part in name for name in paths for part in ('login','register','token','logout','session'))

def test_data_and_trend_consistency():
    observation=client.get(f'/api/datasets/{DATASET_ID}').json()
    trend=client.get(f'/api/datasets/{DATASET_ID}/trend').json()
    assert len(observation['observations']) == 301
    assert trend['included_years'] == 25
    assert trend['mann_kendall']['significant_at_0_05'] is False
    assert 2025 in [entry['year'] for entry in trend['excluded_years']]

def test_read_only_operations_not_exposed():
    for url in ('/api/datasets',f'/api/datasets/{DATASET_ID}/trend'):
        assert client.post(url,json={}).status_code == 405

def test_missing_dataset_rejected():
    assert client.get('/api/datasets/not-found').status_code == 404
    assert client.get('/api/datasets/not-found/trend').status_code == 404

def test_curated_dataset_is_not_in_no_push_and_is_present():
    base=Path(main.__file__).parent
    assert (base/'data'/f'{DATASET_ID}.csv').is_file()
    assert (base/'data'/f'{DATASET_ID}.json').is_file()
