import argparse
import sys
import json
from backend.app.db import SessionLocal, init_db
from backend.app.datasets.registry import DatasetRegistry
from backend.app.datasets.importers.importer_service import DatasetImporterService

def main():
    parser = argparse.ArgumentParser(description="Controlled Hugging Face Dataset Importer with Governance Gates.")
    parser.add_argument("--name", type=str, help="Dataset identifier (e.g., ai4bharat/IndicQA)")
    parser.add_argument("--all-enabled", action="store_true", help="Import all enabled datasets from registry")
    parser.add_argument("--split", type=str, default=None, help="Dataset split (train, validation, test)")
    parser.add_argument("--max-records", type=int, default=100, help="Maximum sample records to import")
    parser.add_argument("--streaming", action="store_true", default=True, help="Stream dataset instead of full download")
    parser.add_argument("--dry-run", action="store_true", help="Simulate import without writing to disk")
    parser.add_argument("--inspect-only", action="store_true", help="Inspect schema and manifest without importing records")
    parser.add_argument("--accept-license", action="store_true", help="Explicitly accept dataset license terms")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing processed data")
    parser.add_argument("--output-format", type=str, default="jsonl", choices=["jsonl", "parquet", "database"], help="Output storage format")
    parser.add_argument("--language", type=str, default=None, help="Language filter (hi, ml, en)")
    parser.add_argument("--namespace", type=str, default=None, help="Target storage namespace")
    parser.add_argument("--redact-pii", action="store_true", default=True, help="Scrub personal data, emails, and secrets")
    parser.add_argument("--validate-only", action="store_true", help="Validate schema conformity only")

    args = parser.parse_args()

    if not args.name and not args.all_enabled:
        print("[ERROR] You must specify either --name <dataset> or --all-enabled.")
        sys.exit(1)

    init_db()
    db = SessionLocal()

    try:
        datasets_to_import = []
        if args.name:
            datasets_to_import.append(args.name)
        elif args.all_enabled:
            enabled = DatasetRegistry.list_datasets(enabled_only=True)
            datasets_to_import = [d["name"] for d in enabled]

        print(f"\n========================================================")
        print(f"  Hugging Face Dataset Importer (Count: {len(datasets_to_import)})")
        print(f"  License Gate: {'ACCEPTED' if args.accept_license else 'NOT ACCEPTED'}")
        print(f"  PII Redaction: {'ENABLED' if args.redact_pii else 'DISABLED'}")
        print(f"========================================================\n")

        for ds_name in datasets_to_import:
            print(f"[PROCESS] Processing '{ds_name}'...")

            if args.inspect_only:
                res = DatasetImporterService.inspect_dataset(ds_name, db)
                print(json.dumps(res, indent=2))
                continue

            result = DatasetImporterService.import_dataset(
                name=ds_name,
                db=db,
                accept_license=args.accept_license,
                redact_pii=args.redact_pii,
                max_records=args.max_records,
                split=args.split,
                streaming=args.streaming
            )

            status = result.get("status")
            if status == "completed":
                print(f"[SUCCESS] {ds_name} imported successfully!")
                print(f"  Records Read: {result.get('records_read')}")
                print(f"  Records Accepted: {result.get('records_accepted')}")
                print(f"  PII Redactions: {result.get('pii_redactions')}")
                print(f"  Quarantined Path: {result.get('target_path')}")
            elif status == "refused_unlicensed":
                print(f"[REFUSED] {ds_name}: {result.get('error')}")
            else:
                print(f"[FAILED] {ds_name}: {result.get('error')}")
            print("-" * 56)

    finally:
        db.close()

if __name__ == "__main__":
    main()
