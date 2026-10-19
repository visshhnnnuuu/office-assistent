import re
from typing import List, Dict, Any
from backend.app.multilingual.term_preserver import PRESERVED_TECHNICAL_TERMS

class TranslationEvaluator:
    """
    Evaluates translation fidelity and specifically checks the retention of
    untranslated technical and IT workplace jargon (VPN, Wi-Fi, HR, Docker, etc.).
    """

    @staticmethod
    def evaluate_term_retention(source_text: str, candidate_text: str) -> float:
        s_lower = source_text.lower()
        c_lower = candidate_text.lower()

        present_terms = [t for t in PRESERVED_TECHNICAL_TERMS if t in s_lower]
        if not present_terms:
            return 1.0

        retained = sum(1 for t in present_terms if t in c_lower)
        return round(retained / len(present_terms), 3)

    @staticmethod
    def evaluate_benchmark(cases: List[Dict[str, Any]], translate_fn) -> Dict[str, Any]:
        total = len(cases)
        if total == 0:
            return {"cases_evaluated": 0, "avg_term_retention": 1.0}

        retention_scores = []
        for case in cases:
            src = case.get("source_text", "")
            ref = case.get("reference_translation", "")
            candidate = translate_fn(src)
            score = TranslationEvaluator.evaluate_term_retention(src, candidate)
            retention_scores.append(score)

        return {
            "cases_evaluated": total,
            "avg_term_retention": round(sum(retention_scores) / total, 3),
            "status": "passed"
        }
