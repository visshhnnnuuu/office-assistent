from sqlalchemy.orm import Session
from backend.app.db.models import DocumentModel, ChunkModel, UserModel
from backend.app.rag.chunker import HeadingAwareChunker
from backend.app.rag.vector_store import generate_local_embedding
from backend.app.api.chat import get_hybrid_retriever

SAMPLE_OFFICE_DOCUMENTS = [
    # --------------------------------------------------------------------------
    # 1. HR Documents
    # --------------------------------------------------------------------------
    {
        "document_id": "hr_leave_policy_v2_1",
        "title": "Employee Leave & Attendance Policy",
        "department": "HR",
        "classification": "internal",
        "allowed_roles": ["employee", "manager", "hr", "finance", "it_support", "it_admin", "executive"],
        "allowed_departments": ["all"],
        "version": "2.1",
        "effective_date": "2026-01-01",
        "review_date": "2026-12-31",
        "owner": "HR Department",
        "approved_by": "Chief People Officer",
        "source_url": "https://intranet.company.internal/policies/hr/leave-policy-v2.1.pdf",
        "source_type": "pdf",
        "language": "eng_Latn",
        "content": """# Employee Leave & Attendance Policy (v2.1)

## 1. Executive Summary & Purpose
This policy sets forth guidelines for all full-time and contract personnel regarding paid time off, casual leave, sick leave, maternity/paternity leave, and remote attendance tracking.

## 2. Annual Leave Entitlements
All full-time employees are entitled to 24 days of paid annual leave per calendar year, accrued at the rate of 2.0 days per completed calendar month of service.
- **Casual Leave (CL):** 12 days per year for personal errands, family emergencies, or brief rest.
- **Medical / Sick Leave (ML):** 12 days per year. Consecutive absences exceeding 3 calendar days require a certified medical practitioner certificate.
- **Carry-Forward Maximum:** A maximum of 10 unused earned leave days may be carried forward into the subsequent calendar year. All excess leaves lapse on December 31st automatically.

## 3. Leave Application Process & Manager Approval
1. **Submit Request:** All leave requests must be lodged via the HRMS Employee Portal at least 5 business days in advance for planned leaves exceeding 2 days.
2. **Manager Review:** Reporting managers must approve or decline leave submissions within 48 business hours of receipt.
3. **Emergency Leave:** In unavoidable personal emergencies, employees must notify their reporting lead via corporate email or Slack by 09:30 AM on the day of absence.

## 4. Exceptions and Encashment
Leave encashment is permitted only upon formal separation or retirement, calculated against base monthly basic salary. Leave cannot be substituted for probationary notice periods without written Human Resources sign-off."""
    },
    {
        "document_id": "hr_wfh_policy_v1_4",
        "title": "Hybrid Work-From-Home (WFH) Guidelines",
        "department": "HR",
        "classification": "internal",
        "allowed_roles": ["employee", "manager", "hr", "finance", "it_support", "it_admin", "executive"],
        "allowed_departments": ["all"],
        "version": "1.4",
        "effective_date": "2026-02-01",
        "review_date": "2026-12-31",
        "owner": "HR Operations",
        "approved_by": "Chief People Officer",
        "source_url": "https://intranet.company.internal/policies/hr/wfh-guidelines.pdf",
        "source_type": "pdf",
        "language": "eng_Latn",
        "content": """# Hybrid Work-From-Home (WFH) Guidelines

## 1. Operating Model
The organization operates on a 3:2 hybrid working cadence: 3 mandatory in-office collaboration days (Tuesday, Wednesday, Thursday) and up to 2 remote working days (Monday, Friday).

## 2. Working Hours & Core Collaboration Window
Remote working hours must strictly mirror standard office timings (09:00 AM to 06:00 PM local time). All personnel are expected to be reachable via Slack and corporate email during the mandatory Core Collaboration Window of 10:30 AM to 04:30 PM.

## 3. Ergonomic & Infrastructure Allowance
Eligible permanent employees after 90 days of tenure may claim a one-time remote workspace subsidy of up to $500 (or INR 40,000) for ergonomic chairs, monitors, or noise-cancelling headsets via the Finance portal."""
    },

    # --------------------------------------------------------------------------
    # 2. IT Documents
    # --------------------------------------------------------------------------
    {
        "document_id": "it_vpn_mfa_guide_v3",
        "title": "Corporate VPN and Multi-Factor Authentication (MFA) Setup Guide",
        "department": "IT",
        "classification": "internal",
        "allowed_roles": ["employee", "manager", "hr", "finance", "it_support", "it_admin", "executive"],
        "allowed_departments": ["all"],
        "version": "3.0",
        "effective_date": "2026-01-15",
        "review_date": "2026-12-31",
        "owner": "IT Infrastructure Team",
        "approved_by": "Head of IT Security",
        "source_url": "https://intranet.company.internal/it/guides/vpn-mfa-setup.pdf",
        "source_type": "pdf",
        "language": "eng_Latn",
        "content": """# Corporate VPN and Multi-Factor Authentication (MFA) Setup Guide

## 1. Remote Connectivity Prerequisites
Connecting to internal staging environments, customer databases, internal portals, and code repositories requires an active corporate VPN session.

## 2. Cisco AnyConnect VPN Client Configuration
1. **Download:** Obtain the official Cisco AnyConnect installer from the Self-Service Portal (`https://it.company.internal/software`).
2. **Gateway Server:** Enter gateway address `vpn.global.company.internal` in the connection dialog.
3. **Authentication:** Enter your enterprise Single Sign-On (SSO) email address and network password.
4. **MFA Push Verification:** Accept the push verification prompt on your registered mobile authenticator application (Okta Verify or Duo Mobile).

## 3. VPN Error 401 & Troubleshooting SOP
- **Error 401 (Unauthorized):** Indicates expired credentials or an unapproved device certificate. Refresh your SSO token by visiting `https://sso.company.internal/myprofile`.
- **Frequent Tunnel Drops:** Ensure your home Wi-Fi MTU is set between 1350 and 1400. Disable IPv6 on the primary network adapter if packet loss occurs.
- **Lost Mobile Device:** Contact IT Helpdesk emergency hotline immediately (+1-800-555-0199) to revoke the active device token."""
    },
    {
        "document_id": "it_security_incident_response_v2",
        "title": "Information Security Incident & Phishing Response Runbook",
        "department": "IT",
        "classification": "internal",
        "allowed_roles": ["employee", "manager", "hr", "finance", "it_support", "it_admin", "executive"],
        "allowed_departments": ["all"],
        "version": "2.2",
        "effective_date": "2026-01-01",
        "review_date": "2026-12-31",
        "owner": "Information Security Operations (ISOC)",
        "approved_by": "Chief Information Security Officer",
        "source_url": "https://intranet.company.internal/security/incident-response-runbook.pdf",
        "source_type": "pdf",
        "language": "eng_Latn",
        "content": """# Information Security Incident & Phishing Response Runbook

## 1. Security Incident Definition & Criticality
A Critical Security Incident involves:
- Suspected phishing email clicks or accidental credential submission on third-party sites.
- Stolen, lost, or compromised laptops, mobile devices, or security badges.
- Ransomware warnings, unusual disk encryption, or unauthorized MFA verification pushes.
- Accidental disclosure of confidential customer records or API keys.

## 2. Immediate Mandatory Employee Actions
1. **Disconnect from Network:** Immediately disconnect Wi-Fi and unplug Ethernet cables from your workstation. Do NOT power down the machine (preserves volatile memory for forensics).
2. **Do NOT Enter Credentials:** Never attempt to 'test' the password or enter secondary OTPs.
3. **Escalate Instantly:** Send an alert to `security-incident@company.internal` or raise a Critical IT Helpdesk Ticket with category `security_incident`.
4. **Zero Penalty Disclosure:** Company policy grants complete immunity for employees who proactively report accidental phishing clicks within 60 minutes."""
    },

    # --------------------------------------------------------------------------
    # 3. Finance Documents
    # --------------------------------------------------------------------------
    {
        "document_id": "fin_travel_expense_policy_v2_4",
        "title": "Domestic and International Travel Expense Reimbursement Policy",
        "department": "Finance",
        "classification": "internal",
        "allowed_roles": ["employee", "manager", "hr", "finance", "it_support", "it_admin", "executive"],
        "allowed_departments": ["all"],
        "version": "2.4",
        "effective_date": "2026-01-01",
        "review_date": "2026-12-31",
        "owner": "Corporate Finance",
        "approved_by": "Chief Financial Officer",
        "source_url": "https://intranet.company.internal/finance/travel-expense-policy-v2.4.pdf",
        "source_type": "pdf",
        "language": "eng_Latn",
        "content": """# Domestic and International Travel Expense Reimbursement Policy

## 1. Purpose & Scope
This policy defines allowable expenses, per diem caps, submission procedures, and approval workflows for domestic and overseas official company travel.

## 2. Daily Per Diem & Meal Allowances
- **Tier 1 Metros (Mumbai, Delhi, Bengaluru, London, New York):** Up to $85 USD (or INR 3,500) per day for meals and incidental local transportation.
- **Tier 2 Cities:** Up to $55 USD (or INR 2,200) per day.
- **Alcohol:** Alcoholic beverages are non-reimbursable under standard business expense codes.

## 3. Expense Claim Submission Workflow (Form 12BB)
1. **Filing Window:** All expense claims must be filed through the Oracle Finance portal within exactly **15 calendar days** of completing travel.
2. **Receipt Requirements:** Itemized tax invoices and original payment receipts are mandatory for any individual expense item exceeding $15 USD (or INR 500).
3. **Approvals:** Claims under $1,000 require Reporting Manager sign-off. Claims exceeding $1,000 require Department Head and Finance Controller dual sign-off."""
    },

    # --------------------------------------------------------------------------
    # 4. Operations & Common Office Documents
    # --------------------------------------------------------------------------
    {
        "document_id": "ops_holidays_locations_2026",
        "title": "2026 Official Holiday Calendar and Office Directory",
        "department": "Operations",
        "classification": "internal",
        "allowed_roles": ["employee", "manager", "hr", "finance", "it_support", "it_admin", "executive"],
        "allowed_departments": ["all"],
        "version": "1.0",
        "effective_date": "2026-01-01",
        "review_date": "2026-12-31",
        "owner": "Facilities & Operations",
        "approved_by": "Chief Operating Officer",
        "source_url": "https://intranet.company.internal/ops/holiday-calendar-2026.pdf",
        "source_type": "pdf",
        "language": "eng_Latn",
        "content": """# 2026 Official Holiday Calendar and Office Directory

## 1. Primary Office Campus Locations
- **Headquarters (Bengaluru):** Tech Park 4, Bellandur Ring Road, Bengaluru 560103. (Ph: +91-80-5555-0100)
- **Regional Hub (Kochi):** Infopark Phase II, Kakkanad, Kochi, Kerala 682042. (Ph: +91-484-5555-0200)
- **Regional Hub (Gurugram):** Cyber City Phase 3, DLF Sector 24, Gurugram, Haryana 122002. (Ph: +91-124-5555-0300)

## 2. 2026 Official Mandatory Holidays
- **New Year's Day:** January 1, 2026
- **Republic Day:** January 26, 2026
- **Holi:** March 4, 2026
- **Eid-ul-Fitr:** March 20, 2026
- **Independence Day:** August 15, 2026
- **Onam / Thiruvonam:** August 27, 2026
- **Gandhi Jayanti:** October 2, 2026
- **Diwali:** November 8, 2026
- **Christmas Day:** December 25, 2026"""
    }
]

def seed_sample_knowledge_base(db: Session):
    """
    Seeds initial realistic office knowledge base if database is empty.
    Creates default test users across roles and populates hybrid search indexes.
    """
    # 1. Ensure Demo Users exist
    demo_roles = [
        ("employee@company.internal", "Employee User", "employee", "Engineering"),
        ("manager@company.internal", "Manager User", "manager", "Engineering"),
        ("hr@company.internal", "HR Lead", "hr", "People Operations"),
        ("finance@company.internal", "Finance Controller", "finance", "Corporate Finance"),
        ("it_support@company.internal", "IT Support Engineer", "it_support", "IT Operations"),
        ("it_admin@company.internal", "IT System Admin", "it_admin", "IT Operations"),
        ("executive@company.internal", "Executive Director", "executive", "Leadership"),
        ("admin@company.internal", "Global System Admin", "system_admin", "Operations"),
    ]

    for email, name, role, dept in demo_roles:
        existing = db.query(UserModel).filter(UserModel.email == email).first()
        if not existing:
            u = UserModel(email=email, name=name, role=role, department=dept)
            db.add(u)
    db.commit()

    # 2. Check if documents already seeded
    existing_docs_count = db.query(DocumentModel).count()
    if existing_docs_count > 0:
        # Load existing chunks into search indexes
        chunks = db.query(ChunkModel).all()
        retriever = get_hybrid_retriever()
        chunk_dicts = [
            {
                "chunk_id": c.chunk_id,
                "document_id": c.document_id,
                "section_title": c.section_title,
                "content": c.content,
                "embedding": c.embedding
            }
            for c in chunks
        ]
        retriever.index_chunks(chunk_dicts)
        return

    # 3. Seed Documents and Chunks
    chunker = HeadingAwareChunker()
    retriever = get_hybrid_retriever()
    all_indexed_chunks = []

    for doc_data in SAMPLE_OFFICE_DOCUMENTS:
        doc = DocumentModel(
            document_id=doc_data["document_id"],
            title=doc_data["title"],
            department=doc_data["department"],
            classification=doc_data["classification"],
            allowed_roles=doc_data["allowed_roles"],
            allowed_departments=doc_data["allowed_departments"],
            version=doc_data["version"],
            effective_date=doc_data["effective_date"],
            review_date=doc_data["review_date"],
            owner=doc_data["owner"],
            approved_by=doc_data["approved_by"],
            source_url=doc_data["source_url"],
            source_type=doc_data["source_type"],
            language=doc_data["language"],
            status="active"
        )
        db.add(doc)

        chunks = chunker.chunk_document(
            document_id=doc_data["document_id"],
            text=doc_data["content"],
            base_metadata=doc_data
        )

        for ch in chunks:
            text_for_embed = f"{ch.get('section_title', '')} {ch.get('content', '')}"
            embedding = generate_local_embedding(text_for_embed)
            ch["embedding"] = embedding
            all_indexed_chunks.append(ch)

            chunk_record = ChunkModel(
                chunk_id=ch["chunk_id"],
                document_id=doc_data["document_id"],
                section_title=ch.get("section_title"),
                page_number=ch.get("page_number", 1),
                content=ch["content"],
                classification=doc_data["classification"],
                allowed_roles=doc_data["allowed_roles"],
                allowed_departments=doc_data["allowed_departments"],
                embedding=embedding
            )
            db.add(chunk_record)

    db.commit()
    retriever.index_chunks(all_indexed_chunks)
