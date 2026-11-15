"""Local scientific preflight for genuine NASA Harmony gridded NetCDF files.

Read-only. No credentials or downloaded observations are sent to the server.
File presence is not equated with valid scientific content or NASA provenance.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

from services.country_boundaries import get_boundary
from services.nasa_batch import BatchValidationError, validate_source_file
from services.research_workspace import ResearchValidationError, _spatial_source_coverage


def inspect_directory(directory, product_id, country=None, limit=None):
    folder = Path(directory)
    if not folder.is_dir():
        raise ValueError('Input directory does not exist: '+str(folder))
    files = sorted((p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in ('.nc', '.nc4')),
                   key=lambda p:p.name)
    if not files:
        raise ValueError('No NetCDF files found in supplied directory')
    if len(files) > 500:
        raise ValueError('Maximum 500 NetCDF files per scientific preflight')
    if limit is not None and not 1 <= limit <= len(files):
        raise ValueError('--limit must be between 1 and source file count')
    selected=files[:limit] if limit else files
    geometry=get_boundary(country)['geometry'] if country else None
    summaries=[]
    for file in selected:
        record=validate_source_file(file,product_id)
        if geometry is not None:
            _spatial_source_coverage(file,geometry,product_id)
        summaries.append(record)
    months=[month for record in summaries for month in record['months']]
    duplicates=sorted(month for month,n in Counter(months).items() if n>1)
    if duplicates:
        raise ValueError('Duplicate monthly observations in files: '+str(duplicates[:8]))
    return {'product_id':product_id,'file_count_in_directory':len(files),
            'files_scientifically_checked':len(selected),
            'months_checked':len(months),'first_month':min(months),'last_month':max(months),
            'study_country':country.upper() if country else None,
            'spatial_extent_check':'passed' if country else 'not_requested',
            'native_units':sorted({r['native_unit'] for r in summaries}),
            'validated':True,
            'nasa_provenance':'local_file_structure_only; record NASA acquisition evidence separately'}


def main(argv=None):
    parser=argparse.ArgumentParser(description='Validate NetCDF group, units, calendar, and optional country extent without Windows long arguments')
    parser.add_argument('--directory',required=True)
    parser.add_argument('--product',required=True,
                        choices=['gpm_3imergm_07_final','gldas_noah025_m_2_1_soil0_10','merra2_m2tmnxslv_t2m'])
    parser.add_argument('--country',help='ISO3 country geometry, e.g., BGD')
    parser.add_argument('--limit',type=int,help='Inspect only first N files for an initial smoke test')
    args=parser.parse_args(argv)
    try:
        result=inspect_directory(args.directory,args.product,args.country,args.limit)
        print(json.dumps(result,indent=2))
        print('NASA SOURCE PREFLIGHT PASSED (local structure, not independent NASA authenticity)')
    except (ValueError, OSError, BatchValidationError, ResearchValidationError, KeyError) as exc:
        parser.error(str(exc))

if __name__=='__main__':main()
