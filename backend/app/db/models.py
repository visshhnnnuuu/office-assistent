import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Boolean, Integer, DateTime, JSON, ForeignKey, Float
)
from sqlalchemy.orm import relationship
from backend.app.db.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, default="employee", index=True)
    department = Column(String, default="All", index=True)
    preferred_language = Column(String, default="auto")
    answer_depth = Column(String, default="standard")
    created_at = Column(DateTime, default=datetime.utcnow)

    memories = relationship("UserMemoryModel", back_populates="user", cascade="all, delete-orphan")
    tickets = relationship("TicketModel", back_populates="user")
    sessions = relationship("ChatSessionModel", back_populates="user", cascade="all, delete-orphan")

class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False, index=True)
    department = Column(String, nullable=False, index=True)
    classification = Column(String, default="internal", index=True) # public, internal, confidential, restricted
    allowed_roles = Column(JSON, default=list) # e.g. ["employee", "manager", "hr"]
    allowed_departments = Column(JSON, default=list) # e.g. ["all", "HR"]
    version = Column(String, default="1.0")
    effective_date = Column(String, nullable=True)
    review_date = Column(String, nullable=True)
    expiry_date = Column(String, nullable=True)
    owner = Column(String, default="Organization")
    approved_by = Column(String, default="Compliance")
    source_url = Column(String, nullable=True)
    status = Column(String, default="active", index=True) # draft, pending_review, active, archived
    source_type = Column(String, default="pdf") # pdf, docx, pptx, xlsx, csv, markdown, url
    language = Column(String, default="eng_Latn")
    created_at = Column(DateTime, default=datetime.utcnow)

    chunks = relationship("ChunkModel", back_populates="document", cascade="all, delete-orphan")

class ChunkModel(Base):
    __tablename__ = "chunks"

    id = Column(String, primary_key=True, default=generate_uuid)
    chunk_id = Column(String, unique=True, index=True, nullable=False)
    document_id = Column(String, ForeignKey("documents.document_id"), nullable=False, index=True)
    section_title = Column(String, nullable=True)
    page_number = Column(Integer, nullable=True)
    slide_number = Column(Integer, nullable=True)
    sheet_name = Column(String, nullable=True)
    row_reference = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    classification = Column(String, default="internal")
    allowed_roles = Column(JSON, default=list)
    allowed_departments = Column(JSON, default=list)
    language = Column(String, default="eng_Latn")
    embedding = Column(JSON, nullable=True) # JSON array of floats for lightweight dense search
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("DocumentModel", back_populates="chunks")

class UserMemoryModel(Base):
    __tablename__ = "user_memories"

    id = Column(String, primary_key=True, default=generate_uuid)
    memory_id = Column(String, unique=True, index=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    memory_type = Column(String, default="preference") # preference, context
    fact = Column(Text, nullable=False)
    consent = Column(Boolean, default=True)
    sensitivity = Column(String, default="low") # low, high
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserModel", back_populates="memories")

class TicketModel(Base):
    __tablename__ = "tickets"

    id = Column(String, primary_key=True, default=generate_uuid)
    ticket_number = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    user_email = Column(String, nullable=True)
    category = Column(String, nullable=False, index=True)
    summary = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String, default="medium", index=True) # critical, high, medium, low
    device_type = Column(String, nullable=True)
    operating_system = Column(String, nullable=True)
    location = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    business_impact = Column(String, nullable=True)
    status = Column(String, default="open", index=True) # open, in_progress, resolved, closed
    assigned_team = Column(String, default="IT Support L1")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserModel", back_populates="tickets")

class DatasetManifestModel(Base):
    __tablename__ = "dataset_manifests"

    id = Column(String, primary_key=True, default=generate_uuid)
    dataset_name = Column(String, unique=True, index=True, nullable=False)
    source = Column(String, default="huggingface")
    revision = Column(String, nullable=True)
    dataset_card_url = Column(String, nullable=True)
    license = Column(String, default="unknown")
    languages = Column(JSON, default=list)
    purpose = Column(String, default="public_evaluation")
    namespace = Column(String, default="public_evaluation")
    splits = Column(JSON, default=list)
    columns = Column(JSON, default=list)
    streaming_default = Column(Boolean, default=False)
    enabled = Column(Boolean, default=True)
    records_read = Column(Integer, default=0)
    records_accepted = Column(Integer, default=0)
    records_rejected = Column(Integer, default=0)
    pii_redactions = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class ImportAuditRecordModel(Base):
    __tablename__ = "import_audit_records"

    id = Column(String, primary_key=True, default=generate_uuid)
    manifest_id = Column(String, nullable=False, index=True)
    dataset_name = Column(String, nullable=False, index=True)
    run_id = Column(String, default=generate_uuid, index=True)
    status = Column(String, default="started") # started, completed, failed
    records_read = Column(Integer, default=0)
    records_accepted = Column(Integer, default=0)
    records_rejected = Column(Integer, default=0)
    pii_redactions = Column(Integer, default=0)
    validation_errors = Column(JSON, default=list)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    triggered_by = Column(String, default="system_admin")

class ChatSessionModel(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, default="New Conversation")
    pinned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserModel", back_populates="sessions")
    messages = relationship("ChatMessageModel", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessageModel.created_at")

class ChatMessageModel(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(String, nullable=False) # user, assistant, system
    content = Column(Text, nullable=False)
    language = Column(String, default="eng_Latn")
    sources = Column(JSON, default=list)
    follow_up_suggestions = Column(JSON, default=list)
    feedback = Column(String, nullable=True) # helpful, not_helpful, reported
    feedback_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSessionModel", back_populates="messages")
