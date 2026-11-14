"""CLI entrypoint: python -m services.import_dataset --csv ... --metadata ..."""
import argparse
import json
from pathlib import Path
from .dataset_store import DatasetValidationError, ingest

def main():
    parser = argparse.ArgumentParser(description="Import a normalized monthly data CSV with NASA source metadata")
    parser.add_argument("--csv", required=True)
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--output-dir", default=str(Path(__file__).resolve().parents[1] / "data"))
    args = parser.parse_args()
    try:
        result = ingest(args.csv, args.metadata, args.output_dir)
    except (DatasetValidationError, ValueError, OSError, json.JSONDecodeError) as exc:
        parser.exit(1, f"IMPORT FAILED: {exc}\n")
    print(json.dumps(result, indent=2))
    print("IMPORT SUCCESS: User-provided NASA source metadata has NOT been independently verified.")

if __name__ == "__main__":
    main()
