from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.db.models import DatasetManifestModel, ImportAuditRecordModel

class ManifestService:
    @staticmethod
    def get_or_create_manifest(dataset_info: Dict[str, Any], db: Session) -> DatasetManifestModel:
        name = dataset_info["name"]
        manifest = db.query(DatasetManifestModel).filter(DatasetManifestModel.dataset_name == name).first()
        if not manifest:
            manifest = DatasetManifestModel(
                dataset_name=name,
                source=dataset_info.get("source", "huggingface"),
                dataset_card_url=dataset_info.get("dataset_card_url"),
                license=dataset_info.get("license", "unknown"),
                languages=dataset_info.get("languages", []),
                purpose=dataset_info.get("purpose", "public_evaluation"),
                namespace=dataset_info.get("namespace", "public_evaluation"),
                splits=dataset_info.get("splits", ["train"]),
                streaming_default=dataset_info.get("streaming_default", False),
                enabled=dataset_info.get("enabled", True),
            )
            db.add(manifest)
            db.commit()
            db.refresh(manifest)
        return manifest

    @staticmethod
    def update_manifest_stats(
        manifest_id: str,
        records_read: int,
        records_accepted: int,
        records_rejected: int,
        pii_redactions: int,
        columns: List[str],
        db: Session
    ) -> DatasetManifestModel:
        manifest = db.query(DatasetManifestModel).filter(DatasetManifestModel.id == manifest_id).first()
        if manifest:
            manifest.records_read = records_read
            manifest.records_accepted = records_accepted
            manifest.records_rejected = records_rejected
            manifest.pii_redactions = pii_redactions
            manifest.columns = columns
            manifest.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(manifest)
        return manifest

    @staticmethod
    def create_audit_record(
        manifest_id: str,
        dataset_name: str,
        triggered_by: str,
        db: Session
    ) -> ImportAuditRecordModel:
        audit = ImportAuditRecordModel(
            manifest_id=manifest_id,
            dataset_name=dataset_name,
            triggered_by=triggered_by,
            status="started"
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)
        return audit

    @staticmethod
    def complete_audit_record(
        audit_id: str,
        status: str,
        records_read: int,
        records_accepted: int,
        records_rejected: int,
        pii_redactions: int,
        errors: List[str],
        db: Session
    ) -> ImportAuditRecordModel:
        audit = db.query(ImportAuditRecordModel).filter(ImportAuditRecordModel.id == audit_id).first()
        if audit:
            audit.status = status
            audit.records_read = records_read
            audit.records_accepted = records_accepted
            audit.records_rejected = records_rejected
            audit.pii_redactions = pii_redactions
            audit.validation_errors = errors
            audit.finished_at = datetime.utcnow()
            db.commit()
            db.refresh(audit)
        return audit
