import pandas as pd

try:
    df = pd.read_excel('FORMAT.xlsx')
    print("Columns found:")
    for col in df.columns:
        print(f"- {col}")
    print("\nFirst few rows:")
    print(df.head())
except Exception as e:
    print(f"Error reading Excel file: {e}")
