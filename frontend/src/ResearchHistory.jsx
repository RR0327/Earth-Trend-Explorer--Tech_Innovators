import React,{useEffect,useState} from 'react';
import {BookOpen,RefreshCw,FileText,ShieldCheck,Database} from 'lucide-react';
import {safeHistoryPayload,researchReportPath,hasPublishedResearchError} from './research-history.mjs';

export default function ResearchHistory({apiBase}){
 const [records,setRecords]=useState([]),[total,setTotal]=useState(0),[offset,setOffset]=useState(0);
 const [busy,setBusy]=useState(false),[error,setError]=useState(''),[unavailable,setUnavailable]=useState(false);
 const [selected,setSelected]=useState(null),[expanded,setExpanded]=useState(''),[explanation,setExplanation]=useState(null);
 const pageSize=10;
 useEffect(()=>{
  const controller=new AbortController();if(!apiBase)return;
  setBusy(true);setError('');
  fetch(`${apiBase}/api/research/history?limit=${pageSize}&offset=${offset}`,{signal:controller.signal})
   .then(async r=>{if(!r.ok){if(hasPublishedResearchError(r.status)){setUnavailable(true);return null;}throw new Error(`Research history request failed (${r.status})`)}return r.json()})
   .then(data=>{if(!data||controller.signal.aborted)return;setUnavailable(false);setRecords(safeHistoryPayload(data));setTotal(data.total)})
   .catch(err=>{if(err.name!=='AbortError')setError(err.message)})
   .finally(()=>{if(!controller.signal.aborted)setBusy(false)});
  return()=>controller.abort();
 },[apiBase,offset]);
 async function show(researchId){
   if(expanded===researchId){setExpanded('');return;}
   setError('');setExplanation(null);try{const r=await fetch(`${apiBase}/api/research/${researchId}`);if(!r.ok)throw Error(`Record unavailable (${r.status})`);
    const body=await r.json();if(body.research_id!==researchId||!Array.isArray(body.studies))throw Error('Unexpected research record');setSelected(body);setExpanded(researchId);try{const e=await fetch(`${apiBase}/api/research/${researchId}/explanation`);if(e.ok){const grounded=await e.json();if(grounded.research_id===researchId)setExplanation(grounded)}}catch(_err){}
   }catch(err){setError(err.message)}
 }
 return <section className="panel research-history" id="research" aria-labelledby="research-title">
   <div className="eyebrow"><BookOpen size={16}/> VERIFIED WORKSPACE / READ-ONLY ARCHIVE</div>
   <div className="research-history-head"><div><h2 id="research-title">Published research library</h2><p className="global-intro">Explore reproducible multi-region analyses approved for public release. Original source files stay private; published results preserve SHA256 and scientific limitations.</p></div><Database size={24}/></div>
   {unavailable?<div className="research-history-message"><ShieldCheck size={20}/><div><strong>Research publication is not enabled on this deployment.</strong><p>Local researchers can create verified SQLite records using the backend CLI. An administrator can publish a reviewed archive when durable storage is configured. No login is required for public datasets or analysis.</p></div></div>:
   <>
    {busy&&<p role="status" className="research-history-message"><RefreshCw size={16}/> Loading verified research history…</p>}
    {!busy&&!records.length&&!error&&<p className="research-history-message">No published studies yet. The existing NASA datasets, investigation and comparison features are still available above.</p>}
    <div className="research-history-list">{records.map(record=><article className="research-history-item" key={record.research_id}><div><small>{record.product_id} · {record.study_count} regions</small><h3>{record.regions}</h3><span>{record.created_at?.slice(0,10)} · Research ID {record.research_id.slice(0,12)}…</span></div><div className="research-history-actions"><button type="button" aria-expanded={expanded===record.research_id} onClick={()=>show(record.research_id)}>{expanded===record.research_id?'Hide':'Inspect'}</button><a href={`${apiBase}${researchReportPath(record.research_id)}`} target="_blank" rel="noopener noreferrer" aria-label={`PDF report for ${record.regions}`}><FileText size={15}/> PDF</a></div>{expanded===record.research_id&&selected?.research_id===record.research_id&&<div className="research-history-detail"><p>Processing: {selected.processing_version}. Observations and statistics are tied to the content SHA256 digest.</p>{selected.studies.map(st=><p key={st.region_id}><strong>{st.name}</strong> · {st.observations?.length} monthly records · {st.trend_status} · Sen slope: {st.trend?.sen_slope?.slope_per_year??'Unavailable'}</p>)}{explanation?.research_id===record.research_id&&<div className="research-grounded-explanation"><h4>Evidence-based interpretation</h4>{explanation.studies.map(st=><p key={st.region_id}>{st.region_name}: {st.summary}</p>)}<small>No AI-generated measurements. Results are derived from the verified research record.</small></div>}<p className="research-history-limitation">{selected.limitations?.[0]}</p></div>}</article>)}</div>
    {total>pageSize&&<div className="research-history-pages"><button disabled={offset===0||busy} onClick={()=>setOffset(v=>Math.max(0,v-pageSize))}>Previous</button><span>{offset+1}–{Math.min(total,offset+pageSize)} of {total}</span><button disabled={offset+pageSize>=total||busy} onClick={()=>setOffset(v=>v+pageSize)}>Next</button></div>}
   </>}
   {error&&<p role="alert" className="lab-error">{error}</p>}
 </section>
}
