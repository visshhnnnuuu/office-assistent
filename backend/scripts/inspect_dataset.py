import argparse
import sys
import json
from backend.app.db import SessionLocal, init_db
from backend.app.datasets.importers.importer_service import DatasetImporterService

def main():
    parser = argparse.ArgumentParser(description="Inspect a Hugging Face dataset schema, splits, and metadata.")
    parser.add_argument("--name", type=str, required=True, help="Hugging Face dataset identifier (e.g., ai4bharat/IndicQA)")

    args = parser.parse_args()

    init_db()
    db = SessionLocal()
    try:
        print(f"\n[INFO] Inspecting dataset '{args.name}'...")
        result = DatasetImporterService.inspect_dataset(args.name, db)
        print(json.dumps(result, indent=2))
    finally:
        db.close()

if __name__ == "__main__":
    main()
