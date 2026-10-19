import argparse
import sys
import json
from pathlib import Path
from backend.app.db import SessionLocal, init_db
from backend.app.datasets.importers.importer_service import DatasetImporterService

def main():
    parser = argparse.ArgumentParser(description="Prepare and Redact IT Ticket Data for Helpdesk Classifiers.")
    parser.add_argument("--output-dir", type=str, default="data/public/processed/public_it_training/", help="Output directory")

    args = parser.parse_args()

    print("\n[INFO] Preparing IT Ticket Classification Benchmark Data...")
    init_db()
    db = SessionLocal()

    try:
        result = DatasetImporterService.import_dataset(
            name="Console-AI/IT-helpdesk-synthetic-tickets",
            db=db,
            accept_license=True,
            redact_pii=True,
            max_records=100
        )
        print("\nIT Ticket Data Preparation Report:")
        print(json.dumps(result, indent=2))
    finally:
        db.close()

if __name__ == "__main__":
    main()
