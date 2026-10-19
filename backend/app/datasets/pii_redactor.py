import re
from typing import Tuple, Dict, Any

EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
PHONE_PATTERN = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\b[6-9]\d{9}\b')
IP_PATTERN = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
SECRET_PATTERN = re.compile(r'\b(ghp_[A-Za-z0-9]{36}|AIza[0-9A-Za-z-_]{35}|sk-[A-Za-z0-9]{32,}|bearer\s+[A-Za-z0-9._\-]{20,})\b', re.IGNORECASE)
CREDIT_CARD_PATTERN = re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b')
EMP_ID_PATTERN = re.compile(r'\b(EMP[_-]?\d{4,8}|ID[_-]?\d{4,8})\b', re.IGNORECASE)

class PIIRedactor:
    """
    Sanitizes public datasets and ingested documents by replacing sensitive PII
    and credentials with standardized redaction tokens.
    """

    @staticmethod
    def redact_text(text: str) -> Tuple[str, int]:
        if not text:
            return text, 0

        redactions_count = 0

        # Redact Secrets
        text, n = SECRET_PATTERN.subn("[REDACTED_SECRET]", text)
        redactions_count += n

        # Redact Emails
        text, n = EMAIL_PATTERN.subn("[REDACTED_EMAIL]", text)
        redactions_count += n

        # Redact Credit Cards
        text, n = CREDIT_CARD_PATTERN.subn("[REDACTED_CARD]", text)
        redactions_count += n

        # Redact Phones
        text, n = PHONE_PATTERN.subn("[REDACTED_PHONE]", text)
        redactions_count += n

        # Redact IPs
        text, n = IP_PATTERN.subn("[REDACTED_IP]", text)
        redactions_count += n

        # Redact Employee IDs
        text, n = EMP_ID_PATTERN.subn("[REDACTED_ID]", text)
        redactions_count += n

        return text, redactions_count

    @staticmethod
    def redact_record(record: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        total_redactions = 0
        cleaned: Dict[str, Any] = {}

        for k, v in record.items():
            if isinstance(v, str):
                redacted_v, count = PIIRedactor.redact_text(v)
                cleaned[k] = redacted_v
                total_redactions += count
            elif isinstance(v, list):
                new_list = []
                for item in v:
                    if isinstance(item, str):
                        redacted_item, count = PIIRedactor.redact_text(item)
                        new_list.append(redacted_item)
                        total_redactions += count
                    else:
                        new_list.append(item)
                cleaned[k] = new_list
            elif isinstance(v, dict):
                sub_dict, count = PIIRedactor.redact_record(v)
                cleaned[k] = sub_dict
                total_redactions += count
            else:
                cleaned[k] = v

        return cleaned, total_redactions
