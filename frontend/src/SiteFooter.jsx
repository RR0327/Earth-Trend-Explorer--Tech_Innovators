import React from 'react';
import {Globe2,ExternalLink,ArrowUpRight,Database,ShieldCheck,BookOpen,Mail} from 'lucide-react';
import {FOOTER_SECTIONS, FOOTER_EXTERNAL} from './footer-content.mjs';

export default function SiteFooter(){
 const year=new Date().getFullYear();
 return <footer className="etd-site-footer" aria-label="EarthTrend Detective website footer">
  <div className="etd-footer-top">
   <div className="etd-footer-mission">
    <a className="etd-footer-brand" href="#overview" aria-label="EarthTrend Detective — back to overview"><span className="etd-footer-symbol"><Globe2 size={22}/></span><span><strong>EARTH<span>TRACE</span></strong><small>EARTH SYSTEM TREND DETECTIVE</small></span></a>
    <p>Explore environmental evidence with NASA Earth science observations, transparent statistical methods and reproducible research workflows.</p>
    <p className="etd-footer-clarifier"><ShieldCheck size={16}/> Independent educational and research project; not an official NASA website or NASA endorsement.</p>
    <p className="etd-footer-clarifier"><Database size={16}/> No account required. Public read-only exploration. Imported data must match the stated study region and source product.</p>
   </div>
   <div className="etd-footer-directory">
   {FOOTER_SECTIONS.map(section=><section className="etd-footer-column" key={section.title}><h2>{section.title}</h2><ul>{section.links.map(link=><li key={link.label}>{link.external?<a href={link.href} target="_blank" rel="noopener noreferrer">{link.label} <ExternalLink aria-hidden="true" size={12}/></a>:<a href={link.href}>{link.label}</a>}</li>)}</ul></section>)}
   </div>
  </div>
  <div className="etd-footer-facts" aria-label="Scientific context"><span><BookOpen size={15}/> MERRA-2 / GPM IMERG / GLDAS documented NASA families</span><span><ShieldCheck size={15}/> Source-dependent geography, coverage and units</span><span>p-value is not proof of causation</span></div>
  <div className="etd-footer-bottom"><span>© {year} EarthTrend Detective · EarthTrace research interface</span><span>Bangladesh is the curated demonstration, not a global dataset.</span><a href="#overview">Back to top <ArrowUpRight size={14}/></a></div>
 </footer>
}
