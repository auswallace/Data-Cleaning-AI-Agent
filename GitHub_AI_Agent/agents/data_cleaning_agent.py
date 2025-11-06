"""
Autonomous Data Cleaning Agent with Planning, Tool Selection, and Memory

This is a REAL agent that:
- Analyzes data and creates a cleaning plan
- Selects appropriate tools to use
- Maintains memory of what it's done
- Validates results and iterates if needed
"""
import logging
from typing import List, Dict, Any, Optional
import pandas as pd
from openai import OpenAI
import json
from datetime import datetime

from ..tools.cleaning_tools import (
    InspectDataTool,
    HandleMissingValuesTool,
    DetectOutliersTool,
    RemoveDuplicatesTool,
    StandardizeColumnNamesTool
)
from ..config.settings import (
    OPENAI_API_KEY,
    DEFAULT_LLM_MODEL,
    LLM_TEMPERATURE,
    MAX_AGENT_ITERATIONS,
    AGENT_MEMORY_SIZE
)

logger = logging.getLogger(__name__)


class DataCleaningAgent:
    """
    Autonomous agent for data cleaning with planning and tool selection
    """

    def __init__(self, df: pd.DataFrame, api_key: Optional[str] = None):
        """
        Initialize the agent with a dataset

        Args:
            df: Input DataFrame to clean
            api_key: Optional OpenAI API key (uses env var if not provided)
        """
        self.df = df.copy()
        self.original_df = df.copy()
        self.api_key = api_key or OPENAI_API_KEY

        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")

        self.client = OpenAI(api_key=self.api_key)

        # Initialize tools
        self.tools = {
            "inspect_data": InspectDataTool(),
            "handle_missing_values": HandleMissingValuesTool(),
            "detect_outliers": DetectOutliersTool(),
            "remove_duplicates": RemoveDuplicatesTool(),
            "standardize_column_names": StandardizeColumnNamesTool(),
        }

        # Agent memory
        self.memory: List[Dict[str, Any]] = []
        self.iterations = 0
        self.max_iterations = MAX_AGENT_ITERATIONS

    def run(self) -> Dict[str, Any]:
        """
        Main agent loop: Plan → Execute → Validate → Iterate

        Returns:
            Dictionary with cleaned DataFrame and execution report
        """
        logger.info("Starting Data Cleaning Agent...")

        # Step 1: Initial inspection
        inspection_result = self.tools["inspect_data"].execute(self.df)
        self._add_to_memory("inspect_data", inspection_result)

        # Step 2: Create cleaning plan
        plan = self._create_plan(inspection_result["metadata"])
        logger.info(f"Agent created plan: {json.dumps(plan, indent=2)}")

        # Step 3: Execute plan
        for step in plan:
            if self.iterations >= self.max_iterations:
                logger.warning(f"Max iterations ({self.max_iterations}) reached")
                break

            tool_name = step.get("tool")
            params = step.get("parameters", {})
            reason = step.get("reason", "")

            logger.info(f"Iteration {self.iterations + 1}: Using {tool_name} - {reason}")

            if tool_name not in self.tools:
                logger.error(f"Unknown tool: {tool_name}")
                continue

            # Execute tool
            result = self.tools[tool_name].execute(self.df, **params)

            if result["success"]:
                self.df = result["df"]
                self._add_to_memory(tool_name, result)
                logger.info(f"✓ {result['message']}")
            else:
                logger.error(f"✗ {result['message']}")

            self.iterations += 1

        # Step 4: Final validation
        validation = self._validate_cleaning()

        # Step 5: Generate report
        report = self._generate_report(validation)

        return {
            "cleaned_df": self.df,
            "original_df": self.original_df,
            "report": report,
            "memory": self.memory,
            "iterations": self.iterations
        }

    def _create_plan(self, inspection_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Use LLM to analyze data and create cleaning plan

        Returns:
            List of steps, each with: {tool, parameters, reason}
        """
        # Build context from inspection
        context = f"""
You are a data cleaning expert. Analyze this dataset and create a cleaning plan.

Dataset Profile:
- Shape: {inspection_data['shape']}
- Columns: {inspection_data['columns']}
- Missing Values: {inspection_data['missing_values']}
- Duplicate Rows: {inspection_data['duplicate_rows']}
- Numeric Columns: {inspection_data['numeric_columns']}
- Categorical Columns: {inspection_data['categorical_columns']}

Available Tools:
1. standardize_column_names - Convert column names to snake_case
2. handle_missing_values - Fill or drop missing values (KNN for numeric, mode for categorical)
3. remove_duplicates - Remove duplicate rows
4. detect_outliers - Find outliers using Isolation Forest (can flag or remove)

Create a step-by-step cleaning plan. Return ONLY a JSON array of steps.
Each step should have: {{"tool": "tool_name", "parameters": {{}}, "reason": "why this step"}}

Example:
[
  {{"tool": "standardize_column_names", "parameters": {{}}, "reason": "Column names have spaces and inconsistent casing"}},
  {{"tool": "remove_duplicates", "parameters": {{}}, "reason": "Dataset has 5 duplicate rows"}},
  {{"tool": "handle_missing_values", "parameters": {{"threshold": 0.5}}, "reason": "Several columns have missing values"}},
  {{"tool": "detect_outliers", "parameters": {{"contamination": 0.05, "remove": false}}, "reason": "Flag outliers for review"}}
]

Return ONLY the JSON array, no other text.
"""

        try:
            response = self.client.chat.completions.create(
                model=DEFAULT_LLM_MODEL,
                messages=[{"role": "user", "content": context}],
                temperature=LLM_TEMPERATURE,
            )

            plan_text = response.choices[0].message.content.strip()

            # Extract JSON if wrapped in code blocks
            if "```json" in plan_text:
                plan_text = plan_text.split("```json")[1].split("```")[0].strip()
            elif "```" in plan_text:
                plan_text = plan_text.split("```")[1].split("```")[0].strip()

            plan = json.loads(plan_text)
            return plan

        except Exception as e:
            logger.error(f"Failed to create plan: {e}")
            # Fallback to default plan
            return self._default_plan(inspection_data)

    def _default_plan(self, inspection_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback plan if LLM fails"""
        plan = []

        # Always standardize column names
        plan.append({
            "tool": "standardize_column_names",
            "parameters": {},
            "reason": "Ensure consistent column naming"
        })

        # Remove duplicates if present
        if inspection_data['duplicate_rows'] > 0:
            plan.append({
                "tool": "remove_duplicates",
                "parameters": {},
                "reason": f"Remove {inspection_data['duplicate_rows']} duplicate rows"
            })

        # Handle missing values if present
        total_missing = sum(inspection_data['missing_values'].values())
        if total_missing > 0:
            plan.append({
                "tool": "handle_missing_values",
                "parameters": {"threshold": 0.5},
                "reason": f"Handle {total_missing} missing values"
            })

        # Detect outliers in numeric data
        if len(inspection_data['numeric_columns']) > 0:
            plan.append({
                "tool": "detect_outliers",
                "parameters": {"contamination": 0.05, "remove": False},
                "reason": "Flag potential outliers for review"
            })

        return plan

    def _validate_cleaning(self) -> Dict[str, Any]:
        """
        Use LLM to validate cleaning quality

        Returns:
            Validation results with score and feedback
        """
        # Get current state
        current_inspection = self.tools["inspect_data"].execute(self.df)

        context = f"""
You are a data quality expert. Evaluate this data cleaning job.

BEFORE CLEANING:
- Shape: {self.original_df.shape}
- Missing values: {self.original_df.isnull().sum().sum()}
- Duplicates: {self.original_df.duplicated().sum()}

AFTER CLEANING:
- Shape: {self.df.shape}
- Missing values: {self.df.isnull().sum().sum()}
- Duplicates: {self.df.duplicated().sum()}

ACTIONS TAKEN:
{json.dumps([m['message'] for m in self.memory], indent=2)}

Rate the cleaning quality from 1-10 and provide brief feedback.
Return JSON: {{"score": 8, "feedback": "Good cleaning, but...", "suggestions": ["Add X", "Consider Y"]}}
"""

        try:
            response = self.client.chat.completions.create(
                model=DEFAULT_LLM_MODEL,
                messages=[{"role": "user", "content": context}],
                temperature=LLM_TEMPERATURE,
            )

            result_text = response.choices[0].message.content.strip()

            # Extract JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            validation = json.loads(result_text)
            return validation

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return {
                "score": 5,
                "feedback": "Validation failed, manual review recommended",
                "suggestions": []
            }

    def _generate_report(self, validation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive cleaning report"""
        return {
            "summary": {
                "original_shape": self.original_df.shape,
                "cleaned_shape": self.df.shape,
                "rows_removed": self.original_df.shape[0] - self.df.shape[0],
                "columns_removed": self.original_df.shape[1] - self.df.shape[1],
                "iterations": self.iterations
            },
            "quality_score": validation.get("score", 0),
            "feedback": validation.get("feedback", ""),
            "suggestions": validation.get("suggestions", []),
            "actions_taken": [m["message"] for m in self.memory],
            "timestamp": datetime.now().isoformat()
        }

    def _add_to_memory(self, tool_name: str, result: Dict[str, Any]):
        """Add execution to agent memory"""
        self.memory.append({
            "iteration": self.iterations,
            "tool": tool_name,
            "success": result["success"],
            "message": result["message"],
            "metadata": result.get("metadata", {}),
            "timestamp": datetime.now().isoformat()
        })

        # Keep only recent memory
        if len(self.memory) > AGENT_MEMORY_SIZE:
            self.memory = self.memory[-AGENT_MEMORY_SIZE:]
