"""
Unified File Parser Interface
Automatically detects file type and calls appropriate parser
"""
import os
from parser_utils import detect_content_type, get_file_extension
from csv_parser import csv_parser
from json_parser import parse_json_file
from pdf_parser import parse_pdf_to_df
from ical_parser import parse_ical_file


def parse_file(file_path):
    """
    Unified parser that auto-detects file type and returns standardized DataFrame
    
    Supports:
    - CSV files
    - JSON files
    - PDF files
    - iCal files (.ics)
    
    Args:
        file_path: Path to file to parse
    
    Returns:
        Standardized DataFrame with columns:
        ['source_file', 'content_type', 'row_index', ...data columns...]
    
    Raises:
        ValueError: If file type is not supported
        FileNotFoundError: If file doesn't exist
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Detect file type
    extension = get_file_extension(file_path)
    
    # Route to appropriate parser
    if extension == 'csv':
        return csv_parser(file_path)
    elif extension == 'json':
        return parse_json_file(file_path)
    elif extension == 'pdf':
        return parse_pdf_to_df(file_path)
    elif extension in ['ics', 'ical']:
        return parse_ical_file(file_path)
    else:
        raise ValueError(f"Unsupported file type: .{extension}")


def main():
    """Test the unified parser with different file types"""
    import pandas as pd
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Test files
    test_files = [
        'validation.csv',
        'listings.json',
        'sch.ics',
        '_Vibhor_Sharma_.pdf'  
    ]
    
    for filename in test_files:
        file_path = os.path.join(script_dir, filename)
        
        if not os.path.exists(file_path):
            print(f"\n  Skipping {filename} - file not found")
            continue
        
        print(f"\n{'='*60}")
        print(f"Testing: {filename}")
        print('='*60)
        
        try:
            df = parse_file(file_path)
            
            if df is not None:
                print(f" Parsed successfully")
                print(f"  Shape: {df.shape}")
                print(f"  Columns: {list(df.columns)}")
                print(f"  Content type: {df['content_type'].iloc[0] if len(df) > 0 else 'N/A'}")
                print(f"\n  First row:")
                print(f"  {df.iloc[0].to_dict()}")
            else:
                print(f" Parser returned None")
                
        except Exception as e:
            print(f" Error: {e}")

if __name__ == "__main__":
    main()
