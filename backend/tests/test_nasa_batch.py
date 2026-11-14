"""Synthetic test fixtures only. No sample is represented as NASA observations."""
import hashlib
import json
import numpy as np
import pytest
import xarray as xr
from services.nasa_batch import BatchValidationError,validate_source_file,extract_batch,write_batch_result

GEO={'type':'Polygon','coordinates':[[[19.5,9.5],[21.5,9.5],[21.5,11.5],[19.5,11.5],[19.5,9.5]]]}
PRODUCT='gpm_3imergm_07_final'

def fixture(tmp_path,name,month,unit='mm/hr',var='precipitation',product='GPM_3IMERGM',version='07'):
    ds=xr.Dataset({var:(('time','lat','lon'),np.ones((1,2,2)),{'units':unit})},
        coords={'time':np.array([month+'-15'],dtype='datetime64[ns]'),'lat':[10.,11.],'lon':[20.,21.]},
        attrs={'product_short_name':product,'product_version':version})
    file=tmp_path/name;ds.to_netcdf(file,engine='scipy');return file

def test_validate_genuine_shape_and_sha(tmp_path):
    f=fixture(tmp_path,'jan.nc','2020-01')
    info=validate_source_file(f,PRODUCT)
    assert info['months']==['2020-01']
    assert info['sha256']==hashlib.sha256(f.read_bytes()).hexdigest()
    assert info['nasa_authenticity']=='not_independently_verified'

def test_batch_merge_coverage_and_export(tmp_path):
    jan=fixture(tmp_path,'jan.nc','2020-01');mar=fixture(tmp_path,'mar.nc','2020-03')
    result=extract_batch([mar,jan],PRODUCT,GEO,'Synthetic example')
    assert [o['date'] for o in result['observations']]==['2020-01','2020-03']
    assert result['metadata']['missing_months']==['2020-02']
    assert result['observations'][0]['value']==pytest.approx(744)
    a,b=write_batch_result(result,tmp_path/'out'/'result')
    assert a.is_file() and json.loads(b.read_text())['observation_count']==2

def test_duplicate_month_rejected(tmp_path):
    a=fixture(tmp_path,'a.nc','2020-01');b=fixture(tmp_path,'b.nc','2020-01')
    with pytest.raises(BatchValidationError,match='Duplicate month'):
        extract_batch([a,b],PRODUCT,GEO,'Test')

def test_wrong_product_and_unit_rejected(tmp_path):
    a=fixture(tmp_path,'a.nc','2020-01',product='GLDAS_NOAH025_M')
    with pytest.raises(BatchValidationError,match='product'):
        validate_source_file(a,PRODUCT)
    b=fixture(tmp_path,'b.nc','2020-01',unit='mm/day')
    with pytest.raises(BatchValidationError,match='units'):
        validate_source_file(b,PRODUCT)

def test_wrong_version_rejected(tmp_path):
    a=fixture(tmp_path,'a.nc','2020-01',version='06')
    with pytest.raises(BatchValidationError,match='version'):
        validate_source_file(a,PRODUCT)

def test_source_url_coverage_rejected(tmp_path):
    a=fixture(tmp_path,'a.nc','2020-01')
    with pytest.raises(BatchValidationError,match='One source URL'):
        extract_batch([a],PRODUCT,GEO,'Test',['one','two'])
    with pytest.raises(BatchValidationError,match='HTTPS'):
        extract_batch([a],PRODUCT,GEO,'Test',['http://example.com'])

def test_real_source_declared_link_not_claimed_authenticated(tmp_path):
    a=fixture(tmp_path,'a.nc','2020-01')
    result=extract_batch([a],PRODUCT,GEO,'Test',['https://disc.gsfc.nasa.gov/test.nc'])
    assert result['metadata']['sources'][0]['declared_source_url'].startswith('https://')
    assert 'do not authenticate' in result['metadata']['provenance_statement']

def test_gl_das_different_product_supported(tmp_path):
    a=fixture(tmp_path,'soil.nc','2020-01',unit='kg m-2',var='SoilMoi0_10cm_inst',product='GLDAS_NOAH025_M',version='2.1')
    result=extract_batch([a],'gldas_noah025_m_2_1_soil0_10',GEO,'Test')
    assert result['metadata']['unit']=='kg m-2'
    assert result['observations'][0]['value']==pytest.approx(1)
