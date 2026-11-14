"""Explicit NASA product capability catalogue and real-data availability preview.

Product recommendations are documentation entries, not evidence of local data.
Only the loaded, versioned datasets are treated as observable records.
"""
from datetime import date
import calendar
from services.dataset_store import list_datasets, load_dataset, IDENTIFIER

PRODUCT_CATALOG = (
    {"id": "merra2_m2tmnxslv_t2m", "family": "MERRA-2", "variable": "temperature", "short_name": "M2TMNXSLV", "variable_id": "T2M", "source_unit": "K", "normalized_unit": "degC", "temporal_resolution": "monthly", "product_version": "5.12.4 (curated example)", "documentation_url": "https://gmao.gsfc.nasa.gov/reanalysis/MERRA-2/", "integration": "curated_example_and_giovanni_import", "note": "Actual coverage depends on the retrieved product and chosen area; not automatically a national mean."},
    {"id": "gpm_3imergm_07_final", "family": "GPM IMERG", "variable": "rainfall", "short_name": "GPM_3IMERGM", "variable_id": "precipitation", "source_unit": "mm/hr", "normalized_unit": "mm/month", "temporal_resolution": "monthly", "spatial_resolution": "0.1 degree", "product_version": "07 (Final)", "doi": "10.5067/GPM/IMERG/3B-MONTH/07", "documentation_url": "https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGM_07/summary", "integration": "verified_catalog_and_local_gridded_file_extraction", "note": "Monthly mean precipitation rate, mm/hr. Multiply by 24 and actual days in month to obtain mm/month. Source file must be supplied; no dataset is bundled."},
    {"id": "gldas_noah025_m_2_1_soil0_10", "family": "GLDAS", "variable": "soil_moisture", "short_name": "GLDAS_NOAH025_M", "variable_id": "SoilMoi0_10cm_inst", "source_unit": "kg m-2", "normalized_unit": "kg m-2", "temporal_resolution": "monthly", "spatial_resolution": "0.25 degree", "product_version": "2.1", "documentation_url": "https://disc.gsfc.nasa.gov/datasets/GLDAS_NOAH025_M_2.1/summary", "integration": "verified_catalog_and_local_gridded_file_extraction", "note": "0–10 cm soil water equivalent layer; not a root-zone or volumetric fraction. Source file must be supplied."},
)


def products(data_dir):
    """Catalogue: report installed observations separately from declared capabilities."""
    installed = list_datasets(data_dir)
    response = []
    for product in PRODUCT_CATALOG:
        matched = [d for d in installed if d.get('product') == product['family'] and d.get('variable') == product['variable']]
        response.append({**product, 'installed_dataset_ids': [d['id'] for d in matched],
                         'available_curated_series': len(matched),
                         'has_live_area_extraction': False})
    return {'products': response, 'data_policy': 'Product catalogue entries are not proof of downloaded data. Only installed datasets are available for immediate area-series analysis.',
            'external_point_service': 'NASA POWER monthly temperature is available separately, subject to NASA availability; it is a point series, not area extraction.'}


class PreviewError(ValueError):
    pass


def preview(data_dir, request):
    """Preview real locally installed monthly observations; never infer from a chosen region."""
    if not isinstance(request, dict):
        raise PreviewError('Request must be a JSON object')
    dataset_id = request.get('dataset_id')
    if not isinstance(dataset_id, str) or not IDENTIFIER.fullmatch(dataset_id):
        raise PreviewError('Specify a valid installed dataset_id')
    try:
        dataset = load_dataset(data_dir, dataset_id)
    except (FileNotFoundError, ValueError, KeyError):
        raise PreviewError('The requested installed dataset is unavailable') from None
    records = dataset['observations']
    meta = dataset['metadata']
    first, last = int(records[0]['date'][:4]), int(records[-1]['date'][:4])
    start = request.get('start_year', first)
    end = request.get('end_year', last)
    if any(isinstance(v, bool) or not isinstance(v, int) for v in (start, end)) or not (first <= start <= end <= last):
        raise PreviewError(f'Requested years must be within the installed series ({first}–{last})')
    subset = [r for r in records if start <= int(r['date'][:4]) <= end]
    if not subset:
        raise PreviewError('No genuine observations available in this period')
    actual = {r['date'] for r in subset}
    expected = [f'{year:04d}-{month:02d}' for year in range(start, end + 1) for month in range(1, 13)]
    missing = [month for month in expected if month not in actual]
    complete_years = [year for year in range(start, end + 1) if all(f'{year:04d}-{m:02d}' in actual for m in range(1,13))]
    region_label = request.get('region')
    if region_label is not None and (not isinstance(region_label, str) or len(region_label) > 180):
        raise PreviewError('region must be a description shorter than 181 characters')
    # No region-label substitution: the metadata always refers to sampled source coverage.
    return {
        'dataset_id':dataset_id,
        'requested_years': {'start':start,'end':end},
        'observation_count':len(subset),
        'complete_years':complete_years,
        'missing_month_count':len(missing),
        'missing_months': missing[:100],
        'missing_months_truncated':len(missing)>100,
        'actual_first_month':subset[0]['date'],
        'actual_last_month':subset[-1]['date'],
        'source_region':meta.get('region'),
        'requested_region':region_label,
        'requested_region_matches_source': region_label is None or region_label.strip().casefold()==str(meta.get('region','')).strip().casefold(),
        'requested_region_is_not_proven_by_selection':True,
        'variable':meta.get('variable'),
        'product':meta.get('product'),
        'unit':meta.get('normalized_unit'),
        'source_file_sha256':meta.get('source_file_sha256'),
        'verification_status':meta.get('verification_status'),
        'coverage_warning':meta.get('coverage_warning') or 'Coverage must be checked against original source geometry.',
        'analysis_available':len(complete_years)>=8,
        'disclaimer':'A preview does not perform new NASA retrieval, polygon masking, or independent source authentication.'
    }
