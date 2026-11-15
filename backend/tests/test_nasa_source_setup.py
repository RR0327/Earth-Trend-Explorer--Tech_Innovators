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
        # Download state is mutable local data, not a constant fixture.
        # Check manifest metadata here; simulated download states are tested separately.
        assert len(info['filenames']) == 300


def test_download_presence_in_isolated_temporary_directory(tmp_path):
    """A real workstation may have 0, some, or all files: test in isolation."""
    base = Path(__file__).resolve().parents[1] / 'no-push' / 'nasa-downloads'
    for product in ('IMERG', 'GLDAS'):
        uid = JOBS[product]['id']
        info = parse_manifest(base / product / f'subset_links_{uid}.txt', product)
        directory = tmp_path / product
        directory.mkdir()
        first_month, first_file = next(iter(sorted(info['filenames'].items())))
        before = inspect_downloads(info, directory)
        assert before['present_count'] == 0
        assert before['missing_count'] == 300
        assert not before['ready_for_scientific_validation']

        (directory / first_file).write_bytes(b'not-a-real-netcdf')
        partial = inspect_downloads(info, directory)
        assert partial['present_count'] == 1
        assert partial['missing_count'] == 299
        assert first_month not in partial['missing_months']
        assert not partial['ready_for_scientific_validation']

        (directory / first_file).write_bytes(b'')
        empty = inspect_downloads(info, directory)
        assert empty['present_count'] == 0
        assert empty['zero_byte_count'] == 1
        assert not empty['ready_for_scientific_validation']

        (directory / first_file).write_bytes(b'not-a-real-netcdf')
        for month, filename in info['filenames'].items():
            if month != first_month:
                (directory / filename).write_bytes(b'not-a-real-netcdf')
        complete = inspect_downloads(info, directory)
        assert complete['present_count'] == 300
        assert complete['missing_count'] == 0
        assert complete['zero_byte_count'] == 0
        assert complete['ready_for_scientific_validation']
        # Only file existence is tested; non-NetCDF bytes still require preflight.


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
