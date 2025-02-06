import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog
from data_scraper.scraper import (
    extract_dataset_name,
    download_kaggle_dataset,
    combine_kaggle_csvs,
    scrape_table,
)
from data_cleaning.cleaning_agent import AIDataCleaningAgent
from data_cleaning.cleaning_agent import SupervisorAIAgent


# User chooses data input method first
print("\n🔹 Welcome to the Data Processing Pipeline! 🔹\n")
print("Choose an option:")
print("1. Upload a dataset")
print("2. Scrape data from a website")
print("3. Download a Kaggle dataset")

user_choice = input("> ")

df_dataset = None  # Ensure no dataset is loaded at the start
dataset_name = None  # Variable to hold dataset name for tracking

if user_choice == "1":
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
        dataset_name = file_path.split("/")[-1]  # Extract filename for naming
        print(f"✅ Selected File: {file_path}")

        if file_path.endswith(".xlsx"):
            df_dataset = pd.read_excel(file_path)
        elif file_path.endswith(".csv"):
            df_dataset = pd.read_csv(file_path)
        else:
            print("❌ Unsupported file type. Please use .xlsx or .csv")
            exit(1)
    else:
        print("❌ No file selected. Exiting...")
        exit(1)

elif user_choice == "2":
    url = input("Enter the website URL to scrape: ").strip()
    dataset_name = "scraped_data"  # Generic name for scraped data
    df_dataset = scrape_table(url)

elif user_choice == "3":
    kaggle_url = input("Enter the Kaggle dataset URL: ").strip()
    dataset_name = extract_dataset_name(kaggle_url)
    if dataset_name:
        download_kaggle_dataset(dataset_name)
        df_dataset = combine_kaggle_csvs()  # Automatically merges Kaggle CSVs
    else:
        print("❌ Invalid Kaggle URL. Exiting.")
        exit(1)

else:
    print("❌ Invalid option. Exiting.")
    exit(1)

# ✅ **Only Run Cleaning if a dataset has been loaded**
if df_dataset is not None:
    print(f"\n🛠️ Cleaning dataset: {dataset_name} with AI...")

    # Run the AI cleaning agent
    cleaning_agent = AIDataCleaningAgent(df_dataset)
    df_cleaned = cleaning_agent.clean_data()

    # Validate the cleaned data
    supervisor = SupervisorAIAgent()
    validation_results = supervisor.validate_cleaning(df_dataset, df_cleaned)

    # Print results
    print("\n📝 CLEANED DATA:")
    print(df_cleaned.head())

    print("\n📝 SUPERVISOR VALIDATION REPORT:")
    for key, value in validation_results.items():
        print(f"{key}: {value}")

    # Ensure the cleaned_data directory exists
    CLEANED_DATA_PATH = "cleaned_data/"
    os.makedirs(CLEANED_DATA_PATH, exist_ok=True)

    # Save cleaned dataset dynamically
    cleaned_file_path = os.path.join(CLEANED_DATA_PATH, f"cleaned_{dataset_name}.csv")
    df_cleaned.to_csv(cleaned_file_path, index=False)

    print(f"✅ Cleaned dataset saved in '{cleaned_file_path}'!")

else:
    print("❌ No dataset loaded. Exiting.")
    exit(1)
