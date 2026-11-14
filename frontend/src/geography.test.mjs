import test from 'node:test';import assert from 'node:assert/strict';import {validateBounds,regionPresets,formatBounds,boxFromPoints} from './geography.mjs';
test('presets contain Bangladesh and global alternatives',()=>{assert.equal(regionPresets[0].id,'BGD');assert.ok(regionPresets.length>=12);for(const p of regionPresets)assert.equal(validateBounds(p.bbox).length,4)});
test('invalid boxes rejected',()=>{for(const b of [[90,20,80,30],[-181,20,40,30],[0,0,0,10],[NaN,0,10,10]])assert.throws(()=>validateBounds(b))});
test('rectangle normalized',()=>{assert.deepEqual(boxFromPoints({lon:10,lat:30},{lon:-20,lat:10}),[-20,10,10,30]);assert.equal(formatBounds([1,2,3,4]),'1.00 / 2.00 / 3.00 / 4.00')});
