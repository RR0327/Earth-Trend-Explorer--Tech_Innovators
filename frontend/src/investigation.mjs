/** Browser-only normalization of NASA Giovanni or date,value monthly CSV exports.
 * Never guess the unit, dataset product, or geographic coverage from a filename.
 */
export function parseMonthlyCsv(input) {
  if (typeof input !== 'string' || input.length > 110000) throw new Error('CSV must be text below 110 KB.');
  const rows = input.replace(/^\uFEFF/, '').split(/\r?\n/).map(line=>line.trim()).filter(Boolean);
  const headerIndex = rows.findIndex(line => /^date\s*,\s*value\s*$/i.test(line) || /^time\s*,\s*mean_[a-zA-Z0-9_]+\s*$/i.test(line));
  if (headerIndex < 0) throw new Error('Expected NASA Giovanni time,mean_… or normalized date,value CSV columns.');
  const observationRows = rows.slice(headerIndex + 1);
  if (observationRows.length > 1000 || observationRows.length < 24) throw new Error('CSV requires 24–1000 monthly observations.');
  const seen = new Set(); const result=[];
  for (const line of observationRows) {
    const cells = line.split(',');
    if (cells.length !== 2) throw new Error('Invalid CSV row: expected two columns.');
    const match = cells[0].trim().match(/^(\d{4})-(\d{2})(?:-\d{2})?(?:[ T].*)?$/);
    if (!match || Number(match[2]) < 1 || Number(match[2]) > 12) throw new Error(`Invalid monthly date: ${cells[0]}`);
    const date = `${match[1]}-${match[2]}`;
    if (seen.has(date)) throw new Error(`Duplicate month: ${date}`);
    seen.add(date);
    const raw = cells[1].trim();
    if (!raw || !/^[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?$/.test(raw)) throw new Error(`Invalid numeric value for ${date}`);
    const value=Number(raw);
    if (!Number.isFinite(value) || Math.abs(value)>=1e14) throw new Error(`Missing or invalid NASA fill-value in ${date}. Export a complete series.`);
    result.push({date,value});
  }
  return result;
}

export const investigatorVariables = [
 {id:'temperature',name:'Air temperature',definition:'Near-surface air temperature at 2 m',product:'MERRA-2',units:['K','degC']},
 {id:'rainfall',name:'Precipitation',definition:'Surface rainfall: daily mean rate or monthly depth',product:'GPM IMERG',units:['mm/day','mm/month']},
 {id:'soil_moisture',name:'Soil moisture',definition:'Soil water storage as mass or equivalent water depth',product:'GLDAS',units:['kg/m2','mm']},
];

export function validateExploration({observations,variable,unit,region,source_url}) {
 if (!Array.isArray(observations) || observations.length < 96) throw new Error('At least eight complete years (96 months) are needed for trend estimation.');
 const v=investigatorVariables.find(item=>item.id===variable);
 if (!v || !v.units.includes(unit)) throw new Error('Select a supported NASA variable and its actual source unit.');
 if (!region || region.trim().length < 3) throw new Error('Describe the sampled study area, not an assumed national estimate.');
 try {const u=new URL(source_url);if (u.protocol!=='https:' || !(u.hostname==='nasa.gov'||u.hostname.endsWith('.nasa.gov'))) throw new Error();} catch {throw new Error('Provide the NASA HTTPS URL from Giovanni or the mission data portal.');}
 return true;
}
