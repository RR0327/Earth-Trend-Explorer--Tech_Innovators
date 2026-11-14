import React, {useCallback, useEffect, useState} from 'react';
import {Database, AlertCircle, CheckCircle2, RefreshCw, ExternalLink} from 'lucide-react';
import {productStatus, coverageVerdict} from './research-catalog.mjs';

export default function ResearchCatalog({apiBase}) {
  const [catalog,setCatalog] = useState(null);
  const [error,setError] = useState('');
  const [pending,setPending] = useState(false);
  const [chosen,setChosen] = useState('');
  const [preview,setPreview] = useState(null);
  const [previewError,setPreviewError] = useState('');
  const reload=useCallback(async()=>{
    if(!apiBase){setError('Set the production VITE_API_URL to load the NASA catalogue.');return;}
    setPending(true);setError('');
    try{
      const response=await fetch(`${apiBase}/api/catalog/products`);
      if(!response.ok)throw new Error(`Catalog request failed (${response.status})`);
      const result=await response.json();
      if(!Array.isArray(result.products))throw new Error('Unexpected catalog response');
      setCatalog(result);
      setChosen(old=>old||result.products.flatMap(p=>p.installed_dataset_ids||[])[0]||'');
    }catch(err){setError(err.message||'Catalog is unavailable');}
    finally{setPending(false);}
  },[apiBase]);
  useEffect(()=>{reload();},[reload]);
  async function inspect(){
    if(!chosen)return;
    setPending(true);setPreviewError('');setPreview(null);
    try{
      const response=await fetch(`${apiBase}/api/data/preview`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({dataset_id:chosen})});
      const body=await response.json();
      if(!response.ok)throw new Error(typeof body.detail==='string'?body.detail:'Could not preview this dataset');
      setPreview(body);
    }catch(err){setPreviewError(err.message||'Preview unavailable');}
    finally{setPending(false);}
  }
  return <section className="panel research-catalog" id="product-catalog" aria-labelledby="research-catalog-heading">
    <div className="section-heading"><div><div className="eyebrow">NASA DATA CAPABILITIES / VERIFIED AVAILABILITY</div><h2 id="research-catalog-heading">Research product catalogue</h2></div><button type="button" className="research-refresh" disabled={pending} onClick={reload}><RefreshCw size={15}/> Refresh</button></div>
    <p className="global-intro">A NASA product being documented does not mean its observations have been downloaded. This catalogue separates supported analysis formats from actual locally installed data.</p>
    {error&&<div className="alert danger" role="alert"><AlertCircle size={16}/>{error}</div>}
    {catalog&&<><div className="research-product-grid">{catalog.products.map(product=><article className="research-product" key={product.id}>
      <div className="research-product-name"><Database size={17}/><strong>{product.family}</strong></div>
      <div className="research-product-variable">{product.variable.replace('_',' ')} · {product.temporal_resolution}</div>
      <div className="research-product-state"><CheckCircle2 size={14}/>{productStatus(product)}</div>
      <p>{product.note}</p>
      <a href={product.documentation_url} target="_blank" rel="noreferrer">NASA product documentation <ExternalLink size={13}/></a>
    </article>)}</div>
      {catalog.products.some(p=>p.installed_dataset_ids?.length>0)&&<div className="research-preview-controls">
        <label htmlFor="research-dataset-selector">Preview an actually installed time series</label>
        <select id="research-dataset-selector" value={chosen} onChange={e=>{setChosen(e.target.value);setPreview(null);}}>{catalog.products.flatMap(p=>p.installed_dataset_ids||[]).map(id=><option key={id} value={id}>{id}</option>)}</select>
        <button type="button" onClick={inspect} disabled={pending||!chosen}>Inspect source coverage</button>
      </div>}
      {previewError&&<div className="alert danger" role="alert">{previewError}</div>}
      {preview&&<div className="research-preview-output" role="status"><strong>{coverageVerdict(preview)}</strong><span>Source coverage: {preview.source_region}</span><span>Measured period: {preview.actual_first_month} to {preview.actual_last_month} · Missing months in requested years: {preview.missing_month_count}</span><span>{preview.coverage_warning}</span></div>}
    </>}
  </section>;
}
