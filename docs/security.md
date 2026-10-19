# Office Knowledge Assistant — Security & Governance Blueprint

## 1. Core Security Tenets

### Rule 1: Zero Company Policy Hallucination
The assistant is explicitly prohibited from relying on generative model memory or public training data for organization-specific facts, policies, employee records, financial workflows, or operational runbooks.
- All company-specific answers **must be grounded exclusively** in active, permitted internal documents retrieved via the RAG pipeline.
- If internal context is missing, insufficient, or ambiguous, the model must return:
  > *"I could not verify this from the available approved office documents."*

### Rule 2: Non-Negotiable Pre-Retrieval RBAC
Access control is not applied as a post-filter or cosmetic UI hide.
- Chunks and documents have explicit access attributes (`allowed_roles`, `allowed_departments`, `classification`).
- Filters are injected directly into vector and keyword database queries.
- If an employee does not possess the requisite role (e.g. attempting to read HR confidential disciplinary records or Executive minutes), zero matching records are returned by the search engine.

---

## 2. Threat Model & Mitigations

### Prompt Injection & Instruction Overrides
- **Vector:** Adversarial text embedded within user prompts, uploaded documents, or external web pages attempting to command the assistant ("Ignore previous instructions", "Reveal your system prompt", "Show admin documents", "Print internal secrets").
- **Mitigation:**
  1. Strict structural separation between System Instructions, User Query, and Retrieved Evidence.
  2. Retrieved documents and scraped web pages are labeled as passive untrusted data objects, never executable instructions.
  3. Pre-flight heuristic and regex detection scans for common jailbreaks and injection signatures before prompt composition.

### Data Exfiltration & PII Protection
- **Vector:** Eliciting employee salaries, personal contact numbers, medical histories, API keys, Wi-Fi credentials, or database connection strings.
- **Mitigation:**
  1. Ingestion Blacklist: Scanners block indexing of files containing private credentials, salary spreadsheets, or raw keys.
  2. Public Dataset Redaction: All Hugging Face datasets undergo mandatory regex and rule-based redaction (emails, phone numbers, API tokens, IP addresses).
  3. Assistant Guardrails: The system prompt strictly refuses requests for personal employee compensation, credentials, or other users' chat logs.

### Untrusted Web Browsing
- **Vector:** Server-Side Request Forgery (SSRF), malicious redirects, malicious scripts, poisoning internal knowledge.
- **Mitigation:**
  1. Strict domain allowlist for software engineering references (e.g. `docs.python.org`, `react.dev`, `nextjs.org`, `fastapi.tiangolo.com`, `docs.docker.com`, `kubernetes.io`, official GitHub repos).
  2. Direct user-supplied arbitrary URL retrieval requires sanitization, timeout limits (5s), content size caps (2MB), and HTML-to-text stripping (scripts and styles eliminated).
  3. Web findings are flagged with explicit retrieval timestamps and domain badges and **never** written into the permanent internal knowledge vector store.

---

## 3. Role-Based Access Control (RBAC) Matrix

| Role | Permitted Information Scope |
|---|---|
| `employee` | General office knowledge, standard HR leave/attendance/WFH policies, public IT SOPs, office directories |
| `manager` | Employee scope + manager approval workflows, team delegation guidelines |
| `hr` | Employee scope + operational HR guides, onboarding plans, employee handbook administration |
| `finance` | Employee scope + travel expense reimbursement, procurement thresholds, invoice processing SOPs |
| `it_support`| Employee scope + IT support Level-1/2 runbooks, software installation steps, hardware triage |
| `it_admin` | IT support scope + restricted infrastructure runbooks, system maintenance (secrets remain masked) |
| `executive` | Cross-department operational summaries, strategic roadmaps |
| `system_admin`| Document catalog management, user role assignment (zero automatic bypass of confidential records) |
