import pandas as pd
from db_utils import import_historical_data
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Import historical price data')
    parser.add_argument('csv_file', help='Path to CSV file')
    args = parser.parse_args()
    
    result = import_historical_data(args.csv_file)
    print(result)