# Evaluation & Benchmarking Guide

## 1. Overview
The Office Knowledge Assistant includes automated evaluation runners for RAG quality, multilingual retrieval, translation fidelity, IT intent classification, and company policy adherence.

---

## 2. CLI Evaluation Tools

### A. Dataset Inspection & Import
Before any public benchmark can be evaluated, inspect and import it through the governance gate:
```bash
# Inspect dataset schema, splits, and licensing without downloading
python -m backend.scripts.inspect_dataset --name ai4bharat/IndicQA

# Import with explicit license acceptance and PII redaction
python -m backend.scripts.import_dataset --name ai4bharat/IndicQA --accept-license --redact-pii --max-records 500

# Import all enabled datasets in batch
python -m backend.scripts.import_dataset --all-enabled --accept-license --redact-pii
```

### B. RAG Grounding & Answer Quality Evaluation
Runs evaluation against `dwb2023/ragas-golden-dataset` or `llmware/rag_instruct_benchmark_tester`:
```bash
python -m backend.scripts.run_rag_evaluation --dataset dwb2023/ragas-golden-dataset --samples 50
```
Metrics computed:
- **Faithfulness / Groundedness:** Ratio of claims in generated answer directly corroborated by retrieved context.
- **Answer Relevance:** Semantic alignment with user question.
- **Context Precision & Recall:** Proportion of retrieved chunks matching reference context.

### C. Multilingual & Cross-Lingual Retrieval Benchmark
Evaluates dual-representation search on `ai4bharat/MSMARCO-XI`:
```bash
python -m backend.scripts.run_retrieval_benchmark --dataset ai4bharat/MSMARCO-XI --top-k 5
```
Metrics computed:
- **Hit Rate@K (Top-1, Top-3, Top-5)**
- **Mean Reciprocal Rank (MRR)**
- **Cross-Lingual Preservation Score:** Recall when Hindi/Malayalam queries match English source documents.

### D. Translation & Technical Term Retention Benchmark
Evaluates conversational fidelity on `ai4bharat/IN22-Conv`:
```bash
python -m backend.scripts.run_translation_benchmark --dataset ai4bharat/IN22-Conv --samples 100
```
Metrics computed:
- **BLEU / ROUGE-L**
- **IT Term Preservation:** Verifies technical terms (e.g., VPN, MFA, SSO, Docker) remain uncorrupted and natural.

### E. IT Helpdesk Classifier Benchmark
Prepares and tests intent and priority classification against `Console-AI/IT-helpdesk-synthetic-tickets`:
```bash
python -m backend.scripts.prepare_it_ticket_data --output-dir data/public/processed/public_it_training/
```
Metrics computed:
- **Intent Accuracy & Macro-F1** across all 16 canonical categories.
- **Priority Matrix Precision:** Specifically checks zero tolerance for under-prioritizing `security_incident` triggers.

---

## 3. Section L: Company-Specific Locked Benchmark
To prevent regression on company policies, a dedicated locked test suite resides in `data/private/evaluation/company_golden_evaluation.json`.

Running the internal benchmark:
```bash
python -m backend.scripts.run_rag_evaluation --company-benchmark
```
Verification checks:
1. **Forbidden Claims Check:** Ensures assistant never quotes obsolete policies or hallucinates allowances.
2. **Mandatory Refusal Check:** Tests unanswerable questions to verify the exact refusal message:
   *"I could not verify this from the available approved office documents."*
3. **Escalation Trigger Check:** Verifies prompt escalation to security or HR teams for high-risk queries.
