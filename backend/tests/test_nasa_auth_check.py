"""Authentication is mocked: tests do not access NASA or use real credentials."""
import types
import pytest
from services import nasa_auth_check

def test_success(monkeypatch):
    monkeypatch.setitem(__import__('sys').modules,'earthaccess',types.SimpleNamespace(login=lambda **kw:types.SimpleNamespace(authenticated=True)))
    assert nasa_auth_check.verify_login() is True

def test_failure_does_not_leak_credentials(monkeypatch):
    def fail(**kwargs):raise ValueError('bad credentials SECRET_SAMPLE')
    monkeypatch.setitem(__import__('sys').modules,'earthaccess',types.SimpleNamespace(login=fail))
    with pytest.raises(RuntimeError) as err:nasa_auth_check.verify_login()
    assert 'SECRET_SAMPLE' not in str(err.value)
