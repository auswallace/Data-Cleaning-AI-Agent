"""
Concrete data cleaning tools for the agent
Each tool performs a specific cleaning operation
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from sklearn.impute import KNNImputer
from sklearn.ensemble import IsolationForest
import logging
from .base_tool import Tool

logger = logging.getLogger(__name__)


class InspectDataTool(Tool):
    """Inspect dataset structure and quality"""

    def __init__(self):
        super().__init__(
            name="inspect_data",
            description="Analyze dataset structure, data types, missing values, and quality issues"
        )

    def execute(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Generate comprehensive data profile"""
        try:
            profile = {
                "shape": df.shape,
                "columns": list(df.columns),
                "dtypes": df.dtypes.astype(str).to_dict(),
                "missing_values": df.isnull().sum().to_dict(),
                "missing_percentage": (df.isnull().sum() / len(df) * 100).to_dict(),
                "duplicate_rows": df.duplicated().sum(),
                "numeric_columns": list(df.select_dtypes(include=[np.number]).columns),
                "categorical_columns": list(df.select_dtypes(include=['object']).columns),
                "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
            }

            # Basic statistics for numeric columns
            if profile["numeric_columns"]:
                profile["numeric_stats"] = df[profile["numeric_columns"]].describe().to_dict()

            message = f"Inspected dataset: {df.shape[0]} rows, {df.shape[1]} columns"

            result = {
                "df": df,
                "success": True,
                "message": message,
                "metadata": profile
            }
            self.log_execution(result)
            return result

        except Exception as e:
            logger.error(f"Data inspection failed: {e}")
            return {
                "df": df,
                "success": False,
                "message": f"Inspection failed: {str(e)}",
                "metadata": {}
            }

    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }


class HandleMissingValuesTool(Tool):
    """Handle missing values using intelligent strategies"""

    def __init__(self):
        super().__init__(
            name="handle_missing_values",
            description="Fill or remove missing values using KNN imputation for numeric, mode for categorical"
        )

    def execute(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Handle missing values intelligently"""
        strategy = kwargs.get("strategy", "auto")  # auto, drop, fill
        threshold = kwargs.get("threshold", 0.5)  # Drop columns with >50% missing

        try:
            df_clean = df.copy()
            initial_missing = df_clean.isnull().sum().sum()
            changes = []

            # Drop columns with too many missing values
            missing_pct = df_clean.isnull().sum() / len(df_clean)
            cols_to_drop = missing_pct[missing_pct > threshold].index.tolist()

            if cols_to_drop:
                df_clean = df_clean.drop(columns=cols_to_drop)
                changes.append(f"Dropped {len(cols_to_drop)} columns with >{threshold*100}% missing: {cols_to_drop}")

            # KNN imputation for numeric columns
            numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0 and df_clean[numeric_cols].isnull().any().any():
                imputer = KNNImputer(n_neighbors=5)
                df_clean[numeric_cols] = imputer.fit_transform(df_clean[numeric_cols])
                changes.append(f"KNN imputed {len(numeric_cols)} numeric columns")

            # Mode imputation for categorical columns
            categorical_cols = df_clean.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                if df_clean[col].isnull().any():
                    mode_value = df_clean[col].mode()[0] if not df_clean[col].mode().empty else "Unknown"
                    df_clean[col].fillna(mode_value, inplace=True)
                    changes.append(f"Mode imputed column '{col}' with '{mode_value}'")

            final_missing = df_clean.isnull().sum().sum()
            message = f"Handled missing values: {initial_missing} → {final_missing} missing values"

            result = {
                "df": df_clean,
                "success": True,
                "message": message,
                "metadata": {
                    "initial_missing": int(initial_missing),
                    "final_missing": int(final_missing),
                    "changes": changes,
                    "dropped_columns": cols_to_drop
                }
            }
            self.log_execution(result)
            return result

        except Exception as e:
            logger.error(f"Missing value handling failed: {e}")
            return {
                "df": df,
                "success": False,
                "message": f"Missing value handling failed: {str(e)}",
                "metadata": {}
            }

    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "strategy": {
                    "type": "string",
                    "enum": ["auto", "drop", "fill"],
                    "description": "Strategy for handling missing values"
                },
                "threshold": {
                    "type": "number",
                    "description": "Drop columns with missing percentage above this threshold"
                }
            },
            "required": []
        }


class DetectOutliersTool(Tool):
    """Detect and optionally remove outliers using Isolation Forest"""

    def __init__(self):
        super().__init__(
            name="detect_outliers",
            description="Detect outliers in numeric columns using Isolation Forest algorithm"
        )

    def execute(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Detect outliers using Isolation Forest"""
        contamination = kwargs.get("contamination", 0.05)
        remove = kwargs.get("remove", False)

        try:
            df_result = df.copy()
            numeric_cols = df_result.select_dtypes(include=[np.number]).columns.tolist()

            if not numeric_cols:
                return {
                    "df": df,
                    "success": True,
                    "message": "No numeric columns found for outlier detection",
                    "metadata": {"outlier_count": 0}
                }

            # Use Isolation Forest (proper outlier detection, not random model!)
            iso_forest = IsolationForest(
                contamination=contamination,
                random_state=42,
                n_estimators=100
            )

            # Fit on numeric columns only
            predictions = iso_forest.fit_predict(df_result[numeric_cols])

            # -1 indicates outlier
            outlier_mask = predictions == -1
            outlier_count = outlier_mask.sum()

            # Add outlier flag column
            df_result['_is_outlier'] = outlier_mask

            metadata = {
                "outlier_count": int(outlier_count),
                "outlier_percentage": float(outlier_count / len(df) * 100),
                "numeric_columns_analyzed": numeric_cols
            }

            if remove:
                df_result = df_result[~outlier_mask].drop(columns=['_is_outlier'])
                message = f"Detected and removed {outlier_count} outliers ({outlier_count/len(df)*100:.1f}%)"
            else:
                message = f"Detected {outlier_count} outliers ({outlier_count/len(df)*100:.1f}%), marked in '_is_outlier' column"

            result = {
                "df": df_result,
                "success": True,
                "message": message,
                "metadata": metadata
            }
            self.log_execution(result)
            return result

        except Exception as e:
            logger.error(f"Outlier detection failed: {e}")
            return {
                "df": df,
                "success": False,
                "message": f"Outlier detection failed: {str(e)}",
                "metadata": {}
            }

    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "contamination": {
                    "type": "number",
                    "description": "Expected proportion of outliers (0.0 to 0.5)"
                },
                "remove": {
                    "type": "boolean",
                    "description": "Whether to remove outliers or just flag them"
                }
            },
            "required": []
        }


class RemoveDuplicatesTool(Tool):
    """Remove duplicate rows from dataset"""

    def __init__(self):
        super().__init__(
            name="remove_duplicates",
            description="Remove duplicate rows from the dataset"
        )

    def execute(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Remove duplicate rows"""
        subset = kwargs.get("subset", None)  # Specific columns to check
        keep = kwargs.get("keep", "first")  # Which duplicate to keep

        try:
            initial_rows = len(df)
            df_clean = df.drop_duplicates(subset=subset, keep=keep)
            duplicates_removed = initial_rows - len(df_clean)

            message = f"Removed {duplicates_removed} duplicate rows"

            result = {
                "df": df_clean,
                "success": True,
                "message": message,
                "metadata": {
                    "initial_rows": initial_rows,
                    "final_rows": len(df_clean),
                    "duplicates_removed": duplicates_removed
                }
            }
            self.log_execution(result)
            return result

        except Exception as e:
            logger.error(f"Duplicate removal failed: {e}")
            return {
                "df": df,
                "success": False,
                "message": f"Duplicate removal failed: {str(e)}",
                "metadata": {}
            }

    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "subset": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Columns to consider for identifying duplicates"
                },
                "keep": {
                    "type": "string",
                    "enum": ["first", "last", "false"],
                    "description": "Which duplicate to keep"
                }
            },
            "required": []
        }


class StandardizeColumnNamesTool(Tool):
    """Standardize column names to snake_case"""

    def __init__(self):
        super().__init__(
            name="standardize_column_names",
            description="Convert column names to lowercase snake_case format"
        )

    def execute(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Standardize column names"""
        try:
            df_clean = df.copy()
            original_columns = df_clean.columns.tolist()

            # Convert to snake_case
            new_columns = []
            for col in original_columns:
                # Replace spaces and special chars with underscore
                new_col = col.lower().strip()
                new_col = new_col.replace(' ', '_').replace('-', '_')
                # Remove multiple underscores
                while '__' in new_col:
                    new_col = new_col.replace('__', '_')
                new_columns.append(new_col)

            df_clean.columns = new_columns
            changes = [f"{old} → {new}" for old, new in zip(original_columns, new_columns) if old != new]

            message = f"Standardized {len(changes)} column names to snake_case"

            result = {
                "df": df_clean,
                "success": True,
                "message": message,
                "metadata": {
                    "changes": changes,
                    "original_columns": original_columns,
                    "new_columns": new_columns
                }
            }
            self.log_execution(result)
            return result

        except Exception as e:
            logger.error(f"Column standardization failed: {e}")
            return {
                "df": df,
                "success": False,
                "message": f"Column standardization failed: {str(e)}",
                "metadata": {}
            }

    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
