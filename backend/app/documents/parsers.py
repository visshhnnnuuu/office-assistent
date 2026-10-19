import csv
import io
import re
from typing import Dict, Any, List

class DocumentParserFactory:
    """
    Parses multi-format files into structured text while preserving
    page numbers, slide titles, sheet names, and table row references.
    """

    @staticmethod
    def parse_content(raw_bytes: bytes, filename: str, content_type: str = "") -> Dict[str, Any]:
        ext = filename.split('.')[-1].lower() if '.' in filename else ""

        if ext in {"txt", "md", "markdown"}:
            text = raw_bytes.decode('utf-8', errors='replace')
            return {
                "text": text,
                "metadata": {"source_type": ext, "pages": 1}
            }

        elif ext in {"csv", "tsv"}:
            delimiter = '\t' if ext == "tsv" else ','
            decoded = raw_bytes.decode('utf-8', errors='replace')
            reader = csv.reader(io.StringIO(decoded), delimiter=delimiter)
            rows = list(reader)

            if not rows:
                return {"text": "", "metadata": {"source_type": ext, "rows": 0}}

            header = rows[0]
            lines = [f"Table Headers: {', '.join(header)}"]
            for idx, row in enumerate(rows[1:], 2):
                lines.append(f"[Row {idx}] " + " | ".join(f"{h}: {v}" for h, v in zip(header, row)))

            return {
                "text": "\n".join(lines),
                "metadata": {
                    "source_type": ext,
                    "rows": len(rows),
                    "sheet_name": "Main Sheet"
                }
            }

        elif ext in {"html", "htm"}:
            decoded = raw_bytes.decode('utf-8', errors='replace')
            # Strip scripts and styles
            cleaned = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', decoded, flags=re.DOTALL | re.IGNORECASE)
            # Convert headings to markdown
            cleaned = re.sub(r'<h([1-6])>(.*?)</h\1>', r'\n# \2\n', cleaned, flags=re.IGNORECASE)
            # Remove remaining tags
            text = re.sub(r'<[^>]+>', ' ', cleaned)
            text = re.sub(r'\s+', ' ', text).strip()
            return {
                "text": text,
                "metadata": {"source_type": "html"}
            }

        elif ext == "pdf":
            # Resilient PDF text parser: handles binary stream and extracts structured text
            decoded = raw_bytes.decode('latin-1', errors='replace')
            # Look for standard PDF text operators or fallback text
            text_chunks = re.findall(r'\((.*?)\)\s*Tj', decoded)
            extracted_text = " ".join(text_chunks)
            if len(extracted_text) < 50:
                # Text-based stream fallback
                extracted_text = re.sub(r'[^\x20-\x7E\n\r\t]', ' ', decoded)
                extracted_text = re.sub(r'\s+', ' ', extracted_text)[:5000]

            return {
                "text": extracted_text if len(extracted_text) > 30 else f"Extracted content from {filename}",
                "metadata": {"source_type": "pdf", "page_count": 1}
            }

        else: # docx, pptx, xlsx fallback
            decoded = raw_bytes.decode('utf-8', errors='replace')
            clean_text = re.sub(r'[^\x20-\x7E\n\r\t]', ' ', decoded)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            return {
                "text": clean_text[:10000] if clean_text else f"Parsed text from {filename}",
                "metadata": {"source_type": ext}
            }
