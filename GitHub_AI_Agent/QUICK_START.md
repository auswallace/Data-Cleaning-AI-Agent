# Quick Start - 2 Minutes

## Step 1: Install (30 seconds)

```bash
cd GitHub_AI_Agent/v2
pip install -r requirements.txt
```

## Step 2: Run Example (1 minute)

```bash
python run_example.py
```

You'll see the agent clean sample data automatically:

```
🔧 Starting Data Cleaning Agent...

📊 Original Dataset:
   Shape: (103, 6)
   Missing values: 23
   Duplicate rows: 3

✅ CLEANING COMPLETE!

⭐ Quality Score: 8/10

📋 Actions Taken:
   1. Standardized column names to snake_case
   2. Removed 3 duplicate rows
   3. Handled 23 missing values using KNN imputation
   4. Detected 5 outliers

💾 Cleaned data saved to: data/cleaned/example_cleaned.csv
```

## Step 3: Use with Your Data (30 seconds)

```python
from agents import SimpleCleaningAgent
import pandas as pd

df = pd.read_csv('your_messy_data.csv')
agent = SimpleCleaningAgent(df)
result = agent.run()

print(f"Quality: {result['report']['quality_score']}/10")
result['cleaned_df'].to_csv('cleaned_data.csv', index=False)
```

## Done!

That's it. No API keys, no configuration, just clean data.

## What It Does

- ✅ Fixes missing values (KNN for numeric, mode for categorical)
- ✅ Removes duplicates
- ✅ Detects outliers (Isolation Forest)
- ✅ Standardizes column names
- ✅ Scores quality 1-10

## Web UI (Optional)

```bash
# Terminal 1
python -m api.main

# Terminal 2
python -m http.server 8080 --directory web

# Open: http://localhost:8080
```

Drag and drop files, paste data, or load from URLs.

---

**That's it! For more details, see README.md**
