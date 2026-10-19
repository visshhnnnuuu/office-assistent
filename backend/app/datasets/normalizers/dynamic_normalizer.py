import uuid
from typing import Dict, Any, Optional, Tuple
from backend.app.datasets.validators import (
    EvaluationCase, RetrievalBenchmarkCase, TranslationBenchmarkCase, ITTicketCase
)
from backend.app.datasets.schema_inspector import SchemaInspector
from backend.app.datasets.pii_redactor import PIIRedactor

class DynamicDatasetNormalizer:
    @staticmethod
    def normalize_record(
        dataset_name: str,
        raw_record: Dict[str, Any],
        mapping_cfg: Optional[Dict[str, Any]] = None,
        redact_pii: bool = True
    ) -> Tuple[Optional[Any], int]:
        """
        Dynamically transforms raw dataset records into standard Pydantic models.
        Returns: (normalized_pydantic_object, redaction_count)
        """
        redactions_performed = 0
        record = raw_record
        if redact_pii:
            record, redactions_performed = PIIRedactor.redact_record(raw_record)

        # 1. IndicQA
        if "IndicQA" in dataset_name:
            q = SchemaInspector.find_best_field_match(record, ["question", "query"]) or "Untitled Question"
            ctx = SchemaInspector.find_best_field_match(record, ["context", "passage"]) or ""
            ans = SchemaInspector.find_best_field_match(record, ["answers.text[0]", "answer", "reference"]) or ""
            lang = SchemaInspector.find_best_field_match(record, ["language", "lang"]) or "hi"
            lang_code = "hin_Deva" if lang == "hi" else ("mal_Mlym" if lang == "ml" else "eng_Latn")
            rec_id = str(SchemaInspector.find_best_field_match(record, ["id", "question_id"]) or uuid.uuid4())

            obj = EvaluationCase(
                source_dataset=dataset_name,
                source_record_id=rec_id,
                namespace="public_evaluation",
                category="rag_qa",
                language=lang_code,
                question=q,
                reference_contexts=[ctx] if isinstance(ctx, str) and ctx else (ctx if isinstance(ctx, list) else []),
                reference_answer=str(ans),
                risk_level="low"
            )
            return obj, redactions_performed

        # 2. MSMARCO-XI
        elif "MSMARCO-XI" in dataset_name:
            query = SchemaInspector.find_best_field_match(record, ["query", "question"]) or ""
            q_lang = SchemaInspector.find_best_field_match(record, ["query_language", "lang"]) or "eng_Latn"
            pos = SchemaInspector.find_best_field_match(record, ["positive_passages", "positives"]) or []
            neg = SchemaInspector.find_best_field_match(record, ["negative_passages", "negatives"]) or []

            obj = RetrievalBenchmarkCase(
                source_dataset=dataset_name,
                namespace="public_retrieval_benchmark",
                query=query,
                query_language=q_lang,
                positive_passages=pos if isinstance(pos, list) else [str(pos)],
                negative_passages=neg if isinstance(neg, list) else [str(neg)],
            )
            return obj, redactions_performed

        # 3. IN22-Conv or IN22-Gen
        elif "IN22" in dataset_name:
            src_text = SchemaInspector.find_best_field_match(record, ["source", "sentence_eng", "en"]) or ""
            ref_tgt = SchemaInspector.find_best_field_match(record, ["target", "sentence_tgt", "translation"]) or ""
            src_lang = SchemaInspector.find_best_field_match(record, ["source_language"]) or "eng_Latn"
            tgt_lang = SchemaInspector.find_best_field_match(record, ["target_language"]) or "hin_Deva"

            obj = TranslationBenchmarkCase(
                source_dataset=dataset_name,
                namespace="public_translation_benchmark",
                source_language=src_lang,
                target_language=tgt_lang,
                source_text=src_text,
                reference_translation=ref_tgt,
                domain="conversation" if "Conv" in dataset_name else "general"
            )
            return obj, redactions_performed

        # 4. IT synthetic tickets & L1 classification
        elif "IT-helpdesk" in dataset_name or "it-support" in dataset_name:
            subj = SchemaInspector.find_best_field_match(record, ["subject", "title", "short_description"]) or "IT Issue"
            desc = SchemaInspector.find_best_field_match(record, ["description", "text", "body"]) or ""
            raw_intent = SchemaInspector.find_best_field_match(record, ["category", "intent", "label"]) or "unknown"
            raw_prio = SchemaInspector.find_best_field_match(record, ["priority", "severity"]) or "medium"

            # Translate intent to canonical taxonomy
            norm_intent = str(raw_intent).lower().replace(" ", "_").replace("-", "_")
            if "vpn" in norm_intent:
                canonical_intent = "vpn_issue"
            elif "password" in norm_intent:
                canonical_intent = "password_reset"
            elif "phish" in norm_intent or "security" in norm_intent:
                canonical_intent = "security_incident"
            elif "wifi" in norm_intent or "network" in norm_intent:
                canonical_intent = "wifi_issue"
            elif "software" in norm_intent:
                canonical_intent = "software_installation"
            elif "printer" in norm_intent:
                canonical_intent = "printer_issue"
            elif "locked" in norm_intent:
                canonical_intent = "account_locked"
            else:
                canonical_intent = "unknown"

            prio = str(raw_prio).lower()
            canonical_priority = "critical" if canonical_intent == "security_incident" or "critical" in prio else ("high" if "high" in prio else ("low" if "low" in prio else "medium"))

            obj = ITTicketCase(
                source_dataset=dataset_name,
                namespace="public_it_training",
                subject=subj,
                description=desc,
                intent=canonical_intent,
                priority=canonical_priority,
                security_incident=(canonical_intent == "security_incident"),
                needs_ticket=True
            )
            return obj, redactions_performed

        # 5. RAGAS Golden / RAG instruct
        elif "ragas" in dataset_name or "rag_instruct" in dataset_name:
            q = SchemaInspector.find_best_field_match(record, ["user_input", "query", "question"]) or ""
            ctx = SchemaInspector.find_best_field_match(record, ["reference_contexts", "context"]) or []
            ans = SchemaInspector.find_best_field_match(record, ["reference", "ground_truth", "answer"]) or ""

            obj = EvaluationCase(
                source_dataset=dataset_name,
                source_record_id=str(uuid.uuid4()),
                namespace="public_evaluation",
                category="rag_qa",
                question=q,
                reference_contexts=ctx if isinstance(ctx, list) else [str(ctx)],
                reference_answer=str(ans)
            )
            return obj, redactions_performed

        # Generic evaluation case fallback
        q = SchemaInspector.find_best_field_match(record, ["question", "query", "text"]) or "Generic Query"
        ans = SchemaInspector.find_best_field_match(record, ["answer", "target", "label"]) or ""

        obj = EvaluationCase(
            source_dataset=dataset_name,
            source_record_id=str(uuid.uuid4()),
            namespace="public_evaluation",
            question=q,
            reference_answer=str(ans)
        )
        return obj, redactions_performed
