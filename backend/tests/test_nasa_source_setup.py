"""NASA job-manifest and local research database diagnostics: synthetic filesystem only."""
import sqlite3
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from services.nasa_source_setup import parse_manifest, inspect_downloads, inspect_research_db, JOBS
from services.research_publication import publication_status
from main import app


def test_original_nasa_manifests():
    base = Path(__file__).resolve().parents[1]/'no-push'/'nasa-downloads'
    for name in ('IMERG','GLDAS'):
        uid = JOBS[name]['id']
        p = base/name/f'subset_links_{uid}.txt'
        info = parse_manifest(p,name)
        assert info['manifest_count']==300
        assert info['first_month']=='200001'
        assert info['last_month']=='202412'
        assert not info['missing_months']
        assert inspect_downloads(info,base/name/uid)['missing_count']==300


def test_manifest_rejects_untrusted_host(tmp_path):
    p = tmp_path/'bad.txt'
    p.write_text('https://evil.example.com/exfiltrate.nc4\n')
    with pytest.raises(ValueError, match='host'):
        parse_manifest(p,'GLDAS')


def test_manifest_rejects_duplicate(tmp_path):
    p = tmp_path/'dup.txt';src=Path(__file__).resolve().parents[1]/'no-push'/'nasa-downloads'/'GLDAS'/f"subset_links_{JOBS['GLDAS']['id']}.txt"
    one=src.read_text().splitlines()[0]
    p.write_text(one+'\n'+one+'\n')
    with pytest.raises(ValueError, match='duplicate'):
        parse_manifest(p,'GLDAS')


def test_database_status_does_not_create_file(tmp_path):
    target=tmp_path/'not_created.sqlite3'
    assert inspect_research_db(target)['status']=='missing'
    assert not target.exists()
    with sqlite3.connect(target) as c:
        pass
    assert inspect_research_db(target)['status']=='uninitialized'
    with sqlite3.connect(target) as c:
        c.execute('CREATE TABLE research_runs (research_id TEXT)')
    assert inspect_research_db(target)['status']=='empty'
    with sqlite3.connect(target) as c:
        c.execute('INSERT INTO research_runs VALUES (?)',('test',))
    assert inspect_research_db(target)['records']==1


def test_status_endpoint_safe(tmp_path,monkeypatch):
    client=TestClient(app)
    monkeypatch.delenv('EARTH_TREND_RESEARCH_PUBLIC',raising=False)
    assert client.get('/api/research/status').json()['state']=='disabled'
    monkeypatch.setenv('EARTH_TREND_RESEARCH_PUBLIC','1')
    monkeypatch.delenv('EARTH_TREND_RESEARCH_DB',raising=False)
    assert client.get('/api/research/status').json()['state']=='not_configured'
    secret=str(tmp_path/'secret-location.sqlite3')
    monkeypatch.setenv('EARTH_TREND_RESEARCH_DB',secret)
    payload=client.get('/api/research/status').json()
    assert payload['state']=='missing'
    assert secret not in str(payload)
