from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from backend.app.rag.bm25 import BM25Okapi
from backend.app.rag.vector_store import VectorStore
from backend.app.auth.rbac import RBACManager
from backend.app.multilingual.translator import CrossLingualQueryExpander
from backend.app.db.models import ChunkModel, DocumentModel

class HybridRetriever:
    def __init__(self, vector_store: VectorStore, bm25: BM25Okapi):
        self.vector_store = vector_store
        self.bm25 = bm25

    def index_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        """
        Populates both the dense vector store and the lexical BM25 index.
        """
        self.vector_store.add_chunks(chunks)
        self.bm25.fit(chunks)

    def retrieve(
        self,
        query: str,
        user_role: str,
        user_department: str,
        db: Session,
        detected_language: str = "eng_Latn",
        top_k: int = 6
    ) -> List[Dict[str, Any]]:
        """
        Executes RBAC-guarded hybrid retrieval:
        1. Pre-filters all active chunks in DB according to user permissions.
        2. Expands cross-lingual query if needed.
        3. Executes BM25 lexical search and Dense vector search over permitted chunks.
        4. Fuses rankings using Reciprocal Rank Fusion (RRF).
        5. Returns best 4-8 permitted chunks with complete metadata.
        """
        # Step 1: RBAC pre-filter
        # Retrieve all active documents allowed for this user
        docs = db.query(DocumentModel).filter(DocumentModel.status == "active").all()
        permitted_doc_ids = set()
        for doc in docs:
            if RBACManager.is_chunk_accessible(
                user_role=user_role,
                user_department=user_department,
                chunk_allowed_roles=doc.allowed_roles or ["all"],
                chunk_allowed_departments=doc.allowed_departments or ["all"],
                chunk_classification=doc.classification
            ):
                permitted_doc_ids.add(doc.document_id)

        if not permitted_doc_ids:
            return []

        # Find permitted chunks
        permitted_chunks = (
            db.query(ChunkModel)
            .filter(ChunkModel.document_id.in_(permitted_doc_ids))
            .all()
        )

        permitted_chunk_lookup: Dict[str, ChunkModel] = {}
        for ch in permitted_chunks:
            if RBACManager.is_chunk_accessible(
                user_role=user_role,
                user_department=user_department,
                chunk_allowed_roles=ch.allowed_roles or ["all"],
                chunk_allowed_departments=ch.allowed_departments or ["all"],
                chunk_classification=ch.classification
            ):
                permitted_chunk_lookup[ch.chunk_id] = ch

        permitted_chunk_ids = list(permitted_chunk_lookup.keys())
        if not permitted_chunk_ids:
            return []

        # Step 2: Cross-lingual query expansion
        expanded_query = CrossLingualQueryExpander.expand_query(query, detected_language)

        # Step 3: Run searches
        vector_results = self.vector_store.search(
            query=expanded_query,
            top_k=20,
            filter_chunk_ids=permitted_chunk_ids
        )
        bm25_results = self.bm25.search(
            query=expanded_query,
            top_k=20
        )

        # Step 4: Reciprocal Rank Fusion (RRF) with k=60
        rrf_scores: Dict[str, float] = {}
        rrf_k = 60.0

        for rank, (cid, score) in enumerate(vector_results, 1):
            if cid in permitted_chunk_lookup:
                rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (rrf_k + rank))

        for rank, (cid, score) in enumerate(bm25_results, 1):
            if cid in permitted_chunk_lookup:
                rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (rrf_k + rank))

        # Sort by fused score
        sorted_chunks = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        top_chunk_ids = [cid for cid, _ in sorted_chunks[:top_k]]

        # Prepare rich chunk objects
        results: List[Dict[str, Any]] = []
        for cid in top_chunk_ids:
            ch = permitted_chunk_lookup[cid]
            parent_doc = db.query(DocumentModel).filter(DocumentModel.document_id == ch.document_id).first()

            results.append({
                "chunk_id": ch.chunk_id,
                "document_id": ch.document_id,
                "title": parent_doc.title if parent_doc else "Internal Document",
                "department": parent_doc.department if parent_doc else "General",
                "classification": ch.classification,
                "version": parent_doc.version if parent_doc else "1.0",
                "effective_date": parent_doc.effective_date if parent_doc else None,
                "review_date": parent_doc.review_date if parent_doc else None,
                "owner": parent_doc.owner if parent_doc else "Internal",
                "source_url": parent_doc.source_url if parent_doc else None,
                "section_title": ch.section_title or "General Overview",
                "page_number": ch.page_number,
                "slide_number": ch.slide_number,
                "sheet_name": ch.sheet_name,
                "row_reference": ch.row_reference,
                "source_type": parent_doc.source_type if parent_doc else "pdf",
                "language": ch.language,
                "content": ch.content,
                "score": round(rrf_scores[cid], 4)
            })

        return results
