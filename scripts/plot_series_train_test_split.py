import plotly.graph_objects as go


def plot_series_train_test_split(
    df,
    series_id,
    horizon,
    smooth_window=0,
    date_col="date",
    series_col="series_id",
    target_col="sales",
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
    - plotly.graph_objects.Figure
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

    # Create plot
    fig = go.Figure()

    # Plot train series line (solid)
    fig.add_trace(
        go.Scatter(
            x=train_df[date_col],
            y=train_df[target_col],
            mode="lines",
            name="Train",
            line=dict(color="blue"),
        )
    )

    # Plot test series line (dashed)
    fig.add_trace(
        go.Scatter(
            x=test_df[date_col],
            y=test_df[target_col],
            mode="lines",
            name="Test (Ground Truth)",
            line=dict(color="red", dash="dot"),
        )
    )

    # Update layout
    fig.update_layout(
        title="Train/Test Split",
        xaxis_title=date_col,
        yaxis_title=target_col,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
    )

    return fig
