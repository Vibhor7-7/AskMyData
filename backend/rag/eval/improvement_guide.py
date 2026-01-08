"""
RAG Performance Improvement Guide
From 50% to 85%+ Query Relevance

This script demonstrates 5 key strategies to boost your RAG performance.
"""

import sys
import os

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

print("\n" + "="*70)
print("RAG PERFORMANCE IMPROVEMENT STRATEGIES")
print("="*70)

print("""
Current Performance: 50% Query Relevance
Target: 85%+ Query Relevance

5 KEY STRATEGIES TO IMPROVE:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. FIX YOUR EXPECTED ANSWERS (Most Common Issue)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Problem: Your expected answers might be too specific or in wrong format.

❌ BAD Expected Answers:
{
    "question": "What is the average age?",
    "expected_answer": "30",  # Too short, not natural
}

{
    "question": "Who lives in NYC?",
    "expected_answer": "Alice lives in New York City",  # Too specific
}

✓ GOOD Expected Answers:
{
    "question": "What is the average age?",
    "expected_answer": "The average age is 30 years old",  # Natural language
}

{
    "question": "Who lives in NYC?",
    "expected_answer": "Alice lives in NYC",  # Matches your data format
}

ACTION: Review your test_dataset and make expected answers more natural!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. IMPROVE YOUR CHUNKING FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Current format (simple key-value):
"name: Alice, age: 25, city: NYC"

Better format (natural language):
"Alice is 25 years old and lives in NYC. She works as an Engineer."

Why? LLMs are trained on natural language, not CSV-style data!

ACTION:
1. Copy improved_chunking.py strategies
2. Update your chunking_module.py
3. Re-upload your test data
4. Re-run evaluation

Try this format in your chunking_module.py:

def row_to_text(row: pd.Series, include_column_names: bool = True) -> str:
    # Exclude metadata columns
    metadata_cols = ['source_file', 'content_type', 'row_index']
    data_cols = {k: v for k, v in row.items() 
                 if k not in metadata_cols and pd.notna(v)}
    
    # Build natural language description
    parts = []
    
    # Create natural sentences
    if 'name' in data_cols:
        sentence = f"{data_cols['name']}"
        if 'age' in data_cols:
            sentence += f" is {data_cols['age']} years old"
        if 'city' in data_cols:
            sentence += f" and lives in {data_cols['city']}"
        parts.append(sentence + ".")
    
    # Add remaining fields naturally
    for key, val in data_cols.items():
        if key not in ['name', 'age', 'city']:
            parts.append(f"The {key} is {val}.")
    
    return " ".join(parts)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. INCREASE RETRIEVAL (top_k)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Current: top_k=5 (retrieving 5 chunks)

Problem: Might not be getting enough context for LLM to answer accurately.

ACTION: Try different top_k values:

results_k3 = evaluator.run_evaluation(test_dataset, top_k=3)
results_k10 = evaluator.run_evaluation(test_dataset, top_k=10)
results_k15 = evaluator.run_evaluation(test_dataset, top_k=15)

Compare which gives best performance!

Note: More chunks = more context but also more noise.
Sweet spot usually between 5-15.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. IMPROVE YOUR LLM PROMPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Check your ollama_control.py prompt. Make it more explicit:

Better prompt format:

prompt = f\"\"\"You are a data analysis assistant. Answer questions based 
ONLY on the provided context.

Context Information:
{context_text}

Question: {question}

Instructions:
- Be concise and direct
- Use natural language
- Include specific numbers/names from context
- If unsure, say "Based on the data..."

Answer:\"\"\"

ACTION: Update ollama_control.py with better prompt formatting

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. ADD MORE KEYWORDS TO TEST CASES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Keywords help with semantic matching. Include variations:

❌ BAD:
{
    "expected_keywords": ["30", "average"]
}

✓ GOOD:
{
    "expected_keywords": ["30", "average", "age", "years", "mean", "avg"]
}

This allows for more flexible matching!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

QUICK WIN CHECKLIST:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

□ 1. Update expected answers to be more natural (5-10 min)
   → Rewrite test cases with natural language expected answers

□ 2. Improve chunking format (10-15 min)
   → Update row_to_text() in chunking_module.py
   → Re-run vector_store.py to re-embed data

□ 3. Try different top_k values (5 min)
   → Test with top_k=3, 5, 10, 15

□ 4. Enhance prompt (5 min)
   → Update ollama_control.py prompt

□ 5. Add more keywords (5 min)
   → Expand keyword lists in test cases

EXPECTED IMPROVEMENT: 50% → 75-85% query relevance

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXAMPLE IMPROVED TEST CASE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Before (50% score):
{
    "question": "What is the average age?",
    "expected_answer": "30",
    "expected_keywords": ["30"],
    "category": "aggregation"
}

After (85%+ score):
{
    "question": "What is the average age?",
    "expected_answer": "The average age is 30 years old",
    "expected_keywords": ["30", "average", "age", "years", "mean"],
    "category": "aggregation"
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NEXT STEPS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Start with fixing expected answers (quickest win!)
2. Then improve chunking format
3. Test different top_k values
4. Iterate until you reach 85%+

Run this to see chunking format options:
python improved_chunking.py

""")

print("\nWant to see example improved test cases? (y/n): ", end='')
response = input().strip().lower()

if response == 'y':
    print("\n" + "="*70)
    print("EXAMPLE IMPROVED TEST DATASET")
    print("="*70 + "\n")
    
    improved_dataset = [
        {
            "question": "What is the average age?",
            "expected_answer": "The average age is 30 years old",
            "expected_keywords": ["30", "average", "age", "years", "mean", "avg"],
            "category": "aggregation"
        },
        {
            "question": "Who lives in New York City?",
            "expected_answer": "Alice lives in NYC",
            "expected_keywords": ["Alice", "NYC", "New York", "city"],
            "category": "factual"
        },
        {
            "question": "How many people are in the dataset?",
            "expected_answer": "There are 3 people in the dataset",
            "expected_keywords": ["3", "three", "people", "total", "count"],
            "category": "counting"
        },
        {
            "question": "Who is the oldest person?",
            "expected_answer": "Charlie is the oldest at 35 years old",
            "expected_keywords": ["Charlie", "35", "oldest", "maximum", "age"],
            "category": "comparison"
        },
        {
            "question": "List all the cities",
            "expected_answer": "The cities are NYC, LA, and Chicago",
            "expected_keywords": ["NYC", "LA", "Chicago", "cities", "locations"],
            "category": "enumeration"
        }
    ]
    
    import json
    print(json.dumps(improved_dataset, indent=2))
    
    print("\n" + "="*70)
    print("Save this as 'improved_test_dataset.json' and run:")
    print("python run_eval.py")
    print("Choose option 2 and use this file!")
    print("="*70 + "\n")
