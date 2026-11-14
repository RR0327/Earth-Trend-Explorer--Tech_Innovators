import React,{useEffect,useMemo,useState} from 'react';
import {Globe2,MapPin,Search,Info,Move,ExternalLink,Check,Compass} from 'lucide-react';
import {validateBounds,formatBounds,regionPresets,pointToLonLat,boxFromPoints} from './geography.mjs';

const GIOVANNI='https://giovanni.gsfc.nasa.gov/giovanni/';
// This is a geographic selection canvas with graticule and schematic landmasses,
// NOT a scientific NASA raster map or accurate country-boundary shapefile.
const landShapes=[
 'M48 45 L74 28 105 24 124 38 118 58 103 67 94 88 76 92 65 75 48 67Z',
 'M102 98 L131 91 151 115 143 150 133 182 116 205 108 171 98 147Z',
 'M164 41 L192 31 225 35 245 23 290 27 316 44 350 48 354 65 330 76 302 68 284 93 249 85 228 64 200 64 182 77 165 65Z',
 'M199 86 L240 89 258 110 243 147 225 176 204 159 194 124Z',
 'M305 148 L335 140 349 161 338 178 304 173Z',
 'M347 83 L355 91 352 105 344 99Z'
];
export default function GlobalExplorer({onSelect,onPowered,apiBase}){
 const [liveBusy,setLiveBusy]=useState(false),[liveError,setLiveError]=useState('');
 const [search,setSearch]=useState('');const [country,setCountry]=useState('BGD');const [mode,setMode]=useState('preset');
 const [bounds,setBounds]=useState(regionPresets[0].bbox);const [drag,setDrag]=useState(null);const [issue,setIssue]=useState('');
 const visible=useMemo(()=>regionPresets.filter(r=>(r.name+' '+r.continent).toLowerCase().includes(search.toLowerCase())),[search]);
 const selected=regionPresets.find(r=>r.id===country);
 function selectRegion(id){const r=regionPresets.find(r=>r.id===id);if(!r)return;setCountry(id);setBounds([...r.bbox]);setMode('preset');setIssue('');onSelect({name:r.name,bbox:[...r.bbox],kind:'approximate country bounding box'});}
 function down(e){const p=pointToLonLat(e);if(!p)return;setMode('custom');setDrag(p);try{e.currentTarget.setPointerCapture(e.pointerId);}catch{}}
 function up(e){if(!drag)return;const p=pointToLonLat(e);setDrag(null);if(!p)return;const box=boxFromPoints(drag,p);try{validateBounds(box);setBounds(box);setIssue('');onSelect({name:'Custom rectangular area',bbox:box,kind:'custom bounding box'});}catch(err){setIssue(err.message)}}
 function edit(index,value){const next=[...bounds];next[index]=Number(value);setBounds(next);setMode('custom');try{validateBounds(next);setIssue('');onSelect({name:'Custom rectangular area',bbox:next,kind:'custom bounding box'});}catch(e){setIssue(e.message)}}
 function posX(lon){return ((lon+180)/360)*400} function posY(lat){return ((90-lat)/180)*220}
 const rect=drag?boxFromPoints(drag,drag):bounds;
 async function analyzePoint(){setLiveBusy(true);setLiveError('');const lat=(bounds[1]+bounds[3])/2,lon=(bounds[0]+bounds[2])/2;try{if(!apiBase)throw Error('The deployed API URL is not configured.');const response=await fetch(`${apiBase}/api/nasa-power/point?latitude=${encodeURIComponent(lat.toFixed(4))}&longitude=${encodeURIComponent(lon.toFixed(4))}&start_year=2001&end_year=2024`);const result=await response.json();if(!response.ok)throw Error(typeof result.detail==='string'?result.detail:'NASA POWER request failed.');onPowered?.(result);document.getElementById('analysis')?.scrollIntoView({behavior:'smooth'});}catch(err){setLiveError(err.message);}finally{setLiveBusy(false)}}
 return <section id="global" className="panel global-panel"><div className="section-heading"><div><div className="eyebrow"><Globe2 size={15}/> GLOBAL STUDY AREA / MISSION SETUP</div><h2>Explore beyond one country.</h2><p className="global-intro">Select an approximate country extent or draw a custom rectangle. Next, export the matching NASA time series from Giovanni to analyze it.</p></div><span className="mini-tag"><Compass size={14}/> Global-ready workflow</span></div>
 <div className="geo-grid"><div className="geo-map-wrap"><svg className="geo-map" viewBox="0 0 400 220" role="img" aria-label="Schematic world map with graticule. Drag a rectangle to select geographic coordinates." onPointerDown={down} onPointerUp={up} onPointerCancel={()=>setDrag(null)}>
 <rect width="400" height="220" rx="13" fill="#0a2637"/>
 {[-120,-60,0,60,120].map(x=><line key={'lon'+x} x1={posX(x)} x2={posX(x)} y1="0" y2="220" stroke="#4ba5b3" opacity=".19" strokeDasharray="2 5"/>)}
 {[-60,-30,0,30,60].map(y=><line key={'lat'+y} x1="0" x2="400" y1={posY(y)} y2={posY(y)} stroke="#4ba5b3" opacity=".19" strokeDasharray="2 5"/>)}
 {landShapes.map((d,i)=><path key={i} d={d} fill="#1b6573" stroke="#3c8796" strokeWidth=".8" opacity=".84"/>)}
 <rect x={posX(rect[0])} y={posY(rect[3])} width={Math.max(1,posX(rect[2])-posX(rect[0]))} height={Math.max(1,posY(rect[1])-posY(rect[3]))} fill="#2fe3d4" fillOpacity=".22" stroke="#63ffdd" strokeWidth="1.6" strokeDasharray="4 3"/>
 </svg><div className="geo-map-caption"><Move size={14}/> Drag to select a box · schematic map, not boundary geometry</div></div>
 <div className="geo-control"><label htmlFor="region-search">Search geographic presets</label><div className="geo-search"><Search size={17}/><input id="region-search" value={search} onChange={e=>setSearch(e.target.value)} placeholder="Bangladesh, Brazil, Kenya…"/></div><label htmlFor="region-preset">Country preset</label><select id="region-preset" value={country} onChange={e=>selectRegion(e.target.value)}>{visible.length?visible.map(r=><option key={r.id} value={r.id}>{r.name} · {r.continent}</option>):<option value="">No matches</option>}</select><div className="geo-bounds"><span>West</span><span>South</span><span>East</span><span>North</span>{bounds.map((v,i)=><input aria-label={['West longitude','South latitude','East longitude','North latitude'][i]} key={i} type="number" min={i%2===0?-180:-90} max={i%2===0?180:90} step="0.1" value={v} onChange={e=>edit(i,e.target.value)}/>)}</div><div className="geo-selected"><MapPin size={16}/><div><b>{mode==='preset'?selected?.name:'Custom rectangle'}</b><span>{formatBounds(bounds)}</span></div></div>{issue&&<p className="geo-error" role="alert">{issue}</p>}<button type="button" className="geo-live" disabled={liveBusy||!!issue} onClick={analyzePoint}>{liveBusy?"Retrieving NASA monthly data…":"Analyze NASA POWER point · 2001–2024"}</button>{liveError&&<p role="alert" className="geo-error">{liveError}</p>}<a className="geo-nasa-link" target="_blank" rel="noopener noreferrer" href={GIOVANNI}>Open NASA Giovanni <ExternalLink size={15}/></a></div></div>
 <div className="geo-disclaimer"><Info size={17}/><span><b>Scientific safeguard:</b> Preset boxes are approximate and do not represent country polygons. Use the NASA POWER button to fetch an actual monthly temperature series at the selected box center (a point/grid observation, not an area average). For country or polygon-average studies, export the matching study-area time series in Giovanni and verify its sampled grid before analysis.</span></div></section>;
}
