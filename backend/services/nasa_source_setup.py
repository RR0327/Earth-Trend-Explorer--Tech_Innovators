"""Local NASA Harmony manifest/download diagnostics; no network access and no file fabrication."""
from __future__ import annotations
import argparse
import json
import re
import sqlite3
from pathlib import Path
from urllib.parse import urlsplit, unquote

JOBS = {
    "GLDAS": {"id": "f8efd328-b615-43e9-8a35-a7308d407000", "product": "GLDAS_NOAH025_M.2.1", "variable": "SoilMoi0_10cm_inst"},
    "IMERG": {"id": "cc68af0e-8e65-48a7-a405-7add8a0eeba7", "product": "GPM_3IMERGM.07", "variable": "precipitation"},
}
MONTH = {"GLDAS": re.compile(r"\.A(\d{6})\.021_"), "IMERG": re.compile(r"3IMERG\.(\d{6})01-S")}


def parse_manifest(path, product):
    """Reject unexpected hosts, missing/duplicate months, or mismatched product files."""
    if product not in JOBS:
        raise ValueError("Unknown NASA product folder")
    urls = [s.strip() for s in Path(path).read_text(encoding="utf-8-sig").splitlines() if s.strip()]
    if not urls:
        raise ValueError("Empty NASA Harmony link manifest")
    months = {}
    for url in urls:
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.hostname != "harmony.earthdata.nasa.gov" or parsed.username or parsed.password:
            raise ValueError("Unexpected NASA data URL host or scheme")
        if JOBS[product]["id"] not in parsed.path:
            raise ValueError("URL does not belong to expected Harmony job")
        name = unquote(parsed.path.rsplit("/", 1)[-1])
        if not name.endswith("_subsetted.nc4") or not name.startswith(JOBS[product]["product"]):
            raise ValueError("Unexpected NASA NetCDF filename")
        if JOBS[product]["variable"] not in name:
            raise ValueError("Unexpected variable in filename")
        found = MONTH[product].search(name)
        if not found:
            raise ValueError("Unrecognized month in NetCDF filename")
        ym = found.group(1)
        if not 1 <= int(ym[4:]) <= 12 or ym in months:
            raise ValueError("Invalid or duplicate observation month: " + ym)
        months[ym] = name
    first, last = min(months), max(months)
    expected = []
    year, month = int(first[:4]), int(first[4:])
    while (year, month) <= (int(last[:4]), int(last[4:])):
        ym = f"{year:04d}{month:02d}"
        if ym not in months:
            expected.append(ym)
        month += 1
        if month == 13:
            year, month = year + 1, 1
    return {"product": product, "job_id": JOBS[product]["id"], "manifest_count": len(urls),
            "first_month": first, "last_month": last, "missing_months": expected,
            "filenames": months}


def inspect_downloads(manifest, download_dir):
    """Only verifies exact expected filenames exist and have nonzero length; NOT NetCDF science."""
    target = Path(download_dir)
    files = manifest["filenames"]
    present, missing, empty = [], [], []
    for month, filename in sorted(files.items()):
        candidate = target / filename
        if not candidate.is_file():
            missing.append(month)
        elif candidate.stat().st_size == 0:
            empty.append(month)
        else:
            present.append(str(candidate))
    return {"download_dir": str(target), "present_count": len(present), "missing_count": len(missing),
            "zero_byte_count": len(empty), "missing_months": missing, "zero_byte_months": empty,
            "ready_for_scientific_validation": len(present)==len(files) and not empty,
            "warning": "Existence and size do not verify NASA provenance, valid NetCDF structure, spatial extent or units."}


def inspect_research_db(db_path):
    """Never creates a database. Diagnoses missing, empty and corrupt SQLite files."""
    if not db_path:
        return {"status": "not_configured", "records": 0}
    db = Path(db_path).expanduser()
    if not db.is_file():
        return {"status": "missing", "records": 0}
    try:
        uri = db.resolve().as_uri() + "?mode=ro"
        with sqlite3.connect(uri, uri=True) as connection:
            exists = connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='research_runs'").fetchone()
            if not exists:
                return {"status": "uninitialized", "records": 0}
            count = connection.execute("SELECT COUNT(*) FROM research_runs").fetchone()[0]
            return {"status": "ready" if count else "empty", "records": count}
    except (sqlite3.Error, OSError):
        return {"status": "unreadable", "records": 0}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Inspect local NASA Harmony manifests/downloads and SQLite research status")
    parser.add_argument("--product", choices=sorted(JOBS), required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--downloads", required=True)
    parser.add_argument("--database")
    args = parser.parse_args(argv)
    try:
        manifest = parse_manifest(args.manifest, args.product)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    report = {"manifest": {k:v for k,v in manifest.items() if k!='filenames'},
              "download": inspect_downloads(manifest,args.downloads),
              "research_database": inspect_research_db(args.database)}
    print(json.dumps(report,indent=2))
    if report["manifest"]["missing_months"]:
        print("MANIFEST INCOMPLETE")
    elif report["download"]["ready_for_scientific_validation"]:
        print("DOWNLOAD FILES PRESENT; SCIENTIFIC VALIDATION STILL REQUIRED")
    else:
        print("DOWNLOADS NOT COMPLETE: NASA DATA FILES REQUIRED")
    return report


if __name__ == "__main__":
    main()
