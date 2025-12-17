import pandas as pd
import os
from parser_utils import standardize_dataframe


def csv_parser(file_path):
    """
    Parse CSV file and return standardized DataFrame
    
    Args:
        file_path: Path to CSV file
    
    Returns:
        Standardized DataFrame with metadata columns
    """
    try:
        df = pd.read_csv(file_path)
        
        # Standardize output
        filename = os.path.basename(file_path)
        standardized_df = standardize_dataframe(df, filename, 'csv')
        
        return standardized_df
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'validation.csv')
    
    df = csv_parser(file_path)
    if df is not None:
        print("=== CSV Parser Output ===")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print("\nFirst 3 rows:")
        print(df.head(3))    

if __name__ == "__main__":
    main()

    