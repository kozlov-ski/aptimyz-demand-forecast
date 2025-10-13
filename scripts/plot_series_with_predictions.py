import plotly.graph_objects as go


def plot_series_with_predictions(
    df,
    series_id,
    horizon=7,
    history_window=100,
    date_col="date",
    series_col="series_id",
    target_col="sales",
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
    - plotly.graph_objects.Figure
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

    # Create plot
    fig = go.Figure()

    # Plot true sales (historical + forecast period)
    fig.add_trace(
        go.Scatter(
            x=plot_df[date_col],
            y=plot_df[target_col],
            mode="lines",
            name="True Sales",
            line=dict(color="blue"),
        )
    )

    # Add forecast period marker (vertical line)
    forecast_start_date = forecast_df[date_col].min()
    fig.add_vline(
        x=forecast_start_date, line_color="gray", line_dash="dash", opacity=0.7
    )

    # Plot predicted mean for forecast period
    fig.add_trace(
        go.Scatter(
            x=forecast_df[date_col],
            y=forecast_df["mean"],
            mode="lines",
            name="Predicted Mean",
            line=dict(color="green", width=2),
        )
    )

    # Plot p90 (upper bound for fill)
    fig.add_trace(
        go.Scatter(
            x=forecast_df[date_col],
            y=forecast_df["p90"],
            mode="lines",
            name="P90",
            line=dict(color="rgba(128,128,128,0.5)", width=1, dash="dash"),
        )
    )

    # Plot p10 (lower bound, with fill to p90)
    fig.add_trace(
        go.Scatter(
            x=forecast_df[date_col],
            y=forecast_df["p10"],
            mode="lines",
            name="P10",
            line=dict(color="rgba(128,128,128,0.5)", width=1, dash="dash"),
            fill="tonexty",  # Fill to previous trace (p90)
            fillcolor="rgba(128,128,128,0.2)",
        )
    )

    # Update layout
    fig.update_layout(
        title=f"Time Series Prediction for {series_id}",
        xaxis_title=date_col,
        yaxis_title=target_col,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
    )

    return fig
