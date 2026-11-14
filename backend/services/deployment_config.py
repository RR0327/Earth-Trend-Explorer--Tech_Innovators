"""Small, testable production settings; avoid CORS wildcard and implicit trust."""
import os
from urllib.parse import urlsplit


def allowed_origins(environment=None, value=None):
    environment = (environment if environment is not None else os.getenv('APP_ENV', 'development')).strip().lower()
    value = value if value is not None else os.getenv('CORS_ORIGINS', '')
    if environment not in {'development', 'test', 'production'}:
        raise ValueError('APP_ENV must be development, test, or production')
    if not value.strip() and environment != 'production':
        value = 'http://localhost:5173,http://127.0.0.1:5173'
    origins = [part.strip().rstrip('/') for part in value.split(',') if part.strip()]
    if environment == 'production' and not origins:
        raise ValueError('Production requires CORS_ORIGINS set to the deployed frontend HTTPS origin')
    for origin in origins:
        parsed = urlsplit(origin)
        if origin == '*' or not parsed.hostname or parsed.path or parsed.query or parsed.fragment or parsed.username or parsed.password:
            raise ValueError(f'Invalid CORS origin: {origin!r}')
        if parsed.scheme not in {'https', 'http'}:
            raise ValueError(f'Invalid CORS origin scheme: {origin!r}')
        if environment == 'production' and parsed.scheme != 'https':
            raise ValueError('Production CORS origins must use HTTPS')
        if parsed.port is not None and not 0 < parsed.port < 65536:
            raise ValueError('Invalid origin port')
    return list(dict.fromkeys(origins))


def is_production():
    return os.getenv('APP_ENV', 'development').strip().lower() == 'production'
