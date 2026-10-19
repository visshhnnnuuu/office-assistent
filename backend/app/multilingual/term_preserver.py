import re
from typing import Set, Dict, List

PRESERVED_TECHNICAL_TERMS: Set[str] = {
    "vpn", "wi-fi", "wifi", "email", "hr", "portal", "ticket", "password",
    "login", "policy", "dashboard", "software", "api", "docker", "kubernetes",
    "database", "deployment", "mfa", "2fa", "sso", "laptop", "server",
    "macbook", "windows", "linux", "cloud", "aws", "gcp", "azure", "git",
    "github", "jira", "slack", "teams", "outlook", "chrome", "admin", "token",
    "reimbursement", "wfh", "leave", "onboarding", "compliance", "pr", "ci/cd"
}

class TermPreserver:
    @staticmethod
    def get_preserved_terms() -> Set[str]:
        return PRESERVED_TECHNICAL_TERMS

    @staticmethod
    def sanitize_text_for_term_preservation(text: str) -> str:
        """
        Ensures technical acronyms and key office terminology are not transliterated or translated
        into awkward literal forms.
        """
        # E.g., make sure terms like VPN, Wi-Fi, HR are properly capitalized
        for term in PRESERVED_TECHNICAL_TERMS:
            pattern = re.compile(rf'\b{re.escape(term)}\b', re.IGNORECASE)
            text = pattern.sub(term.upper() if len(term) <= 4 and term not in {"git", "jira", "wfh"} else term.capitalize(), text)
        return text
