from typing import List, Dict, Any, Tuple

class RetrievalEvaluator:
    """
    Measures passage retrieval efficacy against benchmark queries (e.g. MSMARCO-XI).
    Computes Hit@K (1, 3, 5) and Mean Reciprocal Rank (MRR).
    """

    @staticmethod
    def evaluate_retrieval_cases(cases: List[Dict[str, Any]], retrieve_fn, top_k: int = 5) -> Dict[str, Any]:
        total = len(cases)
        if total == 0:
            return {"cases_evaluated": 0, "hit_at_1": 0.0, "hit_at_3": 0.0, "hit_at_5": 0.0, "mrr": 0.0}

        hit_1 = 0
        hit_3 = 0
        hit_5 = 0
        rr_sum = 0.0

        for case in cases:
            query = case.get("query", "")
            positives = [p.lower() for p in case.get("positive_passages", [])]
            if not query or not positives:
                continue

            retrieved = retrieve_fn(query, top_k=top_k)
            first_hit_rank = None

            for rank, item in enumerate(retrieved, 1):
                item_content = item.lower() if isinstance(item, str) else item.get("content", "").lower()
                # Check overlap with any positive passage
                if any(p[:40] in item_content for p in positives):
                    first_hit_rank = rank
                    break

            if first_hit_rank is not None:
                if first_hit_rank == 1:
                    hit_1 += 1
                if first_hit_rank <= 3:
                    hit_3 += 1
                if first_hit_rank <= 5:
                    hit_5 += 1
                rr_sum += 1.0 / first_hit_rank

        return {
            "cases_evaluated": total,
            "hit_at_1": round(hit_1 / total, 3),
            "hit_at_3": round(hit_3 / total, 3),
            "hit_at_5": round(hit_5 / total, 3),
            "mrr": round(rr_sum / total, 3),
            "status": "passed"
        }
