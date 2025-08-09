import pandas as pd
import sys

def explore_file_shape(filepath):
    try:
        print(f"--- Shape of {filepath} ---")
        if filepath.endswith('.xlsx'):
            df = pd.read_excel(filepath)
            print(f"Shape: {df.shape}")
        else:
            print("Not an excel file.")
        print("-" * (len(filepath) + 17))

    except FileNotFoundError:
        print(f"File not found: {filepath}")
    except Exception as e:
        print(f"An error occurred while reading {filepath}: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        for f in sys.argv[1:]:
            explore_file_shape(f)
    else:
        print("Please provide one or more file paths to explore.")
