"""Ephemeral scientific investigation of monthly NASA Giovanni exports.

A visitor's provenance declaration is NOT independent NASA source authentication.
No file is saved and all data are rejected when invalid.
"""
import math
from datetime import date
from urllib.parse import urlsplit
from services.dataset_store import normalize_value, parse_month, DatasetValidationError
from services.trend_analyzer import analyze_dataset, TrendValidationError

PRODUCTS = {
    'temperature': {'MERRA-2': {'K', 'degC'}},
    'rainfall': {'GPM IMERG': {'mm/day', 'mm/month'}},
    'soil_moisture': {'GLDAS': {'kg/m2', 'mm'}},
}

class ExplorationValidationError(ValueError):
    pass


def nasa_source(url):
    try:
        parsed = urlsplit(url)
        return parsed.scheme == 'https' and parsed.hostname is not None and (parsed.hostname == 'nasa.gov' or parsed.hostname.endswith('.nasa.gov')) and not parsed.username and not parsed.password
    except (TypeError, ValueError):
        return False


def investigate(payload):
    if not isinstance(payload, dict):
        raise ExplorationValidationError('Request must be an object')
    variable = payload.get('variable')
    product = payload.get('product')
    unit = payload.get('unit')
    region = payload.get('region')
    source_url = payload.get('source_url')
    if variable not in PRODUCTS or product not in PRODUCTS[variable]:
        raise ExplorationValidationError('Unsupported variable and NASA product combination')
    if unit not in PRODUCTS[variable][product]:
        raise ExplorationValidationError('Unsupported source unit for selected product')
    if not isinstance(region, str) or not 3 <= len(region.strip()) <= 180:
        raise ExplorationValidationError('A meaningful study-region description (3–180 characters) is required')
    if not isinstance(source_url, str) or not nasa_source(source_url) or len(source_url) > 2048:
        raise ExplorationValidationError('A NASA HTTPS dataset/source URL is required')
    raw = payload.get('observations')
    if not isinstance(raw, list) or not 24 <= len(raw) <= 1000:
        raise ExplorationValidationError('Submit 24–1000 monthly observations')
    observations, seen = [], set()
    for row in raw:
        if not isinstance(row, dict) or not isinstance(row.get('date'), str):
            raise ExplorationValidationError('Each observation requires a monthly date and numeric value')
        try:
            month = parse_month(row['date'])
        except DatasetValidationError as exc:
            raise ExplorationValidationError(str(exc)) from exc
        if month in seen:
            raise ExplorationValidationError('Duplicate observation month: ' + month)
        seen.add(month)
        value = row.get('value')
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ExplorationValidationError('Invalid or non-finite observation at ' + month)
        if variable in {'rainfall', 'soil_moisture'} and value < 0:
            raise ExplorationValidationError('Negative rainfall/soil moisture is invalid')
        y, m = map(int, month.split('-'))
        normalized, normalized_unit = normalize_value(float(value), y, m, variable, unit)
        observations.append({'date':month, 'value':round(normalized,9)})
    observations.sort(key=lambda r:r['date'])
    start_year, end_year = payload.get('start_year'), payload.get('end_year')
    if start_year is not None or end_year is not None:
        if not all(isinstance(y, int) and not isinstance(y, bool) and 1980 <= y <= date.today().year for y in (start_year, end_year)) or start_year > end_year:
            raise ExplorationValidationError('Invalid investigation year range')
        observations = [r for r in observations if start_year <= int(r['date'][:4]) <= end_year]
    metadata = {
        'id':'visitor_ephemeral_investigation', 'variable':variable, 'product':product,
        'normalized_unit':normalized_unit, 'unit':unit, 'region':region.strip(), 'source_url':source_url,
        'first_month':observations[0]['date'] if observations else None,
        'last_month':observations[-1]['date'] if observations else None,
        'observation_count':len(observations), 'temporal_resolution':'monthly',
        'verification_status':'visitor_supplied_source_not_independently_authenticated',
        'coverage_warning':'Coverage is declared by the visitor; validate the actual Giovanni Data Bounding Box before scientific interpretation.',
        'source_file_sha256':None,
    }
    try:
        trend = analyze_dataset({'metadata':metadata, 'observations':observations})
    except TrendValidationError as exc:
        raise ExplorationValidationError(str(exc)) from exc
    return {'dataset': {'metadata': metadata, 'observations': observations}, 'trend':trend,
            'disclosure':'Visitor-supplied observations, region and NASA source link are not independently authenticated; no upload is persisted.'}
