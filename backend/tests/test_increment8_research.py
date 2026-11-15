"""Increment 8 synthetic fixtures, never claimed to be NASA observations."""
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from main import app
from services.research_workspace import store_workspace, _sha
from services.research_insights import explain_research, published_regions
from services.research_storage import verify_and_backup

client=TestClient(app)

def record():
    core={'schema_version':'1','processing_version':'test-only','product_id':'test_product',
          'minimum_valid_cell_fraction':0.95,
          'studies':[{'region_id':'BRA','name':'Fixture region','metadata':{'normalized_unit':'°C','sources':[{'file':'synthetic.nc','sha256':'0'*64}]},
                     'observations':[{'date':'2020-01','value':22.0}],
                     'trend_status':'available',
                     'trend':{'sen_slope':{'slope_per_year':0.2},'mann_kendall':{'p_value':0.02}}}],
          'comparison':{'status':'one_region'},'limitations':['Synthetic, not NASA']}
    return {'research_id':_sha(core),**core}

def test_insight_is_from_actual_fields():
    result=explain_research(record())
    assert result['ai_generated'] is False
    assert result['studies'][0]['significant_at_0_05'] is True
    assert '0.2' in result['studies'][0]['summary']
    assert '0.02' in result['studies'][0]['summary']

def test_insight_insufficient_data():
    data=record();data['studies'][0]['trend']=None
    assert explain_research(data)['studies'][0]['significant_at_0_05'] is None

def test_published_regions_represent_only_records():
    out=published_regions([record()]);assert len(out)==1
    assert out[0]['region_id']=='BRA' and out[0]['first_month']=='2020-01'
    assert published_regions([])==[]

def test_public_routes_disabled(monkeypatch):
    monkeypatch.delenv('EARTH_TREND_RESEARCH_PUBLIC',raising=False)
    assert client.get('/api/research/available-regions').status_code==503
    assert client.get('/api/research/'+'a'*64+'/explanation').status_code==503

def test_public_routes_grounded(tmp_path,monkeypatch):
    db=tmp_path/'records.sqlite3';r=record();store_workspace(db,r)
    monkeypatch.setenv('EARTH_TREND_RESEARCH_PUBLIC','1')
    monkeypatch.setenv('EARTH_TREND_RESEARCH_DB',str(db))
    regions=client.get('/api/research/available-regions')
    assert regions.status_code==200 and regions.json()['regions'][0]['name']=='Fixture region'
    explanation=client.get('/api/research/'+r['research_id']+'/explanation')
    assert explanation.status_code==200 and explanation.json()['research_id']==r['research_id']
    assert client.get('/api/research/'+'z'*64+'/explanation').status_code==404

def test_storage_never_creates_blank_db(tmp_path):
    with pytest.raises(ValueError):verify_and_backup(tmp_path/'missing.sqlite3')
    assert list(tmp_path.iterdir())==[]

def test_verified_backup(tmp_path):
    db=tmp_path/'research.sqlite3';store_workspace(db,record());dest=tmp_path/'backup.sqlite3'
    out=verify_and_backup(db,dest)
    assert out['records']==1 and out['backup_created']
    with pytest.raises(ValueError,match='overwrite'):verify_and_backup(db,dest)
