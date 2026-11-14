"""Production configuration, curated dataset and headers: regression/release gates."""
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
import main
from services.deployment_config import allowed_origins
from services.release_checks import dataset_readiness


def test_development_cors_defaults():
    assert set(allowed_origins('development', '')) == {'http://localhost:5173','http://127.0.0.1:5173'}


def test_production_requires_specific_https_frontend():
    with pytest.raises(ValueError): allowed_origins('production', '')
    with pytest.raises(ValueError): allowed_origins('production', '*')
    with pytest.raises(ValueError): allowed_origins('production', 'http://example.com')
    assert allowed_origins('production', 'https://earthtrace.vercel.app/') == ['https://earthtrace.vercel.app']


def test_rejects_invalid_origins_and_deduplicates():
    for value in ['https://example.com/path','https://user:password@example.com','data:text/plain,x']:
        with pytest.raises(ValueError): allowed_origins('production', value)
    assert allowed_origins('production', 'https://a.example,https://a.example') == ['https://a.example']


def test_readiness_reports_actual_curated_dataset():
    report = dataset_readiness(Path(main.__file__).parent / 'data')
    assert report['ready'] is True and report['observations'] == 301


def test_missing_curated_assets_fail_closed(tmp_path):
    assert dataset_readiness(tmp_path)['reason'] == 'curated_dataset_missing'


def test_ready_endpoint_and_security_headers():
    client = TestClient(main.app)
    response = client.get('/api/ready')
    assert response.status_code == 200 and response.json()['ready'] is True
    assert response.headers['x-content-type-options'] == 'nosniff'
    assert response.headers['x-frame-options'] == 'DENY'


def test_cors_preflight_allowed_for_local_dev_only():
    client = TestClient(main.app)
    response = client.options('/api/datasets', headers={'Origin':'http://localhost:5173','Access-Control-Request-Method':'GET'})
    assert response.status_code == 200
    assert response.headers['access-control-allow-origin'] == 'http://localhost:5173'
    bad = client.options('/api/datasets', headers={'Origin':'https://untrusted.example','Access-Control-Request-Method':'GET'})
    assert 'access-control-allow-origin' not in bad.headers
