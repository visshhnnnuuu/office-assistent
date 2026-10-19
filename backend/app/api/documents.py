import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.db.models import DocumentModel, ChunkModel, UserModel
from backend.app.auth.token import get_current_user
from backend.app.auth.rbac import RBACManager
from backend.app.documents.validator import DocumentSecurityValidator
from backend.app.documents.parsers import DocumentParserFactory
from backend.app.rag.chunker import HeadingAwareChunker
from backend.app.rag.vector_store import generate_local_embedding

router = APIRouter(prefix="/api/documents", tags=["Office Documents & Ingestion"])

@router.get("")
def list_documents(user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    docs = db.query(DocumentModel).filter(DocumentModel.status == "active").all()
    permitted = []
    for d in docs:
        if RBACManager.is_chunk_accessible(
            user_role=user.role,
            user_department=user.department,
            chunk_allowed_roles=d.allowed_roles or ["all"],
            chunk_allowed_departments=d.allowed_departments or ["all"],
            chunk_classification=d.classification
        ):
            permitted.append({
                "document_id": d.document_id,
                "title": d.title,
                "department": d.department,
                "classification": d.classification,
                "version": d.version,
                "owner": d.owner,
                "review_date": d.review_date,
                "source_type": d.source_type,
                "chunks_count": len(d.chunks)
            })
    return permitted

@router.post("/upload-preview")
async def upload_and_preview(
    file: UploadFile = File(...),
    user: UserModel = Depends(get_current_user)
):
    """
    Step 1 of Ingestion:
    File scan, MIME verification, malware scan, blacklist scan, text extraction & chunk preview.
    """
    if user.role not in {"it_admin", "system_admin", "hr", "manager"}:
        raise HTTPException(status_code=403, detail="Document ingestion is restricted to authorized administrative roles.")

    content = await file.read()
    DocumentSecurityValidator.validate_upload(file.filename, file.content_type, len(content))

    parsed = DocumentParserFactory.parse_content(content, file.filename, file.content_type)
    text = parsed["text"]

    # Security Blacklist Scan
    is_violating, violations = DocumentSecurityValidator.scan_for_blacklisted_content(text)
    if is_violating:
        raise HTTPException(
            status_code=400,
            detail=f"Security scan rejected file! Prohibited confidential tokens detected: {', '.join(violations[:3])}"
        )

    # Preview chunking
    chunker = HeadingAwareChunker()
    preview_chunks = chunker.chunk_document(
        document_id="preview_doc",
        text=text,
        base_metadata={"title": file.filename}
    )

    return {
        "status": "scan_passed",
        "filename": file.filename,
        "content_length": len(text),
        "preview_chunks_count": len(preview_chunks),
        "preview_chunks": preview_chunks[:3],
        "extracted_text_preview": text[:400] + "..."
    }

@router.post("/approve-and-index")
def approve_and_index_document(
    title: str = Body(...),
    department: str = Body(...),
    classification: str = Body("internal"),
    allowed_roles: List[str] = Body(["employee", "manager", "hr", "finance", "it_support"]),
    allowed_departments: List[str] = Body(["all"]),
    version: str = Body("1.0"),
    content_text: str = Body(...),
    owner: str = Body("Department"),
    approved_by: str = Body("Compliance Officer"),
    source_type: str = Body("pdf"),
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Step 2 of Ingestion:
    Admin/Department owner approval -> sets status to active -> generates chunks & embeddings.
    """
    if user.role not in {"system_admin", "it_admin", "hr", "manager"}:
        raise HTTPException(status_code=403, detail="Document approval requires admin authorization.")

    doc_id = f"doc_{uuid.uuid4().hex[:10]}"
    doc = DocumentModel(
        document_id=doc_id,
        title=title,
        department=department,
        classification=classification,
        allowed_roles=allowed_roles,
        allowed_departments=allowed_departments,
        version=version,
        owner=owner,
        approved_by=approved_by,
        source_type=source_type,
        status="active"
    )
    db.add(doc)
    db.commit()

    chunker = HeadingAwareChunker()
    chunks = chunker.chunk_document(
        document_id=doc_id,
        text=content_text,
        base_metadata={
            "title": title,
            "classification": classification,
            "allowed_roles": allowed_roles,
            "allowed_departments": allowed_departments,
            "language": "eng_Latn"
        }
    )

    for ch in chunks:
        embedding = generate_local_embedding(f"{ch.get('section_title', '')} {ch.get('content', '')}")
        chunk_model = ChunkModel(
            chunk_id=ch["chunk_id"],
            document_id=doc_id,
            section_title=ch.get("section_title"),
            page_number=ch.get("page_number", 1),
            content=ch["content"],
            classification=classification,
            allowed_roles=allowed_roles,
            allowed_departments=allowed_departments,
            embedding=embedding
        )
        db.add(chunk_model)

    db.commit()

    return {
        "status": "indexed",
        "document_id": doc_id,
        "title": title,
        "chunks_indexed": len(chunks)
    }
