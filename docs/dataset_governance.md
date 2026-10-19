# Hugging Face Dataset Governance & Quarantine Protocol

## 1. Absolute Boundary: Public Benchmarks vs. Private Knowledge

> **CRITICAL ARCHITECTURAL DIRECTIVE:**
> Public Hugging Face datasets MUST NEVER be ingested, embedded, or merged into the production office knowledge base or internal RAG vector index.

### Operational Roles
- **Private Knowledge Base (`private_office_knowledge`):** The single, authoritative source of truth for company policy, HR workflows, IT instructions, employee handbooks, and operational SOPs. Only approved documents vetted by organizational stakeholders may exist here.
- **Public Evaluation Datasets (`public_*`):** Strictly quarantined for model evaluation, retrieval benchmarking, translation regression testing, and IT helpdesk intent classifier fine-tuning or evaluation.

---

## 2. Namespace Segregation Matrix

| Namespace | Intended Purpose | Production Vector Store Access |
|---|---|---|
| `private_office_knowledge` | Production RAG factual retrieval | **YES (Sole Authoritative Source)** |
| `private_office_evaluation` | Locked internal evaluation benchmark | **NO** |
| `public_evaluation` | RAGAS / IndicQA context QA evaluation | **BLOCKED** |
| `public_retrieval_benchmark` | Cross-lingual retrieval quality (MSMARCO) | **BLOCKED** |
| `public_translation_benchmark`| Indic translation accuracy (IN22) | **BLOCKED** |
| `public_it_training` | IT intent & priority classifier testing | **BLOCKED** |
| `public_voice_benchmark` | Speech-to-text / Audio evaluation | **BLOCKED** |

---

## 3. Ingestion Lifecycle & Safeguards

```
[ Hugging Face Hub ]
         |
         v
+-------------------------------+
|  1. Inspection & Metadata     | -> Validates licensing, size, splits, schema columns.
+-------------------------------+
         |
         v
+-------------------------------+
|  2. License Acceptance Gate   | -> Requires explicit --accept-license CLI argument
+-------------------------------+    and ACCEPT_DATASET_LICENSES=true environment flag.
         |
         v
+-------------------------------+
|  3. Streaming & Sample Limiter| -> Prevents unbounded disk consumption (default 1000 records).
+-------------------------------+
         |
         v
+-------------------------------+
|  4. PII & Secrets Redaction   | -> Masks emails, phone numbers, auth tokens, IPs.
+-------------------------------+
         |
         v
+-------------------------------+
|  5. Schema Normalization      | -> Dynamic mapping into canonical Pydantic schemas:
+-------------------------------+    EvaluationCase, RetrievalBenchmarkCase, TranslationBenchmarkCase, ITTicketCase.
         |
         v
+-------------------------------+
|  6. Quarantined Storage       | -> Stored in data/public/processed/<namespace>/<dataset_name>/
+-------------------------------+
         |
         v
+-------------------------------+
|  7. Database Audit Log        | -> Persists ImportAuditRecord with timestamp, record counts,
+-------------------------------+    redaction tallies, and validation metrics.
```

---

## 4. Redaction Specification
The dataset normalizer enforces regular expression and token-level PII scrubbers:
- **Email Addresses:** Matched and replaced with `[REDACTED_EMAIL]`
- **Phone Numbers:** International and Indian 10-digit mobile numbers replaced with `[REDACTED_PHONE]`
- **IP Addresses:** IPv4 addresses replaced with `[REDACTED_IP]`
- **API Keys / Secrets:** High-entropy hexadecimal and alphanumeric keys replaced with `[REDACTED_SECRET]`
- **Employee Identification Numbers:** Pattern-matched enterprise IDs replaced with `[REDACTED_EMPLOYEE_ID]`
