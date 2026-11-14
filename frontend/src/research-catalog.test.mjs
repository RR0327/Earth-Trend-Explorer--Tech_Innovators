import test from 'node:test';
import assert from 'node:assert/strict';
import {productStatus,coverageVerdict} from './research-catalog.mjs';

test('product availability never implies unverified integration',()=>{
 assert.equal(productStatus({integration:'visitor_csv_only',available_curated_series:0}),'NASA export required');
 assert.equal(productStatus({available_curated_series:1}),'Curated series available');
 assert.equal(productStatus(null),'Unknown');
});
test('mismatched areas are never represented as source coverage',()=>{
 assert.match(coverageVerdict({requested_region_matches_source:false,analysis_available:true}),/does not match/);
 assert.match(coverageVerdict({requested_region_matches_source:true,analysis_available:false}),/Insufficient/);
 assert.match(coverageVerdict({requested_region_matches_source:true,analysis_available:true,observation_count:301,complete_years:[2000,2001]}),/301/);
});
