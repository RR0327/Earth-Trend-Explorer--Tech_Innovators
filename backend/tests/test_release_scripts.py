"""Static regression tests for the non-destructive Windows research release scripts."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_launcher_fails_closed_without_sqlite():
    txt = (ROOT/'scripts'/'start-research-api.ps1').read_text(encoding='utf-8')
    assert 'Test-Path -LiteralPath $selected -PathType Leaf' in txt
    assert 'services.research_storage' in txt
    assert 'EARTH_TREND_RESEARCH_DB' in txt
    assert "EARTH_TREND_RESEARCH_PUBLIC = '1'" in txt
    assert '127.0.0.1' in txt
    assert 'New-Item' not in txt

def test_smoke_requires_both_genuine_research_products():
    txt = (ROOT/'scripts'/'verify-release.ps1').read_text(encoding='utf-8')
    assert 'gpm_3imergm_07_final' in txt
    assert 'gldas_noah025_m_2_1_soil0_10' in txt
    assert "state -ne 'ready'" in txt
    assert 'history.total' in txt
