import fev
import pandas as pd
import numpy as np


def cast_predictions(
    window: fev.EvaluationWindow, predictions_df: pd.DataFrame
) -> list:
    """Returns fev-compatible window predictions for evaluation"""
    past_ds, future_ds = window.get_input_data()

    future_dates = np.unique(
        future_ds[window.timestamp_column].astype("datetime64[D]").astype(str)
    )

    predictions = []

    for ts in past_ds[window.id_column]:
        by_series = predictions_df[window.id_column] == ts
        by_dates = predictions_df[window.timestamp_column].isin(future_dates)

        filtered_df = predictions_df[by_series & by_dates].sort_values(
            window.timestamp_column
        )
        assert len(filtered_df) == window.horizon, (
            f"Invalid forecast horizon length {len(filtered_df)} for {ts}"
        )

        predictions.append(
            {
                "predictions": filtered_df["mean"].values.tolist(),
                "0.1": filtered_df["p10"].values.tolist(),
                "0.5": filtered_df["p50"].values.tolist(),
                "0.9": filtered_df["p90"].values.tolist(),
            }
        )

    return predictions
