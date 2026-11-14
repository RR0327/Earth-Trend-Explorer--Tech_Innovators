import test from 'node:test';
import assert from 'node:assert/strict';
import {resolveApiBase} from './api-config.mjs';

test('local development uses explicit local API fallback',()=>{
  assert.equal(resolveApiBase('',true),'http://127.0.0.1:8000');
});
test('production refuses missing API configuration',()=>{
  assert.equal(resolveApiBase('',false),'');
});
test('production requires HTTPS',()=>{
  assert.equal(resolveApiBase('http://api.example.com',false),'');
  assert.equal(resolveApiBase('https://api.example.com/',false),'https://api.example.com');
});
test('non-URL production values are rejected',()=>{
  assert.equal(resolveApiBase('/api',false),'');
});
