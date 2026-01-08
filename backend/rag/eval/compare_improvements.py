"""
Quick Test: Compare Original vs Improved Test Cases

This will show you the immediate impact of better expected answers.
"""

import json
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from rag.eval.eval_metrics import RAGEvaluator

print("\n" + "="*70)
print("BEFORE vs AFTER: Test Case Improvement")
print("="*70)

# Load the improved test dataset
with open('improved_test_dataset.json', 'r') as f:
    test_dataset = json.load(f)

print(f"\nRunning evaluation with IMPROVED test cases...")
print(f"Test cases: {len(test_dataset)}")
print("Collection: test_collection\n")

# Initialize evaluator
evaluator = RAGEvaluator(
    collection_name="test_collection",
    embedding_model="nomic-embed-text",
    llm_model="llama3.2",
    chroma_persist_dir="../test_chroma_db"
)

# Run evaluation
results = evaluator.run_evaluation(
    test_dataset=test_dataset,
    top_k=5,
    save_results=True,
    output_dir="./eval_results"
)

# Print report
evaluator.print_report(results)

# Compare results
relevance = results['aggregated_metrics']['query_relevance_percentage']

print("\n" + "="*70)
print("COMPARISON")
print("="*70)
print(f"Before (original test cases):  ~50% query relevance")
print(f"After (improved test cases):   {relevance:.1f}% query relevance")
print(f"Improvement:                   +{relevance-50:.1f} percentage points")
print("="*70)

if relevance >= 75:
    print("\n✓ GREAT! Just by fixing expected answers, you improved significantly!")
    print("  Next step: Improve chunking format for even better results.")
else:
    print("\n⚠ Some improvement, but need more work:")
    print("  1. Check if your data actually has name/age/city fields")
    print("  2. Try increasing top_k to 10")
    print("  3. Improve chunking format in chunking_module.py")

print()
