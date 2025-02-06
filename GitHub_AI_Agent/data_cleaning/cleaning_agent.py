import pandas as pd
import numpy as np
import joblib
import json
import logging
from sklearn.impute import KNNImputer
from catboost import CatBoostClassifier
from data_cleaning.config import client  # Import OpenAI client
from data_cleaning.model_loader import catboost_model  # Load CatBoost model


class AIDataCleaningAgent:
    def __init__(self, df_dataset):
        """Initializes with a dynamic dataset"""
        self.df_dataset = df_dataset.copy()
        self.rollback_stack = []

    def ai_suggest_column_types(self):
        """Uses OpenAI GPT to infer column data types, ensuring valid output."""
        prompt = (
            "Given this dataset, classify columns as integer, float, categorical, or datetime. "
            "Return a JSON dictionary where keys are column names and values are types. "
            f"Dataset column types: {self.df_dataset.dtypes.to_dict()}"
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )

            inferred_types = json.loads(response.choices[0].message.content)
            if not isinstance(inferred_types, dict):
                raise ValueError("Unexpected response format from OpenAI.")

            inferred_types = {col: inferred_types[col] for col in self.df_dataset.columns if col in inferred_types}
            return inferred_types

        except (json.JSONDecodeError, KeyError, ValueError, AttributeError) as e:
            logging.error(f"Failed to parse AI response: {e}")
            return {col: str(self.df_dataset[col].dtype) for col in self.df_dataset.columns}

    def ai_missing_value_imputation(self):
        """Handles missing values using KNN imputation."""
        logging.info("Handling missing values using KNN imputation...")
        imputer = KNNImputer(n_neighbors=3)
        self.df_dataset.loc[:, self.df_dataset.select_dtypes(include=[np.number]).columns] = imputer.fit_transform(
            self.df_dataset.select_dtypes(include=[np.number])
        )

    def detect_outliers_with_catboost(self):
        """Uses CatBoost to detect and remove outliers from numerical columns."""
        numeric_cols = self.df_dataset.select_dtypes(include=[np.number]).columns.tolist()

        if not numeric_cols:
            logging.warning("No numeric columns found for outlier detection. Skipping...")
            return

        try:
            model_features = catboost_model.feature_names_
            aligned_features = [col for col in model_features if col in self.df_dataset.columns]

            if not aligned_features:
                logging.error("No matching features found for outlier detection. Skipping...")
                return

            aligned_df = self.df_dataset[aligned_features]
            predictions = catboost_model.predict(aligned_df)

            if len(predictions) != len(self.df_dataset):
                logging.error("Outlier detection failed: prediction size mismatch.")
                return
            
            self.df_dataset["Outlier"] = predictions
            outlier_count = (self.df_dataset["Outlier"] == -1).sum()

            self.df_dataset = self.df_dataset[self.df_dataset["Outlier"] != -1].drop(columns=["Outlier"])
            logging.info(f"Outlier removal complete. {outlier_count} rows were removed.")

        except Exception as e:
            logging.error(f"Error in outlier detection: {e}")

    def clean_data(self):
        """Runs all cleaning steps and returns the cleaned DataFrame."""
        logging.info("Starting AI-driven data cleaning...")

        # Ensure rollback_stack is initialized
        if not hasattr(self, "rollback_stack"):
            self.rollback_stack = []

        self.rollback_stack.append(self.df_dataset.copy())

        # Step 1: Missing Value Imputation
        self.ai_missing_value_imputation()

        # Step 2: Outlier Detection
        self.detect_outliers_with_catboost()

        # Step 3: Column Type Enforcement
        inferred_types = self.ai_suggest_column_types()
        for col, col_type in inferred_types.items():
            if col in self.df_dataset.columns:
                try:
                    if col_type == "integer":
                        self.df_dataset[col] = pd.to_numeric(self.df_dataset[col], errors='coerce').fillna(self.df_dataset[col].median()).astype(int)
                    elif col_type == "float":
                        self.df_dataset[col] = pd.to_numeric(self.df_dataset[col], errors='coerce').fillna(self.df_dataset[col].median()).astype(float).round(2)
                    elif col_type == "string":
                        self.df_dataset[col] = self.df_dataset[col].astype(str).fillna("Unknown")
                    elif col_type == "datetime":
                        self.df_dataset[col] = pd.to_datetime(self.df_dataset[col], errors='coerce').fillna(pd.Timestamp("2000-01-01"))
                except Exception as e:
                    logging.error(f"Type conversion failed for {col}: {e}")

        logging.info("Data cleaning completed successfully.")
        return self.df_dataset


class SupervisorAIAgent:
    def validate_cleaning(self, original_df, df_cleaned):
        """Performs post-cleaning validation and AI-driven summarization."""
        report = {
            "missing_values_fixed": sum(df_cleaned.isnull().sum()) == 0,
            "rows_removed": original_df.shape[0] - df_cleaned.shape[0]
        }

        prompt = (
            f"Analyze the dataset before and after cleaning.\n\n"
            f"🔹 **Before Cleaning:**\n"
            f"- Shape: {original_df.shape}\n"
            f"- Missing values per column: {original_df.isnull().sum().to_dict()}\n"
            f"- Data types: {original_df.dtypes.to_dict()}\n"
            f"- Sample rows: {original_df.head(3).to_dict()}\n\n"
            f"🔹 **After Cleaning:**\n"
            f"- Shape: {df_cleaned.shape}\n"
            f"- Missing values per column: {df_cleaned.isnull().sum().to_dict()}\n"
            f"- Data types: {df_cleaned.dtypes.to_dict()}\n"
            f"- Sample rows: {df_cleaned.head(3).to_dict()}\n\n"
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
