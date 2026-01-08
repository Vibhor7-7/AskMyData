# backend/rag/eval/run_evaluation.py

"""
Complete Guide: How to Use the RAG Evaluation System

This script demonstrates the full workflow from creating test data to running evaluations.
"""

import json
import os
import sys

# Add parent directories to path to import modules
current_dir = os.path.dirname(os.path.abspath(__file__))
eval_dir = current_dir
rag_dir = os.path.dirname(eval_dir)
backend_dir = os.path.dirname(rag_dir)

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if eval_dir not in sys.path:
    sys.path.insert(0, eval_dir)

from rag.eval.eval_metrics import RAGEvaluator


def example_1_quick_evaluation():
    """
    Example 1: Quick evaluation with minimal test cases
    Perfect for: Initial testing, debugging
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Quick Evaluation (5 test cases)")
    print("="*70 + "\n")
    
    # Step 1: Define test cases inline
    test_dataset = [
        {
            'question': 'What is the average age?',
            'expected_answer': '30',
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
            'question': 'List all cities',
            'expected_answer': 'NYC, LA, Chicago',
            'expected_keywords': ['NYC', 'LA', 'Chicago'],
            'category': 'enumeration'
        },
        {
            'question': 'Who is the oldest person?',
            'expected_answer': 'Charlie is the oldest at 35 years',
            'expected_keywords': ['Charlie', '35', 'oldest'],
            'category': 'comparison'
        },
        {
            'question': 'How many people are there?',
            'expected_answer': '3',
            'expected_keywords': ['3', 'three'],
            'category': 'counting'
        }
    ]
    
    # Step 2: Initialize evaluator with your collection
    evaluator = RAGEvaluator(
        collection_name="test_collection",  # Change to your collection name
        embedding_model="nomic-embed-text",
        llm_model="llama3.2",
        chroma_persist_dir="../test_chroma_db"  # Change to your DB path
    )
    
    # Step 3: Run evaluation
    results = evaluator.run_evaluation(
        test_dataset=test_dataset,
        top_k=5,
        save_results=True,
        output_dir="./eval_results"
    )
    
    # Step 4: Print formatted report
    evaluator.print_report(results)
    
    # Step 5: Access specific metrics
    relevance = results['aggregated_metrics']['query_relevance_percentage']
    print(f"\n🎯 Result: Achieved {relevance:.1f}% query relevance on {len(test_dataset)} test cases\n")
    
    return results


def example_2_load_from_json():
    """
    Example 2: Load test dataset from JSON file
    Perfect for: Repeatable evaluations, version control
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Load Test Dataset from JSON File")
    print("="*70 + "\n")
    
    # Step 1: Load test dataset from file
    dataset_path = "./test_dataset_template.json"
    
    if not os.path.exists(dataset_path):
        print(f"❌ Test dataset not found at {dataset_path}")
        print("Create one using: python create_test_dataset.py --interactive")
        return None
    
    with open(dataset_path, 'r') as f:
        test_dataset = json.load(f)
    
    print(f"✓ Loaded {len(test_dataset)} test cases from {dataset_path}\n")
    
    # Step 2: Initialize evaluator
    evaluator = RAGEvaluator(
        collection_name="test_collection",
        chroma_persist_dir="../test_chroma_db"
    )
    
    # Step 3: Run evaluation
    results = evaluator.run_evaluation(
        test_dataset=test_dataset,
        top_k=5,
        save_results=True
    )
    
    # Step 4: Print report
    evaluator.print_report(results)
    
    return results


def example_3_evaluate_your_data():
    """
    Example 3: Evaluate against your actual uploaded data
    Perfect for: Real-world performance testing
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Evaluate Your Actual Data")
    print("="*70 + "\n")
    
    # First, you need to upload a file and note its collection name
    print("Prerequisites:")
    print("1. Upload a file via the API: POST /api/files/upload")
    print("2. Note the 'collection_name' from the response")
    print("3. Create test cases based on your data\n")
    
    # Example test cases for a typical CSV file
    test_dataset = [
        {
            'question': 'How many rows are in the dataset?',
            'expected_answer': 'Number varies based on your data',
            'expected_keywords': ['rows', 'records', 'entries'],
            'category': 'counting'
        },
        {
            'question': 'What columns are available?',
            'expected_answer': 'Depends on your CSV',
            'expected_keywords': ['columns', 'fields'],
            'category': 'factual'
        },
        # Add more test cases specific to your data
    ]
    
    # Replace with your actual collection name
    YOUR_COLLECTION_NAME = "avocado_20251222_193628"  # Example
    
    evaluator = RAGEvaluator(
        collection_name=YOUR_COLLECTION_NAME,
        chroma_persist_dir="../chroma_db"  # Your actual DB path
    )
    
    print(f"Testing collection: {YOUR_COLLECTION_NAME}\n")
    
    results = evaluator.run_evaluation(
        test_dataset=test_dataset,
        top_k=5,
        save_results=True
    )
    
    evaluator.print_report(results)
    
    return results


def example_4_compare_models():
    """
    Example 4: Compare different LLM models
    Perfect for: Model selection, performance optimization
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Compare Multiple LLM Models")
    print("="*70 + "\n")
    
    # Test dataset
    test_dataset = [
        {
            'question': 'What is the sum of all values?',
            'expected_answer': '150',
            'expected_keywords': ['150', 'sum', 'total'],
            'category': 'aggregation'
        },
        {
            'question': 'List unique categories',
            'expected_answer': 'Category A, Category B, Category C',
            'expected_keywords': ['Category A', 'Category B', 'Category C'],
            'category': 'enumeration'
        }
    ]
    
    # Models to compare (make sure these are pulled in Ollama)
    models = ['llama3.2', 'mistral']  # Add more models as needed
    
    comparison_results = {}
    
    for model in models:
        print(f"\n{'='*70}")
        print(f"Testing Model: {model}")
        print('='*70)
        
        evaluator = RAGEvaluator(
            collection_name="test_collection",
            llm_model=model,
            chroma_persist_dir="../test_chroma_db"
        )
        
        results = evaluator.run_evaluation(
            test_dataset=test_dataset,
            top_k=5,
            save_results=False  # Don't save individual results
        )
        
        comparison_results[model] = results['aggregated_metrics']
    
    # Print comparison
    print("\n" + "="*70)
    print("MODEL COMPARISON RESULTS")
    print("="*70 + "\n")
    
    print(f"{'Model':<20} {'Query Relevance':<20} {'Avg Latency':<20}")
    print("-" * 70)
    
    for model, metrics in comparison_results.items():
        relevance = metrics['query_relevance_percentage']
        latency = metrics['avg_latency_seconds']
        print(f"{model:<20} {relevance:>6.1f}%{'':<13} {latency:>6.3f}s")
    
    return comparison_results


def example_5_category_analysis():
    """
    Example 5: Analyze performance by question category
    Perfect for: Identifying weaknesses, focused improvements
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Performance by Question Category")
    print("="*70 + "\n")
    
    # Test dataset with various categories
    test_dataset = [
        # Aggregation questions
        {'question': 'What is the total?', 'expected_answer': '500', 
         'expected_keywords': ['500', 'total'], 'category': 'aggregation'},
        {'question': 'What is the average?', 'expected_answer': '50', 
         'expected_keywords': ['50', 'average'], 'category': 'aggregation'},
        
        # Factual questions
        {'question': 'Who is the manager?', 'expected_answer': 'John Smith', 
         'expected_keywords': ['John', 'Smith'], 'category': 'factual'},
        {'question': 'What is the address?', 'expected_answer': '123 Main St', 
         'expected_keywords': ['123', 'Main'], 'category': 'factual'},
        
        # Counting questions
        {'question': 'How many items?', 'expected_answer': '10', 
         'expected_keywords': ['10', 'ten'], 'category': 'counting'},
        {'question': 'How many categories?', 'expected_answer': '5', 
         'expected_keywords': ['5', 'five'], 'category': 'counting'},
    ]
    
    evaluator = RAGEvaluator(
        collection_name="test_collection",
        chroma_persist_dir="../test_chroma_db"
    )
    
    results = evaluator.run_evaluation(
        test_dataset=test_dataset,
        top_k=5,
        save_results=True
    )
    
    # Analyze by category
    detailed = results['detailed_results']
    category_scores = {}
    
    for result in detailed:
        category = result['category']
        score = result['answer_metrics']['semantic_similarity']
        
        if category not in category_scores:
            category_scores[category] = []
        category_scores[category].append(score)
    
    print("\n" + "="*70)
    print("PERFORMANCE BY CATEGORY")
    print("="*70 + "\n")
    
    print(f"{'Category':<20} {'Avg Score':<15} {'Count':<10} {'Status'}")
    print("-" * 70)
    
    for category, scores in sorted(category_scores.items()):
        avg_score = sum(scores) / len(scores)
        status = "✓ Good" if avg_score >= 0.7 else "⚠ Needs Work"
        print(f"{category:<20} {avg_score:>6.1%}{'':<8} {len(scores):<10} {status}")
    
    return results


def create_custom_test_dataset():
    """
    Interactive guide to create your own test dataset
    """
    print("\n" + "="*70)
    print("CREATE YOUR CUSTOM TEST DATASET")
    print("="*70 + "\n")
    
    print("Step-by-step instructions:")
    print("\n1. Run the interactive creator:")
    print("   python create_test_dataset.py --interactive")
    
    print("\n2. Or create a text file (questions.txt) with this format:")
    print("""
    Q: What is the total revenue?
    A: $50,000
    K: 50000, revenue, total
    C: aggregation
    ---
    Q: Who is the CEO?
    A: Jane Doe
    K: Jane, Doe, CEO
    C: factual
    ---
    """)
    
    print("3. Then convert it:")
    print("   python create_test_dataset.py --from-file questions.txt")
    
    print("\n4. Your test dataset will be saved as 'test_dataset.json'")
    print("   Use it with example_2_load_from_json()\n")


def main():
    """
    Main menu - choose which example to run
    """
    print("\n" + "="*70)
    print("RAG EVALUATION SYSTEM - USAGE EXAMPLES")
    print("="*70)
    
    print("""
Choose an example to run:

1. Quick Evaluation (5 test cases, good for testing)
2. Load from JSON File (repeatable, version controlled)
3. Evaluate Your Actual Data (real-world testing)
4. Compare Models (find the best model)
5. Category Analysis (identify weaknesses)
6. How to Create Custom Test Dataset

0. Run all examples

Enter choice (0-6): """, end='')
    
    choice = input().strip()
    
    examples = {
        '1': example_1_quick_evaluation,
        '2': example_2_load_from_json,
        '3': example_3_evaluate_your_data,
        '4': example_4_compare_models,
        '5': example_5_category_analysis,
        '6': create_custom_test_dataset,
    }
    
    if choice == '0':
        # Run all examples
        for key in sorted(examples.keys()):
            if key != '6':  # Skip the guide
                examples[key]()
                input("\nPress Enter to continue to next example...")
    elif choice in examples:
        examples[choice]()
    else:
        print("\n❌ Invalid choice")
        return
    
    print("\n" + "="*70)
    print("✓ Evaluation Complete!")
    print("="*70 + "\n")
    
    print("Next steps:")
    print("• Review results in ./eval_results/ directory")
    print("• Analyze CSV file in Excel/Google Sheets")
    print("• Compare metrics against your 85% target")
    print("• Iterate on improvements (chunking, prompts, model choice)")
    print("• Re-run evaluation to measure progress\n")


if __name__ == "__main__":
    main()