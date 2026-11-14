"""User-selected variables, geographic declarations, year ranges, and scientific guardrails."""
from fastapi.testclient import TestClient
from main import app
from services.exploration import investigate, ExplorationValidationError
import pytest

client = TestClient(app)

def payload(variable='temperature', unit='K', product='MERRA-2', count=301):
    return {'variable':variable,'unit':unit,'product':product,'region':'Visitor-selected grid around Dhaka (verify spatial coverage)','source_url':'https://giovanni.gsfc.nasa.gov/giovanni/',
            'observations':[{'date':f'{2000+i//12}-{i%12+1:02d}', 'value': 295 + (i%12)/3 + i/400} for i in range(count)]}

def test_variable_catalog_is_public_and_explicit_about_missing_data():
    r=client.get('/api/variables'); assert r.status_code==200
    assert [v['product'] for v in r.json()['variables']]==['MERRA-2','GPM IMERG','GLDAS']
    assert 'Only imported datasets' in r.json()['note']

def test_live_exploration_is_ephemeral_and_keeps_curated_catalog():
    before=client.get('/api/datasets').json()
    r=client.post('/api/explore',json=payload()); assert r.status_code==200,r.text
    result=r.json(); assert result['trend']['included_years']==25
    assert result['dataset']['metadata']['verification_status'].startswith('visitor_supplied')
    assert client.get('/api/datasets').json()==before
    assert any(y['year']==2025 for y in result['trend']['excluded_years'])

def test_explicit_year_range_and_incomplete_year_behavior():
    p=payload();p['start_year']=2005;p['end_year']=2015
    result=client.post('/api/explore',json=p).json()['trend']
    assert (result['first_year'],result['last_year'],result['included_years'])==(2005,2015,11)

def test_bad_source_invalid_unit_duplicate_and_bad_region_rejected():
    bads=[]
    x=payload(); x['source_url']='https://nasa.gov.attacker.invalid';bads.append(x)
    x=payload(); x['unit']='km';bads.append(x)
    x=payload(); x['observations'][1]['date']=x['observations'][0]['date'];bads.append(x)
    x=payload();x['region']='x';bads.append(x)
    x=payload();x['observations'][2]['value']=float('nan');bads.append(x)
    for bad in bads:
        try:r=client.post('/api/explore',json=bad)
        except ValueError:continue
        assert r.status_code in (400,422),r.text

def test_prevent_oversized_payload_and_unsupported_media_type():
    assert client.post('/api/explore',data='x'*121000,headers={'content-type':'application/json'}).status_code==413
    assert client.post('/api/explore',data='hello',headers={'content-type':'text/plain'}).status_code==415

def test_only_nasa_dataset_products_and_monthly_normalization():
    p=payload('rainfall','mm/day','GPM IMERG');p['observations']=[{'date':x['date'],'value':2.0} for x in p['observations']]
    result=client.post('/api/explore',json=p).json()
    assert result['dataset']['observations'][0]['value']==62.0 # January daily mean times 31 days
    assert result['trend']['annual_aggregation']=='sum'
    p['product']='MERRA-2';assert client.post('/api/explore',json=p).status_code==422

def test_soil_moisture_analysis_supported_without_fake_catalog_entry():
    p=payload('soil_moisture','kg/m2','GLDAS')
    result=client.post('/api/explore',json=p)
    assert result.status_code==200,result.text
    assert result.json()['trend']['unit']=='kg/m2'

def test_exploration_no_auth_and_existing_catalog_post_blocked():
    assert client.post('/api/explore',json=payload()).status_code==200
    assert client.post('/api/datasets',json=payload()).status_code==405
