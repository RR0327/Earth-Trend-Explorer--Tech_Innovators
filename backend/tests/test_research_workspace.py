"""Synthetic grids prove workflows, NOT authenticity of NASA source files."""
import json
import sqlite3
import numpy as np
import pytest
import xarray as xr
from services.research_workspace import (ResearchValidationError, build_workspace,
                                         store_workspace, load_workspace, export_workspace)
from services.research_workspace_cli import main

PRODUCT = 'gpm_3imergm_07_final'

def region(name,west,east):
    return {'id': name, 'name': name, 'geometry': {'type':'Polygon','coordinates':[[
        [west,9.5],[east,9.5],[east,11.5],[west,11.5],[west,9.5]
    ]]}}

REGIONS = [region('WEST',19.5,20.5),region('EAST',20.5,21.5)]

def grid(tmp_path,years=8,months=None,remove_one=False,invalid_fraction=False):
    if months is None:
        months = [(y,m) for y in range(2010,2010+years) for m in range(1,13)]
    times = np.array([f'{y}-{m:02d}-15' for y,m in months], dtype='datetime64[ns]')
    data = np.empty((len(times),2,2),dtype=float)
    for i,(year,month) in enumerate(months):
        data[i,:,:] = [[1+(year-2010)*0.05, 2+(year-2010)*0.07],
                       [1+(year-2010)*0.05, 2+(year-2010)*0.07]]
    if invalid_fraction:
        data[0,:,0] = np.nan
    ds=xr.Dataset({'precipitation':(('time','lat','lon'),data,{'units':'mm/hr'})},
        coords={'time': times,'lat':[10.,11.],'lon':[20.,21.]},
        attrs={'product_short_name':'GPM_3IMERGM','product_version':'07'})
    path=tmp_path/'synthetic.nc'
    ds.to_netcdf(path,engine='scipy')
    return path

def test_two_regions_share_identical_years_and_refit(tmp_path):
    path=grid(tmp_path)
    result=build_workspace([path], PRODUCT, REGIONS)
    assert len(result['studies'])==2
    assert result['comparison']['status']=='descriptive_comparison'
    assert len(result['comparison']['common_years'])==8
    assert result['studies'][0]['observations'][0]['value']!=result['studies'][1]['observations'][0]['value']
    assert all(s['trend']['included_years']==8 for s in result['studies'])
    assert len(result['research_id'])==64
    assert all(s['coverage_checks'][0]['entire_study_area_within_grid_extent'] for s in result['studies'])

def test_deterministic_identifier_and_immutable_idempotent_database(tmp_path):
    path=grid(tmp_path)
    a=build_workspace([path], PRODUCT, REGIONS)
    b=build_workspace([path], PRODUCT, REGIONS)
    assert a==b
    db=tmp_path/'runs.sqlite3'
    assert store_workspace(db,a)['created'] is True
    assert store_workspace(db,b)['created'] is False
    loaded=load_workspace(db,a['research_id'])
    assert loaded==a
    with sqlite3.connect(db) as c:
        assert c.execute('SELECT COUNT(*) FROM research_runs').fetchone()[0]==1
        assert c.execute('SELECT COUNT(*) FROM research_studies').fetchone()[0]==2
        assert c.execute('SELECT COUNT(*) FROM source_audit').fetchone()[0]==2

def test_stored_data_corruption_detected(tmp_path):
    a=build_workspace([grid(tmp_path)],PRODUCT,REGIONS)
    db=tmp_path/'run.db';store_workspace(db,a)
    with sqlite3.connect(db) as c:
        c.execute('UPDATE research_runs SET payload_json=?', ('{"spoof":true}',))
    with pytest.raises(ResearchValidationError,match='integrity'):
        load_workspace(db,a['research_id'])

def test_edited_result_cannot_be_saved(tmp_path):
    a=build_workspace([grid(tmp_path)],PRODUCT,REGIONS)
    a['studies'][0]['observations'][0]['value']+=99
    with pytest.raises(ResearchValidationError,match='modified'):
        store_workspace(tmp_path/'test.sqlite3',a)

def test_partial_country_grid_rejected(tmp_path):
    path=grid(tmp_path)
    beyond=[region('TOO_WIDE',19.5,28)]
    with pytest.raises(ResearchValidationError,match='does not fully cover'):
        build_workspace([path],PRODUCT,beyond)

def test_missing_valid_cells_are_not_silently_filled(tmp_path):
    path=grid(tmp_path,invalid_fraction=True)
    with pytest.raises(ResearchValidationError,match='valid-grid fraction|Missing all-valid-grid coverage'):
        build_workspace([path],PRODUCT,REGIONS,minimum_valid_cell_fraction=0.95)

def test_minimum_valid_coverage_config_is_enforced(tmp_path):
    path=grid(tmp_path)
    for x in (0, -1, 1.01, True):
        with pytest.raises(ResearchValidationError,match='coverage'):
            build_workspace([path],PRODUCT,REGIONS,minimum_valid_cell_fraction=x)

def test_duplicate_regions_rejected(tmp_path):
    with pytest.raises(ResearchValidationError,match='Duplicate'):
        build_workspace([grid(tmp_path)],PRODUCT,[REGIONS[0],REGIONS[0]])

def test_insufficient_years_cannot_be_labeled_significant(tmp_path):
    a=build_workspace([grid(tmp_path,years=2)],PRODUCT,REGIONS)
    assert all(s['trend'] is None for s in a['studies'])
    assert a['comparison']['status']=='insufficient_complete_years'

def test_gap_reporting_not_interpolation(tmp_path):
    months=[(2015,1),(2015,3)]
    a=build_workspace([grid(tmp_path,months=months)],PRODUCT,[REGIONS[0]])
    assert a['studies'][0]['metadata']['missing_months']==['2015-02']
    assert len(a['studies'][0]['observations'])==2

def test_export_reload_and_cli_roundtrip(tmp_path,capsys):
    path=grid(tmp_path)
    geo=tmp_path/'regions.json';geo.write_text(json.dumps(REGIONS),encoding='utf-8')
    db=tmp_path/'study.db';export=tmp_path/'export.json'
    main(['build','--files',str(path),'--product',PRODUCT,'--regions-json',str(geo),
          '--database',str(db),'--export-json',str(export)])
    assert 'RESEARCH WORKSPACE SUCCESS' in capsys.readouterr().out
    a=json.loads(export.read_text(encoding='utf-8'))
    main(['show','--database',str(db),'--research-id',a['research_id']])
    assert 'RESEARCH RECORD VERIFIED' in capsys.readouterr().out

def test_bad_source_file_or_declared_metadata_rejected(tmp_path):
    path=grid(tmp_path)
    with pytest.raises(ResearchValidationError,match='Source URL'):
        build_workspace([path],PRODUCT,REGIONS,source_urls=['http://fake-source'])

def test_output_can_be_reproducibly_archived(tmp_path):
    a=build_workspace([grid(tmp_path)],PRODUCT,REGIONS)
    target=export_workspace(a,tmp_path/'research'/'study.json')
    assert json.loads(target.read_text(encoding='utf-8'))==a
    assert 'not independently authenticate' in a['limitations'][0]
