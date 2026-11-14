from fastapi.testclient import TestClient
import main

client = TestClient(main.app)

def test_health():
    assert client.get("/api/health").json() == {"status": "healthy", "service": "earthtrend-detective"}

def test_root():
    assert client.get("/").json()["status"] == "running"

def test_unknown_endpoint():
    assert client.get("/api/unknown").status_code == 404

def test_empty_catalog(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DATA_DIR", tmp_path)
    assert client.get("/api/datasets").json() == {"datasets": []}
    assert client.get("/api/datasets/not-here").status_code == 404
