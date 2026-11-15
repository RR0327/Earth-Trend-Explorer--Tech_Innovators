"""Offline, safe CLI for authentic NASA monthly gridded-data files."""
import argparse
import json
from pathlib import Path

from services.nasa_batch import BatchValidationError,extract_batch,write_batch_result


def main():
    p=argparse.ArgumentParser(description='Validate and extract locally downloaded NASA gridded NetCDF files')
    src=p.add_mutually_exclusive_group(required=True)
    src.add_argument('--files',nargs='+',help='Locally downloaded .nc/.nc4 files')
    src.add_argument('--directory',help='Directory containing actual NetCDF files (Windows-safe)')
    p.add_argument('--product',required=True,choices=['gpm_3imergm_07_final','gldas_noah025_m_2_1_soil0_10','merra2_m2tmnxslv_t2m'])
    area=p.add_mutually_exclusive_group(required=True)
    area.add_argument('--country',help='Bundled Natural Earth ISO3 country geometry')
    area.add_argument('--geometry',help='Custom WGS84 GeoJSON polygon file')
    p.add_argument('--region',required=True,help='Study-area label')
    p.add_argument('--output-prefix',required=True,help='Output under backend/no-push until source audit complete')
    p.add_argument('--source-urls-file',help='Optional JSON list of user-recorded NASA download HTTPS URLs')
    args=p.parse_args()
    try:
        if args.country:
            from services.country_boundaries import get_boundary
            geo=get_boundary(args.country)['geometry']
        else:
            geo=json.loads(Path(args.geometry).read_text(encoding='utf-8'))
            if geo.get('type')=='Feature':geo=geo['geometry']
        urls=json.loads(Path(args.source_urls_file).read_text(encoding='utf-8')) if args.source_urls_file else None
        files = args.files if args.files else sorted(
            (file for file in Path(args.directory).iterdir() if file.is_file() and file.suffix.lower() in ('.nc', '.nc4')),
            key=lambda file: file.name
        )
        if not files:
            raise BatchValidationError('No .nc or .nc4 files found in selected directory')
        result=extract_batch(files,args.product,geo,args.region,urls)
        a,b=write_batch_result(result,args.output_prefix)
        print('BATCH EXTRACTION SUCCESS: '+str(len(result['observations']))+' monthly observations')
        print('MISSING MONTHS: '+str(result['metadata']['missing_month_count']))
        print('LOCAL SOURCE VALIDATION ONLY; NASA provenance must be verified separately.')
        print('CSV: '+str(a)+'\nMETADATA: '+str(b))
    except (BatchValidationError,KeyError,ValueError,OSError) as exc:
        p.error(str(exc))

if __name__=='__main__':main()
