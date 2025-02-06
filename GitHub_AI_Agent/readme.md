# 🚀 AI-Powered Data Cleaning Pipeline

## 📌 Overview  
This project is a modular **AI-driven data processing pipeline** designed to **clean, validate, and analyze datasets**. It enables users to:  
✔ Upload local datasets  
✔ Scrape tables from websites  
✔ Download and merge Kaggle datasets  
✔ Perform automated **data cleaning** using AI and ML models  
✔ Validate data transformations with **AI-generated insights**  

The system is built with **modularity and scalability** in mind, allowing future extensions for more advanced analytics.

---

## ⚙️ How It Works  
The project is structured into **three main phases**:

### **1️⃣ Data Ingestion**
- Users can **upload a file**, **scrape data from the web**, or **retrieve a dataset from Kaggle**.
- The system extracts, processes, and standardizes the data.

### **2️⃣ Data Cleaning (AI-Driven)**
- **Missing values** are handled using **KNN Imputation**.
- **Outliers** are detected and removed using a **CatBoost classifier**.
- **Column data types** are inferred and enforced using **OpenAI’s GPT model**.

### **3️⃣ Data Validation & Export**
- The cleaned dataset is **validated** by an AI-powered **Supervisor Agent**.
- Users receive **a report on data quality, transformations, and potential improvements**.
- The cleaned data is saved in the `cleaned_data/` folder for further analysis.

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
```

---

## 🔧 How to Use

### **1️⃣ Running the Pipeline**
1. Clone this repository and navigate to the project folder.
   ```bash
   git clone https://github.com/your-repo/AI-Data-Cleaning-Pipeline.git
   cd AI-Data-Cleaning-Pipeline
   ```
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the main script:
   ```bash
   python main.py
   ```

### **2️⃣ Choosing a Data Source**
Upon running the script, users will be prompted to:
- Upload a local dataset (.csv or .xlsx) via a **file selection window**.
- Enter a URL to **scrape tabular data from a website**.
- Provide a **Kaggle dataset URL** for automated download & merging.

### **3️⃣ Data Cleaning Process**
Once the dataset is loaded, the AI cleaning agent:
- Handles missing values, outliers, and incorrect data types.
- Uses OpenAI's GPT model for column type inference.
- Stores the cleaned dataset in **cleaned_data/**.

### **4️⃣ Viewing Cleaning Reports**
The **Supervisor AI Agent** generates a detailed validation report on:
- Changes made to the dataset.
- Remaining issues and suggested improvements.

---

## 📂 Data Storage & Output
- **Original datasets remain unchanged**.
- **Cleaned datasets** are stored in the `cleaned_data/` folder.
- **Kaggle datasets** are stored in `kaggle_data/`.
- **Scraped datasets** are processed dynamically.

---

## 🔑 API & Configuration
- Ensure `gpt_api_key.txt` is present with a **valid OpenAI API key**.
- The **pre-trained CatBoost outlier detection model** is stored in `outlier_model.pkl`.
- Modify hyperparameters (e.g., KNN neighbors, CatBoost depth) as needed.

---

## 🛠️ Dependencies
Install required Python libraries with:
```bash
pip install -r requirements.txt
```

---

## 📬 Contact & Contributions
For issues, feature requests, or contributions, open a GitHub issue or submit a pull request. Let's build a more powerful AI-driven data cleaning tool together! 🚀

