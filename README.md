# Data-Cleaning-AI-Agent
AI Agent 

AI-Driven Data Cleaning Project

Overview & Goal

This project automates data cleaning using AI-powered agents. The goal is to process raw datasets by handling missing values, detecting outliers, and enforcing correct data types. The system leverages machine learning and OpenAI models to enhance data quality and ensure consistency.

How It Works

The project consists of two primary agents:

AIDataCleaningAgent - Responsible for cleaning the dataset by imputing missing values, detecting/removing outliers, and enforcing column data types.

SupervisorAIAgent - Performs post-cleaning validation and generates a summary report on the cleaning effectiveness.

Agent Setup & Functionality

AIDataCleaningAgent

Initializes with a dataset and creates a backup for rollback.

Handles missing values using KNN imputation.

Detects outliers using a pre-trained CatBoost model and removes them.

Infers correct column data types via OpenAI GPT-4 and applies the appropriate conversions.

Outputs a cleaned DataFrame.

SupervisorAIAgent

Compares the dataset before and after cleaning.

Summarizes cleaning effectiveness using AI-generated insights.

Generates a validation report on missing value handling, row removals, and type enforcement.

How to Use

Prepare your dataset (Excel or CSV file).

Run the script with the dataset path:

file_path = "your_dataset.xlsx"
df_labor = pd.read_excel(file_path)
cleaning_agent = AIDataCleaningAgent(df_labor)
cleaned_df = cleaning_agent.clean_data()

Validate the cleaned data:

supervisor = SupervisorAIAgent()
validation_results = supervisor.validate_cleaning(df_labor, cleaned_df)

Save the cleaned data:

cleaned_df.to_excel("cleaned_data.xlsx", index=False)

Notes

Ensure gpt_api_key.txt is present and contains a valid OpenAI API key.

The pre-trained outlier detection model is stored in catboost_outlier_model.pkl.

Modify hyperparameters (e.g., KNN neighbors, CatBoost depth) as needed for your dataset.

Dependencies

Install the required libraries using:

pip install pandas numpy openai joblib scikit-learn catboost cryptography

Contact

For any issues or improvements, feel free to contribute or report them.

