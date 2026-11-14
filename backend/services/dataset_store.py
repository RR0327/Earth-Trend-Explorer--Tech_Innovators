"""Strict, provenance-conscious import of normalized NASA time series.

CSV columns: date,value with monthly YYYY-MM or YYYY-MM-DD timestamps.
Dataset identity is user-provided metadata and is NOT independently authenticated.
"""
import calendar
import csv
import hashlib
import json
import math
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

VARIABLE_UNITS = {
    "temperature": {"K", "degC"},
    "rainfall": {"mm/day", "mm/month"},
    "soil_moisture": {"kg/m2", "mm"},
}
SOURCE_PRODUCTS = {
    "temperature": ("MERRA-2",),
    "rainfall": ("GPM IMERG",),
    "soil_moisture": ("GLDAS",),
}
IDENTIFIER = re.compile(r"^[a-z][a-z0-9_-]{1,63}$")

class DatasetValidationError(ValueError):
    pass

def validate_metadata(meta):
    required = ("id", "variable", "product", "source_url", "region", "spatial_method", "temporal_resolution", "unit", "retrieved_at")
    if not isinstance(meta, dict) or any(not isinstance(meta.get(k), str) or not meta[k].strip() for k in required):
        raise DatasetValidationError("Missing or empty metadata field; see metadata template")
    if not IDENTIFIER.fullmatch(meta["id"]):
        raise DatasetValidationError("Invalid id: use lowercase letters, numbers, underscores or hyphens")
    if meta["variable"] not in VARIABLE_UNITS:
        raise DatasetValidationError("Unknown environmental variable")
    if meta["product"] not in SOURCE_PRODUCTS[meta["variable"]]:
        raise DatasetValidationError("Product does not match variable")
    if meta["unit"] not in VARIABLE_UNITS[meta["variable"]]:
        raise DatasetValidationError("Unit not supported for variable")
    if meta["temporal_resolution"] != "monthly":
        raise DatasetValidationError("Only monthly time series are supported in Phase 2")
    if meta["spatial_method"] not in {"area_mean", "point", "unspecified"}:
        raise DatasetValidationError("spatial_method must be area_mean, point, or unspecified")
    uri = urlparse(meta["source_url"])
    if uri.scheme != "https" or not uri.netloc or not (uri.hostname == "nasa.gov" or uri.hostname.endswith(".nasa.gov")):
        raise DatasetValidationError("source_url must be a genuine NASA HTTPS URL")
    try:
        date.fromisoformat(meta["retrieved_at"])
    except ValueError as exc:
        raise DatasetValidationError("retrieved_at must be ISO date YYYY-MM-DD") from exc
    return meta

def parse_month(value):
    value = value.strip()
    try:
        parsed = date.fromisoformat(value + "-01" if re.fullmatch(r"\d{4}-\d{2}", value) else value)
    except ValueError as exc:
        raise DatasetValidationError(f"Invalid date: {value}") from exc
    if parsed.year < 1980 or parsed > date.today():
        raise DatasetValidationError(f"Date outside supported historical range: {value}")
    return parsed.strftime("%Y-%m")

def normalize_value(v, year, month, variable, unit):
    # Preserve semantics: mm/day is a monthly *mean daily rate*, not a total.
    if variable == "temperature" and unit == "K":
        return v - 273.15, "degC"
    if variable == "rainfall" and unit == "mm/day":
        return v * calendar.monthrange(year, month)[1], "mm/month"
    return v, unit

def ingest(csv_path, meta_path, data_dir):
    csv_path, meta_path, data_dir = Path(csv_path), Path(meta_path), Path(data_dir)
    meta = validate_metadata(json.loads(meta_path.read_text(encoding="utf-8")))
    if csv_path.stat().st_size > 10_000_000:
        raise DatasetValidationError("CSV exceeds 10 MB")
    observations = []
    seen = set()
    with csv_path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or [x.strip() for x in reader.fieldnames] != ["date", "value"]:
            raise DatasetValidationError("CSV must contain exactly date,value columns")
        for row in reader:
            if None in row or any(v is None for v in row.values()):
                raise DatasetValidationError("Malformed CSV row")
            month_str = parse_month(row["date"])
            if month_str in seen:
                raise DatasetValidationError(f"Duplicate monthly observation: {month_str}")
            seen.add(month_str)
            try:
                value = float(row["value"].strip())
            except (ValueError, AttributeError) as exc:
                raise DatasetValidationError(f"Non-numeric or missing value for {month_str}") from exc
            if not math.isfinite(value):
                raise DatasetValidationError(f"Non-finite value for {month_str}")
            if meta["variable"] in {"rainfall", "soil_moisture"} and value < 0:
                raise DatasetValidationError(f"Negative value not accepted: {month_str}")
            year, month = map(int, month_str.split("-"))
            normalized, output_unit = normalize_value(value, year, month, meta["variable"], meta["unit"])
            observations.append({"date": month_str, "value": round(normalized, 9)})
            if len(observations) > 1000:
                raise DatasetValidationError("More than 1000 observations")
    if len(observations) < 2:
        raise DatasetValidationError("At least two observations required")
    observations.sort(key=lambda row: row["date"])
    gaps = []
    for a, b in zip(observations, observations[1:]):
        ay, am = map(int, a["date"].split("-")); by, bm = map(int, b["date"].split("-"))
        difference = (by - ay) * 12 + bm - am
        if difference > 1:
            gaps.append({"after": a["date"], "before": b["date"], "missing_months": difference-1})
    data_dir.mkdir(parents=True, exist_ok=True)
    checksum = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    summary = {**meta, "normalized_unit": output_unit, "observation_count": len(observations), "first_month": observations[0]["date"], "last_month": observations[-1]["date"], "gaps": gaps, "source_file_sha256": checksum, "verification_status": "source_metadata_user_supplied_not_independently_verified"}
    # atomic publish, with no untrusted file paths derived except validated identifier
    base = data_dir / meta["id"]
    import os
    import tempfile
    for suffix, payload in ((".json", json.dumps(summary, indent=2, ensure_ascii=False)), (".csv", "date,value\n" + "".join(f"{r['date']},{r['value']}\n" for r in observations))):
        fd, temp_name = tempfile.mkstemp(prefix="dataset_", dir=data_dir, text=True)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as output:
                output.write(payload)
            os.replace(temp_name, str(base) + suffix)
        finally:
            if os.path.exists(temp_name): os.remove(temp_name)
    return summary

def list_datasets(data_dir):
    base = Path(data_dir)
    if not base.exists():
        return []
    entries = []
    for metadata_path in sorted(base.glob("*.json")):
        try:
            meta = json.loads(metadata_path.read_text(encoding="utf-8"))
            if IDENTIFIER.fullmatch(meta.get("id", "")) and (base / (meta["id"] + ".csv")).is_file():
                entries.append(meta)
        except (json.JSONDecodeError, OSError, TypeError):
            continue
    return entries

def load_dataset(data_dir, dataset_id):
    if not IDENTIFIER.fullmatch(dataset_id):
        raise ValueError("Invalid dataset id")
    base = Path(data_dir)
    meta_file, csv_file = base / (dataset_id + ".json"), base / (dataset_id + ".csv")
    if not meta_file.is_file() or not csv_file.is_file():
        raise FileNotFoundError(dataset_id)
    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    with csv_file.open(encoding="utf-8", newline="") as source:
        observations = [{"date": item["date"], "value": float(item["value"])} for item in csv.DictReader(source)]
    return {"metadata": meta, "observations": observations}
