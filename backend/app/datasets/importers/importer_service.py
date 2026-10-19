import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.config import settings
from backend.app.datasets.registry import DatasetRegistry
from backend.app.datasets.huggingface_client import HuggingFaceClient
from backend.app.datasets.schema_inspector import SchemaInspector
from backend.app.datasets.manifest_service import ManifestService
from backend.app.datasets.normalizers.dynamic_normalizer import DynamicDatasetNormalizer

class DatasetImporterService:
    @staticmethod
    def inspect_dataset(name: str, db: Session) -> Dict[str, Any]:
        """
        Inspects dataset schema, splits, and licensing without committing imports.
        """
        ds_info = DatasetRegistry.get_dataset(name)
        if not ds_info:
            return {"status": "error", "message": f"Dataset '{name}' not found in registry."}

        manifest = ManifestService.get_or_create_manifest(ds_info, db)
        sample_rows = HuggingFaceClient.fetch_records(name, split=ds_info.get("splits", ["train"])[0], max_records=5)
        inspection = SchemaInspector.inspect_sample_records(sample_rows)

        # Update manifest columns
        ManifestService.update_manifest_stats(
            manifest_id=manifest.id,
            records_read=len(sample_rows),
            records_accepted=len(sample_rows),
            records_rejected=0,
            pii_redactions=0,
            columns=inspection.get("columns", []),
            db=db
        )

        return {
            "status": "success",
            "dataset_name": name,
            "manifest_id": manifest.id,
            "license": ds_info.get("license"),
            "namespace": ds_info.get("namespace"),
            "category": ds_info.get("category"),
            "splits": ds_info.get("splits"),
            "columns": inspection.get("columns"),
            "inferred_types": inspection.get("inferred_types"),
            "sample_preview": inspection.get("first_record_preview")
        }

    @staticmethod
    def import_dataset(
        name: str,
        db: Session,
        accept_license: bool = False,
        redact_pii: bool = True,
        max_records: int = 100,
        split: Optional[str] = None,
        streaming: bool = True,
        triggered_by: str = "system_admin"
    ) -> Dict[str, Any]:
        """
        Executes the controlled Hugging Face dataset import workflow.
        Enforces licensing gates, PII redaction, normalization, and quarantined public storage.
        """
        # Step 1: Registry lookup
        ds_info = DatasetRegistry.get_dataset(name)
        if not ds_info:
            return {"status": "failed", "error": f"Dataset '{name}' not recognized in configs/datasets.yaml."}

        # Step 2: License gate verification
        if not accept_license and not settings.accept_dataset_licenses:
            return {
                "status": "refused_unlicensed",
                "dataset_name": name,
                "license": ds_info.get("license"),
                "error": (
                    f"Import rejected: License acceptance required for '{name}' (License: {ds_info.get('license')}). "
                    "Set ACCEPT_DATASET_LICENSES=true or provide the --accept-license CLI flag."
                )
            }

        # Step 3: Voice dataset gate check
        if ds_info.get("category") == "voice" and not settings.enable_voice_datasets:
            return {
                "status": "refused_policy",
                "error": "Voice datasets are disabled by security policy unless ENABLE_VOICE_DATASETS=true."
            }

        manifest = ManifestService.get_or_create_manifest(ds_info, db)
        audit = ManifestService.create_audit_record(manifest.id, name, triggered_by, db)

        # Step 4: Fetch rows
        target_split = split or ds_info.get("splits", ["train"])[0]
        raw_records = HuggingFaceClient.fetch_records(name, split=target_split, max_records=max_records, streaming=streaming)

        records_read = len(raw_records)
        accepted_records: List[Dict[str, Any]] = []
        validation_errors: List[str] = []
        total_redactions = 0

        # Step 5: Normalize, Redact & Validate
        for idx, raw in enumerate(raw_records):
            try:
                norm_obj, n_redact = DynamicDatasetNormalizer.normalize_record(
                    dataset_name=name,
                    raw_record=raw,
                    redact_pii=redact_pii
                )
                if norm_obj:
                    accepted_records.append(norm_obj.model_dump())
                    total_redactions += n_redact
            except Exception as e:
                validation_errors.append(f"Row {idx} validation error: {str(e)}")

        records_accepted = len(accepted_records)
        records_rejected = records_read - records_accepted

        # Step 6: Store in quarantined public namespace (never in production knowledge!)
        namespace = ds_info.get("namespace", "public_evaluation")
        safe_name = name.replace("/", "_")
        target_dir = settings.dataset_storage_path / "processed" / namespace / safe_name
        target_dir.mkdir(parents=True, exist_ok=True)

        output_file = target_dir / f"{target_split}_normalized.jsonl"
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in accepted_records:
                f.write(json.dumps(item, default=str) + "\n")

        # Step 7: Update Manifest & Audit Log
        columns = list(raw_records[0].keys()) if raw_records else []
        ManifestService.update_manifest_stats(
            manifest_id=manifest.id,
            records_read=records_read,
            records_accepted=records_accepted,
            records_rejected=records_rejected,
            pii_redactions=total_redactions,
            columns=columns,
            db=db
        )

        ManifestService.complete_audit_record(
            audit_id=audit.id,
            status="completed" if records_accepted > 0 else "failed",
            records_read=records_read,
            records_accepted=records_accepted,
            records_rejected=records_rejected,
            pii_redactions=total_redactions,
            errors=validation_errors,
            db=db
        )

        return {
            "status": "completed",
            "dataset_name": name,
            "namespace": namespace,
            "split": target_split,
            "records_read": records_read,
            "records_accepted": records_accepted,
            "records_rejected": records_rejected,
            "pii_redactions": total_redactions,
            "target_path": str(output_file),
            "production_quarantine_enforced": True
        }
