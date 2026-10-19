from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.db.models import UserModel, DatasetManifestModel, ImportAuditRecordModel
from backend.app.auth.token import get_current_user
from backend.app.datasets.registry import DatasetRegistry
from backend.app.datasets.importers.importer_service import DatasetImporterService

router = APIRouter(prefix="/api/datasets", tags=["Hugging Face Dataset Governance & Benchmarks"])

@router.get("")
def list_datasets(category: Optional[str] = None):
    return DatasetRegistry.list_datasets(category=category)

@router.post("/inspect")
def inspect_dataset(
    dataset_name: str = Body(..., embed=True),
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = DatasetImporterService.inspect_dataset(dataset_name, db)
    return result

@router.post("/import")
def import_dataset(
    dataset_name: str = Body(..., embed=True),
    accept_license: bool = Body(False, embed=True),
    redact_pii: bool = Body(True, embed=True),
    max_records: int = Body(100, embed=True),
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user.role not in {"system_admin", "it_admin"}:
        raise HTTPException(status_code=403, detail="Dataset imports require administrative authority.")

    result = DatasetImporterService.import_dataset(
        name=dataset_name,
        db=db,
        accept_license=accept_license,
        redact_pii=redact_pii,
        max_records=max_records,
        triggered_by=user.email
    )
    return result

@router.get("/manifests")
def list_manifests(db: Session = Depends(get_db)):
    manifests = db.query(DatasetManifestModel).all()
    return [
        {
            "id": m.id,
            "dataset_name": m.dataset_name,
            "license": m.license,
            "namespace": m.namespace,
            "purpose": m.purpose,
            "records_read": m.records_read,
            "records_accepted": m.records_accepted,
            "records_rejected": m.records_rejected,
            "pii_redactions": m.pii_redactions,
            "updated_at": m.updated_at.isoformat() if m.updated_at else None
        }
        for m in manifests
    ]

@router.get("/audits")
def list_audits(db: Session = Depends(get_db)):
    audits = db.query(ImportAuditRecordModel).order_by(ImportAuditRecordModel.started_at.desc()).limit(50).all()
    return [
        {
            "id": a.id,
            "dataset_name": a.dataset_name,
            "status": a.status,
            "records_accepted": a.records_accepted,
            "pii_redactions": a.pii_redactions,
            "triggered_by": a.triggered_by,
            "started_at": a.started_at.isoformat() if a.started_at else None,
            "finished_at": a.finished_at.isoformat() if a.finished_at else None
        }
        for a in audits
    ]
