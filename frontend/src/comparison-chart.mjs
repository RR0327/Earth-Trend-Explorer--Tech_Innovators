export function sharedYearChartData(result){
 if (!result || !Array.isArray(result.studies) || result.studies.length!==2) return [];
 const [a,b]=result.studies;
 const ay = new Map((a.annual_series||[]).map(row=>[row.year,row.value]));
 const by = new Map((b.annual_series||[]).map(row=>[row.year,row.value]));
 return [...ay.keys()].filter(year=>by.has(year)&&Number.isFinite(ay.get(year))&&Number.isFinite(by.get(year)))
  .sort((x,y)=>x-y).map(year=>({year,regionA:ay.get(year),regionB:by.get(year)}));
}
export function comparisonPeriodLabel(result){
 if (!result || result.shared_year_count<8) return 'Insufficient shared complete years';
 return `${result.shared_first_year}–${result.shared_last_year}: ${result.shared_year_count} shared complete years`;
}
