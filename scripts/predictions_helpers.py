import pandas as pd
import numpy as np


def remove_duplicates(df: pd.DataFrame, key=("series_id", "date"), atol=1e-2):
    """Remove duplicate rows by key if values match within tolerance, else raise an error."""
    num_cols = df.select_dtypes("number").columns.difference(key)

    # find groups with differences > atol
    spread = df.groupby(list(key))[num_cols].apply(lambda g: (g.max() - g.min()).max())
    conflicts = spread[spread > atol]

    if not conflicts.empty:
        raise ValueError(f"Conflicting duplicates (>{atol}):\n{conflicts}")

    return df.drop_duplicates(subset=key, keep="first")


def drop_header_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows that look like duplicated header lines inside the DataFrame."""
    mask = (df.astype(str) == df.columns).all(axis=1)
    return df[~mask].copy()


def cast_types(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = ["p10", "p50", "p90", "mean"]
    df[numeric_cols] = df[numeric_cols].astype(np.float64)

    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")

    return df
