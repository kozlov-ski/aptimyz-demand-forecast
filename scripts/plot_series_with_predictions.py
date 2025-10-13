import matplotlib.pyplot as plt
import pandas as pd


def plot_series_with_predictions(
    df,
    series_id,
    horizon=7,
    history_window=100,
    date_col="date",
    series_col="series_id",
    target_col="sales",
    fig=None,
    ax=None,
):
    """
    Plot a time series for a given series_id with true values and predictions.

    Parameters:
    - df: pandas DataFrame with date, series_id, sales, and prediction columns (p10, p50, p90, mean)
          Predictions are expected for the last horizon days only.
    - series_id: string, the series identifier to plot
    - horizon: int, number of days for forecast period
    - history_window: int, number of historical days to show before forecast
    - date_col: str, column name for date
    - series_col: str, column name for series_id
    - target_col: str, column name for sales/true values

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

    if len(series_df) == 0:
        raise ValueError(f"No data found for series_id: {series_id}")

    # Select data range: last history_window + horizon days
    plot_length = history_window + horizon
    if len(series_df) < plot_length:
        plot_length = len(series_df)
        history_window = plot_length - horizon

    plot_df = series_df.tail(plot_length).copy()

    # Identify forecast rows (where predictions exist, typically last horizon rows)
    forecast_mask = plot_df["p10"].notna()
    forecast_df = plot_df[forecast_mask]

    if len(forecast_df) != horizon:
        raise ValueError(f"Expected {horizon} forecast rows, found {len(forecast_df)}")

    # Create plot or use provided fig/ax
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(12, 8))

    # Plot true sales (historical + forecast period)
    ax.plot(
        plot_df[date_col],
        plot_df[target_col],
        color="blue",
        label="True Sales",
    )

    # Add forecast period marker (vertical line)
    forecast_start_date = forecast_df[date_col].min()
    ax.axvline(
        x=forecast_start_date,
        color="gray",
        linestyle="--",
        alpha=0.7,
        label="Forecast Start",
    )

    # Plot predicted mean for forecast period
    ax.plot(
        forecast_df[date_col],
        forecast_df["mean"],
        color="green",
        linewidth=2,
        label="Predicted Mean",
    )

    # Plot p90 and p10 bounds with fill between
    ax.fill_between(
        forecast_df[date_col],
        forecast_df["p10"],
        forecast_df["p90"],
        color="gray",
        alpha=0.2,
        label="90% Confidence Interval",
    )

    # Plot p90 dashed line
    ax.plot(
        forecast_df[date_col],
        forecast_df["p90"],
        color="darkgray",
        linewidth=1,
        linestyle="--",
        label="P90",
    )

    # Plot p10 dashed line
    ax.plot(
        forecast_df[date_col],
        forecast_df["p10"],
        color="darkgray",
        linewidth=1,
        linestyle="--",
        label="P10",
    )

    # Update layout
    ax.set_title(f"Time Series Prediction for {series_id}")
    ax.set_xlabel(date_col)
    ax.set_ylabel(target_col)
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.tight_layout()

    return fig
