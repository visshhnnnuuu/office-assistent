import re
from typing import Tuple, List
from fastapi import HTTPException, UploadFile

ALLOWED_EXTENSIONS = {
    "pdf", "docx", "doc", "pptx", "ppt", "xlsx", "xls", "csv", "tsv", "txt", "md", "html"
}

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
    "text/csv",
    "text/plain",
    "text/markdown",
    "text/html"
}

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024 # 25 MB

CRITICAL_BLACKLIST_PATTERNS = [
    re.compile(r'\b(api[_\s]?key|secret[_\s]?key|private[_\s]?key|ssh-rsa)\b', re.IGNORECASE),
    re.compile(r'\b(wifi[_\s]password|wpa2|pre-shared key)\b', re.IGNORECASE),
    re.compile(r'\b(salary[_\s]slip|employee[_\s]payroll|ctc[_\s]breakup|bank[_\s]account[_\s]details)\b', re.IGNORECASE),
    re.compile(r'\b(medical[_\s]records|patient[_\s]diagnosis|confidential[_\s]board[_\s]minutes)\b', re.IGNORECASE),
]

class DocumentSecurityValidator:
    @staticmethod
    def validate_upload(filename: str, content_type: str, file_size: int) -> None:
        ext = filename.split('.')[-1].lower() if '.' in filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file extension '.{ext}'. Supported: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )

        if file_size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024*1024)} MB."
            )

    @staticmethod
    def scan_for_blacklisted_content(text: str) -> Tuple[bool, List[str]]:
        """
        Scans document text against the prohibited content blacklist (passwords, Wi-Fi keys,
        salaries, medical records). Returns (is_violating, list_of_violations).
        """
        violations = []
        for pattern in CRITICAL_BLACKLIST_PATTERNS:
            match = pattern.search(text)
            if match:
                violations.append(match.group(0))

        return len(violations) > 0, violations
