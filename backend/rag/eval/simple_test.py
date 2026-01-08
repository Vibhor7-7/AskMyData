"""
Simple Test Script - Run RAG Evaluation

This is a minimal working example to test the evaluation system.
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

print("\n" + "="*70)
print("SIMPLE RAG EVALUATION TEST")
print("="*70 + "\n")

# Define a small test dataset
test_dataset = [
    {
        'question': 'What is the average age?',
        'expected_answer': '30 years old',
        'expected_keywords': ['30', 'average', 'age'],
        'category': 'aggregation'
    },
    {
        'question': 'Who lives in New York City?',
        'expected_answer': 'Alice lives in New York City',
        'expected_keywords': ['Alice', 'NYC', 'New York'],
        'category': 'factual'
    },
    {
        'question': 'How many people are in the dataset?',
        'expected_answer': '3 people',
        'expected_keywords': ['3', 'three', 'people'],
        'category': 'counting'
    }
]

print(f"Test cases: {len(test_dataset)}")
print("Collection: test_collection")
print("ChromaDB: ../test_chroma_db\n")

# Initialize evaluator
try:
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
    
    # Show main result
    relevance = results['aggregated_metrics']['query_relevance_percentage']
    print(f"\n{'='*70}")
    print(f"🎯 RESULT: {relevance:.1f}% Query Relevance")
    print(f"{'='*70}\n")
    
    if relevance >= 85:
        print("✓ Excellent! Production ready!")
    elif relevance >= 70:
        print("⚠ Good, but could be improved")
    else:
        print("✗ Needs improvement")
    
    print("\n✓ Check ./eval_results/ for detailed results\n")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nMake sure:")
    print("1. Ollama is running (ollama serve)")
    print("2. Models are pulled (ollama pull nomic-embed-text && ollama pull llama3.2)")
    print("3. Test collection exists (run vector_store.py first)")
    print("4. ChromaDB path is correct\n")
    raise
