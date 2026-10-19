import re
from typing import List, Dict, Any, Optional

class HeadingAwareChunker:
    """
    Splits documents into semantic units of 300-600 words preserving
    headings, section hierarchy, page numbers, and tabular context.
    """
    def __init__(self, target_min_words: int = 250, target_max_words: int = 600, overlap_words: int = 40):
        self.target_min_words = target_min_words
        self.target_max_words = target_max_words
        self.overlap_words = overlap_words

    def chunk_document(
        self,
        document_id: str,
        text: str,
        base_metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Parses text by markdown headings (#, ##, ###) or structured section dividers.
        Falls back to sliding window if section is excessively large.
        """
        lines = text.split('\n')
        sections: List[Dict[str, Any]] = []
        current_section_title = base_metadata.get("title", "Overview")
        current_lines: List[str] = []
        current_page = base_metadata.get("page_number", 1)

        heading_pattern = re.compile(r'^(#{1,4}\s+|Section\s+\d+[:\.]?|[A-Z\s]{4,}:)\s*(.+)$', re.IGNORECASE)
        page_pattern = re.compile(r'<!--\s*PAGE\s*(\d+)\s*-->|\[Page\s*(\d+)\]', re.IGNORECASE)

        for line in lines:
            # Check page marker
            page_match = page_pattern.search(line)
            if page_match:
                page_num = page_match.group(1) or page_match.group(2)
                if page_num:
                    current_page = int(page_num)

            # Check heading marker
            heading_match = heading_pattern.match(line.strip())
            if heading_match and len(current_lines) > 5:
                # Flush previous section
                section_text = '\n'.join(current_lines).strip()
                if section_text:
                    sections.append({
                        "section_title": current_section_title,
                        "text": section_text,
                        "page_number": current_page
                    })
                current_section_title = heading_match.group(2).strip()
                current_lines = [line]
            else:
                current_lines.append(line)

        # Flush final section
        if current_lines:
            section_text = '\n'.join(current_lines).strip()
            if section_text:
                sections.append({
                    "section_title": current_section_title,
                    "text": section_text,
                    "page_number": current_page
                })

        # Now subdivide oversized sections or group undersized ones
        chunks: List[Dict[str, Any]] = []
        chunk_idx = 1

        for sec in sections:
            words = sec["text"].split()
            if len(words) <= self.target_max_words:
                chunks.append({
                    "chunk_id": f"{document_id}_c{chunk_idx}",
                    "document_id": document_id,
                    "section_title": sec["section_title"],
                    "page_number": sec["page_number"],
                    "slide_number": base_metadata.get("slide_number"),
                    "sheet_name": base_metadata.get("sheet_name"),
                    "row_reference": base_metadata.get("row_reference"),
                    "content": sec["text"],
                    "classification": base_metadata.get("classification", "internal"),
                    "allowed_roles": base_metadata.get("allowed_roles", ["all"]),
                    "allowed_departments": base_metadata.get("allowed_departments", ["all"]),
                    "language": base_metadata.get("language", "eng_Latn"),
                })
                chunk_idx += 1
            else:
                # Windowed split with overlap
                start = 0
                sub_part = 1
                while start < len(words):
                    end = min(start + self.target_max_words, len(words))
                    chunk_words = words[start:end]
                    chunk_content = ' '.join(chunk_words)

                    chunks.append({
                        "chunk_id": f"{document_id}_c{chunk_idx}_p{sub_part}",
                        "document_id": document_id,
                        "section_title": f"{sec['section_title']} (Part {sub_part})",
                        "page_number": sec["page_number"],
                        "slide_number": base_metadata.get("slide_number"),
                        "sheet_name": base_metadata.get("sheet_name"),
                        "row_reference": base_metadata.get("row_reference"),
                        "content": chunk_content,
                        "classification": base_metadata.get("classification", "internal"),
                        "allowed_roles": base_metadata.get("allowed_roles", ["all"]),
                        "allowed_departments": base_metadata.get("allowed_departments", ["all"]),
                        "language": base_metadata.get("language", "eng_Latn"),
                    })
                    chunk_idx += 1
                    sub_part += 1
                    if end == len(words):
                        break
                    start = end - self.overlap_words

        return chunks
