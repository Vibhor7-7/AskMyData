"""
Chunking Module - Convert DataFrames to text chunks for RAG

What is chunking?
- Breaking data into small, digestible pieces
- Each chunk = one piece of context for the LLM
- Too small = not enough context
- Too big = exceeds LLM context window

For tabular data: 1 row = 1 chunk works well
"""

import pandas as pd 
from typing import List, Dict 
import tiktoken 

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Count the number of tokens in a given text for a specified model."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def row_to_text(row:pd.Series, include_column_names:bool =True) -> str:
    """Convert a single DataFrame row to readable text"""
    if include_column_names:
        parts = [f"{col}: {val}" for col, val in row.items()]
        return ", ".join(parts)
    else: 
        return ", ".join(str(val) for val in row.values)
    
def dataframe_to_chunks(
        df:pd.DataFrame,
        chunk_strategy: str = "row",
        max_tokens: int = 512
) -> List[Dict[str, any]]: 
     """
    Convert entire DataFrame to list of text chunks with metadata
    
    Chunk strategies:
    - 'row': One row = one chunk (best for tabular data)
    - 'grouped': Multiple rows combined into larger chunks (future)
    
    Args:
        df: Input DataFrame (already standardized)
        chunk_strategy: How to split data into chunks
        max_tokens: Maximum tokens per chunk
    
    Returns:
        List of dicts, each containing:
        {
            'text': "name: John, age: 30...",
            'metadata': {
                'source_file': 'data.csv',
                'row_index': 0,
                'chunk_id': 'data.csv_0'
            }
        }
    """
     chunks = []

     if chunk_strategy == "row": 
         for idx, row in df.iterrows():
            #convert the row to text
            text = row_to_text(row)
             #count tokens 
            token_count = count_tokens(text)

            if token_count>max_tokens: 
                print(f"Row {idx} exceeds max tokens ({token_count})")
                

            # Extract metadata from standardized columns
            source_file = row.get('source_file', 'unknown')
            content_type = row.get('content_type', 'unknown')
            row_index = row.get('row_index', idx)
            
            # Create chunk with metadata
            chunk = {
                'text': text,
                'metadata': {
                    'source_file': source_file,
                    'content_type': content_type,
                    'row_index': int(row_index),
                    'chunk_id': f"{source_file}_{row_index}",
                    'token_count': token_count
                }
            }
            
            chunks.append(chunk)
    
     return chunks

def main():
    #Test the chunking modelule with sample data
    sample_data = {
        'source_file': ['test.csv'] * 3,
        'content_type': ['csv'] * 3,
        'row_index': [0, 1, 2],
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'city': ['NYC', 'LA', 'Chicago']
    }
    df = pd.DataFrame(sample_data)
    
    print("=== Original DataFrame ===")
    print(df)
    
    # Convert to chunks
    chunks = dataframe_to_chunks(df)
    
    print("\n=== Generated Chunks ===")
    for i, chunk in enumerate(chunks, 1):
        print(f"\nChunk {i}:")
        print(f"Text: {chunk['text']}")
        print(f"Metadata: {chunk['metadata']}")
        print(f"Token count: {chunk['metadata']['token_count']}")


if __name__ == "__main__":
    main()