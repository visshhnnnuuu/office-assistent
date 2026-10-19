from backend.app.db.database import Base, engine, SessionLocal, get_db
from backend.app.db.models import (
    UserModel, DocumentModel, ChunkModel, UserMemoryModel,
    TicketModel, DatasetManifestModel, ImportAuditRecordModel,
    ChatSessionModel, ChatMessageModel
)

def init_db():
    Base.metadata.create_all(bind=engine)
