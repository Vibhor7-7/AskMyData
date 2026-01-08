"""
RAG Evaluation Module

Measures RAG system performance using multiple metrics:
1. Retrieval Quality (Precision@K, Recall@K, MRR)
2. Answer Quality (Semantic similarity, exactness)
3. Latency & Throughput
4. End-to-End Accuracy

Usage:
    evaluator = RAGEvaluator(collection_name="my_collection")
    results = evaluator.run_evaluation(test_dataset)
    evaluator.print_report(results)
"""

import time
import json
import os
import sys
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import pandas as pd

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
rag_dir = os.path.dirname(current_dir)
backend_dir = os.path.dirname(rag_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from rag.query_processor import QueryProcessor
from rag.embeddings import EmbeddingGenerator, cosine_similarity


class RAGEvaluator:
    """
    Comprehensive RAG evaluation framework
    """

    def __init__(
        self,
        collection_name: str,
        embedding_model: str = "nomic-embed-text",
        llm_model: str = "llama3.2",
        chroma_persist_dir: str = "./chroma_db",
    ):
        """
        Initialize evaluator

        Args:
            collection_name: ChromaDB collection to test
            embedding_model: Embedding model name
            llm_model: LLM model name
            chroma_persist_dir: Path to ChromaDB
        """
        self.processor = QueryProcessor(
            collection_name=collection_name,
            embedding_model=embedding_model,
            llm_model=llm_model,
            chroma_persist_dir=chroma_persist_dir,
        )
        self.embedder = EmbeddingGenerator(model_name=embedding_model)
        print("✓ RAG Evaluator initialized")

    def evaluate_retrieval_quality(
        self, question: str, expected_doc_ids: List[str], top_k: int = 5
    ) -> Dict:
        """
        Evaluate retrieval quality metrics

        Metrics:
        - Precision@K: % of retrieved docs that are relevant
        - Recall@K: % of relevant docs that were retrieved
        - MRR (Mean Reciprocal Rank): 1/rank of first relevant doc

        Args:
            question: Query to test
            expected_doc_ids: List of document IDs that should be retrieved
            top_k: Number of documents to retrieve

        Returns:
            Dict with precision, recall, mrr
        """
        # Get embeddings and search
        question_embedding = self.embedder.embed(question)
        search_results = self.processor.vector_store.search(
            query_embedding=question_embedding, top_k=top_k
        )

        retrieved_ids = search_results.get("ids", [])

        # Calculate metrics
        relevant_retrieved = set(retrieved_ids) & set(expected_doc_ids)

        precision = len(relevant_retrieved) / len(retrieved_ids) if retrieved_ids else 0
        recall = len(relevant_retrieved) / len(expected_doc_ids) if expected_doc_ids else 0

        # MRR: Find rank of first relevant document
        mrr = 0
        for rank, doc_id in enumerate(retrieved_ids, 1):
            if doc_id in expected_doc_ids:
                mrr = 1 / rank
                break

        return {
            "precision_at_k": precision,
            "recall_at_k": recall,
            "mrr": mrr,
            "retrieved_count": len(retrieved_ids),
            "relevant_count": len(expected_doc_ids),
            "relevant_retrieved": len(relevant_retrieved),
        }

    def evaluate_answer_quality(
        self,
        question: str,
        generated_answer: str,
        expected_answer: str,
        expected_keywords: Optional[List[str]] = None,
    ) -> Dict:
        """
        Evaluate answer quality using multiple approaches

        Metrics:
        - Semantic Similarity: Cosine similarity between embeddings
        - Keyword Match: % of expected keywords present
        - Exact Match: Boolean for exact string match
        - Length Ratio: Ratio of generated to expected length

        Args:
            question: The question asked
            generated_answer: LLM's generated answer
            expected_answer: Ground truth answer
            expected_keywords: Optional list of keywords that should appear

        Returns:
            Dict with quality metrics
        """
        # Semantic similarity
        gen_embedding = self.embedder.embed(generated_answer.lower())
        exp_embedding = self.embedder.embed(expected_answer.lower())
        semantic_sim = cosine_similarity(gen_embedding, exp_embedding)

        # Exact match
        exact_match = generated_answer.strip().lower() == expected_answer.strip().lower()

        # Keyword matching
        keyword_score = 0
        if expected_keywords:
            gen_lower = generated_answer.lower()
            matched_keywords = [kw for kw in expected_keywords if kw.lower() in gen_lower]
            keyword_score = len(matched_keywords) / len(expected_keywords)

        # Length ratio
        length_ratio = len(generated_answer) / len(expected_answer) if expected_answer else 0

        return {
            "semantic_similarity": semantic_sim,
            "exact_match": exact_match,
            "keyword_match_score": keyword_score,
            "length_ratio": length_ratio,
            "generated_length": len(generated_answer),
            "expected_length": len(expected_answer),
        }

    def evaluate_single_query(
        self, test_case: Dict, top_k: int = 5
    ) -> Dict:
        """
        Evaluate a single test case end-to-end

        Args:
            test_case: Dict with:
                - question: str
                - expected_answer: str
                - expected_keywords: List[str] (optional)
                - expected_doc_ids: List[str] (optional)
                - category: str (optional, e.g., "factual", "aggregation")
            top_k: Number of chunks to retrieve

        Returns:
            Complete evaluation results
        """
        question = test_case["question"]
        expected_answer = test_case["expected_answer"]

        # Measure latency
        start_time = time.time()

        # Run query through RAG pipeline
        result = self.processor.process_query(
            question=question, top_k=top_k, include_metadata=True
        )

        latency = time.time() - start_time

        # Evaluate retrieval quality (if expected docs provided)
        retrieval_metrics = {}
        if "expected_doc_ids" in test_case:
            retrieval_metrics = self.evaluate_retrieval_quality(
                question=question,
                expected_doc_ids=test_case["expected_doc_ids"],
                top_k=top_k,
            )

        # Evaluate answer quality
        answer_metrics = self.evaluate_answer_quality(
            question=question,
            generated_answer=result["answer"],
            expected_answer=expected_answer,
            expected_keywords=test_case.get("expected_keywords"),
        )

        return {
            "question": question,
            "expected_answer": expected_answer,
            "generated_answer": result["answer"],
            "category": test_case.get("category", "general"),
            "success": result["success"],
            "latency_seconds": latency,
            "retrieval_metrics": retrieval_metrics,
            "answer_metrics": answer_metrics,
            "num_chunks_retrieved": result.get("num_chunks_used", 0),
        }

    def run_evaluation(
        self,
        test_dataset: List[Dict],
        top_k: int = 5,
        save_results: bool = True,
        output_dir: str = "./eval_results",
    ) -> Dict:
        """
        Run evaluation on entire test dataset

        Args:
            test_dataset: List of test cases
            top_k: Number of chunks to retrieve
            save_results: Whether to save detailed results to file
            output_dir: Where to save results

        Returns:
            Aggregated evaluation metrics
        """
        print(f"\n{'='*60}")
        print(f"Running RAG Evaluation on {len(test_dataset)} test cases")
        print(f"{'='*60}\n")

        results = []
        start_time = time.time()

        for i, test_case in enumerate(test_dataset, 1):
            print(f"[{i}/{len(test_dataset)}] Evaluating: {test_case['question'][:50]}...")

            eval_result = self.evaluate_single_query(test_case, top_k=top_k)
            results.append(eval_result)

            # Show quick feedback
            sim = eval_result["answer_metrics"]["semantic_similarity"]
            print(f"           Semantic Similarity: {sim:.2%}")

        total_time = time.time() - start_time

        # Aggregate metrics
        aggregated = self._aggregate_results(results, total_time)

        # Save detailed results if requested
        if save_results:
            self._save_results(results, aggregated, output_dir)

        return {"aggregated_metrics": aggregated, "detailed_results": results}

    def _aggregate_results(self, results: List[Dict], total_time: float) -> Dict:
        """Aggregate individual results into overall metrics"""

        if not results:
            return {}

        # Answer quality metrics
        semantic_sims = [r["answer_metrics"]["semantic_similarity"] for r in results]
        keyword_scores = [r["answer_metrics"]["keyword_match_score"] for r in results]
        exact_matches = [r["answer_metrics"]["exact_match"] for r in results]

        # Retrieval metrics (if available)
        retrieval_precisions = []
        retrieval_recalls = []
        mrrs = []

        for r in results:
            if r["retrieval_metrics"]:
                retrieval_precisions.append(r["retrieval_metrics"]["precision_at_k"])
                retrieval_recalls.append(r["retrieval_metrics"]["recall_at_k"])
                mrrs.append(r["retrieval_metrics"]["mrr"])

        # Latency metrics
        latencies = [r["latency_seconds"] for r in results]

        # Success rate
        success_rate = sum(1 for r in results if r["success"]) / len(results)

        # Query relevance score (primary metric - semantic similarity)
        avg_semantic_sim = sum(semantic_sims) / len(semantic_sims)

        aggregated = {
            # Primary Metrics
            "query_relevance_score": avg_semantic_sim,  # Main metric (0-1)
            "query_relevance_percentage": avg_semantic_sim * 100,  # As percentage
            "exact_match_rate": sum(exact_matches) / len(exact_matches),
            "success_rate": success_rate,
            # Answer Quality
            "avg_semantic_similarity": avg_semantic_sim,
            "avg_keyword_match_score": sum(keyword_scores) / len(keyword_scores)
            if keyword_scores
            else 0,
            "semantic_similarity_std": pd.Series(semantic_sims).std(),
            # Retrieval Quality (if available)
            "avg_precision_at_k": sum(retrieval_precisions) / len(retrieval_precisions)
            if retrieval_precisions
            else None,
            "avg_recall_at_k": sum(retrieval_recalls) / len(retrieval_recalls) if retrieval_recalls else None,
            "avg_mrr": sum(mrrs) / len(mrrs) if mrrs else None,
            # Performance
            "avg_latency_seconds": sum(latencies) / len(latencies),
            "median_latency_seconds": pd.Series(latencies).median(),
            "p95_latency_seconds": pd.Series(latencies).quantile(0.95),
            "throughput_queries_per_second": len(results) / total_time,
            # Dataset Info
            "total_queries": len(results),
            "total_time_seconds": total_time,
        }

        return aggregated

    def _save_results(self, results: List[Dict], aggregated: Dict, output_dir: str):
        """Save evaluation results to files"""
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save aggregated metrics
        agg_path = os.path.join(output_dir, f"aggregated_metrics_{timestamp}.json")
        with open(agg_path, "w") as f:
            json.dump(aggregated, f, indent=2)

        # Save detailed results
        detailed_path = os.path.join(output_dir, f"detailed_results_{timestamp}.json")
        with open(detailed_path, "w") as f:
            json.dump(results, f, indent=2)

        # Save CSV for easy analysis
        csv_data = []
        for r in results:
            row = {
                "question": r["question"],
                "category": r["category"],
                "semantic_similarity": r["answer_metrics"]["semantic_similarity"],
                "keyword_match": r["answer_metrics"]["keyword_match_score"],
                "exact_match": r["answer_metrics"]["exact_match"],
                "latency_seconds": r["latency_seconds"],
                "success": r["success"],
            }
            if r["retrieval_metrics"]:
                row.update(
                    {
                        "precision_at_k": r["retrieval_metrics"]["precision_at_k"],
                        "recall_at_k": r["retrieval_metrics"]["recall_at_k"],
                        "mrr": r["retrieval_metrics"]["mrr"],
                    }
                )
            csv_data.append(row)

        df = pd.DataFrame(csv_data)
        csv_path = os.path.join(output_dir, f"results_{timestamp}.csv")
        df.to_csv(csv_path, index=False)

        print(f"\n✓ Results saved to {output_dir}/")
        print(f"  - {os.path.basename(agg_path)}")
        print(f"  - {os.path.basename(detailed_path)}")
        print(f"  - {os.path.basename(csv_path)}")

    def print_report(self, evaluation_results: Dict):
        """Print formatted evaluation report"""
        agg = evaluation_results["aggregated_metrics"]

        print(f"\n{'='*70}")
        print(f"{'RAG SYSTEM EVALUATION REPORT':^70}")
        print(f"{'='*70}\n")

        # Primary Metric (Highlighted)
        print(f"{'PRIMARY METRIC':^70}")
        print(f"{'-'*70}")
        relevance_pct = agg["query_relevance_percentage"]
        status = (
            "✓ EXCELLENT"
            if relevance_pct >= 85
            else "⚠ NEEDS IMPROVEMENT"
            if relevance_pct >= 70
            else "✗ POOR"
        )
        print(f"  Query Relevance Score: {relevance_pct:.1f}%  [{status}]")
        print(f"  (Target: 85%+ for production systems)\n")

        # Answer Quality
        print(f"{'ANSWER QUALITY METRICS':^70}")
        print(f"{'-'*70}")
        print(f"  Semantic Similarity:     {agg['avg_semantic_similarity']:.2%}")
        print(f"  Exact Match Rate:        {agg['exact_match_rate']:.2%}")
        print(f"  Keyword Match Score:     {agg['avg_keyword_match_score']:.2%}")
        print(f"  Success Rate:            {agg['success_rate']:.2%}")
        print(f"  Std Deviation:           {agg['semantic_similarity_std']:.4f}\n")

        # Retrieval Quality
        if agg["avg_precision_at_k"] is not None:
            print(f"{'RETRIEVAL QUALITY METRICS':^70}")
            print(f"{'-'*70}")
            print(f"  Precision@K:             {agg['avg_precision_at_k']:.2%}")
            print(f"  Recall@K:                {agg['avg_recall_at_k']:.2%}")
            print(f"  Mean Reciprocal Rank:    {agg['avg_mrr']:.4f}\n")

        # Performance
        print(f"{'PERFORMANCE METRICS':^70}")
        print(f"{'-'*70}")
        print(f"  Avg Latency:             {agg['avg_latency_seconds']:.3f}s")
        print(f"  Median Latency:          {agg['median_latency_seconds']:.3f}s")
        print(f"  P95 Latency:             {agg['p95_latency_seconds']:.3f}s")
        print(f"  Throughput:              {agg['throughput_queries_per_second']:.2f} queries/sec\n")

        # Dataset Info
        print(f"{'DATASET INFO':^70}")
        print(f"{'-'*70}")
        print(f"  Total Queries:           {agg['total_queries']}")
        print(f"  Total Time:              {agg['total_time_seconds']:.2f}s\n")

        print(f"{'='*70}\n")


def create_sample_test_dataset() -> List[Dict]:
    """
    Create a sample test dataset for demonstration

    Returns:
        List of test cases
    """
    return [
        {
            "question": "What is the average age?",
            "expected_answer": "30",
            "expected_keywords": ["30", "average", "age"],
            "category": "aggregation",
        },
        {
            "question": "Who lives in New York City?",
            "expected_answer": "Alice lives in New York City",
            "expected_keywords": ["Alice", "NYC", "New York"],
            "category": "factual",
        },
        {
            "question": "List all cities mentioned",
            "expected_answer": "NYC, LA, Chicago",
            "expected_keywords": ["NYC", "LA", "Chicago"],
            "category": "enumeration",
        },
        {
            "question": "Who is the oldest person?",
            "expected_answer": "Charlie is the oldest at 35 years old",
            "expected_keywords": ["Charlie", "35", "oldest"],
            "category": "comparison",
        },
        {
            "question": "How many people are there?",
            "expected_answer": "3",
            "expected_keywords": ["3", "three"],
            "category": "counting",
        }
    ]


def main():
    """
    Example usage of RAG evaluator
    """
    # Initialize evaluator
    evaluator = RAGEvaluator(
        collection_name="test_collection",
        chroma_persist_dir="./test_chroma_db",
    )

    # Create or load test dataset
    test_dataset = create_sample_test_dataset()

    # You can also load from JSON file:
    # with open('test_dataset.json', 'r') as f:
    #     test_dataset = json.load(f)

    # Run evaluation
    results = evaluator.run_evaluation(
        test_dataset=test_dataset, top_k=5, save_results=True, output_dir="./eval_results"
    )

    # Print report
    evaluator.print_report(results)

    # Access specific metrics
    relevance_score = results["aggregated_metrics"]["query_relevance_percentage"]
    print(
        f"\n🎯 Achieved {relevance_score:.1f}% query relevance on test set of {len(test_dataset)} questions"
    )


if __name__ == "__main__":
    main()

