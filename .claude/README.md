# Claude Code Configuration

This directory contains configuration for Claude Code when working with this repository.

## Project Overview

**Data Cleaning Agent** - An automated tool for cleaning messy datasets.

Built because I was tired of rewriting the same data cleaning code for every project.

## Project Structure

```
Data-Cleaning-AI-Agent/
└── GitHub_AI_Agent/           # Main project directory
    ├── agents/                # Cleaning logic
    ├── tools/                 # Individual cleaning operations
    ├── api/                   # REST API
    ├── web/                   # Web UI
    ├── config/                # Settings
    ├── data/                  # Auto-created folders
    │   ├── uploads/
    │   ├── cleaned/
    │   └── cache/
    ├── run_example.py         # Working demo
    ├── README.md              # Main documentation
    └── old_version_archive/   # Archived v1 code (don't use)
```

## Quick Commands

### Run Example
```bash
cd GitHub_AI_Agent
python run_example.py
```

### Start Web UI
```bash
cd GitHub_AI_Agent
python -m api.main  # Terminal 1
python -m http.server 8080 --directory web  # Terminal 2
```

### Use in Python
```python
from agents.simple_cleaning_agent import SimpleCleaningAgent
import pandas as pd

df = pd.read_csv('messy.csv')
agent = SimpleCleaningAgent(df)
result = agent.run()
```

## Key Files

| File | Purpose |
|------|---------|
| `agents/simple_cleaning_agent.py` | Main cleaning agent |
| `tools/cleaning_tools.py` | 5 cleaning operations |
| `api/main.py` | REST API server |
| `web/index.html` | Web UI |
| `run_example.py` | Demo script |

## What It Does

1. **Standardizes column names** → snake_case
2. **Removes duplicates**
3. **Fills missing values** → KNN for numeric, mode for categorical
4. **Detects outliers** → Isolation Forest algorithm
5. **Scores quality** → 1-10 rating

## Important Notes

- **No API keys required** - Runs 100% locally
- **No AI dependencies** - Uses scikit-learn only
- **Old version archived** - Don't use `old_version_archive/`
- **Works with**: CSV, Excel, JSON, Parquet

## Common Tasks

### Add New Cleaning Tool
1. Create class in `tools/cleaning_tools.py`
2. Inherit from `Tool` base class
3. Implement `execute()` method
4. Add to agent's tool list in `agents/simple_cleaning_agent.py`

### Modify Web UI
Edit `web/index.html` - it's a standalone file

### Add API Endpoint
Add route in `api/main.py`

### Change Configuration
Edit `config/settings.py` or create `.env` file

## Testing

Run the example to verify everything works:
```bash
cd GitHub_AI_Agent && python run_example.py
```

Should output:
```
✅ CLEANING COMPLETE!
⭐ Quality Score: 9/10
```

## Dependencies

Install with:
```bash
pip install -r requirements.txt
```

Core dependencies:
- pandas
- numpy
- scikit-learn
- FastAPI (for API)
- uvicorn (for API)

## Project History

- **v1**: Built with ChatGPT, had broken CatBoost model trained on random data
- **v2**: Rebuilt with Claude, fixed outlier detection, removed API dependencies
- **Current**: Clean, organized, actually works!
