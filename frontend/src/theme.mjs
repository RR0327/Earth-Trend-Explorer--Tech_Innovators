/** Theme-only UI state. Never affects observations or statistical computation. */
export const THEMES = Object.freeze(['dark', 'light']);
export const nextTheme = current => current === 'dark' ? 'light' : 'dark';
export const isTheme = value => THEMES.includes(value);
export function getInitialTheme() {
  try {
    const saved = window.localStorage.getItem('earthtrace-theme');
    if (isTheme(saved)) return saved;
    return window.matchMedia?.('(prefers-color-scheme: light)')?.matches ? 'light' : 'dark';
  } catch { return 'dark'; }
}
export function persistTheme(theme) {
  if (!isTheme(theme)) return false;
  try { window.localStorage.setItem('earthtrace-theme', theme); return true; }
  catch { return false; }
}
