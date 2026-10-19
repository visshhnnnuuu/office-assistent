# Office Knowledge Assistant — System Architecture

## 1. Overview
**Office Knowledge Assistant** (also deployable as *Office AI Copilot*, *Bhasha Office Assistant*, *Namma Office AI*, *Office Sahayak*, or *Office AI Helpdesk*) is an enterprise-grade private RAG assistant designed for internal organizations.

The system enforces strict data sovereignty:
- **Zero Company Policy Hallucination:** Internal company facts, policies, employee procedures, and workflows are answered **exclusively** from approved, permission-authorized internal sources.
- **Strict Isolation of Public Benchmarks:** Public datasets from Hugging Face are relegated strictly to evaluation, retrieval benchmarking, translation testing, and IT intent training. They are **never** indexed into production knowledge.
- **Multilingual Support:** First-class support for English (`eng_Latn`), Hindi in Devanagari (`hin_Deva`), Hinglish (`hin_Latn`), Malayalam (`mal_Mlym`), and Manglish (`mal_Latn`).
- **Role-Based Access Control (RBAC):** Content filtering is enforced at the chunk and document metadata level **before** vector and keyword retrieval.

---

## 2. High-Level Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                                 Next.js 14 Frontend                               |
|  - Claude-like UI (Markdown, code blocks, citation badges, expandable sources)     |
|  - Real-time Server-Sent Events (SSE) streaming                                   |
|  - Multilingual typography (Noto Sans, Devanagari, Malayalam)                     |
|  - Settings: Language override, Answer depth, Memory controls                     |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          | HTTP / SSE
                                          v
+-----------------------------------------------------------------------------------+
|                               FastAPI Backend Core                                |
|                                                                                   |
|  +--------------------+  +----------------------+  +---------------------------+  |
|  |  Auth & RBAC Layer |  | Multilingual Engine  |  | Intent & Routing Router   |  |
|  |  JWT / Entra / SSO |  | IndicLID / Script    |  | Internal RAG vs Web Doc   |  |
|  +---------+----------+  +----------+-----------+  +-------------+-------------+  |
|            |                        |                            |                |
|            +------------------------+----------------------------+                |
|                                     |                                             |
|                                     v                                             |
|                   +------------------------------------+                          |
|                   | Hybrid Retrieval Engine            |                          |
|                   |  1. Pre-filter by user role/dept   |                          |
|                   |  2. Semantic Vector Search         |                          |
|                   |  3. BM25 Keyword Search            |                          |
|                   |  4. Reciprocal Rank Fusion (RRF)   |                          |
|                   +-----------------+------------------+                          |
|                                     |                                             |
|                                     v                                             |
|                   +------------------------------------+                          |
|                   | Structured Prompt Generator & LLM  |                          |
|                   |  - Executive summary               |                          |
|                   |  - Detailed explanation            |                          |
|                   |  - Step-by-step process            |                          |
|                   |  - Forms, exceptions, next actions |                          |
|                   |  - Verified inline citations       |                          |
|                   +------------------------------------+                          |
+-----------------------------------------------------------------------------------+
```

---

## 3. Core Subsystems

### A. Authentication & RBAC Engine
- Roles supported: `employee`, `manager`, `hr`, `finance`, `it_support`, `it_admin`, `executive`, `system_admin`.
- Documents and chunks carry explicit access tags:
  - `allowed_roles`
  - `allowed_departments`
  - `classification` (`public`, `internal`, `confidential`, `restricted`)
- Security filter is evaluated inside the retrieval query before computing similarities, guaranteeing zero unauthorized data leakage.

### B. Ingestion & Document Processing Pipeline
- Supports PDF, Scanned PDF (OCR), DOCX, PPTX, XLSX, CSV, Markdown, TXT, and approved Web URLs.
- Sanitizes headers, footers, and noise.
- Heading-aware chunker partitions text into 300–600 word semantic units while maintaining parent section context, page numbers, sheet rows, and document versioning.

### C. Multilingual Processing & Retrieval
- Language ID: Detects script (`Deva`, `Mlym`, `Latn`) and code-mixing (Hinglish, Manglish).
- Cross-lingual retrieval: Queries posed in Hindi or Malayalam trigger dual-representation search across English and Indic policy corpora.
- Preservation of technical jargon: Acronyms and IT terms (VPN, Wi-Fi, HR, SSO, Docker, MFA) are guarded against artificial or awkward translation.

### D. IT Helpdesk & Ticketing Subsystem
- Automated intent classification covering 16 canonical categories (`password_reset`, `vpn_issue`, `security_incident`, etc.).
- Priority evaluation: `critical`, `high`, `medium`, `low`.
- Critical security incident protocol: Halts unsafe user actions, urges caution against credential sharing, and offers instant escalation ticketing.
- Explicit confirmation required prior to persisting or dispatching any ticket.

### E. Memory Architecture
1. **Short-Term Conversation Memory:** Retains the preceding 6–12 context-relevant turns.
2. **Long-Term Preference Memory:** User-consented preferences (language, response depth, tech stack). PII and secret scanners prevent ingestion of credentials. User retains full CRUD authority.
3. **Organization Memory:** Backed exclusively by versioned, approved RAG documents.
