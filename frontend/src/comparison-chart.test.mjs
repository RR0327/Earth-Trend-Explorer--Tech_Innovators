import test from 'node:test';import assert from 'node:assert/strict';
import {sharedYearChartData,comparisonPeriodLabel} from './comparison-chart.mjs';
test('chart aligns by actual matching years instead of array position',()=>{const out=sharedYearChartData({studies:[{annual_series:[{year:2022,value:3},{year:2021,value:2}]},{annual_series:[{year:2021,value:5},{year:2022,value:7}]}]});assert.deepEqual(out,[{year:2021,regionA:2,regionB:5},{year:2022,regionA:3,regionB:7}]);});
test('chart omits unshared and invalid observations',()=>{assert.deepEqual(sharedYearChartData({studies:[{annual_series:[{year:2020,value:1},{year:2021,value:NaN}]},{annual_series:[{year:2020,value:2},{year:2021,value:3},{year:2022,value:4}]}]}),[{year:2020,regionA:1,regionB:2}]);});
test('empty and malformed comparison cannot invent chart data',()=>{assert.deepEqual(sharedYearChartData({}),[]);assert.deepEqual(sharedYearChartData(null),[])});
test('period label reflects shared years',()=>{assert.match(comparisonPeriodLabel({shared_year_count:8,shared_first_year:2000,shared_last_year:2007}),/2000–2007/)});
