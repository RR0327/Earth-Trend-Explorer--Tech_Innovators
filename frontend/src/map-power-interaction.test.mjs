import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {polygonExtent,pointCenterFromSelection,closePolygon} from './polygon-selection.mjs';

const component=readFileSync(fileURLToPath(new URL('./GlobalExplorer.jsx',import.meta.url)),'utf8');
test('oversized draft is reported without fabricating a completed polygon',()=>{
 const world=[[-130,55],[-100,40],[60,20],[50,50]];
 const size=polygonExtent(world);
 assert.ok(size.width>25);
 assert.throws(()=>closePolygon(world),/25 degrees/);
});
test('valid local polygon finishes with the original coordinates and geographic bbox',()=>{
 const shape=closePolygon([[88.1,22.3],[89.4,22.4],[89.1,23.2]]);
 assert.deepEqual(shape.bbox,[88.1,22.3,89.4,23.2]);
 assert.equal(shape.polygon.length,4);
});
test('NASA POWER uses a point independently of an oversized draft polygon',()=>{
 const center=pointCenterFromSelection([88,20.5,92.7,26.7],[[-130,55],[-100,40],[60,20]]);
 assert.equal(center.lon,-35);
 assert.equal(center.lat,37.5);
 assert.deepEqual(pointCenterFromSelection([88,20.5,92.7,26.7]),{lon:90.35,lat:23.6});
});
test('POWER button is not disabled by polygon validation; users see size and redraw guidance',()=>{
 assert.match(component,/disabled=\{liveBusy\} onClick=\{analyzePoint\}/);
 assert.match(component,/Zoom to selected country and redraw/);
 assert.match(component,/exceedsPolygonLimit/);
 assert.match(component,/pointCenterFromSelection/);
});
