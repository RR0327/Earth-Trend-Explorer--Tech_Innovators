import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

test('Google Fonts CSS import precedes design-token rules', () => {
  const css = readFileSync(new URL('./style.css', import.meta.url), 'utf8');
  const importIndex = css.indexOf('@import url(');
  const firstRule = css.indexOf(':root');
  assert.equal(importIndex, 0);
  assert.ok(firstRule > importIndex);
  assert.equal((css.match(/@import url\(/g) ?? []).length, 1);
});
