"""Synthetic fixtures only; NOT NASA observations."""
import numpy as np
import pytest
import xarray as xr
from services.grid_extraction import GridExtractionError,spatial_weights,extract_gridded_series


def polygon(west,south,east,north):
    return {'type':'Polygon','coordinates':[[[west,south],[east,south],[east,north],[west,north],[west,south]]]}


def make_grid(tmp_path,variable,unit,values,product=None):
    arr=np.asarray(values,dtype=float)
    d=xr.Dataset({variable:(('time','lat','lon'),arr,{'units':unit})},
                 coords={'time':np.array(['2020-01-15','2020-02-15'],dtype='datetime64[ns]'),
                         'lat':[10.,11.],'lon':[20.,21.]},
                 attrs={'product_short_name':product} if product else {})
    p=tmp_path/'fixture.nc';d.to_netcdf(p,engine='scipy');return p


def test_polygon_fractional_weights():
    area=spatial_weights([10.,11.],[20.,21.],polygon(19.5,9.5,20.5,11.5))
    assert area[0,0]>0 and area[1,0]>0
    assert area[:,1].sum()==0
    half=spatial_weights([10.,11.],[20.,21.],polygon(20.,9.5,20.5,10.5))
    assert half[0,0]>0 and half[0,1:].sum()==0 and half[1].sum()==0


def test_full_grid_weighted_monthly_precipitation(tmp_path):
    p=make_grid(tmp_path,'precipitation','mm/hr',[[[1,3],[1,3]],[[1,3],[1,3]]],'GPM_3IMERGM')
    r=extract_gridded_series(p,'gpm_3imergm_07_final',polygon(19.5,9.5,21.5,11.5),'Synthetic test area')
    assert len(r['observations'])==2
    assert r['metadata']['original_unit']=='mm/hr'
    assert r['observations'][0]['value']==pytest.approx(2*31*24,rel=0.002)
    assert r['observations'][1]['value']==pytest.approx(2*29*24,rel=0.002) # leap Feb 2020
    assert r['metadata']['verification_status']=='local_file_not_independently_authenticated'


def test_masked_soil_moisture_layer(tmp_path):
    p=make_grid(tmp_path,'SoilMoi0_10cm_inst','kg m-2',[[[12,100],[12,100]],[[13,101],[13,101]]],'GLDAS_NOAH025_M')
    r=extract_gridded_series(p,'gldas_noah025_m_2_1_soil0_10',polygon(19.5,9.5,20.5,11.5),'Test only')
    assert [x['value'] for x in r['observations']]==[12,13]
    assert r['metadata']['normalized_unit']=='kg m-2'


def test_kelvin_conversion(tmp_path):
    p=make_grid(tmp_path,'T2M','K',[[[300,300],[300,300]],[[301,301],[301,301]]],'M2TMNXSLV')
    r=extract_gridded_series(p,'merra2_m2tmnxslv_t2m',polygon(19.5,9.5,21.5,11.5),'Test')
    assert r['observations'][0]['value']==pytest.approx(26.85)


def test_quality_missing_cells(tmp_path):
    p=make_grid(tmp_path,'SoilMoi0_10cm_inst','kg m-2',[[[10,np.nan],[10,np.nan]],[[np.nan,np.nan],[np.nan,np.nan]]])
    r=extract_gridded_series(p,'gldas_noah025_m_2_1_soil0_10',polygon(19.5,9.5,21.5,11.5),'Test')
    assert len(r['observations'])==1
    assert r['observations'][0]['valid_region_weight_fraction'] < 0.51


def test_reject_mismatch_product_unit_checksum_and_empty(tmp_path):
    p=make_grid(tmp_path,'precipitation','mm/day',[[[1,1],[1,1]],[[1,1],[1,1]]])
    with pytest.raises(GridExtractionError,match='Unexpected unit'):
        extract_gridded_series(p,'gpm_3imergm_07_final',polygon(19.5,9.5,21.5,11.5),'Test')
    with pytest.raises(GridExtractionError,match='checksum'):
        extract_gridded_series(p,'gpm_3imergm_07_final',polygon(19.5,9.5,21.5,11.5),'Test', 'bad-hash')


def test_reject_invalid_geometry_and_outside():
    with pytest.raises(GridExtractionError):spatial_weights([10,11],[20,21],polygon(5,5,5,6))
    with pytest.raises(GridExtractionError,match='does not intersect'):
        spatial_weights([10,11],[20,21],polygon(40,40,41,41))
    with pytest.raises(GridExtractionError,match='antimeridian'):
        spatial_weights([10,11],[20,21],polygon(-179,10,179,11))

def test_local_capabilities_api_does_not_claim_public_upload():
    from fastapi.testclient import TestClient
    import main
    response=TestClient(main.app).get('/api/geospatial/capabilities')
    assert response.status_code==200
    body=response.json()
    assert not body['public_upload_enabled']
    assert {p['id'] for p in body['products']}=={'gpm_3imergm_07_final','gldas_noah025_m_2_1_soil0_10','merra2_m2tmnxslv_t2m'}


def test_exact_nasa_product_catalog():
    from services.research_catalog import PRODUCT_CATALOG
    imerg=next(p for p in PRODUCT_CATALOG if p['family']=='GPM IMERG')
    gldas=next(p for p in PRODUCT_CATALOG if p['family']=='GLDAS')
    assert (imerg['short_name'],imerg['product_version'],imerg['source_unit'])==('GPM_3IMERGM','07 (Final)','mm/hr')
    assert (gldas['short_name'],gldas['product_version'],gldas['variable_id'])==('GLDAS_NOAH025_M','2.1','SoilMoi0_10cm_inst')
