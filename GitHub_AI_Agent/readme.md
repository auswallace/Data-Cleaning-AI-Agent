# Data Cleaning Agent 🧹

> **"I got tired of copy-pasting the same data cleaning code into every project."**
> So I built a reusable agent that does it for me.

## Why I Built This

Every time I started a new data project, I'd spend the first hour doing the same boring stuff:
- Fixing column names with spaces and weird characters
- Dealing with missing values
- Removing duplicate rows
- Finding outliers in the data

I was literally copy-pasting the same cleaning code between projects. It was getting ridiculous.

So I built this as a **fun side project** to solve my own problem. Now I just load messy data, run the agent, and get clean data back. No more rewriting the same code over and over.

---

## What It Does

**Automated data cleaning with 5 operations:**

1. **Standardizes column names** → Converts "User ID" to "user_id"
2. **Removes duplicates** → Keeps unique rows only
3. **Fills missing values** → Smart imputation (KNN for numbers, mode for categories)
4. **Detects outliers** → Flags weird data points using Isolation Forest
5. **Scores quality** → Tells you how clean your data is (1-10)

**Zero configuration. No API keys. Just works.**

---

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Run example
python run_example.py
```

You'll see:
```
✅ CLEANING COMPLETE!
⭐ Quality Score: 9/10

📊 Original: 103 rows, 52 missing values, 3 duplicates
📊 Cleaned: 100 rows, 0 missing values, 0 duplicates

💾 Saved to: data/cleaned/example_cleaned.csv
```

---

## How to Use It

### Option 1: Python Script (My Most Common Use)

```python
from agents.simple_cleaning_agent import SimpleCleaningAgent
import pandas as pd

# Load your messy data
df = pd.read_csv('messy_data.csv')

# Clean it
agent = SimpleCleaningAgent(df)
result = agent.run()

# Get cleaned data
cleaned_df = result['cleaned_df']
print(f"Quality: {result['report']['quality_score']}/10")

# Save it
cleaned_df.to_csv('clean_data.csv', index=False)
```

### Option 2: Web UI (For Quick One-Offs)

```bash
# Start the server
python -m api.main

# Serve the web UI (in another terminal)
python -m http.server 8080 --directory web

# Open http://localhost:8080
```

**Then:**
- Drag & drop your file
- Or copy/paste data from Excel
- Or load from a URL
- Click "Clean Data"
- Download cleaned CSV

### Option 3: REST API (For Automation)

```bash
# Upload a file
curl -X POST http://localhost:8000/api/upload \
  -F "file=@data.csv"

# Check status
curl http://localhost:8000/api/jobs/YOUR_JOB_ID

# Download cleaned data
curl http://localhost:8000/api/download/YOUR_JOB_ID > cleaned.csv
```

---

## What It Handles

| Problem | Solution |
|---------|----------|
| Missing values in numbers | KNN imputation (estimates from similar rows) |
| Missing values in text | Mode imputation (most common value) |
| Duplicate rows | Removes them (keeps first occurrence) |
| Messy column names | Converts to snake_case |
| Outliers | Flags them using Isolation Forest |
| Bad data types | Auto-fixes where possible |

---

## Real-World Examples

### Quick Excel Cleanup
```
1. Have messy Excel data
2. Copy it (Ctrl+C)
3. Go to web UI → "Paste Data" tab
4. Paste and click "Clean"
5. Download cleaned CSV
```

### Daily ETL Pipeline
```python
# Morning data import job
import pandas as pd
from agents.simple_cleaning_agent import SimpleCleaningAgent

df = pd.read_csv('daily_export.csv')
agent = SimpleCleaningAgent(df)
clean_df = agent.run()['cleaned_df']

# Load into database
clean_df.to_sql('clean_table', engine)
```

### Pre-Process ML Data
```python
# Before training your model
df = pd.read_csv('training_data.csv')
agent = SimpleCleaningAgent(df)
result = agent.run()

if result['report']['quality_score'] >= 7:
    # Good enough for training
    train_model(result['cleaned_df'])
else:
    print("Data quality too low:", result['report']['feedback'])
```

---

## Project Structure

```
├── agents/                    # Cleaning logic
│   └── simple_cleaning_agent.py
├── tools/                     # Individual cleaning operations
│   ├── base_tool.py
│   └── cleaning_tools.py
├── api/                       # REST API server
│   └── main.py
├── web/                       # Web interface
│   └── index.html
├── config/                    # Configuration
│   └── settings.py
├── data/                      # Auto-created
│   └── cleaned/              # Cleaned outputs go here
├── run_example.py            # Demo script
├── requirements.txt          # Dependencies
├── QUICK_START.md           # 2-minute guide
└── old_version_archive/     # Previous iteration (don't use)
```

---

## Supported Formats

- ✅ CSV (`.csv`)
- ✅ Excel (`.xlsx`, `.xls`)
- ✅ JSON (`.json`)
- ✅ Parquet (`.parquet`)

---

## Configuration (Optional)

You can tweak settings by creating a `.env` file:

```bash
# File upload limits
MAX_FILE_SIZE_MB=100

# Cleaning parameters
MISSING_VALUE_THRESHOLD=0.5    # Drop columns with >50% missing
OUTLIER_CONTAMINATION=0.05     # Expected outlier rate (5%)
KNN_NEIGHBORS=5                # Neighbors for KNN imputation
```

But honestly, the defaults work fine for most cases.

---

## The Cleaning Tools

Each tool is a self-contained operation:

### 1. InspectDataTool
Analyzes your data structure and finds issues

### 2. HandleMissingValuesTool
- Numbers → KNN imputation
- Categories → Mode imputation
- High missing % → Drops column

### 3. DetectOutliersTool
Uses Isolation Forest to find anomalies (actually works, unlike the old version!)

### 4. RemoveDuplicatesTool
Finds and removes exact duplicate rows

### 5. StandardizeColumnNamesTool
Converts "User Name" → "user_name"

---

## Performance

- **Speed:** < 5 seconds for typical datasets (1000 rows)
- **Cost:** $0 (no API calls, completely local)
- **Memory:** Handles datasets up to available RAM
- **Accuracy:** Depends on your data, but quality scores are usually 7-9/10

---

## Common Questions

**Q: Do I need an API key?**
A: Nope. Runs 100% locally.

**Q: What if I don't like Python?**
A: Use the web UI or REST API. No coding required.

**Q: Can I add custom cleaning rules?**
A: Yes! Add a new tool in `tools/cleaning_tools.py` following the same pattern.

**Q: What happened to the old version in `old_version_archive/`?**
A: That was my first attempt (built with ChatGPT). It had a broken outlier detection model trained on random data. Don't use it. This new version actually works.

**Q: Why no tests?**
A: It's a personal project I use for myself. Works for my needs. If you want tests, PRs welcome!

---

## Limitations

**What it does well:**
- Standard tabular data cleaning
- Common data quality issues
- Quick iterations

**What it doesn't do:**
- Complex data validation (regex patterns, business rules)
- Time series specific cleaning
- Multi-table relationships
- Custom domain logic
- Data augmentation

For those, you'll still need custom code. But for the boring 80% of data cleaning? This handles it.

---

## Future Ideas (Maybe)

Things I might add if I get bored again:

- [ ] Email/phone validation tool
- [ ] Date range validation
- [ ] Auto-detect and suggest data types
- [ ] Export cleaning steps as code
- [ ] Batch processing multiple files
- [ ] Integration with cloud storage (S3, GCS)

But honestly, it solves my problem as-is. ¯\\\_(ツ)_/¯

---

## Contributing

This is a personal tool I use for my own projects. But if you want to:

- **Report bugs:** Open an issue
- **Suggest features:** Open an issue
- **Submit fixes:** Send a PR
- **Use it:** Go for it! MIT licensed.

Just keep in mind this is a side project, not a production library with SLAs.

---

## License

MIT - Do whatever you want with it.

---

## The Real Story

I built this over a weekend because I was procrastinating on a different project.

You know how it is:
1. Need to clean data for Project A
2. Spend 3 hours building a reusable cleaning tool instead
3. Never actually finish Project A
4. But hey, now I have this!

Classic developer move. 😅

At least now every time I need to clean data, I just run this instead of writing it from scratch. Small wins.

---

**Made by [@auswallace](https://github.com/auswallace)**
_"Automating the boring stuff since [whenever I built this]"_
