import pandas as pd 
import json
import os


def parse_json_file(file_path):
    try: 
        df = pd.read_json(file_path)
        return df
    except: 
        with open(file_path, 'r') as file:
            data = json.load(file)

        if isinstance(data, list):
            df = pd.json_normalize(data)
        elif isinstance(data, dict):
            df = pd.json_normalize(data)
        return df

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'listings.json')
    
    df = parse_json_file(file_path)
    print(df.head())

if __name__ == "__main__":
    main()