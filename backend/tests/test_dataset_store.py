"""Synthetic fixtures for tests ONLY; never presented as NASA observations."""
import csv
import json
import pytest
from services.dataset_store import ingest, load_dataset, list_datasets, DatasetValidationError

META = {"id":"merra_test", "variable":"temperature", "product":"MERRA-2", "source_url":"https://giovanni.gsfc.nasa.gov/giovanni/", "region":"Bangladesh", "spatial_method":"area_mean", "temporal_resolution":"monthly", "unit":"K", "retrieved_at":"2026-11-14"}

def make_files(tmp_path, rows=None, meta=None):
    raw = tmp_path / "raw.csv"; info = tmp_path / "source.json"
    with raw.open("w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out); writer.writerow(["date", "value"])
        writer.writerows(rows if rows is not None else [("2024-01", 300), ("2024-02", 301)])
    info.write_text(json.dumps(meta or META), encoding="utf-8")
    return raw, info

def test_import_conversion_provenance_and_api_read(tmp_path):
    raw, info = make_files(tmp_path)
    dest = tmp_path / "data"
    summary = ingest(raw, info, dest)
    assert summary["normalized_unit"] == "degC"
    assert summary["observation_count"] == 2
    assert len(summary["source_file_sha256"]) == 64
    assert summary["verification_status"].startswith("source_metadata_user_supplied")
    assert len(list_datasets(dest)) == 1
    result = load_dataset(dest, "merra_test")
    assert result["observations"][0]["value"] == pytest.approx(26.85)

def test_missing_month_reported(tmp_path):
    raw, info = make_files(tmp_path, [("2024-01", 300), ("2024-03", 301)])
    assert ingest(raw, info, tmp_path / "data")["gaps"][0]["missing_months"] == 1

def test_rain_rate_uses_leap_year_days(tmp_path):
    meta = {**META, "id":"rain_test", "variable":"rainfall", "product":"GPM IMERG", "unit":"mm/day"}
    raw, info = make_files(tmp_path, [("2024-02", 2), ("2024-03", 2)], meta)
    dest = tmp_path / "data"; summary = ingest(raw, info, dest)
    assert summary["normalized_unit"] == "mm/month"
    assert load_dataset(dest, "rain_test")["observations"] == [{"date":"2024-02", "value":58}, {"date":"2024-03", "value":62}]

@pytest.mark.parametrize("rows", [[], [("2024-01", 300)], [("2024-01",300),("2024-01",301)], [("2024-01", ""),("2024-02",300)], [("2024-01", "nan"),("2024-02",300)], [("2024-01", 300),("2040-02",301)]])
def test_bad_rows_rejected(tmp_path, rows):
    raw, info = make_files(tmp_path, rows)
    with pytest.raises(DatasetValidationError): ingest(raw, info, tmp_path / "data")

@pytest.mark.parametrize("change", [{"source_url":"https://example.com/"}, {"unit":"unknown"}, {"product":"GLDAS"}, {"id":"../oops"}, {"temporal_resolution":"daily"}])
def test_invalid_metadata_rejected(tmp_path, change):
    raw, info = make_files(tmp_path, meta={**META, **change})
    with pytest.raises(DatasetValidationError): ingest(raw, info, tmp_path / "data")

def test_csv_header_validation(tmp_path):
    raw, info = make_files(tmp_path)
    raw.write_text("time,observation\n2024-01,300\n", encoding="utf-8")
    with pytest.raises(DatasetValidationError): ingest(raw, info, tmp_path / "data")

def test_path_traversal_rejected(tmp_path):
    with pytest.raises(ValueError): load_dataset(tmp_path, "../../secret")
