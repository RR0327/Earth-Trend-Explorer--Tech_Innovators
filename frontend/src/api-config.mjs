/** Production builds must never call a visitor's localhost API. */
export function resolveApiBase(configured, development) {
  const url = String(configured || '').trim().replace(/\/+$/, '');
  if (!url) return development ? 'http://127.0.0.1:8000' : '';
  if (!/^https?:\/\//.test(url)) return '';
  if (!development && !url.startsWith('https://')) return '';
  return url;
}
