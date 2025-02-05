import pandas as pd
import numpy as np
import logging
import json
import openai
import os
import sys
import joblib
import hashlib
from sklearn.ensemble import IsolationForest
from sklearn.impute import KNNImputer
from catboost import CatBoostClassifier
from cryptography.fernet import Fernet



# Force a fresh script execution
for name in list(globals().keys()):
    if not name.startswith("_"):
        del globals()[name]
print("✅ Resetting memory. Running fresh script...")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
openai.api_key = os.getenv("OPENAI_API_KEY")


# Ensure API key is securely loaded from an external configuration file
def load_api_key():
    key_path = "gpt_api_key.txt"
    if os.path.exists(key_path):
        with open(key_path, "r") as key_file:
            return key_file.read().strip()
    else:
        logging.error("API key file not found. Please create 'gpt_api_key.txt' and store your key there.")
        return None  # Return None instead of proceeding with an undefined key

# Load API key and initialize OpenAI Client
api_key = load_api_key()
if api_key:
    client = openai.OpenAI(api_key=api_key)
else:
    logging.error("API key is missing! Exiting script.")
    exit(1)  # Terminate script if API key is not found

openai.api_key = load_api_key()

# Load or train CatBoost Outlier Detection Model
MODEL_FILE = "catboost_outlier_model.pkl"

def load_or_train_outlier_model():
    if os.path.exists(MODEL_FILE):
        return joblib.load(MODEL_FILE)
    else:
        logging.info("Training new CatBoost outlier model...")
        X_train = np.random.randn(1000, 5)
        y_train = np.random.choice([1, -1], size=1000, p=[0.95, 0.05])
        model = CatBoostClassifier(iterations=100, depth=6, learning_rate=0.1, loss_function='Logloss', verbose=False)
        model.fit(X_train, y_train)
        joblib.dump(model, MODEL_FILE)
        return model

catboost_model = load_or_train_outlier_model()

class AIDataCleaningAgent:
    def __init__(self, df):
        "Initializes with a dynamic dataset"
        self.df = df.copy()
        self.rollback_stack = []

    def ai_suggest_column_types(self):
        """Uses OpenAI GPT to infer column data types, ensuring valid output."""

        prompt = (
            "Given this dataset, classify columns as integer, float, categorical, or datetime. "
            "Return a JSON dictionary where keys are column names and values are types. "
            f"Dataset column types: {self.df.dtypes.to_dict()}"
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            
            inferred_types = json.loads(response.choices[0].message.content)
            if not isinstance(inferred_types, dict):
                raise ValueError("Unexpected response format from OpenAI.")

            inferred_types = {col: inferred_types[col] for col in self.df.columns if col in inferred_types}
            return inferred_types

        except (json.JSONDecodeError, KeyError, ValueError, AttributeError) as e:
            logging.error(f"Failed to parse AI response: {e}")
            return {col: str(self.df[col].dtype) for col in self.df.columns}

    def ai_missing_value_imputation(self):
        """Handles missing values using KNN imputation."""
        logging.info("Handling missing values using KNN imputation...")
        imputer = KNNImputer(n_neighbors=3)
        self.df.loc[:, self.df.select_dtypes(include=[np.number]).columns] = imputer.fit_transform(
            self.df.select_dtypes(include=[np.number])
        )

    def detect_outliers_with_catboost(self):
        """Uses CatBoost to detect and remove outliers from numerical columns."""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()

        if not numeric_cols:
            logging.warning("No numeric columns found for outlier detection. Skipping...")
            return

        try:
            model_features = catboost_model.feature_names_
            aligned_features = [col for col in model_features if col in self.df.columns]

            if not aligned_features:
                logging.error("No matching features found for outlier detection. Skipping...")
                return

            aligned_df = self.df[aligned_features]
            predictions = catboost_model.predict(aligned_df)

            if len(predictions) != len(self.df):
                logging.error("Outlier detection failed: prediction size mismatch.")
                return
            
            self.df["Outlier"] = predictions
            outlier_count = (self.df["Outlier"] == -1).sum()

            self.df = self.df[self.df["Outlier"] != -1].drop(columns=["Outlier"])
            logging.info(f"Outlier removal complete. {outlier_count} rows were removed.")

        except Exception as e:
            logging.error(f"Error in outlier detection: {e}")

    def clean_data(self):
        """Runs all cleaning steps and returns the cleaned DataFrame."""
        logging.info("Starting AI-driven data cleaning...")

        # Ensure rollback_stack is initialized
        if not hasattr(self, "rollback_stack"):
            self.rollback_stack = []

        self.rollback_stack.append(self.df.copy())

        # Step 1: Missing Value Imputation
        self.ai_missing_value_imputation()

        # Step 2: Outlier Detection
        self.detect_outliers_with_catboost()

        # Step 3: Column Type Enforcement
        inferred_types = self.ai_suggest_column_types()
        for col, col_type in inferred_types.items():
            if col in self.df.columns:
                try:
                    if col_type == "integer":
                        self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(self.df[col].median()).astype(int)
                    elif col_type == "float":
                        self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(self.df[col].median()).astype(float).round(2)
                    elif col_type == "string":
                        self.df[col] = self.df[col].astype(str).fillna("Unknown")
                    elif col_type == "datetime":
                        self.df[col] = pd.to_datetime(self.df[col], errors='coerce').fillna(pd.Timestamp("2000-01-01"))
                except Exception as e:
                    logging.error(f"Type conversion failed for {col}: {e}")

        logging.info("Data cleaning completed successfully.")
        return self.df

class SupervisorAIAgent:
    def validate_cleaning(self, original_df, cleaned_df):
        """Performs post-cleaning validation and AI-driven summarization."""
        report = {
            "missing_values_fixed": sum(cleaned_df.isnull().sum()) == 0,
            "rows_removed": original_df.shape[0] - cleaned_df.shape[0]
        }

        prompt = (
            f"Analyze the dataset before and after cleaning.\n\n"
            f"🔹 **Before Cleaning:**\n"
            f"- Shape: {original_df.shape}\n"
            f"- Missing values per column: {original_df.isnull().sum().to_dict()}\n"
            f"- Data types: {original_df.dtypes.to_dict()}\n"
            f"- Sample rows: {original_df.head(3).to_dict()}\n\n"
            f"🔹 **After Cleaning:**\n"
            f"- Shape: {cleaned_df.shape}\n"
            f"- Missing values per column: {cleaned_df.isnull().sum().to_dict()}\n"
            f"- Data types: {cleaned_df.dtypes.to_dict()}\n"
            f"- Sample rows: {cleaned_df.head(3).to_dict()}\n\n"
            "➡️ Concisely summarize the cleaning effectiveness, evaluate it on a scale of 1-10 (10 being most confident),\n"
            "and provide a bullet-point summary of what was done. If you have any short improvement suggestions, indicate them."
        )

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            report["ai_summary"] = response.choices[0].message.content
        except Exception as e:
            logging.error(f"Failed to get AI summary: {e}")
            report["ai_summary"] = "AI summary unavailable due to an error."

        return report


file_path = "/Users/austinwallace/delete_after_test/labor_stat.xlsx"


df_labor = pd.read_excel(file_path)

cleaning_agent = AIDataCleaningAgent(df_labor)
cleaned_df = cleaning_agent.clean_data()

supervisor = SupervisorAIAgent()
validation_results = supervisor.validate_cleaning(df_labor, cleaned_df)

print("\n📝 CLEANED DATA:")
print(cleaned_df)
print("\n📝 SUPERVISOR VALIDATION REPORT:")
for key, value in validation_results.items():
    print(f"{key}: {value}")
