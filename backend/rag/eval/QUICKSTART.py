"""
QUICK START GUIDE - RAG Evaluation in 3 Steps
"""

import json
import os
import sys

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from rag.eval.eval_metrics import RAGEvaluator

# =============================================================================
# STEP 1: Create Test Dataset
# =============================================================================

# Option A: Define inline (good for quick testing)
test_dataset = [
    {
        'question': 'What is the average age?',
        'expected_answer': '30',
        'expected_keywords': ['30', 'average'],
        'category': 'aggregation'
    },
    {
        'question': 'Who lives in NYC?',
        'expected_answer': 'Alice',
        'expected_keywords': ['Alice', 'NYC'],
        'category': 'factual'
    },
    {
        'question': 'How many people are there?',
        'expected_answer': '3',
        'expected_keywords': ['3', 'three'],
        'category': 'counting'
    }
    # Add more test cases for better evaluation (aim for 20-100 test cases)
]

# Option B: Load from JSON file (recommended for production)
# with open('test_dataset.json', 'r') as f:
#     test_dataset = json.load(f)

# =============================================================================
# STEP 2: Initialize Evaluator
# =============================================================================

print("\n" + "="*70)
print("RAG EVALUATION - QUICKSTART")
print("="*70 + "\n")

# IMPORTANT: Change these to match your setup
YOUR_COLLECTION_NAME = "test_collection"      # Change this!
YOUR_CHROMA_PATH = "../test_chroma_db"        # Change this!

print(f"Collection: {YOUR_COLLECTION_NAME}")
print(f"ChromaDB: {YOUR_CHROMA_PATH}")
print(f"Test Cases: {len(test_dataset)}\n")

evaluator = RAGEvaluator(
    collection_name=YOUR_COLLECTION_NAME,
    embedding_model="nomic-embed-text",
    llm_model="llama3.2",
    chroma_persist_dir=YOUR_CHROMA_PATH
)

# =============================================================================
# STEP 3: Run Evaluation & Get Results
# =============================================================================

results = evaluator.run_evaluation(
    test_dataset=test_dataset,
    top_k=5,                    # Number of chunks to retrieve
    save_results=True,          # Save detailed results
    output_dir="./eval_results" # Where to save results
)

# Print formatted report
evaluator.print_report(results)

# =============================================================================
# STEP 4: Access Metrics
# =============================================================================

# Get your main score
relevance_score = results['aggregated_metrics']['query_relevance_percentage']
print(f"\n{'='*70}")
print(f"🎯 FINAL RESULT: {relevance_score:.1f}% Query Relevance")
print(f"{'='*70}\n")

# Target: 85%+ for production
if relevance_score >= 85:
    print("✓ Production ready! Great job!")
elif relevance_score >= 70:
    print("⚠ Good, but could be improved")
else:
    print("✗ Needs improvement - try:")
    print("  - Better chunking strategy")
    print("  - More relevant test cases")
    print("  - Increase top_k retrieval")
    print("  - Improve data quality")

# Access other metrics
metrics = results['aggregated_metrics']
print(f"\nKey Metrics:")
print(f"  Exact Match Rate: {metrics['exact_match_rate']:.1%}")
print(f"  Avg Latency: {metrics['avg_latency_seconds']:.3f}s")
print(f"  Success Rate: {metrics['success_rate']:.1%}")
print(f"  Total Queries: {metrics['total_queries']}")

print(f"\n✓ Results saved to: ./eval_results/\n")
