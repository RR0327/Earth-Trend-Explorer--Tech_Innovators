import React,{useMemo,useState} from 'react';
import {BookOpen,CheckCircle2,ChevronDown,Database,ExternalLink,FileUp,Globe2,Info,Lightbulb,MapPin,Microscope,Play,RotateCcw,Satellite,ShieldAlert,Target} from 'lucide-react';
import {parseMonthlyCsv,investigatorVariables,validateExploration} from './investigation.mjs';

const GIOVANNI='https://giovanni.gsfc.nasa.gov/giovanni/';
const PRODUCT_GUIDES={temperature:'Search MERRA-2 monthly 2-meter air temperature (T2M).',rainfall:'Search GPM IMERG monthly precipitation. Check whether the exported numbers are rates or depths.',soil_moisture:'Search GLDAS monthly soil moisture. Check model layer and water-equivalent unit.'};
function detectSpatialNotes(text) {
 const data=text.match(/^Data Bounding Box:\s*,\s*"?([^"\r\n]+)/im);
 const requested=text.match(/^User Bounding Box:\s*,\s*"?([^"\r\n]+)/im);
 return {sampled:data?.[1]?.trim()||'',requested:requested?.[1]?.trim()||''};
}
export default function InvestigationLab({apiBase,onExplored,onRestore,hasCurated}) {
 const [variable,setVariable]=useState('temperature');
 const config=investigatorVariables.find(v=>v.id===variable);
 const [unit,setUnit]=useState('K');
 const [region,setRegion]=useState('');
 const [sourceUrl,setSourceUrl]=useState(GIOVANNI);
 const [file,setFile]=useState(null);
 const [observations,setObservations]=useState([]);
 const [spatial,setSpatial]=useState({sampled:'',requested:''});
 const [startYear,setStartYear]=useState('');
 const [endYear,setEndYear]=useState('');
 const [working,setWorking]=useState(false);
 const [problem,setProblem]=useState('');
 const [success,setSuccess]=useState(false);
 const years=useMemo(()=>[...new Set(observations.map(r=>r.date.slice(0,4)))].sort(),[observations]);
 function updateVariable(id){setVariable(id);setUnit(investigatorVariables.find(v=>v.id===id)?.units[0]||'');setProblem('');setSuccess(false)}
 async function selectFile(event){
  setProblem('');setSuccess(false);setObservations([]);
  const next=event.target.files?.[0];setFile(next||null);
  if(!next)return;
  if(next.size>110000){setProblem('CSV exceeds 110 KB. Use a monthly time series of at most 1000 months.');return;}
  try {
   const contents=await next.text();const parsed=parseMonthlyCsv(contents);
   setObservations(parsed);setStartYear(parsed[0].date.slice(0,4));setEndYear(parsed[parsed.length-1].date.slice(0,4));
   const bounds=detectSpatialNotes(contents);setSpatial(bounds);
   if(bounds.sampled)setRegion(`Giovanni sampled grid bounding box: ${bounds.sampled}`);
  }catch(e){setProblem(e.message)}
 }
 async function run(event){
  event.preventDefault();setProblem('');setSuccess(false);
  const first=Number(startYear),last=Number(endYear);
  const payload={variable,product:config.product,unit,region,source_url:sourceUrl,observations,start_year:first,end_year:last};
  try{validateExploration(payload);if(first>last)throw new Error('Start year must not exceed end year.');}
  catch(e){setProblem(e.message);return;}
  if(!apiBase){setProblem('Set VITE_API_URL for this deployed application.');return;}
  setWorking(true);
  try{
   const response=await fetch(`${apiBase}/api/explore`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
   const body=await response.json();
   if(!response.ok)throw new Error(typeof body.detail==='string'?body.detail:`Analysis failed (${response.status}).`);
   onExplored(body);setSuccess(true);
   document.getElementById('analysis')?.scrollIntoView({behavior:'smooth'});
  }catch(e){setProblem(e.message||'Unable to analyze.');}
  finally{setWorking(false)}
 }
 return <section className="investigator panel" id="investigate" aria-labelledby="investigate-heading">
   <div className="lab-header"><div><div className="eyebrow"><Satellite size={15}/> CHALLENGE OBJECTIVE / INTERACTIVE INVESTIGATION</div><h2 id="investigate-heading">Start your own Earth investigation</h2><p>Choose a NASA variable and study area, upload a monthly Giovanni time series, then test how strongly the evidence supports a trend.</p></div><div className="lab-top-icon"><Target size={28}/></div></div>
   <div className="investigation-path" aria-label="Investigation steps"><span><b>01</b> Select variable</span><span><b>02</b> Choose geography</span><span><b>03</b> Add NASA observations</span><span><b>04</b> Test the trend</span></div>
   <form className="investigator-form" onSubmit={run}>
    <div className="lab-row"><div className="lab-field"><label htmlFor="investigate-variable">Earth science variable</label><div className="lab-input-wrap"><select id="investigate-variable" value={variable} onChange={e=>updateVariable(e.target.value)}>{investigatorVariables.map(v=><option value={v.id} key={v.id}>{v.name} · {v.product}</option>)}</select><ChevronDown size={16}/></div><span className="field-caption">{config.definition}</span></div>
     <div className="lab-field"><label htmlFor="investigate-unit">Original NASA export unit</label><div className="lab-input-wrap"><select id="investigate-unit" value={unit} onChange={e=>setUnit(e.target.value)}>{config.units.map(x=><option key={x} value={x}>{x}</option>)}</select><ChevronDown size={16}/></div><span className="field-caption">The unit must match the downloaded source, not your preferred chart unit.</span></div></div>
    <div className="lab-field"><label htmlFor="investigate-region"><MapPin size={15}/> Actual study area / sampled grid</label><input id="investigate-region" value={region} maxLength={180} onChange={e=>setRegion(e.target.value)} placeholder="Example: Giovanni sampled grid at 91.25°E, 23–23.5°N" required/><span className="field-caption">Describe the actual <b>Data Bounding Box</b>; it may be smaller than the region you requested.</span></div>
    <div className="lab-field"><label htmlFor="investigate-source"><Globe2 size={15}/> NASA source or Giovanni reproduction URL</label><input id="investigate-source" type="url" value={sourceUrl} onChange={e=>setSourceUrl(e.target.value)} required/><span className="field-caption">Only nasa.gov HTTPS source URLs are accepted. Entering one does not authenticate the uploaded observations.</span></div>
    <div className="lab-upload"><label htmlFor="investigate-file"><FileUp size={24}/><strong>{file?file.name:'Upload NASA Giovanni CSV'}</strong><span>Raw Giovanni time,mean_… or normalized date,value · max 110 KB</span></label><input id="investigate-file" type="file" accept=".csv,text/csv" onChange={selectFile}/></div>
    {spatial.sampled&&<div className="lab-spatial"><MapPin size={16}/> <span>Giovanni data grid: <strong>{spatial.sampled}</strong>{spatial.requested&&<> · originally requested: {spatial.requested}</>}</span></div>}
    {observations.length>0&&<div className="lab-preview"><CheckCircle2 size={18}/><span>{observations.length} monthly records parsed · {observations[0].date} to {observations[observations.length-1].date}. Not independently authenticated.</span></div>}
    <div className="lab-row"><div className="lab-field"><label htmlFor="investigate-first">Start year</label><div className="lab-input-wrap"><select id="investigate-first" value={startYear} onChange={e=>setStartYear(e.target.value)} disabled={!years.length}>{!years.length&&<option value="">Upload CSV first</option>}{years.map(y=><option value={y} key={y}>{y}</option>)}</select><ChevronDown size={16}/></div></div><div className="lab-field"><label htmlFor="investigate-last">End year</label><div className="lab-input-wrap"><select id="investigate-last" value={endYear} onChange={e=>setEndYear(e.target.value)} disabled={!years.length}>{!years.length&&<option value="">Upload CSV first</option>}{years.map(y=><option value={y} key={y}>{y}</option>)}</select><ChevronDown size={16}/></div></div></div>
    <div className="lab-actions"><button className="lab-submit" type="submit" disabled={working||!observations.length}><Microscope size={17}/>{working?'Calculating…':'Analyze this investigation'}</button>{hasCurated&&<button className="lab-reset" type="button" onClick={()=>{onRestore();setSuccess(false);document.getElementById('analysis')?.scrollIntoView({behavior:'smooth'});}}><RotateCcw size={16}/> Restore curated example</button>}</div>
    {problem&&<div role="alert" className="lab-error"><ShieldAlert size={18}/>{problem}</div>}
    {success&&<div role="status" className="lab-success"><CheckCircle2 size={18}/> Investigation analyzed. Charts below now show your visitor-supplied dataset; it has not been saved to the server.</div>}
   </form>
   <div className="lab-guidance"><div className="lab-guidance-icon"><Lightbulb size={20}/></div><div><strong>How to collect suitable NASA observations</strong><p>{PRODUCT_GUIDES[variable]} Use <a href={GIOVANNI} target="_blank" rel="noopener noreferrer">NASA Giovanni <ExternalLink size={12}/></a> to generate a monthly area-average time series, export CSV, and check its original unit and sampled data bounds. Choose a sufficiently long record (at least eight full years). Avoid mixing unrelated regions or variables.</p></div></div>
   <p className="lab-integrity"><Info size={15}/> Visitor uploads are processed in memory, never saved or added to the public data catalog. A NASA URL is not proof of data authenticity. No automatic source retrieval or geographic interpolation is implied.</p>
  </section>
}
