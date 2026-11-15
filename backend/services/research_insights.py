"""Deterministic, grounded explanation of previously verified research records.

No AI model, network request or generated measurements are involved. An optional
LLM may only be added with an explicit provenance-aware service and controls.
"""
from __future__ import annotations
import math


def _as_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        return None
    return float(value)


def explain_research(record):
    """Explain only values already present in a verified research record."""
    studies=[]
    for item in record.get('studies', []):
        trend=item.get('trend') or {}
        mk=trend.get('mann_kendall') or {}
        sen=trend.get('sen_slope') or {}
        p=_as_number(mk.get('p_value'))
        slope=_as_number(sen.get('slope_per_year'))
        meta=item.get('metadata') or {}
        unit=str(meta.get('normalized_unit') or 'source-normalized unit')
        if slope is None or p is None or not 0 <= p <= 1:
            statement='Insufficient validated annual data for a significance conclusion.'
            significant=None
        else:
            direction='increasing' if slope>0 else ('decreasing' if slope<0 else 'flat')
            significant=p<0.05
            qualifier='statistically significant' if significant else 'not statistically significant'
            statement=(f'The estimated Sen slope is {slope:.6g} {unit}/year ({direction}); '
                       f'the recorded Mann-Kendall p-value is {p:.5g}, {qualifier} at alpha=0.05.')
        studies.append({'region_id':item.get('region_id'), 'region_name':item.get('name'),
                        'observation_count':len(item.get('observations') or []),
                        'sen_slope_per_year':slope,'p_value':p,'significant_at_0_05':significant,
                        'summary':statement,
                        'disclaimer':'A trend does not establish causation. Geographic coverage, missing observations and serial dependence affect interpretation.'})
    return {'research_id':record['research_id'],'product_id':record.get('product_id'),
            'explanation_type':'deterministic_from_verified_record','ai_generated':False,
            'studies':studies,
            'limitations':record.get('limitations',[]),
            'provenance_note':'Numeric results are copied from the integrity-checked research record; no measurements are inferred.'}


def published_regions(records):
    """Summaries of actual saved-study coverage, not claims of downloadable global data."""
    regions={}
    for record in records:
        for study in record.get('studies', []):
            key=(str(study.get('region_id')),str(record.get('product_id')))
            obs=study.get('observations') or []
            regions[key]={'region_id':key[0], 'name':study.get('name'), 'product_id':key[1],
                          'research_id':record['research_id'],'observation_count':len(obs),
                          'first_month':obs[0].get('date') if obs else None,
                          'last_month':obs[-1].get('date') if obs else None,
                          'data_status':'published_verified_record'}
    return sorted(regions.values(), key=lambda r:(r['name'] or '',r['product_id']))
