# Quick Commands for This Project

## Development

### Run the Example
```bash
cd GitHub_AI_Agent
python run_example.py
```

### Start Web Interface
```bash
cd GitHub_AI_Agent

# Terminal 1: Start API
python -m api.main

# Terminal 2: Serve web UI
python -m http.server 8080 --directory web

# Open: http://localhost:8080
```

### Install Dependencies
```bash
cd GitHub_AI_Agent
pip install -r requirements.txt
```

## Testing

### Test with Sample Data
```bash
cd GitHub_AI_Agent
python run_example.py
```

### Test Specific Tool
```python
from tools.cleaning_tools import InspectDataTool
import pandas as pd

df = pd.read_csv('test.csv')
tool = InspectDataTool()
result = tool.execute(df)
print(result['metadata'])
```

## Git

### Add and Commit
```bash
git add .
git commit -m "Your message"
git push
```

### Check Status
```bash
git status
```

## Cleanup

### Remove Generated Data
```bash
cd GitHub_AI_Agent
rm -rf data/uploads/* data/cleaned/* data/cache/*
```

### Remove Python Cache
```bash
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
```

## Common Use Cases

### Clean a CSV File
```python
from agents.simple_cleaning_agent import SimpleCleaningAgent
import pandas as pd

df = pd.read_csv('messy_data.csv')
agent = SimpleCleaningAgent(df)
result = agent.run()
result['cleaned_df'].to_csv('clean_data.csv', index=False)
print(f"Quality: {result['report']['quality_score']}/10")
```

### Upload via API
```bash
# Start server first
cd GitHub_AI_Agent
python -m api.main

# Then upload (in another terminal)
curl -X POST http://localhost:8000/api/upload \
  -F "file=@data.csv"
```

### Batch Process Multiple Files
```python
import os
import pandas as pd
from agents.simple_cleaning_agent import SimpleCleaningAgent

for file in os.listdir('messy_data'):
    if file.endswith('.csv'):
        df = pd.read_csv(f'messy_data/{file}')
        agent = SimpleCleaningAgent(df)
        result = agent.run()
        result['cleaned_df'].to_csv(f'clean_data/{file}', index=False)
```
