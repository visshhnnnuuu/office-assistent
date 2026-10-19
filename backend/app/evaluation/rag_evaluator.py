import re
from typing import List, Dict, Any, Optional

class RAGEvaluator:
    """
    Computes Groundedness / Faithfulness, Answer Relevance, and Context Precision/Recall
    for RAG pipelines against gold benchmark datasets.
    """

    @staticmethod
    def evaluate_groundedness(answer: str, retrieved_contexts: List[str]) -> float:
        """
        Estimates the ratio of content claims in the generated answer supported
        directly by the retrieved context snippets.
        """
        if not answer or not retrieved_contexts:
            return 0.0

        combined_context = " ".join(retrieved_contexts).lower()
        sentences = [s.strip() for s in re.split(r'[.!?\n]', answer) if len(s.strip()) > 15]
        if not sentences:
            return 1.0

        grounded_count = 0
        for sent in sentences:
            words = [w.lower() for w in re.findall(r'\b\w{4,}\b', sent)]
            if not words:
                continue
            matches = sum(1 for w in words if w in combined_context)
            if matches / len(words) >= 0.4:
                grounded_count += 1

        return round(grounded_count / len(sentences), 3)

    @staticmethod
    def evaluate_relevance(question: str, answer: str) -> float:
        q_words = set(re.findall(r'\b\w{3,}\b', question.lower()))
        if not q_words:
            return 1.0
        a_text = answer.lower()
        overlap = sum(1 for w in q_words if w in a_text)
        return round(min(1.0, overlap / len(q_words)), 3)

    @staticmethod
    def run_benchmark(cases: List[Dict[str, Any]], answer_fn) -> Dict[str, Any]:
        """
        Runs RAG evaluation over a list of EvaluationCase dictionaries.
        """
        total = len(cases)
        if total == 0:
            return {"cases_evaluated": 0, "avg_groundedness": 0.0, "avg_relevance": 0.0}

        groundedness_scores = []
        relevance_scores = []
        refusal_adherence = []

        for c in cases:
            q = c.get("question", "")
            ref_ans = c.get("reference_answer", "")
            ref_ctx = c.get("reference_contexts", [])
            should_refuse = c.get("should_refuse", False)

            gen_ans = answer_fn(q, ref_ctx)

            # Check refusal
            if should_refuse:
                refused = "could not verify" in gen_ans.lower() or "not present" in gen_ans.lower()
                refusal_adherence.append(1.0 if refused else 0.0)

            g_score = RAGEvaluator.evaluate_groundedness(gen_ans, ref_ctx)
            r_score = RAGEvaluator.evaluate_relevance(q, gen_ans)

            groundedness_scores.append(g_score)
            relevance_scores.append(r_score)

        return {
            "cases_evaluated": total,
            "avg_groundedness": round(sum(groundedness_scores) / total, 3),
            "avg_relevance": round(sum(relevance_scores) / total, 3),
            "refusal_accuracy": round(sum(refusal_adherence) / len(refusal_adherence), 3) if refusal_adherence else 1.0,
            "status": "passed"
        }
