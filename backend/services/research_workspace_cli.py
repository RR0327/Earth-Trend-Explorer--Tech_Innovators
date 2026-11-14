"""Offline research CLI. Use only locally audited NASA NetCDF files.

No public API writes or unauthenticated admin operations are introduced.
"""
import argparse
import json
from pathlib import Path

from services.country_boundaries import get_boundary
from services.research_workspace import (ResearchValidationError, build_workspace,
                                         export_workspace, load_workspace, store_workspace)


def main(argv=None):
    parser = argparse.ArgumentParser(description='EarthTrend Detective local reproducible research workspace')
    commands = parser.add_subparsers(dest='command', required=True)
    build = commands.add_parser('build', help='Verify grids, extract several regions, persist immutable research run')
    build.add_argument('--files', nargs='+', required=True, help='Trusted downloaded monthly NASA NetCDF files')
    build.add_argument('--product', required=True,
                       choices=['gpm_3imergm_07_final','gldas_noah025_m_2_1_soil0_10','merra2_m2tmnxslv_t2m'])
    area = build.add_mutually_exclusive_group(required=True)
    area.add_argument('--countries', nargs='+', help='Natural Earth ISO3 countries (e.g., BGD IND)')
    area.add_argument('--regions-json', help='JSON list of {id,name,geometry} objects')
    build.add_argument('--source-urls-file', help='Optional JSON list of documented NASA source URLs')
    build.add_argument('--min-valid-fraction', type=float, default=0.95)
    build.add_argument('--database', required=True, help='SQLite path; use backend/no-push/research/*.sqlite3')
    build.add_argument('--export-json', required=True, help='JSON output under no-push until publication is approved')
    read = commands.add_parser('show', help='Load and verify a saved immutable research record')
    read.add_argument('--database', required=True)
    read.add_argument('--research-id', required=True)
    read.add_argument('--export-json', help='Optional destination for a verified research JSON snapshot')
    args = parser.parse_args(argv)
    try:
        if args.command == 'build':
            if args.countries:
                regions = []
                for code in args.countries:
                    feature = get_boundary(code)
                    regions.append({'id': code.upper(), 'name': feature['properties']['name'],
                                    'geometry': feature['geometry']})
            else:
                regions = json.loads(Path(args.regions_json).read_text(encoding='utf-8'))
            urls = (json.loads(Path(args.source_urls_file).read_text(encoding='utf-8'))
                    if args.source_urls_file else None)
            result = build_workspace(args.files,args.product,regions,urls,args.min_valid_fraction)
            status = store_workspace(args.database,result)
            export_workspace(result,args.export_json)
            print('RESEARCH WORKSPACE SUCCESS')
            print('RESEARCH ID:', result['research_id'])
            print('STUDIES:', len(result['studies']))
            print('COMPARISON:', result['comparison']['status'])
            print('CREATED:', status['created'])
            print('DATABASE:', args.database)
            print('EXPORT:', args.export_json)
            print('NASA authenticity: not independently verified; preserve original source evidence.')
        else:
            result = load_workspace(args.database,args.research_id)
            if args.export_json:
                export_workspace(result,args.export_json)
            print('RESEARCH RECORD VERIFIED:',result['research_id'])
            print('STUDIES:',len(result['studies']))
    except (KeyError, ResearchValidationError, ValueError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
