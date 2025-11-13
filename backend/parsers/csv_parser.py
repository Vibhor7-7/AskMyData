import pandas as pd
import os


def csv_parser(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'validation.csv')
    
    df = csv_parser(file_path)
    print(df.head())    

if __name__ == "__main__":
    main()

    