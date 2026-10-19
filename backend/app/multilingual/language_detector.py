import re
from typing import Dict, Any, Tuple

DEVANAGARI_REGEX = re.compile(r'[\u0900-\u097F]')
MALAYALAM_REGEX = re.compile(r'[\u0D00-\u0D7F]')
LATIN_REGEX = re.compile(r'[a-zA-Z]')

HINGLISH_KEYWORDS = {
    "kya", "hai", "kaise", "kare", "karna", "karo", "mujhe", "mera", "meri", "mere",
    "hoga", "hogi", "hote", "nahi", "nahin", "chahiye", "batao", "bataiye", "aap", "tum",
    "hum", "kab", "kyun", "kyu", "wala", "wali", "wale", "process", "apply", "form", "kabse",
    "kisko", "mail", "leave", "chutti", "paise", "kaam", "kitna", "kitne", "dena", "milega"
}

MANGLISH_KEYWORDS = {
    "entha", "engane", "cheyyan", "cheyyuka", "cheyyenda", "patto", "undoo", "undo", "illa",
    "aano", "ano", "patti", "parayamo", "parayu", "evide", "innu", "nokku", "nokkuka",
    "vechu", "athil", "ente", "nammude", "steps", "leave", "apply", "balance", "chodikkam",
    "varum", "vannu", "poyi", "ethra", "divasam", "ariyamo", "kitto"
}

class LanguageDetector:
    @staticmethod
    def detect(text: str) -> Dict[str, Any]:
        """
        Detects language form, script, confidence, and code-mixed status.
        Supported forms:
        - eng_Latn: English
        - hin_Deva: Hindi in Devanagari
        - hin_Latn: Hinglish (Romanized Hindi)
        - mal_Mlym: Malayalam in Malayalam script
        - mal_Latn: Manglish (Romanized Malayalam)
        - mixed: English-Hindi or English-Malayalam mixed
        """
        if not text or not text.strip():
            return {
                "language_id": "eng_Latn",
                "script": "Latn",
                "confidence": 0.5,
                "is_code_mixed": False,
                "detected_form": "English (Default)",
            }

        total_chars = len(text)
        deva_chars = len(DEVANAGARI_REGEX.findall(text))
        mlym_chars = len(MALAYALAM_REGEX.findall(text))
        latin_chars = len(LATIN_REGEX.findall(text))

        deva_ratio = deva_chars / total_chars if total_chars else 0
        mlym_ratio = mlym_chars / total_chars if total_chars else 0
        latin_ratio = latin_chars / total_chars if total_chars else 0

        # Script-first classification
        if deva_ratio > 0.25:
            is_mixed = latin_ratio > 0.15
            confidence = min(0.98, 0.7 + deva_ratio)
            return {
                "language_id": "hin_Deva",
                "script": "Deva",
                "confidence": round(confidence, 2),
                "is_code_mixed": is_mixed,
                "detected_form": "Hindi (Devanagari)" + (" with English" if is_mixed else ""),
            }

        if mlym_ratio > 0.25:
            is_mixed = latin_ratio > 0.15
            confidence = min(0.98, 0.7 + mlym_ratio)
            return {
                "language_id": "mal_Mlym",
                "script": "Mlym",
                "confidence": round(confidence, 2),
                "is_code_mixed": is_mixed,
                "detected_form": "Malayalam (Script)" + (" with English" if is_mixed else ""),
            }

        # Latin script: could be English, Hinglish, or Manglish
        words = [w.lower().strip(",.?!;:()[]{}\"'") for w in text.split()]
        word_count = len(words)

        if word_count == 0:
            return {"language_id": "eng_Latn", "script": "Latn", "confidence": 0.5, "is_code_mixed": False, "detected_form": "English"}

        hinglish_matches = sum(1 for w in words if w in HINGLISH_KEYWORDS)
        manglish_matches = sum(1 for w in words if w in MANGLISH_KEYWORDS)

        hinglish_score = hinglish_matches / word_count
        manglish_score = manglish_matches / word_count

        if hinglish_score >= 0.15 or (hinglish_matches >= 2 and word_count <= 8):
            return {
                "language_id": "hin_Latn",
                "script": "Latn",
                "confidence": round(min(0.95, 0.6 + hinglish_score), 2),
                "is_code_mixed": True,
                "detected_form": "Hinglish (Romanized Hindi)",
            }

        if manglish_score >= 0.15 or (manglish_matches >= 2 and word_count <= 8):
            return {
                "language_id": "mal_Latn",
                "script": "Latn",
                "confidence": round(min(0.95, 0.6 + manglish_score), 2),
                "is_code_mixed": True,
                "detected_form": "Manglish (Romanized Malayalam)",
            }

        # Default to English
        return {
            "language_id": "eng_Latn",
            "script": "Latn",
            "confidence": 0.92,
            "is_code_mixed": False,
            "detected_form": "English",
        }
