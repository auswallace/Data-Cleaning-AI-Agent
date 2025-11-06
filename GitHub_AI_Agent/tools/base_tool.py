"""
Base Tool class for the agent system
All data cleaning operations inherit from this
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import pandas as pd
from datetime import datetime


class Tool(ABC):
    """Base class for all agent tools"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.execution_history = []

    @abstractmethod
    def execute(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool on a DataFrame

        Returns:
            Dict with keys:
                - df: Modified DataFrame
                - success: Boolean
                - message: Description of what was done
                - metadata: Additional information
        """
        pass

    def log_execution(self, result: Dict[str, Any]):
        """Log tool execution for agent memory"""
        self.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "success": result.get("success", False),
            "message": result.get("message", ""),
            "metadata": result.get("metadata", {})
        })

    def get_schema(self) -> Dict[str, Any]:
        """Return tool schema for LLM function calling"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self._get_parameters()
        }

    @abstractmethod
    def _get_parameters(self) -> Dict[str, Any]:
        """Define parameters for this tool"""
        pass

    def __repr__(self):
        return f"Tool({self.name})"
