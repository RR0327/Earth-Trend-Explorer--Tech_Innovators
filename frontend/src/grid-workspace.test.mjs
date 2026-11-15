import test from 'node:test';
import assert from 'node:assert/strict';
import {prepareGridRequest,gridResultToDashboard} from './grid-workspace.mjs';
test('country selection sends only approved fields',()=> assert.deepEqual(prepareGridRequest('gpm_3imergm_07_final','country','BGD',[]),{product_id:'gpm_3imergm_07_final',country_code:'BGD'}));
test('rectangle selection checks bounds',()=> assert.deepEqual(prepareGridRequest('gpm_3imergm_07_final','rectangle','',[88,20,92,26]).bbox,[88,20,92,26]));
test('rejects oversized rectangle',()=> assert.throws(()=>prepareGridRequest('gpm_3imergm_07_final','rectangle','',[0,0,90,20])));
test('rejects arbitrary paths and invalid codes',()=>assert.throws(()=>prepareGridRequest('../../secret','country','BGD',[])));
test('rejects unsupported region type',()=>assert.throws(()=>prepareGridRequest('gpm_3imergm_07_final','polygon','',[])));
test('refuses fabricated or missing extraction marker',()=>assert.throws(()=>gridResultToDashboard({observations:[{date:'2020-01',value:2}]})));
test('converts validated extraction without changing observations',()=>{const observations=[{date:'2020-01',value:2}];const v=gridResultToDashboard({data_status:'computed_from_operator_approved_local_grids',observations,observation_count:1,region_name:'Selected region',product_id:'gpm_3imergm_07_final',metadata:{normalized_unit:'mm'},trend:null});assert.equal(v.dataset.observations,observations);assert.equal(v.dataset.metadata.normalized_unit,'mm');});

test('valid drawn polygon is sent as bounded geometry',()=>{const ring=[[88.1,22.1],[88.3,22.1],[88.2,22.3],[88.1,22.1]];assert.deepEqual(prepareGridRequest('gpm_3imergm_07_final','polygon','',[],ring),{product_id:'gpm_3imergm_07_final',polygon:ring})});
