"""Opt-in read-only publication of already-approved, content-addressed studies.

This service NEVER runs NetCDF code, accepts uploads, or creates research runs.
Public publishing requires an administrator-selected SQLite file on durable storage.
"""
from __future__ import annotations

import io
import os
import re
import sqlite3
from pathlib import Path
from xml.sax.saxutils import escape

from services.research_workspace import load_workspace, ResearchValidationError

ID_PATTERN = re.compile(r'^[0-9a-f]{64}$')


class PublicationError(ValueError):
    pass


def publication_status():
    """Non-sensitive readiness information. Does not expose filesystem paths."""
    if os.getenv('EARTH_TREND_RESEARCH_PUBLIC', '').strip() != '1':
        return {'enabled': False, 'state': 'disabled', 'record_count': None,
                'next_action': 'An administrator must approve and enable a reviewed research database.'}
    raw = os.getenv('EARTH_TREND_RESEARCH_DB', '').strip()
    if not raw:
        return {'enabled': True, 'state': 'not_configured', 'record_count': None,
                'next_action': 'Set EARTH_TREND_RESEARCH_DB to an existing reviewed SQLite file.'}
    from services.nasa_source_setup import inspect_research_db
    status = inspect_research_db(raw)
    state = status['status']
    instructions = {'missing':'The configured database file does not exist; build a real research record first.',
                    'uninitialized':'The SQLite file has no research_runs table; use the trusted research CLI.',
                    'empty':'No published research runs yet; build and review one first.',
                    'unreadable':'The database cannot be read; inspect permissions and integrity.',
                    'ready':'Read-only research publication is available.'}
    return {'enabled': True, 'state': state,
            'record_count': status['records'] if state in ('empty','ready') else None,
            'next_action': instructions.get(state,'Check database configuration.')}


def publication_database():
    if os.getenv('EARTH_TREND_RESEARCH_PUBLIC', '').strip() != '1':
        raise PublicationError('Research publication is disabled. Set EARTH_TREND_RESEARCH_PUBLIC=1 after curating records.')
    raw = os.getenv('EARTH_TREND_RESEARCH_DB', '').strip()
    if not raw:
        raise PublicationError('No research database configured')
    path = Path(raw).expanduser()
    if not path.is_file():
        raise PublicationError('Research database unavailable')
    return path


def _open_readonly(database):
    # SQLite URI read-only prevents unintended creation or alteration.
    return sqlite3.connect(Path(database).resolve().as_uri() + '?mode=ro', uri=True)


def list_published(database, *, limit=20, offset=0):
    if not 1 <= limit <= 50 or not 0 <= offset <= 10000:
        raise PublicationError('Invalid pagination')
    try:
        with _open_readonly(database) as conn:
            total = conn.execute('SELECT COUNT(*) FROM research_runs').fetchone()[0]
            records = conn.execute('''
                SELECT r.research_id, r.product_id, r.created_at, r.processing_version,
                       r.study_count, GROUP_CONCAT(s.region_name, ', ') AS regions
                FROM research_runs AS r JOIN research_studies AS s ON s.research_id = r.research_id
                GROUP BY r.research_id
                ORDER BY r.created_at DESC, r.research_id DESC LIMIT ? OFFSET ?
            ''', (limit, offset)).fetchall()
    except sqlite3.Error as exc:
        raise PublicationError('Research database cannot be read') from exc
    return {'total': total, 'limit': limit, 'offset': offset,
            'records': [{'research_id': a, 'product_id': b, 'created_at': c,
                         'processing_version': d, 'study_count': e, 'regions': f}
                        for a,b,c,d,e,f in records],
            'note': 'Only administrator-curated records in the configured read-only database are published.'}


def get_published(database, research_id):
    if not isinstance(research_id, str) or not ID_PATTERN.fullmatch(research_id):
        raise PublicationError('Invalid research identifier')
    try:
        # load_workspace verifies SHA256 of the entire payload.
        return load_workspace(database, research_id)
    except (ResearchValidationError, sqlite3.Error, OSError, ValueError) as exc:
        raise PublicationError('Research record not found or integrity check failed') from exc


def report_pdf(result):
    """Generate a reproducible PDF from validated stored statistics, not AI estimates."""
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.graphics.shapes import Drawing, Line, String, PolyLine

    stream = io.BytesIO()
    document = SimpleDocTemplate(stream, pagesize=(595.28, 841.89),
                                 leftMargin=49, rightMargin=49, topMargin=45, bottomMargin=44,
                                 title='EarthTrend Detective Scientific Research Report',
                                 author='EarthTrend Detective')
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='ReportTitleET', parent=styles['Title'], fontSize=19, leading=24, textColor=colors.HexColor('#10334C')))
    styles.add(ParagraphStyle(name='ReportBodyET', parent=styles['BodyText'], fontSize=9, leading=14, spaceAfter=7))
    styles.add(ParagraphStyle(name='ReportSmallET', parent=styles['BodyText'], fontSize=8, leading=12, spaceAfter=5))
    flow = [Paragraph('EarthTrend Detective', styles['ReportTitleET']),
            Paragraph('Reproducible regional environmental trend report',styles['Heading2']),
            Paragraph('Research ID: '+escape(result['research_id']), styles['ReportSmallET']),
            Paragraph('NASA source identity is declared by the researcher; local file validation does not independently authenticate a NASA download.',styles['ReportBodyET'])]
    def p(value, style='ReportBodyET'):
        return Paragraph(escape(str(value)), styles[style])
    def section(title):
        flow.append(Spacer(1,9));flow.append(Paragraph(escape(title),styles['Heading2']))
    section('Study configuration and scientific provenance')
    flow.append(p('NASA product: '+str(result['product_id'])+' | Processing version: '+str(result['processing_version'])))
    flow.append(p('Content SHA256: '+result['research_id']))
    for s in result['studies']:
        section(s['name']+' - '+s['region_id'])
        meta = s['metadata']; observed=s['observations'];trend=s.get('trend')
        rows=[['Item','Recorded value'],['Study area',s['name']],['Monthly observations',str(len(observed))],
              ['Observed period',str(observed[0]['date'])+' to '+str(observed[-1]['date'])],
              ['Spatial method',str(meta.get('spatial_method','see source metadata'))],
              ['Native / processed unit',str(meta.get('product_id',result['product_id']))+' / '+str(meta.get('normalized_unit','see metadata'))]]
        if trend:
            linear=trend.get('linear_regression') or {};sen=trend.get('sen_slope') or {};mk=trend.get('mann_kendall') or {}
            rows.extend([['Complete annual observations',str(trend.get('included_years','n/a'))],
                         ['Linear slope / year',str(linear.get('slope_per_year','n/a'))],
                         ['Sen slope / year',str(sen.get('slope_per_year','n/a'))],
                         ['Mann-Kendall p-value',str(mk.get('p_value','n/a'))],
                         ['Statistically significant at 0.05',str(mk.get('significant_at_0_05','n/a'))]])
        else:
            rows.append(['Trend','Not calculable: '+str(s['trend_status'])])
        table=Table([[p(v,'ReportSmallET') for v in row] for row in rows], colWidths=[183,302], repeatRows=1)
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E5F3F3')),
                                   ('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-1),0.3,colors.HexColor('#CBD9E1')),
                                   ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7)]))
        flow.append(table)
        flow.append(Spacer(1,8))
        for src in meta.get('sources',[]):
            flow.append(p('Source file: '+str(src.get('file','unknown'))+' | SHA256: '+str(src.get('sha256','unavailable')),'ReportSmallET'))
        if trend and len(trend.get('annual_series') or [])>=2:
            valid=[row for row in trend['annual_series'] if isinstance(row.get('value'),(int,float))]
            if len(valid)>1:
                values=[float(row['value']) for row in valid];years=[int(row['year']) for row in valid]
                low=min(values);high=max(values);span=max(high-low,0.00001)
                picture=Drawing(470,155)
                picture.add(Line(37,22,457,22,strokeColor=colors.HexColor('#8DA7B8')))
                picture.add(Line(37,22,37,138,strokeColor=colors.HexColor('#8DA7B8')))
                coords=[(37+420*(year-min(years))/max(1,max(years)-min(years)), 25+109*(v-low)/span) for year,v in zip(years,values)]
                picture.add(PolyLine([coord for point in coords for coord in point],strokeColor=colors.HexColor('#007E92'),strokeWidth=1.8))
                picture.add(String(39,7,str(min(years)),fontSize=8,fillColor=colors.HexColor('#496474')))
                picture.add(String(432,7,str(max(years)),fontSize=8,fillColor=colors.HexColor('#496474')))
                picture.add(String(40,144,'Observed annual series (source-normalized units)',fontSize=8,fillColor=colors.HexColor('#496474')))
                flow.append(picture)
        if trend:
            flow.append(p('Scientific interpretation: '+str(trend.get('interpretation','See numeric findings.'))))
            for limitation in (trend.get('limitations') or [])[:6]:
                flow.append(p('Statistical limitation: '+str(limitation),'ReportSmallET'))
    section('Regional comparison')
    cmp = result.get('comparison') or {}
    flow.append(p('Comparison status: '+str(cmp.get('status','unavailable'))))
    if cmp.get('common_years'):
        flow.append(p('Shared complete years: '+str(cmp['common_years'][0])+'-'+str(cmp['common_years'][-1])))
    section('Scientific limitations and reproducibility')
    for limitation in result.get('limitations',[]):
        flow.append(p('- '+str(limitation),'ReportSmallET'))
    flow.append(p('Data provenance, source file SHA256, method version and the full observation series are retained in the JSON research record. This report does not demonstrate attribution of observed trends to causes.'))
    def footer(canvas, doc):
        canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#667C89'))
        canvas.drawString(49,28,'EarthTrend Detective | Evidence-led Earth system research')
        canvas.drawRightString(546,28,f'Page {doc.page}')
    document.build(flow,onFirstPage=footer,onLaterPages=footer)
    return stream.getvalue()
