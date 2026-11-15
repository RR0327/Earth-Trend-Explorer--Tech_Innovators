"""Regression checks for the November 2026 NASA Harmony NetCDF recovery."""
from pathlib import Path
import numpy as np
import pytest
import xarray as xr
from services.grid_extraction import open_product_dataset
from services.research_workspace_cli import main as research_main
from services.extract_nasa_batch_cli import main as batch_main

PRODUCT='gpm_3imergm_07_final'


def test_imerg_uses_grid_group_when_root_empty(tmp_path, monkeypatch):
    root = xr.Dataset(attrs={'FileHeader': 'NASA Harmony result'})
    grid = xr.Dataset({'precipitation': (('time','lon','lat'), np.ones((1,2,2)))},
        coords={'time':np.array(['2000-01-01'],dtype='datetime64[ns]'),
                'lon':[90.,91.], 'lat':[22.,23.]})
    calls=[]
    def fake_open(path, **kwargs):
        calls.append(kwargs.get('group'))
        return (grid if kwargs.get('group')=='Grid' else root).copy()
    monkeypatch.setattr('services.grid_extraction.xr.open_dataset',fake_open)
    result=open_product_dataset(tmp_path/'example.nc4',PRODUCT)
    try:
        assert 'precipitation' in result
        assert result['precipitation'].dims==('time','lon','lat')
        assert calls==[None,'Grid']
    finally:
        result.close()


def test_root_level_dataset_remains_supported(tmp_path,monkeypatch):
    root=xr.Dataset({'precipitation': (('time','lat','lon'),np.ones((1,2,2)))})
    seen=[]
    def fake_open(path, **kwargs):
        seen.append(kwargs.get('group'))
        return root.copy()
    monkeypatch.setattr('services.grid_extraction.xr.open_dataset',fake_open)
    result=open_product_dataset(tmp_path/'fixture.nc',PRODUCT)
    try:
        assert seen==[None]
    finally:result.close()


def test_directory_option_collects_sorted_nc4_without_shell_long_argument(tmp_path,monkeypatch):
    folder=tmp_path/'NASA';folder.mkdir()
    (folder/'b.nc4').write_bytes(b'fixture-b')
    (folder/'a.nc4').write_bytes(b'fixture-a')
    (folder/'README.txt').write_text('ignore this')
    captured={}
    def fake_build(paths,product,regions,urls,min_fraction):
        captured['names']=[Path(p).name for p in paths]
        return {'research_id':'a'*64,'studies':[{}], 'comparison':{'status':'requires_two_regions'}}
    monkeypatch.setattr('services.research_workspace_cli.build_workspace',fake_build)
    monkeypatch.setattr('services.research_workspace_cli.store_workspace',lambda *args: {'created':True})
    monkeypatch.setattr('services.research_workspace_cli.export_workspace',lambda *args:None)
    research_main(['build','--directory',str(folder),'--product',PRODUCT,'--countries','BGD',
                   '--database',str(tmp_path/'record.sqlite3'),'--export-json',str(tmp_path/'research.json')])
    assert captured['names']==['a.nc4','b.nc4']


def test_empty_directory_rejected_cleanly(tmp_path):
    with pytest.raises(SystemExit) as error:
        research_main(['build','--directory',str(tmp_path),'--product',PRODUCT,'--countries','BGD',
                       '--database',str(tmp_path/'record.sqlite3'),'--export-json',str(tmp_path/'research.json')])
    assert error.value.code==2


def test_preflight_empty_directory_fails(tmp_path):
    from services.nasa_preflight_cli import inspect_directory
    with pytest.raises(ValueError,match='No NetCDF'):
        inspect_directory(tmp_path,PRODUCT)


def test_preflight_validates_without_long_argv(tmp_path,monkeypatch):
    from services.nasa_preflight_cli import inspect_directory
    for month in ('200001','200002'):
        (tmp_path/(month+'.nc4')).write_bytes(b'placeholder')
    def fake_validate(path, product):
        return {'months':[f'{Path(path).stem[:4]}-{Path(path).stem[4:6]}'], 'native_unit':'mm/hr'}
    monkeypatch.setattr('services.nasa_preflight_cli.validate_source_file',fake_validate)
    result=inspect_directory(tmp_path,PRODUCT)
    assert result['months_checked']==2
    assert result['first_month']=='2000-01'
    assert result['last_month']=='2000-02'
    assert result['spatial_extent_check']=='not_requested'
