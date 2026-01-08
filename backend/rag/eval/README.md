# RAG Evaluation System - Usage Guide

## ✓ Setup Complete!

The evaluation system is now working. You just ran your first evaluation and got **78.6% query relevance**.

## Quick Start

### 1. Simple Test (What you just ran)
```bash
cd backend/rag/eval
python simple_test.py
```

### 2. Interactive Examples
```bash
python run_eval.py
# Choose from menu options
```

### 3. Custom Test Dataset
```bash
# Create interactively
python create_test_dataset.py --interactive

# Or from text file
python create_test_dataset.py --from-file questions.txt
```

## Understanding Your Results

### Primary Metric: Query Relevance Score
- **85%+** = Production ready ✓
- **70-85%** = Good, needs tuning ⚠
- **<70%** = Needs improvement ✗

Your current score: **78.6%** - Good start!

### Improving Your Score

#### 1. Better Test Cases
Create test cases that match your actual data:
```json
[
  {
    "question": "What is the total revenue in Q1?",
    "expected_answer": "$45,000",
    "expected_keywords": ["45000", "45,000", "Q1", "revenue"],
    "category": "aggregation"
  }
]
```

#### 2. Optimize Chunking
Edit [chunking_module.py](../chunking_module.py):
- Adjust chunk size
- Improve text formatting
- Add more context

#### 3. Tune Retrieval
In your evaluation calls:
```python
results = evaluator.run_evaluation(
    test_dataset=test_dataset,
    top_k=10,  # Try 3, 5, 10, 15
    save_results=True
)
```

#### 4. Try Different Models
```python
evaluator = RAGEvaluator(
    collection_name="test_collection",
    llm_model="mistral",  # or llama3.2, gemma, etc.
)
```

## Evaluating Your Real Data

### Step 1: Upload a file
```bash
# Via your API
curl -X POST http://localhost:5000/api/files/upload \
  -F "file=@your_data.csv"
```

### Step 2: Note the collection name
The API response includes a `collection_name` like `avocado_20251222_193628`

### Step 3: Create test cases for your data
```python
test_dataset = [
    {
        'question': 'How many rows are in the avocado dataset?',
        'expected_answer': '18249 rows',
        'expected_keywords': ['18249', 'rows'],
        'category': 'counting'
    },
    {
        'question': 'What is the average price?',
        'expected_answer': '$1.40',
        'expected_keywords': ['1.40', 'average', 'price'],
        'category': 'aggregation'
    }
    # Add more specific to your data
]
```

### Step 4: Run evaluation
```python
from rag.eval.eval_metrics import RAGEvaluator

evaluator = RAGEvaluator(
    collection_name="avocado_20251222_193628",  # Your collection
    chroma_persist_dir="../chroma_db"  # Your actual DB
)

results = evaluator.run_evaluation(test_dataset)
evaluator.print_report(results)
```

## Files Created

- `eval_metrics.py` - Main evaluation framework
- `run_eval.py` - Interactive examples
- `simple_test.py` - Quick test script
- `create_test_dataset.py` - Dataset creator
- `QUICKSTART.py` - Minimal working example

## Output Files

After each evaluation, check `./eval_results/`:
- `aggregated_metrics_*.json` - Summary statistics
- `detailed_results_*.json` - Per-question details
- `results_*.csv` - Spreadsheet for analysis

## Common Issues

### "Collection not found"
```bash
# Create test data first
cd ../
python vector_store.py
```

### "Ollama not running"
```bash
ollama serve
# In another terminal:
ollama pull nomic-embed-text
ollama pull llama3.2
```

### Low relevance scores
1. Check if test cases match your data
2. Increase `top_k` parameter
3. Improve chunking strategy
4. Use better expected answers

## Next Steps

1. **Create 20-30 test cases** covering your main use cases
2. **Run baseline evaluation** to measure current performance
3. **Optimize one thing at a time**:
   - Chunking strategy
   - Retrieval parameters
   - Prompt engineering
   - Model selection
4. **Re-evaluate** after each change
5. **Track progress** over time

## Example Workflow

```bash
# 1. Create test dataset
python create_test_dataset.py --interactive
# Save as my_tests.json

# 2. Run baseline evaluation
python -c "
from rag.eval.eval_metrics import RAGEvaluator
import json

with open('my_tests.json') as f:
    tests = json.load(f)

evaluator = RAGEvaluator(
    collection_name='your_collection',
    chroma_persist_dir='../chroma_db'
)

results = evaluator.run_evaluation(tests)
evaluator.print_report(results)
"

# 3. Make improvements to your RAG system

# 4. Re-evaluate and compare
# Repeat until you reach 85%+
```

## Metrics Reference

| Metric | Description | Good Value |
|--------|-------------|-----------|
| Query Relevance | Overall answer quality | 85%+ |
| Semantic Similarity | Answer matches expected | 80%+ |
| Keyword Match | Contains key terms | 70%+ |
| Exact Match | Perfect matches | Variable |
| Success Rate | Queries that worked | 95%+ |
| Avg Latency | Response time | <2s |
| Precision@K | Retrieval accuracy | 60%+ |
| Recall@K | Retrieval coverage | 70%+ |

## Support

Your evaluation system is ready! Start with the simple test, then create custom test cases for your specific data.

Goal: **Achieve 85%+ query relevance on 100 question-answer pairs** ✨
