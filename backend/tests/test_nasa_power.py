import pytest
from fastapi.testclient import TestClient
from main import app
from services.nasa_power import check_params,power_to_series,PowerError

client=TestClient(app)

def test_request_validates_coordinates_and_years():
    check_params(23.0,90.0,2001,2024)
    for x in [(95,90,2001,2024),(24,190,2001,2024),(23,90,2022,2024),(23,90,2000,2100)]:
        with pytest.raises(PowerError):check_params(*x)

def test_power_json_conversion_uses_actual_values_without_area_claim():
    monthly={f'{y}{m:02d}':float(20+m/10+(y-2000)/10) for y in range(2000,2010) for m in range(1,13)}
    response={'properties':{'parameter':{'T2M':monthly}}}
    d=power_to_series(response,23.5,90.2,2000,2009)
    assert len(d['observations'])==120
    assert d['observations'][0]=={'date':'2000-01','value':20.1}
    assert 'not_country_average' in d['metadata']['spatial_method']
    assert d['metadata']['verification_status']=='retrieved_live_from_nasa_power_api'

def test_fill_values_omitted_and_insufficient_data_rejected():
    monthly={f'{y}{m:02d}':-999 for y in range(2001,2010) for m in range(1,13)}
    with pytest.raises(PowerError):power_to_series({'properties':{'parameter':{'T2M':monthly}}},23,90,2001,2009)

def test_public_endpoint_rejects_invalid_params_before_external_calls():
    assert client.get('/api/nasa-power/point?latitude=91&longitude=90').status_code==422
    assert client.get('/api/nasa-power/point?latitude=23&longitude=200').status_code==422
