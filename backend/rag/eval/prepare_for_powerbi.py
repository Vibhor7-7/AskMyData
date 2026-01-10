# backend/rag/eval/prepare_for_powerbi.py

"""
Prepare RAG Evaluation Results for Power BI Dashboard

Consolidates all evaluation runs into Power BI-ready formats:
1. Time series data (tracking improvements)
2. Category performance analysis
3. Model comparison data
4. Question-level details
"""

import json
import os
import pandas as pd
from datetime import datetime
import glob

def consolidate_all_results(eval_results_dir='./eval_results'):
    """
    Consolidate all evaluation results into a single dataset
    
    Creates:
    - powerbi_time_series.csv: Metrics over time
    - powerbi_questions.csv: Individual question performance
    - powerbi_summary.csv: Latest metrics summary
    """
    
    print("\n" + "="*70)
    print("PREPARING DATA FOR POWER BI DASHBOARD")
    print("="*70 + "\n")
    
    # Find all result files
    agg_files = sorted(glob.glob(os.path.join(eval_results_dir, 'aggregated_metrics_*.json')))
    detail_files = sorted(glob.glob(os.path.join(eval_results_dir, 'detailed_results_*.json')))
    csv_files = sorted(glob.glob(os.path.join(eval_results_dir, 'results_*.csv')))
    
    print(f"Found {len(agg_files)} evaluation runs\n")
    
    if len(agg_files) == 0:
        print("❌ No evaluation results found!")
        print("\nTo generate evaluation results:")
        print("  cd /Users/sharvibhor/Desktop/Projects/AskMyData-1/backend/rag/eval")
        print("  python3 simple_test.py")
        print("  # or")
        print("  python3 run_eval.py\n")
        return None
    
    # ========================================================================
    # 1. TIME SERIES DATA (Metrics Over Time)
    # ========================================================================
    
    time_series_data = []
    
    for agg_file in agg_files:
        # Extract timestamp from filename
        timestamp_str = os.path.basename(agg_file).replace('aggregated_metrics_', '').replace('.json', '')
        
        try:
            timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
        except:
            timestamp = datetime.now()
        
        with open(agg_file, 'r') as f:
            metrics = json.load(f)
        
        # Create row for time series
        row = {
            'timestamp': timestamp,
            'date': timestamp.date(),
            'time': timestamp.time(),
            'run_id': timestamp_str,
            'query_relevance_pct': metrics.get('query_relevance_percentage', 0),
            'semantic_similarity': metrics.get('avg_semantic_similarity', 0),
            'exact_match_rate': metrics.get('exact_match_rate', 0),
            'keyword_match_score': metrics.get('avg_keyword_match_score', 0),
            'success_rate': metrics.get('success_rate', 0),
            'avg_latency_ms': metrics.get('avg_latency_seconds', 0) * 1000,
            'median_latency_ms': metrics.get('median_latency_seconds', 0) * 1000,
            'p95_latency_ms': metrics.get('p95_latency_seconds', 0) * 1000,
            'throughput_qps': metrics.get('throughput_queries_per_second', 0),
            'total_queries': metrics.get('total_queries', 0),
            'total_time_seconds': metrics.get('total_time_seconds', 0)
        }
        
        time_series_data.append(row)
    
    df_time_series = pd.DataFrame(time_series_data)
    
    # Only sort if we have data
    if len(df_time_series) > 0:
        df_time_series = df_time_series.sort_values('timestamp')
    else:
        print("⚠ Warning: No time series data created")
        return None
    
    output_file = os.path.join(eval_results_dir, 'powerbi_time_series.csv')
    df_time_series.to_csv(output_file, index=False)
    print(f"✓ Created {output_file}")
    print(f"  Columns: {list(df_time_series.columns)}")
    print(f"  Rows: {len(df_time_series)}\n")
    
    # ========================================================================
    # 2. QUESTION-LEVEL PERFORMANCE
    # ========================================================================
    
    all_questions = []
    
    for detail_file in detail_files:
        # Extract timestamp
        timestamp_str = os.path.basename(detail_file).replace('detailed_results_', '').replace('.json', '')
        
        try:
            timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
        except:
            timestamp = datetime.now()
        
        with open(detail_file, 'r') as f:
            details = json.load(f)
        
        for result in details:
            row = {
                'timestamp': timestamp,
                'run_id': timestamp_str,
                'question': result.get('question', ''),
                'category': result.get('category', 'unknown'),
                'expected_answer': result.get('expected_answer', ''),
                'generated_answer': result.get('generated_answer', ''),
                'semantic_similarity': result.get('answer_metrics', {}).get('semantic_similarity', 0),
                'keyword_match_score': result.get('answer_metrics', {}).get('keyword_match_score', 0),
                'exact_match': result.get('answer_metrics', {}).get('exact_match', False),
                'latency_ms': result.get('latency_seconds', 0) * 1000,
                'success': result.get('success', False),
                'num_chunks_retrieved': result.get('num_chunks_retrieved', 0)
            }
            all_questions.append(row)
    
    df_questions = pd.DataFrame(all_questions)
    
    output_file = os.path.join(eval_results_dir, 'powerbi_questions.csv')
    df_questions.to_csv(output_file, index=False)
    print(f"✓ Created {output_file}")
    print(f"  Columns: {list(df_questions.columns)}")
    print(f"  Rows: {len(df_questions)}\n")
    
    # ========================================================================
    # 3. CATEGORY PERFORMANCE ANALYSIS
    # ========================================================================
    
    category_stats = df_questions.groupby(['run_id', 'category']).agg({
        'semantic_similarity': ['mean', 'std', 'min', 'max', 'count'],
        'keyword_match_score': 'mean',
        'exact_match': lambda x: x.sum() / len(x),  # exact match rate
        'latency_ms': 'mean',
        'success': lambda x: x.sum() / len(x)  # success rate
    }).reset_index()
    
    # Flatten column names
    category_stats.columns = [
        'run_id', 'category',
        'avg_semantic_similarity', 'std_semantic_similarity', 
        'min_semantic_similarity', 'max_semantic_similarity', 'question_count',
        'avg_keyword_match', 'exact_match_rate', 'avg_latency_ms', 'success_rate'
    ]
    
    output_file = os.path.join(eval_results_dir, 'powerbi_category_performance.csv')
    category_stats.to_csv(output_file, index=False)
    print(f"✓ Created {output_file}")
    print(f"  Columns: {list(category_stats.columns)}")
    print(f"  Rows: {len(category_stats)}\n")
    
    # ========================================================================
    # 4. SUMMARY (Latest Run)
    # ========================================================================
    
    if len(df_time_series) > 0:
        latest = df_time_series.iloc[-1].to_dict()
        
        summary = {
            'metric': [
                'Query Relevance Score',
                'Semantic Similarity',
                'Exact Match Rate',
                'Keyword Match Score',
                'Success Rate',
                'Average Latency (ms)',
                'Median Latency (ms)',
                'P95 Latency (ms)',
                'Throughput (queries/sec)',
                'Total Queries'
            ],
            'value': [
                latest['query_relevance_pct'],
                latest['semantic_similarity'] * 100,
                latest['exact_match_rate'] * 100,
                latest['keyword_match_score'] * 100,
                latest['success_rate'] * 100,
                latest['avg_latency_ms'],
                latest['median_latency_ms'],
                latest['p95_latency_ms'],
                latest['throughput_qps'],
                latest['total_queries']
            ],
            'unit': ['%', '%', '%', '%', '%', 'ms', 'ms', 'ms', 'qps', 'count'],
            'target': [85, 85, 50, 80, 95, 2000, 1000, 3000, 1, None],
            'status': []
        }
        
        # Calculate status (met target or not)
        for i, val in enumerate(summary['value']):
            target = summary['target'][i]
            if target is None:
                summary['status'].append('N/A')
            elif summary['unit'][i] == 'ms':
                # Lower is better for latency
                summary['status'].append('✓ Good' if val <= target else '⚠ Needs Work')
            else:
                # Higher is better for everything else
                summary['status'].append('✓ Good' if val >= target else '⚠ Needs Work')
        
        df_summary = pd.DataFrame(summary)
        
        output_file = os.path.join(eval_results_dir, 'powerbi_summary.csv')
        df_summary.to_csv(output_file, index=False)
        print(f"✓ Created {output_file}")
        print(f"  Columns: {list(df_summary.columns)}")
        print(f"  Rows: {len(df_summary)}\n")
    
    # ========================================================================
    # 5. MODEL COMPARISON (if multiple models tested)
    # ========================================================================
    
    # Check if there are different models in the data (future enhancement)
    # For now, just show improvements over time
    
    if len(df_time_series) > 1:
        improvements = []
        for i in range(1, len(df_time_series)):
            prev = df_time_series.iloc[i-1]
            curr = df_time_series.iloc[i]
            
            improvements.append({
                'from_run': prev['run_id'],
                'to_run': curr['run_id'],
                'query_relevance_change': curr['query_relevance_pct'] - prev['query_relevance_pct'],
                'semantic_similarity_change': curr['semantic_similarity'] - prev['semantic_similarity'],
                'latency_change_ms': curr['avg_latency_ms'] - prev['avg_latency_ms'],
                'throughput_change': curr['throughput_qps'] - prev['throughput_qps']
            })
        
        df_improvements = pd.DataFrame(improvements)
        output_file = os.path.join(eval_results_dir, 'powerbi_improvements.csv')
        df_improvements.to_csv(output_file, index=False)
        print(f"✓ Created {output_file}")
        print(f"  Tracks improvements between consecutive runs\n")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    
    print("="*70)
    print("POWER BI PREPARATION COMPLETE")
    print("="*70 + "\n")
    
    print("Files created in eval_results/:")
    print("  1. powerbi_time_series.csv      - Metrics over time (line charts)")
    print("  2. powerbi_questions.csv         - Individual questions (drill-down)")
    print("  3. powerbi_category_performance.csv - By category (bar charts)")
    print("  4. powerbi_summary.csv           - Latest metrics (KPI cards)")
    if len(df_time_series) > 1:
        print("  5. powerbi_improvements.csv      - Run-to-run changes\n")
    
    print("\nNext Steps:")
    print("  1. Open Power BI Desktop")
    print("  2. Get Data → Text/CSV → Load these files")
    print("  3. Create relationships if needed")
    print("  4. Build visuals using the template below\n")
    
    return {
        'time_series': df_time_series,
        'questions': df_questions,
        'category_performance': category_stats,
        'summary': df_summary if len(df_time_series) > 0 else None
    }


def print_powerbi_template():
    """Print a Power BI dashboard layout template"""
    
    print("\n" + "="*70)
    print("RECOMMENDED POWER BI DASHBOARD LAYOUT")
    print("="*70 + "\n")
    
    template = """
┌─────────────────────────────────────────────────────────────────────┐
│                      RAG SYSTEM PERFORMANCE DASHBOARD                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────┐ │
│  │Query Relevance│  │ Exact Match  │  │Avg Latency   │  │Success  │ │
│  │    96.8%     │  │    60.0%     │  │   571ms      │  │  100%   │ │
│  │  [KPI CARD]  │  │  [KPI CARD]  │  │  [KPI CARD]  │  │[CARD]   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────┘ │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  Query Relevance Over Time [LINE CHART]                         │ │
│  │  X: timestamp, Y: query_relevance_pct                           │ │
│  │  Add trend line to show improvement                             │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌──────────────────────────────┐  ┌─────────────────────────────┐ │
│  │ Performance by Category      │  │ Latency Distribution        │ │
│  │ [BAR CHART]                  │  │ [HISTOGRAM]                 │ │
│  │ X: category                  │  │ X: latency_ms bins          │ │
│  │ Y: avg_semantic_similarity   │  │ Y: count                    │ │
│  └──────────────────────────────┘  └─────────────────────────────┘ │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  Question Details [TABLE]                                       │ │
│  │  Columns: question, category, semantic_similarity, latency_ms   │ │
│  │  Filter: Allow drill-down by category                           │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  Filters: [Date Range] [Category] [Min Similarity]                  │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
"""
    
    print(template)
    
    print("\nKEY VISUALS TO CREATE:\n")
    
    visuals = [
        ("1. KPI Cards", [
            "Query Relevance Score (powerbi_summary.csv)",
            "Exact Match Rate (powerbi_summary.csv)",
            "Average Latency (powerbi_summary.csv)",
            "Success Rate (powerbi_summary.csv)"
        ]),
        ("2. Line Charts", [
            "Query Relevance Over Time (powerbi_time_series.csv)",
            "Latency Trends (powerbi_time_series.csv)",
            "Throughput Over Time (powerbi_time_series.csv)"
        ]),
        ("3. Bar Charts", [
            "Performance by Category (powerbi_category_performance.csv)",
            "Question Count by Category (powerbi_questions.csv)"
        ]),
        ("4. Scatter Plots", [
            "Semantic Similarity vs Latency (powerbi_questions.csv)",
            "Keyword Match vs Semantic Similarity (powerbi_questions.csv)"
        ]),
        ("5. Tables", [
            "Top 10 Best Performing Questions (powerbi_questions.csv)",
            "Bottom 10 Questions Needing Improvement (powerbi_questions.csv)"
        ]),
        ("6. Gauges", [
            "Query Relevance vs 85% Target",
            "Success Rate vs 95% Target"
        ])
    ]
    
    for title, items in visuals:
        print(f"\n{title}:")
        for item in items:
            print(f"  • {item}")
    
    print("\n" + "="*70 + "\n")


def create_powerbi_dax_measures():
    """Generate DAX measures for Power BI"""
    
    dax_measures = """
-- DAX MEASURES FOR POWER BI --

-- 1. Average Query Relevance
Avg Query Relevance = AVERAGE(time_series[query_relevance_pct])

-- 2. Target Achievement (85%)
Target Achievement = 
    IF(
        AVERAGE(time_series[query_relevance_pct]) >= 85,
        "✓ Met",
        "✗ Not Met"
    )

-- 3. Improvement from First Run
Improvement = 
    VAR FirstRun = CALCULATE(
        AVERAGE(time_series[query_relevance_pct]),
        time_series[timestamp] = MIN(time_series[timestamp])
    )
    VAR CurrentRun = AVERAGE(time_series[query_relevance_pct])
    RETURN CurrentRun - FirstRun

-- 4. Questions Passing Threshold (70%+)
Questions Passing = 
    CALCULATE(
        COUNTROWS(questions),
        questions[semantic_similarity] >= 0.7
    )

-- 5. Average Latency (Latest Run)
Latest Avg Latency = 
    CALCULATE(
        AVERAGE(time_series[avg_latency_ms]),
        time_series[timestamp] = MAX(time_series[timestamp])
    )

-- 6. Category Performance Color
Category Color = 
    SWITCH(
        TRUE(),
        AVERAGE(category_performance[avg_semantic_similarity]) >= 0.85, "Green",
        AVERAGE(category_performance[avg_semantic_similarity]) >= 0.70, "Yellow",
        "Red"
    )

-- 7. Total Test Cases
Total Questions = COUNTROWS(questions)

-- 8. Success Rate %
Success Rate % = 
    DIVIDE(
        CALCULATE(COUNTROWS(questions), questions[success] = TRUE),
        COUNTROWS(questions)
    ) * 100
"""
    
    output_file = './eval_results/powerbi_dax_measures.txt'
    with open(output_file, 'w') as f:
        f.write(dax_measures)
    
    print(f"\n✓ Created {output_file}")
    print("  Copy these DAX measures into Power BI for calculated fields\n")
    
    return dax_measures


def main():
    """Main function"""
    
    # Consolidate all results
    data = consolidate_all_results()
    
    if data is None:
        print("\n❌ Cannot proceed without evaluation results")
        print("Run some evaluations first, then try again.\n")
        return
    
    # Print Power BI template
    print_powerbi_template()
    
    # Create DAX measures
    create_powerbi_dax_measures()
    
    print("\n🎉 All Power BI files ready!")
    print("\nQuick Start:")
    print("  1. Open Power BI Desktop")
    print("  2. Get Data → Text/CSV")
    print("  3. Load: powerbi_time_series.csv")
    print("  4. Load: powerbi_questions.csv")
    print("  5. Load: powerbi_summary.csv")
    print("  6. Create visuals as shown in template above")
    print("  7. Save as 'RAG_Performance_Dashboard.pbix'\n")


if __name__ == "__main__":
    main()