# Hugging Face Dataset Licensing Registry & Terms

This document details the licensing terms, restrictions, and attribution requirements for all 21 recognized evaluation and benchmark datasets supported by the Office Knowledge Assistant.

---

## 1. Multilingual Datasets

| Dataset Identifier | Author / Org | License | Permitted Commercial Use | Attribution Requirement | Status |
|---|---|---|---|---|---|
| `ai4bharat/IndicQA` | AI4Bharat | CC-BY-4.0 | Yes (with attribution) | Must cite AI4Bharat paper | **Enabled** |
| `ai4bharat/MSMARCO-XI` | AI4Bharat | CC-BY-4.0 | Yes (with attribution) | Must cite AI4Bharat paper | **Enabled** |
| `ai4bharat/IN22-Conv` | AI4Bharat | CC-BY-4.0 | Yes (with attribution) | Must cite AI4Bharat paper | **Enabled** |
| `ai4bharat/IN22-Gen` | AI4Bharat | CC-BY-4.0 | Yes (with attribution) | Must cite AI4Bharat paper | **Enabled** |
| `ai4bharat/indic-instruct-data-v0.1` | AI4Bharat | Research / Academic | No (Non-commercial) | Required | *Disabled by Default* |
| `SandLogicTechnologies/Indic_Chat_Dataset`| SandLogic | Apache-2.0 | Yes | Apache-2.0 Notice | *Disabled by Default* |

---

## 2. IT Helpdesk & Ticketing Datasets

| Dataset Identifier | Author / Org | License | Permitted Commercial Use | Attribution Requirement | Status |
|---|---|---|---|---|---|
| `Console-AI/IT-helpdesk-synthetic-tickets` | Console-AI | MIT | Yes | Standard MIT license notice | **Enabled** |
| `w1z4rd3k/it-support-l1-ticket-classification` | w1z4rd3k | MIT | Yes | Standard MIT license notice | **Enabled** |
| `benjaminmacklin/IT_Support_V2` | Benjamin Macklin | Apache-2.0 | Yes | Standard Apache-2.0 notice | *Disabled by Default* |
| `mindweave/help-desk-tickets` | Mindweave | Proprietary / Sample | Evaluation sample only | Prohibited from training commercial models | *Disabled by Default* |
| `MakTek/Customer_support_faqs_dataset` | MakTek | MIT | Yes | Standard MIT license notice | *Disabled by Default* |

---

## 3. RAG Evaluation Datasets

| Dataset Identifier | Author / Org | License | Permitted Commercial Use | Attribution Requirement | Status |
|---|---|---|---|---|---|
| `dwb2023/ragas-golden-dataset` | DWB | Apache-2.0 | Yes | Apache-2.0 Notice | **Enabled** |
| `llmware/rag_instruct_benchmark_tester` | LLMWare | Apache-2.0 | Yes | Apache-2.0 Notice | **Enabled** |
| `vectara/open_ragbench` | Vectara | Apache-2.0 | Yes | Apache-2.0 Notice | *Disabled by Default* |
| `ingalepratap/EnterpriseRAG-Bench` | Pratap Ingale | Research | No | Research Only | *Disabled by Default* |
| `grasson/t2-ragbench` | Grasson | MIT | Yes | Standard MIT notice | *Disabled by Default* |
| `ruslanmv/moc-rag-benchmark` | Ruslan MV | Apache-2.0 | Yes | Apache-2.0 Notice | *Disabled by Default* |

---

## 4. Voice Datasets (Must Remain Disabled Unless Explicitly Enabled)

| Dataset Identifier | Author / Org | License | Permitted Commercial Use | Voice Gate Rule | Status |
|---|---|---|---|---|---|
| `ai4bharat/IndicVoices` | AI4Bharat | CC-BY-4.0 | Yes | Requires `ENABLE_VOICE_DATASETS=true` | *Disabled* |
| `snorbyte/indic-audio-dialog-sample` | Snorbyte | CC-BY-4.0 | Yes | Requires `ENABLE_VOICE_DATASETS=true` | *Disabled* |
| `snorbyte/indic-audio-natural-conversations-sample`| Snorbyte | CC-BY-4.0 | Yes | Requires `ENABLE_VOICE_DATASETS=true` | *Disabled* |
| `ai4bharat/Rasa` | AI4Bharat | CC-BY-4.0 | Yes | Requires `ENABLE_VOICE_DATASETS=true` | *Disabled* |
