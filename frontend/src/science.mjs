/** Presentation helpers; do not alter scientific results. */
export const number = (value, digits = 4) => typeof value === 'number' && Number.isFinite(value) ? value.toFixed(digits) : 'N/A';
export const changeDirection = slope => slope > 0 ? 'Increasing' : slope < 0 ? 'Decreasing' : 'No directional change';
export const significance = trend => trend?.mann_kendall?.significant_at_0_05 === true ? 'Statistically significant' : trend?.mann_kendall?.significant_at_0_05 === false ? 'Not statistically significant' : 'Undetermined';
export const seriesFor = (dataset, trend, view) => view === 'annual' ? (trend?.annual_series ?? []) : (dataset?.observations ?? []);
export const annualRange = trend => trend ? `${trend.first_year}–${trend.last_year}` : '—';
export const safeExternalUrl = (value) => {
  try { const u = new URL(value); return u.protocol === 'https:' ? u.href : null; } catch { return null; }
};
export const safeFilename = name => String(name || 'analysis').replace(/[^a-zA-Z0-9_-]+/g, '_').slice(0, 90);
