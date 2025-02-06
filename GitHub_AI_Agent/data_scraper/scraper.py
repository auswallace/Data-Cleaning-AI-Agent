import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from kaggle.api.kaggle_api_extended import KaggleApi
import tkinter as tk
from tkinter import filedialog

KAGGLE_DOWNLOAD_PATH = "kaggle_data/"


# 🟢 Function to Extract Dataset Name from a Kaggle URL
def extract_dataset_name(url):
    """Extracts dataset name from Kaggle dataset URL."""
    match = re.search(r"kaggle.com/datasets/([^/]+/[^/?]+)", url)
    return match.group(1) if match else None


# 🟢 Function to Download a Kaggle Dataset
def download_kaggle_dataset(dataset_name):
    """Downloads a specified Kaggle dataset."""
    api = KaggleApi()
    api.authenticate()

    if not os.path.exists(KAGGLE_DOWNLOAD_PATH):
        os.makedirs(KAGGLE_DOWNLOAD_PATH)

    api.dataset_download_files(dataset_name, path=KAGGLE_DOWNLOAD_PATH, unzip=True)
    print(f"✅ Dataset '{dataset_name}' downloaded to '{KAGGLE_DOWNLOAD_PATH}'.")


# 🟢 Function to Combine Multiple CSVs into One
def combine_kaggle_csvs():
    """Combines multiple CSV files in the Kaggle download directory."""
    csv_files = [f for f in os.listdir(KAGGLE_DOWNLOAD_PATH) if f.endswith(".csv")]

    if not csv_files:
        print("❌ No CSV files found in Kaggle dataset.")
        return None

    df_list = [pd.read_csv(os.path.join(KAGGLE_DOWNLOAD_PATH, file)) for file in csv_files]
    combined_df = pd.concat(df_list, ignore_index=True)

    output_file = os.path.join(KAGGLE_DOWNLOAD_PATH, "combined_kaggle_data.csv")
    combined_df.to_csv(output_file, index=False)
    print(f"✅ Combined {len(csv_files)} files into {output_file}")

    return combined_df


# 🟢 Function to Handle Kaggle Dataset Download and Processing
def handle_kaggle_download():
    """Handles the process of downloading a Kaggle dataset."""
    kaggle_url = input("Enter the Kaggle dataset URL: ").strip()
    dataset_name = extract_dataset_name(kaggle_url)

    if dataset_name:
        print(f"📥 Downloading dataset: {dataset_name}...")
        download_kaggle_dataset(dataset_name)
        print("✅ Kaggle dataset downloaded successfully!")

        # Automatically combine all CSVs from the Kaggle dataset
        df = combine_kaggle_csvs()
        return df
    else:
        print("❌ Invalid Kaggle URL. Please try again.")
        return None


# 🟢 Function to Scrape Data from a Website
def scrape_table(url):
    """Scrapes tabular data from a webpage and converts it to a DataFrame."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table")  # Adjust selector based on site
    if not table:
        print("❌ No table found on the page.")
        return None

    rows = table.find_all("tr")

    data = []
    for row in rows:
        cols = [col.text.strip() for col in row.find_all(["th", "td"])]
        data.append(cols)

    df = pd.DataFrame(data)
    return df


# 🟢 Function to Browse and Select a Local Dataset
def select_local_dataset():
    """Opens a file selection dialog for choosing a dataset."""
    print("📂 Select a dataset file (Excel or CSV)...")

    # Initialize Tkinter root window (hidden)
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Open file selection dialog
    file_path = filedialog.askopenfilename(
        title="Select a dataset",
        filetypes=[("Excel Files", "*.xlsx"), ("CSV Files", "*.csv")]
    )

    # If a file was selected, load it
    if file_path:
        print(f"✅ Selected File: {file_path}")
        if file_path.endswith(".xlsx"):
            return pd.read_excel(file_path)
        elif file_path.endswith(".csv"):
            return pd.read_csv(file_path)
        else:
            print("❌ Unsupported file type. Please use .xlsx or .csv")
            return None
    else:
        print("❌ No file selected. Exiting...")
        return None
