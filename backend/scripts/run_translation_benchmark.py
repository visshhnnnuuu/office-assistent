import argparse
import sys
import json
from backend.app.datasets.huggingface_client import HuggingFaceClient
from backend.app.evaluation.translation_evaluator import TranslationEvaluator
from backend.app.multilingual.term_preserver import TermPreserver

def main():
    parser = argparse.ArgumentParser(description="Run Indic Translation & Term Preservation Benchmark.")
    parser.add_argument("--dataset", type=str, default="ai4bharat/IN22-Conv", help="Target translation benchmark")
    parser.add_argument("--samples", type=int, default=10, help="Number of benchmark samples to evaluate")

    args = parser.parse_args()

    print(f"\n[INFO] Evaluating Translation & Term Preservation on '{args.dataset}' ({args.samples} samples)...")
    raw_records = HuggingFaceClient.fetch_records(args.dataset, max_records=args.samples)
    cases = []
    for r in raw_records:
        cases.append({
            "source_text": r.get("source", ""),
            "reference_translation": r.get("target", "")
        })

    def eval_translate_fn(src):
        return TermPreserver.sanitize_text_for_term_preservation(src)

    results = TranslationEvaluator.evaluate_benchmark(cases, eval_translate_fn)
    print("\nTranslation Benchmark Report:")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
