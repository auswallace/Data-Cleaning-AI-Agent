# Quick Start - 5 Minutes to Running System

## Step 1: Get Your API Key (2 min)

1. Go to https://platform.openai.com/api-keys
2. Create new API key
3. Copy it (starts with `sk-...`)

## Step 2: Setup (1 min)

```bash
cd GitHub_AI_Agent/v2

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

Edit `.env` and paste your API key:
```bash
OPENAI_API_KEY=sk-your-key-here
```

## Step 3: Test It! (2 min)

### Option A: Run Example Script

```bash
python example_usage.py
```

You'll see:
- Agent analyzing data
- Creating a cleaning plan
- Executing tools
- Quality score and feedback

### Option B: Use Web UI

```bash
# Terminal 1: Start API server
python -m api.main

# Terminal 2: Serve web UI
python -m http.server 8080 --directory web
```

Open browser: http://localhost:8080

Drag & drop any CSV file!

### Option C: Use API

```python
from agents.data_cleaning_agent import DataCleaningAgent
import pandas as pd

df = pd.read_csv('your_file.csv')
agent = DataCleaningAgent(df)
result = agent.run()

print(f"Score: {result['report']['quality_score']}/10")
result['cleaned_df'].to_csv('cleaned.csv', index=False)
```

## What You'll See

```
🤖 Starting AI Data Cleaning Agent...

📊 Original Dataset:
   Shape: (100, 6)
   Missing values: 23
   Duplicate rows: 3

[Agent creates plan based on your specific data]

✅ CLEANING COMPLETE!

⭐ Quality Score: 8/10

💬 AI Feedback:
   "Good cleaning. Missing values handled appropriately..."

📋 Actions Taken (4 iterations):
   1. Standardized column names to snake_case
   2. Removed 3 duplicate rows
   3. Handled 23 missing values using KNN imputation
   4. Detected 5 outliers (flagged in _is_outlier column)

📈 Summary:
   • Rows: 100 → 97 (3 removed)
   • Columns: 6 → 6

💾 Cleaned data saved to: data/cleaned/example_cleaned.csv
```

## Troubleshooting

**"No API key found"**
```bash
# Make sure .env exists
ls -la .env

# Check it has your key
cat .env | grep OPENAI_API_KEY
```

**"Module not found"**
```bash
# Make sure you're in v2 directory
cd GitHub_AI_Agent/v2

# Reinstall dependencies
pip install -r requirements.txt
```

**"Connection refused on API"**
```bash
# Start the API server first
python -m api.main

# In another terminal, then access it
```

**"File too large"**
```bash
# Edit .env and increase limit
MAX_FILE_SIZE_MB=200
```

## Next Steps

1. ✅ Try your own data
2. ✅ Check the UPGRADE_GUIDE.md to see what's different from v1
3. ✅ Read v2/README.md for full documentation
4. ✅ Customize tools in `tools/cleaning_tools.py`
5. ✅ Deploy to production

## Common Use Cases

### Clean a CSV file
```python
import pandas as pd
from agents.data_cleaning_agent import DataCleaningAgent

df = pd.read_csv('messy.csv')
agent = DataCleaningAgent(df)
result = agent.run()
result['cleaned_df'].to_csv('clean.csv', index=False)
```

### Upload via API
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@messy_data.csv"
```

### Paste data from Excel
1. Copy cells from Excel
2. Open web UI
3. Click "Paste Data" tab
4. Paste and click "Clean Data"

### Load from URL
```bash
curl -X POST http://localhost:8000/api/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/data.csv"}'
```

## Cost Estimate

Using `gpt-4o-mini` (default):
- **$0.0003 per cleaning** (yes, less than a penny!)

For 1,000 cleanings:
- **$0.30 total**

Compare to v1 using `gpt-4`:
- **$40 for 1,000 cleanings**

v2 is **133x cheaper**!

## What Makes v2 Special

1. **Real AI Agent** - Plans and adapts, not just fixed steps
2. **Proper Outlier Detection** - Isolation Forest, not random model
3. **Modern Web UI** - Drag & drop, progress tracking
4. **Multiple Upload Methods** - File, paste, URL
5. **Cost Efficient** - 133x cheaper than v1
6. **Production Ready** - Proper config, error handling, API

## Need Help?

- Check `UPGRADE_GUIDE.md` for detailed comparison with v1
- Read `v2/README.md` for complete API documentation
- Review `example_usage.py` for Python usage examples
- Open `web/index.html` to see the UI implementation

---

**You're ready to go! Try it with your own data now.**
