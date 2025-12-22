import pandas as pd 
import json
import os
from .parser_utils import standardize_dataframe


def parse_json_file(file_path):
    """
    Parse JSON file and return standardized DataFrame
    
    Args:
        file_path: Path to JSON file
    
    Returns:
        Standardized DataFrame with metadata columns
    """
    try: 
        df = pd.read_json(file_path)
    except Exception as e:
        print(f"Error reading JSON file with pandas: {e}")
        with open(file_path, 'r') as file:
            data = json.load(file)

        if isinstance(data, list):
            df = pd.json_normalize(data)
        elif isinstance(data, dict):
            df = pd.json_normalize(data)
    
    # Standardize output
    filename = os.path.basename(file_path)
    standardized_df = standardize_dataframe(df, filename, 'json')
    
    return standardized_df

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'listings.json')
    
    df = parse_json_file(file_path)
    print("=== JSON Parser Output ===")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print("\nFirst 3 rows:")
    print(df.head(3))

if __name__ == "__main__":
    main()