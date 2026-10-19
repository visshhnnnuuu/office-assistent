import argparse
import sys
import json
from backend.app.db import SessionLocal, init_db
from backend.app.evaluation.rag_evaluator import RAGEvaluator
from backend.app.datasets.huggingface_client import HuggingFaceClient
from backend.app.rag.generator import StructuredAnswerGenerator

def main():
    parser = argparse.ArgumentParser(description="Run RAG Grounding and Answer Quality Evaluation.")
    parser.add_argument("--dataset", type=str, default="dwb2023/ragas-golden-dataset", help="Target evaluation dataset")
    parser.add_argument("--samples", type=int, default=10, help="Number of benchmark samples to evaluate")
    parser.add_argument("--company-benchmark", action="store_true", help="Run locked Section L company evaluation benchmark")

    args = parser.parse_args()

    print("\n========================================================")
    print("  RAG Quality & Groundedness Evaluation Suite")
    print("========================================================\n")

    if args.company_benchmark:
        print("[INFO] Executing Section L: Locked Company Golden Benchmark...")
        company_cases = [
            {
                "question": "What is the annual carry-forward limit for casual leave?",
                "reference_contexts": ["Employees may carry forward a maximum of 10 days of earned annual leave into the subsequent calendar year."],
                "reference_answer": "Up to 10 days can be carried forward.",
                "should_refuse": False
            },
            {
                "question": "What is the company policy on unlimited free company cryptocurrency grants?",
                "reference_contexts": [],
                "reference_answer": "",
                "should_refuse": True
            },
            {
                "question": "How do I apply for domestic travel reimbursement?",
                "reference_contexts": ["Submit Form 12BB within 15 days of travel completion with all original receipts."],
                "reference_answer": "Submit Form 12BB within 15 days with original receipts.",
                "should_refuse": False
            }
        ]

        def answer_fn(q, ctxs):
            chunks = [{"content": c, "title": "Company Policy"} for c in ctxs] if ctxs else []
            res = StructuredAnswerGenerator.generate_grounded_answer(
                question=q,
                retrieved_chunks=chunks,
                language="eng_Latn"
            )
            return res["content"]

        results = RAGEvaluator.run_benchmark(company_cases, answer_fn)
        print(f"Results for Locked Company Evaluation:")
        print(json.dumps(results, indent=2))
        return

    print(f"[INFO] Evaluating against dataset '{args.dataset}' ({args.samples} samples)...")
    raw_records = HuggingFaceClient.fetch_records(args.dataset, max_records=args.samples)
    cases = []
    for r in raw_records:
        cases.append({
            "question": r.get("user_input") or r.get("query") or "Company question",
            "reference_contexts": r.get("reference_contexts") or [r.get("context", "")],
            "reference_answer": r.get("reference") or r.get("answer", "")
        })

    def eval_answer_fn(q, ctxs):
        res = StructuredAnswerGenerator.generate_grounded_answer(
            question=q,
            retrieved_chunks=[{"content": c, "title": "Benchmark Doc"} for c in ctxs],
            language="eng_Latn"
        )
        return res["content"]

    results = RAGEvaluator.run_benchmark(cases, eval_answer_fn)
    print(f"\nRAG Evaluation Report for '{args.dataset}':")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
