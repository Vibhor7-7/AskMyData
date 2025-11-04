import pandas as pd 
import json 

def parse_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    df = pd.json_normalize(data)
    return df

def main():
    ...

if __name__ == "__main__":
    main()