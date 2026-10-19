# Office Knowledge Assistant

> **Enterprise Multilingual Copilot with Role-Based Access Control, Zero Company Policy Hallucination, IT Helpdesk Ticketing, and Hugging Face Benchmark Governance.**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg?logo=next.js&logoColor=white)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4+-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)

---

## 1. Executive Summary & Core Tenets

The **Office Knowledge Assistant** (deployable as *Office AI Copilot*, *Bhasha Office Assistant*, *Namma Office AI*, *Office Sahayak*, or *Office AI Helpdesk*) is an enterprise-grade private AI assistant designed to provide deep, structured, source-backed answers for modern organizations.

### Non-Negotiable Product Tenets
1. **Zero Company Policy Hallucination:**
   Company policies, HR procedures, finance guidelines, employee records, IT runbooks, and SOPs are answered **exclusively from approved and permission-authorized internal sources** via hybrid RAG (BM25 + Dense Semantic Vectors + Reciprocal Rank Fusion). If unverified, the assistant strictly returns:
   > *"I could not verify this from the available approved office documents."*
2. **Strict Quarantine of Public Benchmarks:**
   Public Hugging Face evaluation datasets (e.g., IndicQA, MSMARCO-XI, IN22, IT synthetic tickets) are **strictly isolated** into quarantined evaluation namespaces (`data/public/processed/`). They are **never merged or indexed** into the production organizational vector store.
3. **Defense-in-Depth Pre-Retrieval RBAC:**
   Role-based access filters (`employee`, `manager`, `hr`, `finance`, `it_support`, `it_admin`, `executive`, `system_admin`) and classification levels (`public`, `internal`, `confidential`, `restricted`) are enforced **inside the retrieval queries before similarity search**.
4. **First-Class Indic Multilingualism:**
   Supports English (`eng_Latn`), Hindi in Devanagari (`hin_Deva`), Hinglish (`hin_Latn`), Malayalam in Malayalam script (`mal_Mlym`), and Manglish (`mal_Latn`). Features IndicLID-style language detection, cross-lingual query mapping, and natural preservation of workplace technical terminology (VPN, Wi-Fi, HR, MFA, SSO, Docker).
5. **IT Helpdesk & Safe Level-1 Triage:**
   Automated classification across 16 canonical intents, priority scoring, urgent security warnings for phishing/malware, and ticket persistence requiring explicit user confirmation.
6. **Triple-Layer Memory Architecture:**
   Short-term conversation history, long-term user preference memory with automated PII and credentials blacklisting, and versioned organizational memory.

---

## 2. System Architecture

```
+-----------------------------------------------------------------------------------+
|                           Next.js 14 Frontend Interface                           |
|  - Claude-like UI (Warm neutrals, custom scrollbars, typography, responsive)      |
|  - Real-time Server-Sent Events (SSE) streaming                                   |
|  - Noto Sans, Noto Sans Devanagari, and Noto Sans Malayalam fonts                 |
|  - Expandable source panel (version, page numbers, excerpts, classification)      |
|  - Modals: Long-term Memory CRUD, IT Ticketing, Dataset Governance Portal         |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          | SSE / HTTP Requests
                                          v
+-----------------------------------------------------------------------------------+
|                                FastAPI Backend                                    |
|                                                                                   |
|  +--------------------+  +----------------------+  +---------------------------+  |
|  |  Auth & RBAC Layer |  | Multilingual Engine  |  | Intent & Routing Policy   |  |
|  |  JWT / Role Scopes |  | Script Detection     |  | Internal vs Web Official  |  |
|  +---------+----------+  +----------+-----------+  +-------------+-------------+  |
|            |                        |                            |                |
|            v                        v                            v                |
|  +-----------------------------------------------------------------------------+  |
|  | Hybrid Retrieval Engine (BM25 + Semantic Vector + Reciprocal Rank Fusion)   |  |
|  | Pre-filtered by user role and classification ceiling                        |  |
|  +--------------------------------------+--------------------------------------+  |
|                                         |                                         |
|                                         v                                         |
|  +-----------------------------------------------------------------------------+  |
|  | Structured 7-Point Answer Generator (Summary, Steps, Exceptions, Citations) |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 3. Project Directory Structure

```text
office-knowledge-assistant/
├── frontend/                     # Next.js 14 + Tailwind CSS + TypeScript Interface
│   ├── src/
│   │   ├── app/                  # App Router, Layouts, CSS
│   │   ├── components/           # Sidebar, ChatPane, SourcePanel, Modals
│   │   └── lib/api.ts            # SSE streaming client & API adapters
│   ├── package.json
│   ├── tailwind.config.js
│   └── tsconfig.json
├── backend/                      # FastAPI Python Application Core
│   ├── app/
│   │   ├── api/                  # Chat, Auth, Memory, Documents, Tickets, Datasets
│   │   ├── auth/                 # RBAC matrix & JWT token dependencies
│   │   ├── rag/                  # Chunker, BM25, VectorStore, HybridRetriever, Generator
│   │   ├── multilingual/         # Language detector, term preserver, cross-lingual mapper
│   │   ├── memory/               # Short-term and long-term preference memory managers
│   │   ├── web/                  # Routing policy & allowlisted web search client
│   │   ├── documents/            # Multi-format parsers and security validators
│   │   ├── tickets/              # Canonical intent classifier and ticketing service
│   │   ├── datasets/             # HF registry, inspector, PII redactor, normalizer
│   │   ├── evaluation/           # RAG grounding, retrieval, and translation evaluators
│   │   ├── db/                   # SQLAlchemy database models and knowledge base seeder
│   │   ├── prompts/              # Section J system prompt and injection defenses
│   │   └── main.py               # FastAPI entrypoint
│   └── scripts/                  # CLI evaluation and ingestion scripts
│       ├── inspect_dataset.py
│       ├── import_dataset.py
│       ├── run_rag_evaluation.py
│       ├── run_retrieval_benchmark.py
│       ├── run_translation_benchmark.py
│       └── prepare_it_ticket_data.py
├── configs/                      # Governance and mapping specifications
│   ├── datasets.yaml             # Registry of 21 Hugging Face datasets with licensing
│   └── dataset_mappings.yaml     # Dynamic schema normalization rules
├── data/
│   ├── public/                   # Quarantined benchmark imports (evaluation only)
│   └── private/                  # Internal authoritative office policy documents
├── docs/                         # Production documentation
│   ├── architecture.md
│   ├── security.md
│   ├── dataset_governance.md
│   ├── dataset_licenses.md
│   └── evaluation_guide.md
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 4. Quickstart Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### A. Backend Setup
1. Open terminal in `office-knowledge-assistant/`:
```bash
# Create and activate Python virtual environment
python -m venv venv
.\venv\Scripts\activate   # On Windows
# source venv/bin/activate # On Linux/macOS

# Install dependencies
pip install -r backend/requirements.txt

# Launch FastAPI backend (seeds initial documents automatically on startup)
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
The API documentation is accessible at `http://127.0.0.1:8000/docs`.

### B. Frontend Setup
1. In a separate terminal tab:
```bash
cd frontend
npm install
npm run dev
```
2. Open your browser at `http://localhost:3000`.

---

## 5. CLI Benchmark & Evaluation Tools

### 1. Inspect a Hugging Face Dataset
```bash
python -m backend.scripts.inspect_dataset --name ai4bharat/IndicQA
```

### 2. Controlled Import with Licensing Gate & PII Redaction
```bash
python -m backend.scripts.import_dataset --name ai4bharat/IndicQA --accept-license --redact-pii --max-records 100
```

### 3. Run Section L Locked Company Evaluation Benchmark
```bash
python -m backend.scripts.run_rag_evaluation --company-benchmark
```

### 4. Run Cross-Lingual Retrieval Benchmark (Hit@K, MRR)
```bash
python -m backend.scripts.run_retrieval_benchmark --dataset ai4bharat/MSMARCO-XI --top-k 5
```

### 5. Run Indic Translation & Term Preservation Benchmark
```bash
python -m backend.scripts.run_translation_benchmark --dataset ai4bharat/IN22-Conv
```

### 6. Prepare IT Helpdesk Training & Evaluation Data
```bash
python -m backend.scripts.prepare_it_ticket_data
```

---

## 6. Docker Deployment

Deploy the full stack (PostgreSQL 16, FastAPI backend, Next.js frontend) using Docker Compose:
```bash
docker-compose up --build
```
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
