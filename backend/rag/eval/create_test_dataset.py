# backend/rag/create_test_dataset.py

"""
Helper script to create and manage test datasets for RAG evaluation

Usage:
    python create_test_dataset.py --interactive
    python create_test_dataset.py --from-file questions.txt
"""

import json
import argparse
from typing import List, Dict

def create_test_case_interactive() -> Dict:
    """Interactive CLI to create a test case"""
    print("\n" + "="*50)
    print("Create New Test Case")
    print("="*50)
    
    question = input("\nQuestion: ").strip()
    expected_answer = input("Expected Answer: ").strip()
    keywords = input("Expected Keywords (comma-separated): ").strip()
    category = input("Category (factual/aggregation/counting/comparison/enumeration): ").strip()
    difficulty = input("Difficulty (easy/medium/hard): ").strip()
    
    test_case = {
        "question": question,
        "expected_answer": expected_answer,
        "expected_keywords": [kw.strip() for kw in keywords.split(',') if kw.strip()],
        "category": category or "general",
        "difficulty": difficulty or "medium"
    }
    
    return test_case

def create_dataset_interactive(output_file: str = "test_dataset.json"):
    """Create a test dataset interactively"""
    dataset = []
    
    print("\n" + "="*50)
    print("RAG Test Dataset Creator")
    print("="*50)
    print("\nPress Ctrl+C to finish and save\n")
    
    try:
        while True:
            test_case = create_test_case_interactive()
            dataset.append(test_case)
            print(f"\n✓ Added test case #{len(dataset)}")
            
            continue_prompt = input("\nAdd another? (y/n): ").strip().lower()
            if continue_prompt != 'y':
                break
    except KeyboardInterrupt:
        print("\n\nSaving dataset...")
    
    # Save to file
    with open(output_file, 'w') as f:
        json.dump(dataset, f, indent=2)
    
    print(f"\n✓ Saved {len(dataset)} test cases to {output_file}")
    return dataset

def load_from_file(input_file: str, output_file: str = "test_dataset.json"):
    """
    Load questions from a text file and create test dataset
    
    Expected format:
        Q: What is the total?
        A: $500
        K: 500, total
        C: aggregation
        ---
    """
    dataset = []
    
    with open(input_file, 'r') as f:
        content = f.read()
    
    # Parse entries separated by ---
    entries = content.split('---')
    
    for entry in entries:
        lines = [line.strip() for line in entry.strip().split('\n') if line.strip()]
        if not lines:
            continue
        
        test_case = {}
        for line in lines:
            if line.startswith('Q:'):
                test_case['question'] = line[2:].strip()
            elif line.startswith('A:'):
                test_case['expected_answer'] = line[2:].strip()
            elif line.startswith('K:'):
                keywords = line[2:].strip()
                test_case['expected_keywords'] = [kw.strip() for kw in keywords.split(',')]
            elif line.startswith('C:'):
                test_case['category'] = line[2:].strip()
        
        if 'question' in test_case and 'expected_answer' in test_case:
            dataset.append(test_case)
    
    # Save to JSON
    with open(output_file, 'w') as f:
        json.dump(dataset, f, indent=2)
    
    print(f"✓ Created {len(dataset)} test cases from {input_file}")
    print(f"✓ Saved to {output_file}")
    
    return dataset

def main():
    parser = argparse.ArgumentParser(description='Create RAG test datasets')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('--from-file', type=str, help='Load from text file')
    parser.add_argument('--output', type=str, default='test_dataset.json', help='Output file')
    
    args = parser.parse_args()
    
    if args.interactive:
        create_dataset_interactive(args.output)
    elif args.from_file:
        load_from_file(args.from_file, args.output)
    else:
        print("Please specify --interactive or --from-file")
        print("\nExample usage:")
        print("  python create_test_dataset.py --interactive")
        print("  python create_test_dataset.py --from-file questions.txt")

if __name__ == "__main__":
    main()