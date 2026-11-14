"""Check that curated data needed for production is actually present and usable."""
import csv
import json
from pathlib import Path

CURATED_DATASET = 'merra2_selected_area_temperature_2000_2025'


def dataset_readiness(data_dir):
    folder = Path(data_dir)
    csv_path = folder / f'{CURATED_DATASET}.csv'
    meta_path = folder / f'{CURATED_DATASET}.json'
    if not csv_path.is_file() or not meta_path.is_file():
        return {'ready': False, 'reason': 'curated_dataset_missing'}
    try:
        metadata = json.loads(meta_path.read_text(encoding='utf-8'))
        if metadata.get('id') != CURATED_DATASET or metadata.get('observation_count') != 301 or metadata.get('first_month') != '2000-01' or metadata.get('last_month') != '2025-01':
            return {'ready': False, 'reason': 'metadata_mismatch'}
        with csv_path.open(encoding='utf-8', newline='') as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != ['date', 'value']:
                return {'ready': False, 'reason': 'invalid_columns'}
            rows = list(reader)
        if len(rows) != 301 or rows[0]['date'] != '2000-01' or rows[-1]['date'] != '2025-01':
            return {'ready': False, 'reason': 'observation_coverage_mismatch'}
        for row in rows:
            float(row['value'])
        return {'ready': True, 'dataset': CURATED_DATASET, 'observations': 301}
    except (OSError, ValueError, KeyError, TypeError, IndexError, json.JSONDecodeError):
        return {'ready': False, 'reason': 'invalid_dataset'}
