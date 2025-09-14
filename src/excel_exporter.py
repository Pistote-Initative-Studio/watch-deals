"""Excel export utilities."""

import pandas as pd


def export_to_excel(df: pd.DataFrame, filename: str = "listings.xlsx") -> None:
    """Export the provided DataFrame to an Excel file."""
    df.to_excel(filename, index=False)
