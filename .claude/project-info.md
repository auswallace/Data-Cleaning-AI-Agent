# Data Cleaning Agent - Project Information

## Purpose

Personal tool to automate data cleaning tasks I was repeating in every project.

**Problem**: Kept copy-pasting the same data cleaning code (handling missing values, removing duplicates, fixing column names, detecting outliers).

**Solution**: Built a reusable agent that does it automatically.

## Architecture

### Simple Agent Pattern

**Not** a complex AI agent with LLM planning. Just a simple, rule-based cleaning agent:

1. **Inspect** → Analyze data structure
2. **Plan** → Fixed strategy based on what's found
3. **Execute** → Run cleaning tools in sequence
4. **Validate** → Score quality (1-10)
5. **Report** → Show what was done

### Tool System

Each cleaning operation is a standalone tool:

```python
class Tool(ABC):
    def execute(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        # Do cleaning
        return {
            "df": cleaned_df,
            "success": True,
            "message": "What was done",
            "metadata": {...}
        }
```

Tools available:
1. `InspectDataTool` - Analyze structure
2. `HandleMissingValuesTool` - Fill/drop missing values
3. `DetectOutliersTool` - Find anomalies
4. `RemoveDuplicatesTool` - Remove duplicates
5. `StandardizeColumnNamesTool` - Fix column names

### Three Interfaces

1. **Python** - Direct import and use
2. **Web UI** - Drag-drop interface
3. **REST API** - HTTP endpoints

All use the same core `SimpleCleaningAgent`.

## Key Design Decisions

### No API Keys
- **Why**: Didn't want external dependencies or costs
- **How**: Uses only scikit-learn (Isolation Forest for outliers)
- **Tradeoff**: Less "intelligent" but more reliable and free

### Fixed Strategy
- **Why**: Simpler and more predictable than AI planning
- **How**: Always runs same sequence based on data inspection
- **Tradeoff**: Not adaptive, but works well for common cases

### Rule-Based Quality Scoring
- **Why**: No LLM needed for validation
- **How**: Scores based on improvements (missing values fixed, duplicates removed)
- **Tradeoff**: Simple scoring, but transparent

### Single Agent File
- **Why**: Easy to understand and modify
- **Location**: `agents/simple_cleaning_agent.py`
- **Benefit**: Everything in one place

## Technologies Used

**Core**:
- pandas - Data manipulation
- numpy - Numerical operations
- scikit-learn - Isolation Forest for outliers, KNN for imputation

**API**:
- FastAPI - REST API
- uvicorn - ASGI server

**Web**:
- Pure HTML/JavaScript - No frameworks
- Fetch API - HTTP requests

## What Makes It Different

### vs Other Data Cleaning Tools

**This tool**:
- ✅ Zero configuration
- ✅ Works offline
- ✅ No costs
- ✅ Simple to understand
- ✅ Easy to extend

**Commercial tools** (Trifacta, etc.):
- ❌ Complex setup
- ❌ Expensive
- ❌ Cloud-based
- ❌ Black box

**Custom scripts**:
- ❌ Rewrite every time
- ❌ No consistency
- ❌ Hard to share

## Limitations

**Good for**:
- Tabular data (CSV, Excel, etc.)
- Common cleaning tasks
- Quick iterations
- Exploratory data analysis

**Not good for**:
- Complex validation rules
- Domain-specific logic
- Time series data
- Multi-table relationships
- Production ETL pipelines

For complex needs, use proper ETL tools (Airflow, dbt, etc.)

## Future Enhancements (Maybe)

Low priority, but could add:
- Email/phone validation
- Date range checks
- Schema validation
- Export cleaning steps as code
- Batch file processing
- Cloud storage integration

Currently: Solves my problem, so not urgent.

## Version History

### v1 (Archived)
- Built with ChatGPT
- Had broken CatBoost model trained on random data
- Required OpenAI API key
- Overly complex

### v2 (Current)
- Rebuilt with Claude
- Fixed outlier detection (Isolation Forest)
- Removed API requirements
- Simplified architecture
- Actually works!

## Maintenance

**Active development**: No
**Status**: Works for my needs
**Updates**: Only when I find bugs or need new features
**Support**: Best effort, personal project

## Contributing

Open to:
- Bug reports
- Feature suggestions
- Pull requests

But keep in mind:
- Personal tool, not production library
- No SLAs or guarantees
- I'll merge what makes sense for my use case

## License

MIT - Do whatever you want with it
