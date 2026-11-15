"""Publication tests use synthetic data only; never claim NASA authenticity."""
import io
import json
import sqlite3
import pytest
from fastapi.testclient import TestClient
from services.research_publication import (publication_database, list_published, get_published,
                                           report_pdf, PublicationError)
from services.research_workspace import store_workspace, _sha
from main import app

client=TestClient(app)


def example_record():
    observation={'date':'2020-01','value':25.0}
    core={'schema_version':'1','processing_version':'test-only','product_id':'test_source',
          'minimum_valid_cell_fraction':0.95,
          'studies':[{'region_id':'BDG','name':'Sample study area','metadata':{'sources':[{'file':'trusted.nc','sha256':'0'*64}]},
                      'observations':[observation], 'trend_status':'not_calculable: insufficient data','trend':None}],
          'comparison':{'status':'requires_two_regions'},'limitations':['Synthetic test input; no NASA origin claimed.']}
    return {'research_id':_sha(core),**core}


def prepared_db(tmp_path):
    db=tmp_path/'research.sqlite3';record=example_record();store_workspace(db,record)
    return db,record


def test_disabled_by_default(monkeypatch):
    monkeypatch.delenv('EARTH_TREND_RESEARCH_PUBLIC',raising=False)
    assert client.get('/api/research/history').status_code==503
    assert client.get('/api/research/'+'a'*64).status_code==503
    assert client.post('/api/research/history').status_code==405


def test_published_history_and_readonly_db(tmp_path,monkeypatch):
    db,record=prepared_db(tmp_path)
    monkeypatch.setenv('EARTH_TREND_RESEARCH_PUBLIC','1')
    monkeypatch.setenv('EARTH_TREND_RESEARCH_DB',str(db))
    listing=client.get('/api/research/history').json()
    assert listing['total']==1
    assert listing['records'][0]['research_id']==record['research_id']
    assert listing['records'][0]['regions']=='Sample study area'
    assert client.get('/api/research/'+record['research_id']).json()==record
    assert client.get('/api/research/'+record['research_id']+'/report.pdf').content.startswith(b'%PDF-')
    assert client.get('/api/research/'+record['research_id']+'/report.pdf').headers['content-type']=='application/pdf'
    assert client.get('/api/research/'+'z'*64).status_code==404
    with sqlite3.connect(db) as c:
        assert c.execute('SELECT COUNT(*) FROM research_runs').fetchone()[0]==1


def test_report_has_valid_pages(tmp_path):
    data=report_pdf(example_record())
    assert data.startswith(b'%PDF-')
    assert len(data)>1500


def test_history_pagination_bounds(tmp_path):
    db,_=prepared_db(tmp_path)
    assert list_published(db,limit=1,offset=1)['records']==[]
    with pytest.raises(PublicationError):list_published(db,limit=100)
    with pytest.raises(PublicationError):list_published(db,offset=-1)


def test_corrupted_record_is_never_published(tmp_path):
    db,record=prepared_db(tmp_path)
    with sqlite3.connect(db) as c:
        c.execute('UPDATE research_runs SET payload_json=?', ('{"invalid":true}',))
    with pytest.raises(PublicationError,match='integrity'):
        get_published(db,record['research_id'])


def test_not_configured_is_explicit(tmp_path,monkeypatch):
    monkeypatch.setenv('EARTH_TREND_RESEARCH_PUBLIC','1')
    monkeypatch.delenv('EARTH_TREND_RESEARCH_DB',raising=False)
    assert client.get('/api/research/history').status_code==503


def test_safe_invalid_research_id(tmp_path):
    db,_=prepared_db(tmp_path)
    with pytest.raises(PublicationError,match='identifier'):
        get_published(db,'../research.sqlite3')
