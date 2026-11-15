"""Interactive Earthdata authentication check; never logs or stores credentials.

Run only on a trusted local machine. Never include Earthdata credentials in Git,
frontend code or a public backend environment by default.
"""
from __future__ import annotations


def verify_login():
    try:
        import earthaccess
    except ImportError as exc:
        raise RuntimeError('Install earthaccess: python -m pip install earthaccess') from exc
    try:
        auth=earthaccess.login(strategy='interactive',persist=False)
    except Exception as exc:
        raise RuntimeError('Earthdata Login rejected authentication. Verify your account at urs.earthdata.nasa.gov; check username, password, account activation, and any required authorizations. No credentials were stored.') from exc
    if not getattr(auth, 'authenticated', False):
        raise RuntimeError('Earthdata Login was not authenticated. No files downloaded.')
    return True


def main():
    try:
        verify_login()
    except RuntimeError as exc:
        print('EARTHDATA AUTH FAILED: '+str(exc))
        return 1
    print('EARTHDATA AUTH PASSED: rerun the NASA Harmony downloader using the same verified account credentials.')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
