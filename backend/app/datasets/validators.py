import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# ------------------------------------------------------------------------------
# 1. DatasetManifest
# ------------------------------------------------------------------------------
class DatasetManifest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    dataset_name: str
    source: str = "huggingface"
    revision: Optional[str] = None
    dataset_card_url: Optional[str] = None
    license: str = "unknown until inspected"
    languages: List[str] = Field(default_factory=list)
    purpose: str = "public_evaluation"
    namespace: str = "public_evaluation"
    splits: List[str] = Field(default_factory=list)
    columns: List[str] = Field(default_factory=list)
    streaming_default: bool = False
    enabled: bool = True
    records_read: int = 0
    records_accepted: int = 0
    records_rejected: int = 0
    pii_redactions: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# ------------------------------------------------------------------------------
# 2. EvaluationCase (for RAG / IndicQA / Ragas)
# ------------------------------------------------------------------------------
class EvaluationCase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_dataset: str
    source_record_id: str
    namespace: str = "public_evaluation"
    category: str = "rag_qa"
    language: str = "eng_Latn"
    question: str
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    answerable: bool = True
    expected_action: str = "answer"
    should_refuse: bool = False
    should_escalate: bool = False
    reference_contexts: List[str] = Field(default_factory=list)
    reference_answer: str
    expected_document_ids: List[str] = Field(default_factory=list)
    expected_chunk_ids: List[str] = Field(default_factory=list)
    required_answer_points: List[str] = Field(default_factory=list)
    forbidden_answer_points: List[str] = Field(default_factory=list)
    risk_level: str = "low"
    metadata: Dict[str, Any] = Field(default_factory=dict)

# ------------------------------------------------------------------------------
# 3. RetrievalBenchmarkCase (for MSMARCO-XI)
# ------------------------------------------------------------------------------
class RetrievalBenchmarkCase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_dataset: str = "ai4bharat/MSMARCO-XI"
    namespace: str = "public_retrieval_benchmark"
    query: str
    query_language: str = "eng_Latn" # hin_Deva, mal_Mlym, eng_Latn
    positive_passages: List[str] = Field(default_factory=list)
    negative_passages: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

# ------------------------------------------------------------------------------
# 4. TranslationBenchmarkCase (for IN22-Conv / IN22-Gen)
# ------------------------------------------------------------------------------
class TranslationBenchmarkCase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_dataset: str = "ai4bharat/IN22-Conv"
    namespace: str = "public_translation_benchmark"
    source_language: str = "eng_Latn"
    target_language: str = "hin_Deva" # hin_Deva, mal_Mlym
    source_text: str
    reference_translation: str
    domain: str = "conversation"
    metadata: Dict[str, Any] = Field(default_factory=dict)

# ------------------------------------------------------------------------------
# 5. ITTicketCase (for IT Helpdesk ticket classifiers)
# ------------------------------------------------------------------------------
class ITTicketCase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_dataset: str
    namespace: str = "public_it_training"
    subject: str
    description: str
    intent: str # one of the 16 canonical intents
    priority: str = "medium" # critical, high, medium, low
    security_incident: bool = False
    needs_ticket: bool = True
    required_fields: List[str] = Field(default_factory=list)
    safe_response_guidance: str = "Standard Level-1 Support"
    metadata: Dict[str, Any] = Field(default_factory=dict)

# ------------------------------------------------------------------------------
# 6. ImportAuditRecord
# ------------------------------------------------------------------------------
class ImportAuditRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    manifest_id: str
    dataset_name: str
    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "started" # started, completed, failed
    records_read: int = 0
    records_accepted: int = 0
    records_rejected: int = 0
    pii_redactions: int = 0
    validation_errors: List[str] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None
    triggered_by: str = "system_admin"
