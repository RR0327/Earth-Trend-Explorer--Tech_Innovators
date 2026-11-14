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

/** Calendar-month averages from actual observations only; missing months stay absent. */
export function seasonalClimatology(data){
 const groups=Array.from({length:12},()=>[]);
 for(const point of data?.observations||[]){const m=Number(String(point.date).slice(5,7));const v=Number(point.value);if(Number.isInteger(m)&&m>=1&&m<=12&&Number.isFinite(v))groups[m-1].push(v);}
 const names=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
 return groups.map((values,i)=>({month:names[i],mean:values.length?Math.round(values.reduce((a,b)=>a+b,0)/values.length*10000)/10000:null,count:values.length}));
}
