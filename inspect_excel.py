import pandas as pd

try:
    df = pd.read_excel("tRADE-4.xlsx")
    if not df.empty:
        print(f"ENTRY TIME: '{df.iloc[0]['ENTRY TIME']}' (Type: {type(df.iloc[0]['ENTRY TIME'])})")
        print(f"EXIT TIME: '{df.iloc[0]['EXIT TIME']}' (Type: {type(df.iloc[0]['EXIT TIME'])})")
except Exception as e:
    print(f"Error: {e}")
