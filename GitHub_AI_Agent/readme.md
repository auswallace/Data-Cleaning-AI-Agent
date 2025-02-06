# 🚀 AI-Powered Data Cleaning Pipeline

## 📌 Table of Contents
- [Overview](#overview)
- [How It Works](#how-it-works)
  - [1️⃣ Data Ingestion](#1️⃣-data-ingestion)
  - [2️⃣ Data Cleaning (AI-Driven)](#2️⃣-data-cleaning-ai-driven)
  - [3️⃣ Data Validation & Export](#3️⃣-data-validation--export)
- [Project Structure](#🏗️-project-structure)
- [How to Use](#🔧-how-to-use)
  - [Running the Pipeline](#1️⃣-running-the-pipeline)
  - [Choosing a Data Source](#2️⃣-choosing-a-data-source)
  - [Data Cleaning Process](#3️⃣-data-cleaning-process)
  - [Viewing Cleaning Reports](#4️⃣-viewing-cleaning-reports)
- [Data Storage & Output](#📂-data-storage--output)
- [AI Agents & Customization](#🔑-ai-agents--customization)
- [Dependencies](#🛠️-dependencies)
- [Contact & Contributions](#📬-contact--contributions)
- [Why Use AI Agents for Data Cleaning?](#🔥-why-use-ai-agents-for-data-cleaning)
- [Get Started](#🚀-ready-to-automate-your-data-cleaning)

---

## 📌 Overview  
This project is a modular **AI-driven data processing pipeline** designed to **clean, validate, and analyze datasets** using intelligent **AI Agents**. These AI Agents automate data transformations and validation, ensuring high data quality.  

### 🔥 **What Makes This AI-Powered?**
- Uses **OpenAI’s GPT models** to **understand and validate column types**.  
- Uses **KNN Imputation & Mode Filling** for intelligent **missing value handling**.  
- Uses a **pre-trained CatBoost model** for **outlier detection & removal**.  
- AI **Supervisor Agent** provides **post-cleaning validation & suggestions**.  

---

## ⚙️ How It Works  
The project is structured into **three main phases**, all driven by AI-powered cleaning methods:

### **1️⃣ Data Ingestion**
- Users can:
  - **Upload a local dataset** (.csv or .xlsx)
  - **Scrape tabular data** from a website  
  - **Fetch & merge a Kaggle dataset**  
- The system extracts, processes, and standardizes data.

### **2️⃣ Data Cleaning (AI-Driven)**
| Column Type      | Cleaning Method Used |
|-----------------|---------------------|
| **Numerical**   | **KNN Imputation** estimates missing values based on similar rows |
| **Categorical** | **Mode Imputation** fills missing values with the most common category |
| **IDs**         | **Sequential Filling** ensures IDs remain unique and follow a logical order |
| **Outliers**    | **Isolation Forest (ML model)** detects and removes anomalies |
| **Data Types**  | **OpenAI GPT model** infers and enforces correct column types |

### **3️⃣ Data Validation & Export**
- AI **Supervisor Agent** evaluates cleaning steps and suggests **further improvements**.  
- Users receive **a detailed report on changes and transformations applied**.  
- Cleaned data is saved in `cleaned_data/` for **further analysis or model training**.  

---

## 🏗️ Project Structure  

```plaintext
📂 AI-Data-Cleaning-Pipeline
│── 📂 data_cleaning
│   │── cleaning_agent.py      # AI-based data cleaning module
│   │── config.py              # Loads API keys & configurations
│   │── outlier_model.pkl      # Pre-trained CatBoost outlier model
│
│── 📂 data_scraper
│   │── scraper.py             # Web scraping module (table extraction)
│
│── 📂 user_interface
│   │── uploader.py            # Handles dataset uploads & merging
│
│── 📂 tests
│   │── test_cleaning.py       # Unit tests for data cleaning functions
│   │── test_scraper.py        # Unit tests for web scraping functions
│
│── 📂 cleaned_data             # Stores all cleaned datasets
│── main.py                    # Entry point for the pipeline
│── gpt_api_key.txt             # OpenAI API key (DO NOT COMMIT TO GITHUB)
│── requirements.txt            # Python dependencies
│── README.md                   # Project documentation
