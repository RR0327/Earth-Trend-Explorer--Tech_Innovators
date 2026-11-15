import React from 'react';
import { Earth, Leaf, Satellite } from 'lucide-react';
import { FOOTER_SECTIONS } from './footer-content.mjs';

/** Public, responsive footer. Its internal links target existing app sections. */
export default function SiteFooter() {
  return (
    <footer className="earthtrend-footer" aria-label="EarthTrend Detective website footer">
      <div className="earthtrend-footer-glow earthtrend-footer-glow-left" aria-hidden="true" />
      <div className="earthtrend-footer-glow earthtrend-footer-glow-right" aria-hidden="true" />
      <div className="earthtrend-footer-inner">
        <div className="earthtrend-footer-grid">
          <div className="earthtrend-footer-identity">
            <a href="#overview" className="earthtrend-footer-brand" aria-label="EarthTrend Detective — home">
              <span className="earthtrend-footer-logo"><Earth size={23} aria-hidden="true" /></span>
              <span>EarthTrend <span className="earthtrend-footer-brand-highlight">Detective</span></span>
            </a>
            <p className="earthtrend-footer-description">
              Explore Earth. Investigate environmental change. Follow the evidence.
              Discover meaningful insights from NASA Earth science observations through
              transparent and data-driven research.
            </p>
            <div className="earthtrend-footer-tags">
              <span className="earthtrend-footer-tag earthtrend-footer-tag-leaf"><Leaf size={13} aria-hidden="true" /> Environmental Research</span>
              <span className="earthtrend-footer-tag earthtrend-footer-tag-satellite"><Satellite size={13} aria-hidden="true" /> NASA Data Insights</span>
            </div>
          </div>
          {FOOTER_SECTIONS.map(section => (
            <nav className="earthtrend-footer-column" aria-label={`${section.title} footer links`} key={section.title}>
              <h2>{section.title}</h2>
              <ul>{section.links.map(link => (
                <li key={link.label}>
                  <a href={link.href} {...(link.external ? { target: '_blank', rel: 'noopener noreferrer' } : {})}>{link.label}</a>
                </li>
              ))}</ul>
            </nav>
          ))}
        </div>
        <div className="earthtrend-footer-bottom">
          <div className="earthtrend-footer-meta">
            <p>© {new Date().getFullYear()} Tech_Innovators. All rights reserved.</p>
            <div className="earthtrend-footer-credits">
              <span>Built for a sustainable future</span>
              <span className="earthtrend-footer-separator" aria-hidden="true">•</span>
              <span>NASA Space Apps Challenge</span>
              <span className="earthtrend-footer-separator" aria-hidden="true">•</span>
              <span>Independent Research Project</span>
            </div>
          </div>
          <p className="earthtrend-footer-disclaimer">
            EarthTrend Detective is an independent project and is not affiliated with or endorsed by NASA.
            Environmental trends and statistical associations presented here do not necessarily establish causation.
            No account required for public read-only exploration.
          </p>
        </div>
      </div>
    </footer>
  );
}
