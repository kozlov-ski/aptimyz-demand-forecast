import numpy as np
import pandas as pd


def eda(df, date_col="date"):
    """
    Generate comprehensive EDA statistics for time series forecasting dataset
    """
    print(f"Dataset Shape: {df.shape[0]:,} rows, {df.shape[1]} columns")
    print(f"Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

    print(f"\nData Types:")
    print(df.dtypes.to_string())

    null_counts = df.isnull().sum()
    total_nulls = null_counts.sum()
    if total_nulls == 0:
        print("\nNo missing values in any column")
    else:
        print("\nMissing values:")
        for col, count in null_counts.items():
            if count > 0:
                pct = count / len(df) * 100
                print(f"{col}: {count:,} ({pct:.1f}%)")

    print("\nUniqueness:")
    for col in df.columns:
        unique = df[col].nunique()
        print(f"{col}: {unique:,} unique values")

    numerical_cols = df.select_dtypes(include=[np.number]).columns
    if len(numerical_cols) > 0:
        print("\nSummary Statistics:")
        print(df[numerical_cols].describe())

        print("\nSkewness & Kurtosis:")
        print("  Skewness: 0=symmetric, positive=right-skewed, negative=left-skewed")
        print("  Kurtosis: near 0=normal tails, >0=heavy tails, <0=light tails")
        for col in numerical_cols:
            sk = df[col].skew()
            ku = df[col].kurtosis()
            print(f"{col}: Skewness {sk:.3f}, Kurtosis {ku:.3f}")

    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    for col in cat_cols:
        if col == date_col:
            continue
        print(f"\n{col} Distribution (top 5):")
        dist = df[col].value_counts().head()
        print(dist.to_string())

    if date_col in df.columns:
        print(f"\nDate Range: {df[date_col].min()} to {df[date_col].max()}")
        dates = pd.to_datetime(df[date_col]).sort_values().unique()
        expected_days = (dates.max() - dates.min()).days + 1
        actual_days = len(dates)
        print(f"Total Days in Range: {expected_days}")
        if actual_days == expected_days:
            print("No missing days")
        else:
            daily_diff = expected_days - actual_days
            print(f"{daily_diff:,} missing days")
