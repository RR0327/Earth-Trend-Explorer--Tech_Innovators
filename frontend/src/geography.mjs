export const regionPresets=[
 {id:'BGD',name:'Bangladesh',continent:'Asia',bbox:[88,20.5,92.7,26.7]},
 {id:'IND',name:'India',continent:'Asia',bbox:[68.1,6.5,97.5,35.5]},
 {id:'BRA',name:'Brazil',continent:'South America',bbox:[-73.99,-33.75,-34.79,5.27]},
 {id:'USA',name:'United States (contiguous)',continent:'North America',bbox:[-124.8,24.4,-66.9,49.4]},
 {id:'CAN',name:'Canada',continent:'North America',bbox:[-141,41.7,-52.6,83.1]},
 {id:'AUS',name:'Australia',continent:'Oceania',bbox:[112.9,-43.8,153.7,-10.7]},
 {id:'ZAF',name:'South Africa',continent:'Africa',bbox:[16.3,-34.9,32.9,-22.1]},
 {id:'KEN',name:'Kenya',continent:'Africa',bbox:[33.9,-4.7,41.9,5.1]},
 {id:'DEU',name:'Germany',continent:'Europe',bbox:[5.9,47.2,15.1,55.1]},
 {id:'JPN',name:'Japan',continent:'Asia',bbox:[122.9,24,145.9,45.6]},
 {id:'IDN',name:'Indonesia',continent:'Asia',bbox:[95,-11.1,141,6.1]},
 {id:'EGY',name:'Egypt',continent:'Africa',bbox:[24.7,21.7,36.9,31.7]},
 {id:'ARG',name:'Argentina',continent:'South America',bbox:[-73.6,-55.1,-53.6,-21.8]},
 {id:'FRA',name:'France (metropolitan)',continent:'Europe',bbox:[-5.2,41.3,9.7,51.1]},
 {id:'GBR',name:'United Kingdom',continent:'Europe',bbox:[-8.7,49.9,2.1,59]},
 {id:'CHN',name:'China',continent:'Asia',bbox:[73.5,18.2,134.8,53.6]},
];
export function validateBounds(v){if(!Array.isArray(v)||v.length!==4||v.some(n=>typeof n!=='number'||!Number.isFinite(n)))throw Error('Four finite bbox coordinates required.');const [w,s,e,n]=v;if(w < -180||e>180||s < -90||n>90||w>=e||s>=n)throw Error('Expected west < east and south < north, within the world coordinate limits.');return v;}
export function formatBounds(b){return b.map(n=>Number(n).toFixed(2)).join(' / ');}
export function boxFromPoints(a,b){return [Math.min(a.lon,b.lon),Math.min(a.lat,b.lat),Math.max(a.lon,b.lon),Math.max(a.lat,b.lat)].map(x=>Math.round(x*1000)/1000);}
export function pointToLonLat(e){const r=e.currentTarget?.getBoundingClientRect?.();if(!r||!r.width||!r.height)return null;const x=Math.max(0,Math.min(1,(e.clientX-r.left)/r.width)),y=Math.max(0,Math.min(1,(e.clientY-r.top)/r.height));return {lon:Math.round((x*360-180)*1000)/1000,lat:Math.round((90-y*180)*1000)/1000};}
