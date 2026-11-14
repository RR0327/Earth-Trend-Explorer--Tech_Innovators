import test from 'node:test';
import assert from 'node:assert/strict';
import {FOOTER_SECTIONS} from './footer-content.mjs';
test('footer contains project-specific exploration, data and resource sections',()=>{
 assert.equal(FOOTER_SECTIONS.length,3);
 assert.deepEqual(FOOTER_SECTIONS.map(x=>x.title),['EXPLORE','DATA & SCIENCE','PROJECT & RESOURCES']);
 assert.ok(FOOTER_SECTIONS.some(s=>s.links.some(l=>l.href==='#investigate')));
});
test('footer does not invent external links or untrusted schemes',()=>{
 for(const s of FOOTER_SECTIONS)for(const l of s.links){
  assert.ok(l.label.trim().length>5);
  assert.ok(l.external ? l.href.startsWith('https://') : l.href.startsWith('#'));
  assert.ok(!l.href.includes('example.com'));
 }
});
