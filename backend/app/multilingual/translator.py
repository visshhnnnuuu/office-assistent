import re
from typing import Dict, List, Set

# Common Indic-to-English semantic mapping for office and IT concepts
CROSS_LINGUAL_DICTIONARY: Dict[str, List[str]] = {
    # Hindi / Hinglish terms
    "chutti": ["leave", "time off", "vacation"],
    "chhutti": ["leave", "time off"],
    "paisa": ["reimbursement", "expense", "claim"],
    "paise": ["reimbursement", "expenses", "allowance"],
    "kharcha": ["expense", "reimbursement", "claim"],
    "safarnama": ["travel", "travel reimbursement"],
    "tankha": ["salary", "payroll", "compensation"],
    "naukri": ["employment", "job", "onboarding"],
    "karyalaya": ["office", "workplace"],
    "niyam": ["policy", "rule", "guidelines"],
    "madad": ["help", "support", "ticket"],
    "shikayat": ["complaint", "incident", "grievance"],
    "pustak": ["handbook", "guide"],
    "suraksha": ["security", "safety", "firewall"],
    "khata": ["account", "login"],
    "gopneeyata": ["privacy", "confidentiality"],

    # Malayalam / Manglish terms
    "avadhi": ["leave", "holiday", "vacation"],
    "chelave": ["expense", "reimbursement"],
    "chelal": ["expense", "claim"],
    "panam": ["salary", "payment", "reimbursement"],
    "sahayam": ["help", "support", "assistance"],
    "niyamangal": ["policies", "rules", "regulations"],
    "surakshitha": ["security", "safety"],
    "parathi": ["complaint", "issue", "incident"],
    "thudaruka": ["continue", "escalate"],
    "aavashyam": ["requirement", "request"],
    "prashnam": ["issue", "error", "problem"],
}

class CrossLingualQueryExpander:
    @staticmethod
    def expand_query(query: str, detected_language: str) -> str:
        """
        Enriches non-English or code-mixed queries with English canonical office terms
        to facilitate robust cross-lingual retrieval against English office policies.
        """
        words = re.findall(r'\b\w+\b', query.lower())
        added_keywords: Set[str] = set()

        for word in words:
            if word in CROSS_LINGUAL_DICTIONARY:
                for kw in CROSS_LINGUAL_DICTIONARY[word]:
                    added_keywords.add(kw)

        if not added_keywords:
            return query

        expanded = f"{query} {' '.join(added_keywords)}"
        return expanded
