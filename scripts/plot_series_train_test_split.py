import matplotlib.pyplot as plt


def plot_series_train_test_split(
    df,
    series_id,
    horizon,
    smooth_window=0,
    date_col="date",
    series_col="series_id",
    target_col="sales",
    fig=None,
    ax=None,
):
    """
    Plot a time series for a given series_id with train/test split indication.

    Parameters:
    - df: pandas DataFrame with date, sales, series_id columns
    - series_id: string, the series identifier to plot
    - horizon: int, number of days for test set
    - smooth_window: int, window size for moving average smoothing (0 means no smoothing)
    - date_col: str, column name for date
    - series_col: str, column name for series_id
    - target_col: str, column name for sales/target

    Returns:
    - matplotlib.figure.Figure
    """
    # Filter for the specific series
    series_df = (
        df[df[series_col] == series_id]
        .copy()
        .sort_values(date_col)
        .reset_index(drop=True)
    )

    # Calculate split index (last 'horizon' rows as test)
    if len(series_df) <= horizon:
        raise ValueError(
            f"Horizon {horizon} is too large for series with {len(series_df)} data points"
        )

    split_idx = len(series_df) - horizon

    # Apply smoothing if requested
    if smooth_window > 0:
        series_df[target_col] = (
            series_df[target_col].rolling(window=smooth_window, min_periods=1).mean()
        )

    # Split into train and test
    train_df = series_df.iloc[:split_idx].copy()
    test_df = series_df.iloc[split_idx:].copy()

    # Create plot or use provided fig/ax
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(12, 8))

    # Plot train series line (solid)
    ax.plot(
        train_df[date_col],
        train_df[target_col],
        color="blue",
        label="Train",
    )

    # Plot test series line (dashed)
    ax.plot(
        test_df[date_col],
        test_df[target_col],
        color="red",
        linestyle="dotted",
        label="Test (Ground Truth)",
    )

    # Update layout
    ax.set_title("Train/Test Split")
    ax.set_xlabel(date_col)
    ax.set_ylabel(target_col)
    ax.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    return fig
