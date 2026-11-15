import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { FOOTER_SECTIONS, FOOTER_EXTERNAL } from './footer-content.mjs';

test('footer navigation uses real in-app sections', () => {
  assert.deepEqual(FOOTER_SECTIONS.map(section => section.title), ['Explore', 'Resources']);
  assert.deepEqual(FOOTER_SECTIONS[0].links.map(link => link.href), ['#overview', '#global', '#compare', '#research']);
});

test('NASA and Natural Earth resource links have safe HTTPS URLs', () => {
  assert.equal(FOOTER_EXTERNAL.length, 4);
  for (const link of FOOTER_EXTERNAL) {
    assert.match(link.href, /^https:\/\//);
    assert.ok(!link.href.includes('example.com'));
  }
});

test('footer component has required disclaimer, copyright and secure external links', () => {
  const source = readFileSync(new URL('./SiteFooter.jsx', import.meta.url), 'utf8');
  assert.match(source, /not affiliated with or endorsed by NASA/);
  assert.match(source, /do not necessarily establish causation/);
  assert.match(source, /new Date\(\)\.getFullYear\(\)/);
  assert.match(source, /noopener noreferrer/);
  assert.match(source, /Environmental Research/);
  assert.match(source, /NASA Data Insights/);
});
