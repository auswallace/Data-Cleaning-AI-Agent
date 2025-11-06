"""
Simple Data Cleaning Agent - NO AI REQUIRED

This version uses a fixed cleaning strategy without LLM planning.
Good for when you don't have an API key or want deterministic behavior.
"""
import logging
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime

try:
    from ..tools.cleaning_tools import (
        InspectDataTool,
        HandleMissingValuesTool,
        DetectOutliersTool,
        RemoveDuplicatesTool,
        StandardizeColumnNamesTool
    )
except ImportError:
    from tools.cleaning_tools import (
        InspectDataTool,
        HandleMissingValuesTool,
        DetectOutliersTool,
        RemoveDuplicatesTool,
        StandardizeColumnNamesTool
    )

logger = logging.getLogger(__name__)


class SimpleCleaningAgent:
    """
    Deterministic data cleaning agent that doesn't require AI API keys.
    Uses a fixed strategy based on data inspection.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initialize the agent with a dataset

        Args:
            df: Input DataFrame to clean
        """
        self.df = df.copy()
        self.original_df = df.copy()

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

    def run(self) -> Dict[str, Any]:
        """
        Main cleaning loop with fixed strategy

        Returns:
            Dictionary with cleaned DataFrame and execution report
        """
        logger.info("Starting Simple Data Cleaning Agent (no AI required)...")

        # Step 1: Initial inspection
        inspection_result = self.tools["inspect_data"].execute(self.df)
        self._add_to_memory("inspect_data", inspection_result)
        inspection = inspection_result["metadata"]

        # Step 2: Create fixed plan based on data characteristics
        plan = self._create_fixed_plan(inspection)
        logger.info(f"Agent created plan with {len(plan)} steps")

        # Step 3: Execute plan
        for step in plan:
            tool_name = step["tool"]
            params = step.get("parameters", {})
            reason = step.get("reason", "")

            logger.info(f"Step {self.iterations + 1}: {tool_name} - {reason}")

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

        # Step 4: Generate report (without AI validation)
        report = self._generate_report()

        return {
            "cleaned_df": self.df,
            "original_df": self.original_df,
            "report": report,
            "memory": self.memory,
            "iterations": self.iterations
        }

    def _create_fixed_plan(self, inspection: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create deterministic cleaning plan based on data inspection.
        No AI required - uses rule-based logic.

        Args:
            inspection: Data inspection results

        Returns:
            List of cleaning steps
        """
        plan = []

        # Step 1: Always standardize column names first
        plan.append({
            "tool": "standardize_column_names",
            "parameters": {},
            "reason": "Ensure consistent column naming convention"
        })

        # Step 2: Remove duplicates if present
        if inspection["duplicate_rows"] > 0:
            plan.append({
                "tool": "remove_duplicates",
                "parameters": {},
                "reason": f"Remove {inspection['duplicate_rows']} duplicate rows"
            })

        # Step 3: Handle missing values if present
        total_missing = sum(inspection["missing_values"].values())
        if total_missing > 0:
            missing_pct = total_missing / (inspection["shape"][0] * inspection["shape"][1]) * 100
            plan.append({
                "tool": "handle_missing_values",
                "parameters": {"threshold": 0.5, "strategy": "auto"},
                "reason": f"Handle {total_missing} missing values ({missing_pct:.1f}% of data)"
            })

        # Step 4: Detect outliers if there are numeric columns
        if len(inspection["numeric_columns"]) > 0:
            # Only remove outliers if dataset is large enough
            if inspection["shape"][0] > 100:
                plan.append({
                    "tool": "detect_outliers",
                    "parameters": {"contamination": 0.05, "remove": False},
                    "reason": f"Flag potential outliers in {len(inspection['numeric_columns'])} numeric columns"
                })
            else:
                plan.append({
                    "tool": "detect_outliers",
                    "parameters": {"contamination": 0.05, "remove": False},
                    "reason": "Dataset small, flagging outliers for manual review"
                })

        return plan

    def _generate_report(self) -> Dict[str, Any]:
        """Generate cleaning report without AI validation"""

        # Calculate basic quality metrics
        original_missing = self.original_df.isnull().sum().sum()
        cleaned_missing = self.df.isnull().sum().sum()
        original_dupes = self.original_df.duplicated().sum()
        cleaned_dupes = self.df.duplicated().sum()

        # Simple quality score based on improvements
        quality_score = 5  # Base score

        # Add points for fixing issues
        if original_missing > 0 and cleaned_missing == 0:
            quality_score += 2  # Fixed all missing values
        elif cleaned_missing < original_missing:
            quality_score += 1  # Reduced missing values

        if original_dupes > 0 and cleaned_dupes == 0:
            quality_score += 2  # Removed all duplicates
        elif cleaned_dupes < original_dupes:
            quality_score += 1  # Reduced duplicates

        # Cap at 10
        quality_score = min(quality_score, 10)

        # Generate feedback
        improvements = []
        if original_missing > cleaned_missing:
            improvements.append(f"Reduced missing values: {original_missing} → {cleaned_missing}")
        if original_dupes > cleaned_dupes:
            improvements.append(f"Removed duplicates: {original_dupes} → {cleaned_dupes}")
        if self.df.shape[0] < self.original_df.shape[0]:
            improvements.append(f"Removed {self.original_df.shape[0] - self.df.shape[0]} problematic rows")

        feedback = "Automated cleaning completed. " + " | ".join(improvements) if improvements else "Dataset was already clean."

        # Basic suggestions
        suggestions = []
        if cleaned_missing > 0:
            suggestions.append(f"Manual review recommended: {cleaned_missing} missing values remain")
        if cleaned_dupes > 0:
            suggestions.append(f"Check for partial duplicates: {cleaned_dupes} duplicates remain")
        if self.df.shape[1] < self.original_df.shape[1]:
            suggestions.append(f"Some columns were dropped - verify this is intended")

        return {
            "summary": {
                "original_shape": self.original_df.shape,
                "cleaned_shape": self.df.shape,
                "rows_removed": self.original_df.shape[0] - self.df.shape[0],
                "columns_removed": self.original_df.shape[1] - self.df.shape[1],
                "iterations": self.iterations
            },
            "quality_score": quality_score,
            "feedback": feedback,
            "suggestions": suggestions,
            "actions_taken": [m["message"] for m in self.memory],
            "timestamp": datetime.now().isoformat(),
            "mode": "rule-based (no AI)"
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
