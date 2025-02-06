import pandas as pd
import os

UPLOAD_FOLDER = "raw_data/"

def load_data(file_path):
    """Loads a CSV or Excel file into a Pandas DataFrame."""
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == ".csv":
        return pd.read_csv(file_path)
    elif ext in [".xls", ".xlsx"]:
        return pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format! Use CSV or Excel.")

def save_data(df, filename):
    """Saves cleaned data to the cleaned_data folder."""
    save_path = f"cleaned_data/{filename}"
    df.to_csv(save_path, index=False)
    print(f"✅ Cleaned data saved to {save_path}")
