"""Auditable, local-only, multi-region scientific research workspace.

Sources must be trusted *local* NASA files obtained by the researcher; this
module does not download or independently authenticate them. No public write
routes are exposed. Research records are immutable (identified by SHA-256).
"""
from __future__ import annotations

import hashlib
import json
import math
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import xarray as xr
from shapely.geometry import box, shape

from services.grid_extraction import PRODUCTS, _bounds, _geometry
from services.nasa_batch import BatchValidationError, extract_batch
from services.trend_analyzer import TrendValidationError, analyze_dataset

SCHEMA_VERSION = '1'
PROCESSING_VERSION = 'increment5-1.0'
MAX_REGIONS = 8

class ResearchValidationError(ValueError):
    pass


def _canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def _sha(value):
    return hashlib.sha256(_canonical(value).encode('utf-8')).hexdigest()


def _spatial_source_coverage(path, geometry):
    """Ensure the WHOLE study polygon lies inside supplied grid-cell extent.

    Coordinates are rectilinear WGS84. This does not establish whether the
    source file itself was cropped from a larger dataset.
    """
    study = _geometry(geometry)
    try:
        with xr.open_dataset(path, decode_times=False) as ds:
            lat_edges = _bounds(ds.lat.values)
            lon_edges = _bounds(ds.lon.values)
            envelope = box(float(lon_edges.min()), float(lat_edges.min()),
                           float(lon_edges.max()), float(lat_edges.max()))
    except Exception as exc:
        raise ResearchValidationError(f'Cannot inspect spatial extent: {Path(path).name}: {exc}') from exc
    if not envelope.is_valid:
        raise ResearchValidationError('Invalid source grid extent')
    fraction = 1 - study.difference(envelope).area / study.area
    if fraction < 0.999999:
        raise ResearchValidationError(
            f'{Path(path).name}: supplied grid does not fully cover study area '
            f'(planar geographic containment {fraction:.4%}); no partial-region national claims'
        )
    return {'filename': Path(path).name, 'source_grid_bbox': [round(float(v), 7) for v in envelope.bounds],
            'entire_study_area_within_grid_extent': True}


def _as_trend_dataset(result, study_id):
    meta = result['metadata']
    product = PRODUCTS[meta['product_id']]
    variable = {'T2M': 'temperature', 'precipitation': 'rainfall',
                'SoilMoi0_10cm_inst': 'soil_moisture'}[product['variable']]
    return {
        'metadata': {'id': study_id, 'region': meta['region'], 'variable': variable,
                     'normalized_unit': product['out_unit'], 'product': product['family'],
                     'source_url': meta['sources'][0].get('declared_source_url', 'not supplied'),
                     'source_file_sha256': [s['sha256'] for s in meta['sources']],
                     'verification_status': 'local_scientific_checks_only',
                     'coverage_warning': meta['scientific_limitations']},
        'observations': result['observations'],
    }


def _shared_annual_comparison(studies):
    """Compare same-variable region trends using identical complete years."""
    if len(studies) < 2:
        return {'status': 'requires_two_regions'}
    if any(s['trend'] is None for s in studies):
        return {'status': 'insufficient_complete_years', 'note': 'At least 8 complete years per study are required.'}
    series = [{row['year']: row['value'] for row in s['trend']['annual_series']} for s in studies]
    shared = sorted(set.intersection(*(set(s) for s in series)))
    if len(shared) < 8:
        return {'status': 'insufficient_shared_years', 'shared_years': shared}
    from scipy.stats import theilslopes, kendalltau
    trends = []
    for s, annual in zip(studies, series):
        values = [annual[y] for y in shared]
        if len(set(values)) < 2:
            trends.append({'region_id': s['region_id'], 'sen_slope_per_year': 0.0,
                           'mann_kendall_p_value': None, 'constant_series': True})
        else:
            sen = theilslopes(values, shared)
            tau, p = kendalltau(shared, values)
            trends.append({'region_id': s['region_id'], 'sen_slope_per_year': float(sen.slope),
                           'mann_kendall_p_value': float(p), 'constant_series': False})
    return {'status': 'descriptive_comparison', 'common_years': shared,
            'unit': studies[0]['trend']['slope_unit'], 'regions': trends,
            'note': 'Each region is refitted on identical complete years. Difference of slopes is descriptive, NOT a hypothesis test of between-region differences.'}


def build_workspace(files, product_id, regions, source_urls=None, minimum_valid_cell_fraction=0.95):
    """Validate files and extract every region from exactly the same source set.

    Regions: [{'id':'BGD','name':'Bangladesh','geometry': GeoJSON}, ...]
    Source observations are never invented or interpolated.
    """
    files = [Path(p) for p in files]
    if not 1 <= len(files) <= 500:
        raise ResearchValidationError('Supply between 1 and 500 locally downloaded source files')
    if product_id not in PRODUCTS:
        raise ResearchValidationError('Unsupported NASA product')
    if not isinstance(regions, list) or not 1 <= len(regions) <= MAX_REGIONS:
        raise ResearchValidationError(f'Supply 1–{MAX_REGIONS} study regions')
    if not isinstance(minimum_valid_cell_fraction, (int, float)) or isinstance(minimum_valid_cell_fraction, bool) or not 0 < minimum_valid_cell_fraction <= 1:
        raise ResearchValidationError('Minimum valid-cell coverage must be in (0,1]')
    identifiers = set()
    checked = []
    for region in regions:
        if not isinstance(region, dict):
            raise ResearchValidationError('Each region requires id, name and GeoJSON geometry')
        region_id, name = region.get('id'), region.get('name')
        if not isinstance(region_id, str) or not (1 <= len(region_id) <= 64) or not all(c.isalnum() or c in '_-' for c in region_id):
            raise ResearchValidationError('Region id must be 1–64 ASCII-like identifier characters')
        if region_id in identifiers:
            raise ResearchValidationError('Duplicate study region identifier')
        identifiers.add(region_id)
        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 150:
            raise ResearchValidationError('Valid region name required')
        try:
            geo = _geometry(region.get('geometry'))
        except Exception as exc:
            raise ResearchValidationError(f'Invalid {region_id} study geometry: {exc}') from exc
        checked.append({'id': region_id, 'name': name.strip(), 'geometry': region['geometry']})
    # Pre-check prevents source files covering just a small part of a country
    # being passed off as whole-country averages.
    extent_checks = {}
    for region in checked:
        extent_checks[region['id']] = [_spatial_source_coverage(p, region['geometry']) for p in files]
    studies = []
    for region in checked:
        try:
            result = extract_batch(files, product_id, region['geometry'], region['name'], source_urls)
        except BatchValidationError as exc:
            raise ResearchValidationError(f"{region['id']}: {exc}") from exc
        weak = [row['date'] for row in result['observations']
                if row['valid_region_weight_fraction'] < minimum_valid_cell_fraction]
        if weak:
            raise ResearchValidationError(
                f"{region['id']}: {len(weak)} months fall below required valid-grid fraction "
                f'{minimum_valid_cell_fraction:.1%}; examples: {weak[:5]}'
            )
        trend_dataset = _as_trend_dataset(result, region['id'])
        try:
            trend = analyze_dataset(trend_dataset)
        except TrendValidationError as exc:
            trend = None
            trend_status = f'not_calculable: {exc}'
        else:
            trend_status = 'calculated'
        studies.append({'region_id': region['id'], 'name': region['name'],
                        'metadata': result['metadata'], 'observations': result['observations'],
                        'coverage_checks': extent_checks[region['id']],
                        'trend_status': trend_status, 'trend': trend})
    comparison = _shared_annual_comparison(studies)
    core = {'schema_version': SCHEMA_VERSION, 'processing_version': PROCESSING_VERSION,
            'product_id': product_id, 'minimum_valid_cell_fraction': minimum_valid_cell_fraction,
            'studies': studies, 'comparison': comparison,
            'limitations': [
                'Local NetCDF structure, SHA256 and metadata do not independently authenticate NASA origin.',
                'Grid-extent containment and valid-data fractions do not establish correct product geographic representativeness.',
                'Country polygons use generalized Natural Earth 110m boundaries, not authoritative administrative borders.',
                'Fractional-cell area weights are approximate for rectilinear WGS84 grids and not exact geodesic integration.',
                'Annual trend p-values are uncorrected for autocorrelation; slope comparisons are descriptive, not inferential.',
                'No missing measurements have been fabricated or interpolated.'
            ]}
    return {'research_id': _sha(core), **core}


_SQL = '''
CREATE TABLE IF NOT EXISTS research_runs (
    research_id TEXT PRIMARY KEY, schema_version TEXT NOT NULL, product_id TEXT NOT NULL,
    created_at TEXT NOT NULL, processing_version TEXT NOT NULL,
    study_count INTEGER NOT NULL, payload_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research_studies (
    research_id TEXT NOT NULL, region_id TEXT NOT NULL, region_name TEXT NOT NULL,
    observation_count INTEGER NOT NULL, first_month TEXT NOT NULL, last_month TEXT NOT NULL,
    PRIMARY KEY(research_id,region_id),
    FOREIGN KEY(research_id) REFERENCES research_runs(research_id)
);
CREATE TABLE IF NOT EXISTS source_audit (
    research_id TEXT NOT NULL, region_id TEXT NOT NULL,
    sha256 TEXT NOT NULL, filename TEXT NOT NULL, declared_source_url TEXT,
    PRIMARY KEY(research_id, region_id, sha256, filename),
    FOREIGN KEY(research_id,region_id) REFERENCES research_studies(research_id,region_id)
);
'''


def store_workspace(database_path, result):
    """Persist an immutable JSON research record plus indexed study/source audit rows.

    Restricted to explicit local CLI operation. There is no public API writer.
    """
    db = Path(database_path)
    if not result.get('research_id') or len(result['research_id']) != 64:
        raise ResearchValidationError('Missing research content hash')
    core = {k: v for k, v in result.items() if k != 'research_id'}
    if _sha(core) != result['research_id']:
        raise ResearchValidationError('Research content was modified after calculation')
    db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db) as connection:
        connection.execute('PRAGMA foreign_keys=ON')
        connection.executescript(_SQL)
        encoded = _canonical(result)
        current = connection.execute('SELECT payload_json FROM research_runs WHERE research_id=?',
                                     (result['research_id'],)).fetchone()
        if current is not None:
            if current[0] != encoded:
                raise ResearchValidationError('Existing research identifier has conflicting data')
            return {'research_id': result['research_id'], 'created': False, 'database': str(db)}
        connection.execute('INSERT INTO research_runs VALUES(?,?,?,?,?,?,?)',
                           (result['research_id'], result['schema_version'], result['product_id'],
                            datetime.now(timezone.utc).isoformat(), result['processing_version'],
                            len(result['studies']), encoded))
        for s in result['studies']:
            observations = s['observations']
            connection.execute('INSERT INTO research_studies VALUES(?,?,?,?,?,?)',
                               (result['research_id'], s['region_id'], s['name'],len(observations),
                                observations[0]['date'], observations[-1]['date']))
            for source in s['metadata']['sources']:
                connection.execute('INSERT INTO source_audit VALUES(?,?,?,?,?)',
                                   (result['research_id'], s['region_id'], source['sha256'],
                                    source['file'], source.get('declared_source_url')))
    return {'research_id': result['research_id'], 'created': True, 'database': str(db)}


def load_workspace(database_path, research_id):
    if not isinstance(research_id, str) or len(research_id) != 64 or any(c not in '0123456789abcdef' for c in research_id):
        raise ResearchValidationError('Invalid research identifier')
    with sqlite3.connect(database_path) as connection:
        row = connection.execute('SELECT payload_json FROM research_runs WHERE research_id=?', (research_id,)).fetchone()
    if row is None:
        raise ResearchValidationError('Research run not found')
    result = json.loads(row[0])
    if _sha({k:v for k,v in result.items() if k!='research_id'}) != research_id:
        raise ResearchValidationError('Stored research record failed SHA256 integrity verification')
    return result


def export_workspace(result, output_path):
    """Write a reproducible full JSON export, including observations and source hashes."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')
    return path
