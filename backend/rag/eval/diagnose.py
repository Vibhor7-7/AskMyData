"""
Diagnostic Script - See What's Actually Happening

This will show you EXACTLY why your scores are low by displaying:
1. The question
2. What you EXPECTED
3. What the LLM ACTUALLY generated
4. The semantic similarity score

This helps you understand if the problem is:
- Data mismatch (LLM can't find the info)
- Format mismatch (LLM answers correctly but in different words)
- Prompt issue (LLM not following instructions)
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
print("RAG DIAGNOSTIC - See What's Wrong")
print("="*70)

# Load improved test dataset
with open('improved_test_dataset.json', 'r') as f:
    test_dataset = json.load(f)

print(f"\nTesting {len(test_dataset)} questions...")
print(f"Collection: test_collection")
print(f"ChromaDB: ../test_chroma_db\n")

# Initialize evaluator
evaluator = RAGEvaluator(
    collection_name="test_collection",
    embedding_model="nomic-embed-text",
    llm_model="llama3.2",
    chroma_persist_dir="../test_chroma_db"
)

print("="*70)
print("DETAILED COMPARISON (Expected vs Actual)")
print("="*70)

scores = []

for i, test_case in enumerate(test_dataset, 1):
    result = evaluator.evaluate_single_query(test_case, top_k=5)
    
    print(f"\n{'='*70}")
    print(f"QUESTION {i}: {result['question']}")
    print('='*70)
    
    print(f"\n✓ EXPECTED ANSWER:")
    print(f"  '{result['expected_answer']}'")
    
    print(f"\n✓ ACTUAL LLM ANSWER:")
    print(f"  '{result['generated_answer']}'")
    
    sim = result['answer_metrics']['semantic_similarity']
    keyword_score = result['answer_metrics']['keyword_match_score']
    
    print(f"\n✓ SCORES:")
    print(f"  Semantic Similarity: {sim:.2%}")
    print(f"  Keyword Match: {keyword_score:.2%}")
    
    # Diagnosis
    print(f"\n✓ DIAGNOSIS:")
    if sim < 0.5:
        print("  ❌ VERY DIFFERENT - LLM answer doesn't match expected")
        if "cannot" in result['generated_answer'].lower() or "don't have" in result['generated_answer'].lower():
            print("  → Problem: LLM can't find the data in context")
            print("  → Solution: Check if test data exists in collection")
        else:
            print("  → Problem: LLM answers in different format")
            print("  → Solution: Update expected answer to match LLM's style")
    elif sim < 0.7:
        print("  ⚠ SOMEWHAT DIFFERENT - Similar meaning, different words")
        print("  → Solution: Adjust expected answer or improve prompt")
    else:
        print("  ✓ GOOD MATCH - Semantically similar")
    
    scores.append(sim)

# Overall summary
avg_score = sum(scores) / len(scores)

print("\n" + "="*70)
print("SUMMARY & RECOMMENDATIONS")
print("="*70)

print(f"\nOverall Query Relevance: {avg_score*100:.1f}%")

if avg_score < 0.5:
    print("\n❌ CRITICAL ISSUES:")
    print("1. CHECK YOUR DATA:")
    print("   → Run: cd ../../ && python vector_store.py")
    print("   → Verify test_collection has Alice, Bob, Charlie data")
    print("\n2. VIEW WHAT'S IN YOUR COLLECTION:")
    print("   → The test questions assume specific data exists")
    print("   → If your collection has different data, questions won't work")
    
elif avg_score < 0.7:
    print("\n⚠ FORMAT MISMATCH:")
    print("1. Your LLM generates different phrasing than expected")
    print("2. QUICK FIX: Update expected answers based on what you see above")
    print("3. Example:")
    print("   If LLM says 'Based on the data, the average age is 30'")
    print("   Change expected from 'The average age is 30 years old'")
    print("   To: 'Based on the data, the average age is 30'")

else:
    print("\n✓ GOOD PERFORMANCE!")
    print("Your RAG system is working well!")

print("\n" + "="*70)
print("NEXT STEPS")
print("="*70)

print("""
Based on the comparison above:

1. If LLM says "I cannot answer" or "I don't have data":
   → Your collection doesn't have the expected data
   → Create new test questions that match YOUR actual data
   
2. If LLM answers correctly but in different words:
   → Update your expected answers to match LLM's style
   → This is NORMAL and easy to fix!
   
3. If similarity is already >70%:
   → Try increasing top_k to 10 or 15
   → Improve chunking format (see improved_chunking.py)
   → Better prompts in ollama_control.py

Want to see what's actually in your collection?
Run: cd ../../ && python query_processor.py
""")
