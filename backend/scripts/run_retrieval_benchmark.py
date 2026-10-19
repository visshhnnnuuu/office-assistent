import argparse
import sys
import json
from backend.app.datasets.huggingface_client import HuggingFaceClient
from backend.app.evaluation.retrieval_evaluator import RetrievalEvaluator

def main():
    parser = argparse.ArgumentParser(description="Run Retrieval Quality Benchmark (Hit@K, MRR).")
    parser.add_argument("--dataset", type=str, default="ai4bharat/MSMARCO-XI", help="Retrieval benchmark dataset")
    parser.add_argument("--top-k", type=int, default=5, help="Top-K threshold")

    args = parser.parse_args()

    print(f"\n[INFO] Running Retrieval Benchmark on '{args.dataset}' (Top-{args.top_k})...")
    raw_records = HuggingFaceClient.fetch_records(args.dataset, max_records=20)
    cases = []
    for r in raw_records:
        cases.append({
            "query": r.get("query", ""),
            "positive_passages": r.get("positive_passages", [])
        })

    def mock_retrieve_fn(query, top_k):
        return [
            {"content": f"Passage matching {query} with corporate Cisco AnyConnect and HRMS portal instructions."}
        ]

    results = RetrievalEvaluator.evaluate_retrieval_cases(cases, mock_retrieve_fn, top_k=args.top_k)
    print("\nRetrieval Benchmark Report:")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
