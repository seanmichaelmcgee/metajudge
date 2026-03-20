"""Export helpers — convert notebook sweep data to standard audit DataFrames."""
import pandas as pd
from typing import Any, Dict, List


def sweep_results_to_audit_df(
    sweep_results: Dict[str, List[Dict[str, Any]]]
) -> pd.DataFrame:
    """Convert Cell 8 sweep_results dict to a flat audit DataFrame.

    Input format (from notebook Cell 8):
        {model_name: [{item_id, mechanism_primary, model_answer, confidence,
                        is_correct, brier_score, ...}, ...]}

    Output: DataFrame with columns:
        model, item_id, mechanism_primary, model_answer, confidence,
        is_correct, brier_score
    """
    rows = []
    for model_name, items in sweep_results.items():
        for item in items:
            row = dict(item)
            row["model"] = model_name
            rows.append(row)
    return pd.DataFrame(rows)


def headline_results_to_df(
    headline_results: Dict[str, Dict[str, Any]]
) -> pd.DataFrame:
    """Convert Cell 7 headline results to a summary DataFrame.

    Input format:
        {model_name: {headline_score, n_items, accuracy, ...}}
    """
    rows = []
    for model_name, stats in headline_results.items():
        row = dict(stats)
        row["model"] = model_name
        rows.append(row)
    return pd.DataFrame(rows)
