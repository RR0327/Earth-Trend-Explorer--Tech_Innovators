"""Local-only verified-source NetCDF grid extraction. Do not expose untrusted public NetCDF uploads."""
import argparse,json,sys,csv
from pathlib import Path
from services.grid_extraction import extract_gridded_series,GridExtractionError

def main():
    p=argparse.ArgumentParser(description='Extract monthly regional NASA grid observations from a trusted local NetCDF')
    p.add_argument('--nc',required=True)
    p.add_argument('--product',required=True,choices=['gpm_3imergm_07_final','gldas_noah025_m_2_1_soil0_10','merra2_m2tmnxslv_t2m'])
    p.add_argument('--geometry',help='Path to GeoJSON geometry (Polygon or MultiPolygon, EPSG:4326)')
    p.add_argument('--country',help='ISO A3 country code from bundled Natural Earth geometry; use instead of --geometry')
    p.add_argument('--region',required=True)
    p.add_argument('--output-prefix',required=True)
    p.add_argument('--sha256',default=None,help='Optional expected SHA256 of source input')
    args=p.parse_args()
    if bool(args.geometry)==bool(args.country): p.error('Provide exactly one of --geometry or --country')
    if args.country:
        from services.country_boundaries import get_boundary
        try: geo=get_boundary(args.country)['geometry']
        except KeyError as exc: p.error(str(exc))
    else:
        geo=json.loads(Path(args.geometry).read_text(encoding='utf-8'))
        if geo.get('type')=='Feature':geo=geo['geometry']
    try:result=extract_gridded_series(args.nc,args.product,geo,args.region,args.sha256)
    except GridExtractionError as exc:p.error(str(exc))
    prefix=Path(args.output_prefix)
    prefix.parent.mkdir(parents=True,exist_ok=True)
    with prefix.with_suffix('.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=['date','value','quality_flag','valid_region_weight_fraction'])
        writer.writeheader();writer.writerows(result['observations'])
    prefix.with_suffix('.json').write_text(json.dumps(result['metadata'],indent=2),encoding='utf-8')
    print(f'GRID EXTRACTION SUCCESS: {len(result["observations"])} real monthly samples; source sha256={result["metadata"]["source_file_sha256"]}')

if __name__=='__main__':main()
