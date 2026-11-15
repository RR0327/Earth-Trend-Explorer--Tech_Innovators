"""Offline-only research SQLite integrity and backup utility.

No network access, authentication secrets, or automatic database creation.
"""
from __future__ import annotations
import argparse
import json
import sqlite3
from pathlib import Path
from services.nasa_source_setup import inspect_research_db


def verify_and_backup(source, destination=None):
    source=Path(source).expanduser()
    current=inspect_research_db(source)
    if current['status'] not in ('ready','empty'):
        raise ValueError('Research database must exist and have a valid research_runs table')
    uri=source.resolve().as_uri()+'?mode=ro'
    with sqlite3.connect(uri,uri=True) as conn:
        integrity=conn.execute('PRAGMA integrity_check').fetchone()[0]
        if integrity!='ok':
            raise ValueError('SQLite integrity check failed')
        if destination:
            target=Path(destination).expanduser()
            if target.exists():
                raise ValueError('Refusing to overwrite an existing backup')
            target.parent.mkdir(parents=True,exist_ok=True)
            with sqlite3.connect(target) as copy:
                conn.backup(copy)
                copy.commit()
            with sqlite3.connect(target.resolve().as_uri()+'?mode=ro',uri=True) as verify:
                if verify.execute('PRAGMA integrity_check').fetchone()[0]!='ok':
                    raise ValueError('Backup verification failed')
    return {'state':current['status'],'records':current['records'],'integrity':'ok',
            'backup_created':bool(destination)}


def main(argv=None):
    parser=argparse.ArgumentParser(description='Check and optionally back up an existing research SQLite database')
    parser.add_argument('--database',required=True)
    parser.add_argument('--backup')
    args=parser.parse_args(argv)
    try:
        result=verify_and_backup(args.database,args.backup)
    except (ValueError,sqlite3.Error,OSError) as exc:
        parser.error(str(exc))
    print(json.dumps(result,indent=2))
    print('RESEARCH STORAGE VERIFIED')
    return result

if __name__=='__main__':
    main()
