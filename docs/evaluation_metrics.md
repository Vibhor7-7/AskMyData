# RAG System Evaluation Guide

## Overview

Comprehensive evaluation framework to measure RAG system performance with industry-standard metrics.

## Key Metrics

### Primary Metric: Query Relevance Score
- **Target: 85%+** for production systems
- Measures semantic similarity between generated and expected answers
- Range: 0-100%

### Answer Quality Metrics
- **Semantic Similarity**: Cosine similarity of answer embeddings
- **Exact Match Rate**: Percentage of perfect matches
- **Keyword Match Score**: Coverage of expected keywords
- **Success Rate**: Queries that returned valid answers

### Retrieval Quality Metrics
- **Precision@K**: Accuracy of retrieved documents
- **Recall@K**: Coverage of relevant documents
- **MRR**: Mean Reciprocal Rank of first relevant document

### Performance Metrics
- **Latency**: Average, median, P95 response times
- **Throughput**: Queries per second

## Quick Start

### 1. Create Test Dataset

```python
from rag.create_test_dataset import create_dataset_interactive

# Interactive creation
dataset = create_dataset_interactive('my_test_dataset.json')