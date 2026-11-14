"""Public deployment smoke test; Python stdlib only. Usage: python scripts/smoke_check.py https://api.example.com"""
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DATASET = 'merra2_selected_area_temperature_2000_2025'


def fetch(base, path, method='GET'):
    req = Request(base.rstrip('/') + path, method=method, headers={'User-Agent': 'EarthTrace-release-smoke/1.0'})
    with urlopen(req, timeout=35) as response:
        return response.status, json.load(response)


def run(base):
    if not base.startswith(('http://localhost:', 'http://127.0.0.1:', 'https://')):
        raise ValueError('Remote API must be HTTPS')
    health = fetch(base, '/api/health')[1]
    assert health['status'] == 'healthy'
    ready = fetch(base, '/api/ready')[1]
    assert ready['ready'] and ready['observations'] == 301
    catalog = fetch(base, '/api/datasets')[1]['datasets']
    assert any(x['id'] == DATASET for x in catalog)
    detail = fetch(base, f'/api/datasets/{DATASET}')[1]
    assert len(detail['observations']) == 301
    trend = fetch(base, f'/api/datasets/{DATASET}/trend')[1]
    assert trend['included_years'] == 25
    assert trend['mann_kendall']['significant_at_0_05'] is False
    try:
        fetch(base, '/api/datasets', 'POST')
    except HTTPError as ex:
        assert ex.code == 405, f'Expected 405, got {ex.code}'
    else:
        raise AssertionError('POST should not be allowed')
    print('RELEASE SMOKE PASS: health, readiness, catalog, 301 observations, annual trend, public read-only')


if __name__ == '__main__':
    try:
        if len(sys.argv) != 2:
            raise ValueError('Usage: python scripts/smoke_check.py https://your-api.onrender.com')
        run(sys.argv[1])
    except (AssertionError, ValueError, HTTPError, URLError, TimeoutError) as exc:
        print(f'RELEASE SMOKE FAIL: {exc}', file=sys.stderr)
        sys.exit(1)
