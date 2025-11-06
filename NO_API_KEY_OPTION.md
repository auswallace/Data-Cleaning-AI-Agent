# Using Without API Keys - Your Options

## Why Does It Need an API Key?

The **AI agent** uses an LLM (Large Language Model) for two things:

1. **Planning** - Analyzes YOUR specific data and creates a custom cleaning strategy
2. **Validation** - Scores quality (1-10) and provides intelligent feedback

**Without AI:** The agent would just run fixed steps (like your v1) - not a real "intelligent agent"

---

## 🆓 Option 1: Use Free Credits

### OpenAI (Recommended)
- Sign up at https://platform.openai.com
- Get **$5 free credit** (enough for ~16,000 cleanings!)
- v2 uses `gpt-4o-mini` - only $0.0003 per cleaning

### Anthropic Claude
- Sign up at https://console.anthropic.com
- Get free credits
- Already supported in the code!

---

## 🔧 Option 2: Simple Agent (No AI Required!)

I created a **second agent** that works WITHOUT any API key:

### How to Use:

```python
from agents.simple_cleaning_agent import SimpleCleaningAgent
import pandas as pd

df = pd.read_csv('messy.csv')
agent = SimpleCleaningAgent(df)  # No API key needed!
result = agent.run()

print(f"Quality: {result['report']['quality_score']}/10")
result['cleaned_df'].to_csv('clean.csv', index=False)
```

### Or run the example:

```bash
python example_no_ai.py
```

### What's Different?

| Feature | AI Agent (with API key) | Simple Agent (no API key) |
|---------|-------------------------|---------------------------|
| Planning | ✅ Custom per dataset | ⚙️ Fixed rule-based |
| Validation | ✅ AI scores & feedback | ⚙️ Basic metrics |
| Quality Score | ✅ Intelligent (1-10) | ⚙️ Rule-based (1-10) |
| Suggestions | ✅ Smart recommendations | ⚙️ Basic checks |
| Cost | $0.0003 per cleaning | $0 (FREE!) |
| Adaptability | ✅ Adapts to data | ⚙️ Fixed strategy |

---

## 🏠 Option 3: Use Local LLM (Ollama)

Run AI **locally** on your computer (free, private):

```bash
# Install Ollama
brew install ollama  # Mac
# or download from ollama.ai

# Download a model
ollama pull llama3.2

# Use in Python
pip install ollama

# Modify agent to use Ollama instead of OpenAI
```

Update `agents/data_cleaning_agent.py`:

```python
import ollama

def _create_plan(self, inspection_data):
    response = ollama.chat(
        model='llama3.2',
        messages=[{'role': 'user', 'content': context}]
    )
    # Rest of code...
```

**Pros:** Free, private, no API needed
**Cons:** Requires ~8GB RAM, slower than cloud APIs

---

## 🔀 Option 4: Make API Key Optional

Modify `agents/__init__.py`:

```python
from .simple_cleaning_agent import SimpleCleaningAgent
from .data_cleaning_agent import DataCleaningAgent

def create_agent(df, api_key=None):
    """
    Auto-select agent based on API key availability
    """
    if api_key:
        return DataCleaningAgent(df, api_key=api_key)
    else:
        print("⚠️  No API key provided. Using simple rule-based agent.")
        return SimpleCleaningAgent(df)
```

Then use it:

```python
from agents import create_agent

# Will use SimpleAgent (no API key)
agent = create_agent(df)

# Will use AI Agent (with API key)
agent = create_agent(df, api_key="sk-...")
```

---

## 🤔 Which Option Should You Choose?

### Use **AI Agent** (with API key) if:
- ✅ You want intelligent, adaptive cleaning
- ✅ You want quality validation & feedback
- ✅ You can afford $0.0003 per cleaning
- ✅ You want the best results

**Get API key:** https://platform.openai.com ($5 free = 16,000 cleanings!)

### Use **Simple Agent** (no API key) if:
- ✅ You want completely free operation
- ✅ You need reproducible, deterministic results
- ✅ You're okay with fixed cleaning rules
- ✅ You want privacy (no API calls)

**Run:** `python example_no_ai.py`

### Use **Local LLM** (Ollama) if:
- ✅ You want AI without cloud APIs
- ✅ You have 8GB+ RAM available
- ✅ You need complete privacy
- ✅ You're okay with slower processing

**Install:** https://ollama.ai

---

## 📊 Comparison

| | AI Agent | Simple Agent | Local LLM |
|---|---|---|---|
| **Cost** | $0.0003/clean | $0 | $0 |
| **API Key** | ✅ Required | ❌ None | ❌ None |
| **Intelligence** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Speed** | Fast (~5s) | Very Fast (<1s) | Slow (~30s) |
| **Privacy** | Cloud API | Fully local | Fully local |
| **Adaptability** | High | Fixed rules | High |
| **Setup Difficulty** | Easy | Easiest | Medium |

---

## 🚀 Quick Decision Tree

```
Do you have an OpenAI/Anthropic API key?
│
├── YES → Use AI Agent (best results)
│         python example_usage.py
│
└── NO → Do you want AI?
         │
         ├── YES → Get free API key ($5 credit)
         │         OR use Ollama (local)
         │
         └── NO → Use Simple Agent (rule-based)
                   python example_no_ai.py
```

---

## 💡 My Recommendation

1. **Start with Simple Agent** - See if it works for your needs (free!)
   ```bash
   python example_no_ai.py
   ```

2. **If you need smarter cleaning** - Get OpenAI free $5 credit
   - Go to https://platform.openai.com
   - Sign up (requires credit card but won't charge without permission)
   - Get $5 free credit = 16,000+ cleanings with v2!

3. **For production** - Use AI Agent (costs pennies, much better results)

---

## 📝 Files to Check

- **With AI:** `agents/data_cleaning_agent.py` (requires API key)
- **Without AI:** `agents/simple_cleaning_agent.py` (no API key!)
- **Example with AI:** `example_usage.py`
- **Example without AI:** `example_no_ai.py`

---

## ❓ FAQ

**Q: Can't I just remove the API key requirement?**
A: Yes! Use `SimpleCleaningAgent` - it's specifically built for this.

**Q: Why not make everything rule-based?**
A: Rule-based works, but AI provides:
- Adaptive strategies for different data types
- Intelligent quality validation
- Contextual suggestions
- Better results overall

**Q: Is the Simple Agent good enough?**
A: For basic cleaning, yes! It handles:
- Missing values
- Duplicates
- Outliers
- Column standardization

But the AI agent is **smarter** and provides better feedback.

**Q: How much does the API key actually cost?**
A: With `gpt-4o-mini`:
- **1 cleaning = $0.0003** (less than a penny!)
- **100 cleanings = $0.03** (3 cents)
- **1,000 cleanings = $0.30** (30 cents)
- **10,000 cleanings = $3**

OpenAI gives $5 free = **16,000+ free cleanings!**

**Q: Can I use both agents?**
A: Yes! Use Simple Agent for quick/free cleaning, AI Agent for important datasets.

---

## 🎯 Bottom Line

**You have 4 options:**

1. ✅ **Get free OpenAI credits** ($5 = 16,000 cleanings) - Best option!
2. ✅ **Use SimpleAgent** (no API key) - Good for basic cleaning
3. ✅ **Use Ollama** (local AI) - Privacy + free, but slower
4. ✅ **Use Anthropic Claude** (alternative to OpenAI)

**My recommendation:** Just get the free $5 OpenAI credit. It'll last you forever and gives way better results!

---

**Quick start without API key:**
```bash
python example_no_ai.py
```

**Quick start with API key:**
```bash
# Add to .env: OPENAI_API_KEY=sk-...
python example_usage.py
```
