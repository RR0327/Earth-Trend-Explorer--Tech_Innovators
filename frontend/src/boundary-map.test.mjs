import test from 'node:test';
import assert from 'node:assert/strict';
import {geometryToSvgPath} from './boundary-map.mjs';
test('projects authentic-style polygon coordinates to SVG',()=>{
 const g={type:'Polygon',coordinates:[[[90,20],[91,20],[91,21],[90,21],[90,20]]]};
 const d=geometryToSvgPath(g);
 assert.match(d,/M 300 85.56/);
 assert.match(d,/ Z$/);
});
test('malformed or unsupported geometry does not produce a misleading path',()=>{
 assert.equal(geometryToSvgPath(null),'');
 assert.equal(geometryToSvgPath({type:'Point',coordinates:[0,0]}),'');
});
