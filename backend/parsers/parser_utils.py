"""
Parser Utilities - Standardization Layer
Ensures all parsers return consistent DataFrame format for RAG pipeline
"""
import pandas as pd
from typing import Union, Dict, List
import os


def standardize_dataframe(df: pd.DataFrame, source_file: str, content_type: str) -> pd.DataFrame:
    """
    Standardize any DataFrame to consistent format for RAG pipeline
    
    Adds metadata columns that RAG pipeline expects:
    - source_file: Name of the original file
    - content_type: Type of content (csv, json, pdf_text, pdf_table, ical)
    - row_index: Sequential index for each row
    
    Args:
        df: Input DataFrame from any parser
        source_file: Name of source file (e.g., 'data.csv')
        content_type: Type of content ('csv', 'json', 'pdf_text', 'pdf_table', 'ical')
    
    Returns:
        Standardized DataFrame with metadata columns prepended
    """
    if df is None or df.empty:
        # Return empty DataFrame with standard columns
        return pd.DataFrame(columns=['source_file', 'content_type', 'row_index'])
    
    standardized = df.copy()
    
    # Add standard metadata columns at the beginning
    standardized.insert(0, 'source_file', source_file)
    standardized.insert(1, 'content_type', content_type)
    standardized.insert(2, 'row_index', range(len(df)))
    
    return standardized


def validate_dataframe(df: pd.DataFrame) -> bool:
    """
    Validate that DataFrame meets standardization requirements
    
    Checks for:
    - Not None or empty
    - Has required metadata columns
    
    Args:
        df: DataFrame to validate
    
    Returns:
        True if valid
        
    Raises:
        ValueError: If validation fails
    """
    if df is None or df.empty:
        raise ValueError("DataFrame is None or empty")
    
    required_columns = ['source_file', 'content_type', 'row_index']
    missing = [col for col in required_columns if col not in df.columns]
    
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    return True


def merge_dataframes(dfs: List[pd.DataFrame]) -> pd.DataFrame:
    """
    Merge multiple standardized DataFrames
    Useful for combining multiple file uploads
    
    Args:
        dfs: List of standardized DataFrames
    
    Returns:
        Single merged DataFrame with re-indexed rows
    """
    if not dfs:
        return pd.DataFrame(columns=['source_file', 'content_type', 'row_index'])
    
    # Validate all DataFrames
    for df in dfs:
        validate_dataframe(df)
    
    # Concatenate and reset index
    merged = pd.concat(dfs, ignore_index=True)
    merged['row_index'] = range(len(merged))
    
    return merged


def get_file_extension(file_path: str) -> str:
    """
    Get file extension from file path
    
    Args:
        file_path: Path to file
    
    Returns:
        Extension without dot (e.g., 'csv', 'json', 'pdf')
    """
    return os.path.splitext(file_path)[1][1:].lower()


def detect_content_type(file_path: str) -> str:
    """
    Detect content type from file extension
    
    Args:
        file_path: Path to file
    
    Returns:
        Content type string
    """
    extension = get_file_extension(file_path)
    
    type_mapping = {
        'csv': 'csv',
        'json': 'json',
        'pdf': 'pdf',
        'ics': 'ical',
        'ical': 'ical'
    }
    
    return type_mapping.get(extension, 'unknown')
