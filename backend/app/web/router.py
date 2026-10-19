import re
from typing import Dict, Any, Tuple

INTERNAL_POLICY_PATTERNS = [
    re.compile(r'\b(leave|vacation|chutti|wfh|work from home|attendance|holiday|reimbursement|expense|claim|invoice|salary|bonus|procurement|handbook|code of conduct|sop)\b', re.IGNORECASE),
    re.compile(r'\b(hr policy|finance policy|travel policy|company rules|maternity|paternity|bereavement|probation|notice period)\b', re.IGNORECASE),
]

IT_INTERNAL_PATTERNS = [
    re.compile(r'\b(vpn|wi-fi|wifi|sso|mfa|password reset|account locked|printer|laptop asset|access request|badge)\b', re.IGNORECASE),
]

SOFTWARE_TECH_PATTERNS = [
    re.compile(r'\b(python|javascript|typescript|react|next\.?js|fastapi|docker|kubernetes|k8s|postgres|sql|git|github actions|api|graphql|rest api|ci/cd|pydantic|asyncio)\b', re.IGNORECASE),
    re.compile(r'\b(how to fix|error code|syntax error|module not found|import error|typeerror|dockerfile|helm chart)\b', re.IGNORECASE),
]

SECURITY_INCIDENT_PATTERNS = [
    re.compile(r'\b(phishing|malware|ransomware|hacked|data leak|lost device|lost laptop|compromised|unknown login|stolen)\b', re.IGNORECASE),
]

RESTRICTED_PATTERNS = [
    re.compile(r'\b(bypass mfa|disable antivirus|disable firewall|crack password|steal token|ignore previous instructions|reveal system prompt|show admin credentials)\b', re.IGNORECASE),
]

class QueryRouter:
    @staticmethod
    def route_query(query: str) -> Dict[str, Any]:
        """
        Determines the routing policy for a user question according to Section F:
        - target: 'internal_rag', 'web_search', 'hybrid', 'security_incident', 'restricted_refusal'
        - allow_web: bool
        - is_software_mode: bool
        - reason: explanation
        """
        q_lower = query.lower()

        # 1. Restricted check
        for pattern in RESTRICTED_PATTERNS:
            if pattern.search(q_lower):
                return {
                    "target": "restricted_refusal",
                    "allow_web": False,
                    "is_software_mode": False,
                    "is_security_incident": False,
                    "reason": "Request violates security governance or attempts instruction override."
                }

        # 2. Security incident check
        for pattern in SECURITY_INCIDENT_PATTERNS:
            if pattern.search(q_lower):
                return {
                    "target": "security_incident",
                    "allow_web": False,
                    "is_software_mode": False,
                    "is_security_incident": True,
                    "reason": "Security incident detected: Triggering urgent security triage protocol."
                }

        # 3. Internal company policy / HR / Finance check
        for pattern in INTERNAL_POLICY_PATTERNS:
            if pattern.search(q_lower):
                return {
                    "target": "internal_rag",
                    "allow_web": False,
                    "is_software_mode": False,
                    "is_security_incident": False,
                    "reason": "Internal organizational policy query: Routed strictly to approved internal RAG."
                }

        # 4. IT internal check
        for pattern in IT_INTERNAL_PATTERNS:
            if pattern.search(q_lower):
                return {
                    "target": "internal_rag",
                    "allow_web": False,
                    "is_software_mode": False,
                    "is_security_incident": False,
                    "reason": "IT service / internal asset query: Routed to internal IT SOPs."
                }

        # 5. Software / Technical developer query
        for pattern in SOFTWARE_TECH_PATTERNS:
            if pattern.search(q_lower):
                return {
                    "target": "web_search",
                    "allow_web": True,
                    "is_software_mode": True,
                    "is_security_incident": False,
                    "reason": "Technical software question: Software Expert mode enabled with official documentation research."
                }

        # Default fallback: Internal RAG first
        return {
            "target": "internal_rag",
            "allow_web": False,
            "is_software_mode": False,
            "is_security_incident": False,
            "reason": "Default enterprise knowledge retrieval."
        }
