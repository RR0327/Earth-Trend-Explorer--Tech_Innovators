import test from 'node:test';
import assert from 'node:assert/strict';
import {RESEARCH_ID, safeHistoryPayload, researchReportPath, hasPublishedResearchError} from './research-history.mjs';
const id='a'.repeat(64);
test('requires valid research digest',()=>{assert.equal(RESEARCH_ID.test(id),true);assert.equal(RESEARCH_ID.test('../bad'),false)});
test('filters untrusted research identifiers',()=>{assert.equal(safeHistoryPayload({total:2,records:[{research_id:id,product_id:'MERRA',regions:'Bangladesh'}, {research_id:'unsafe',product_id:'X',regions:'Y'}]}).length,1)});
test('rejects malformed API responses',()=>assert.throws(()=>safeHistoryPayload({records:[]})));
test('report path only accepts content digest',()=>{assert.match(researchReportPath(id),/report.pdf$/);assert.throws(()=>researchReportPath('..'))});
test('publication unavailability is distinct from empty history',()=>{assert.equal(hasPublishedResearchError(503),true);assert.equal(hasPublishedResearchError(200),false)});
