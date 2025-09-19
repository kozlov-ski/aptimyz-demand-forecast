import marimo

__generated_with = "0.15.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# Autogluon Time Series Jumpstart""")
    return


@app.cell
def _():
    # Forecasting days ahead
    PREDICTION_AHEAD = 7
    return (PREDICTION_AHEAD,)


@app.cell
def _(pd):
    # load data from file
    data_df = pd.read_csv("data/train.csv")

    # parse types
    data_df["date"] = pd.to_datetime(data_df["date"], utc=False)
    data_df["store"] = data_df["store"].astype(str)
    data_df["item"] = data_df["item"].astype(str)

    # composite series id = (store, item)
    data_df["series_id"] = data_df["store"] + "_" + data_df["item"]
    return (data_df,)


@app.cell
def _(PREDICTION_AHEAD, TimeSeriesDataFrame, data_df):
    # build static covariates dataframe (one row per series)
    _static_df = (
        data_df[["series_id", "store", "item"]]
          .drop_duplicates()
          .astype({"store": "category", "item": "category"})
    )

    _data = TimeSeriesDataFrame.from_data_frame(
        data_df[["series_id", "date", "sales"]],
        id_column="series_id",
        timestamp_column="date",
        static_features_df=_static_df.copy(deep=True)
    )

    train_data, test_data = _data.train_test_split(PREDICTION_AHEAD)
    return test_data, train_data


@app.cell
def _(np, plt, test_data, train_data):
    item_id = "9_1"

    fig, (ax1, ax2) = plt.subplots(nrows=2, figsize=[10, 4], sharex=True)

    train_ts = train_data.loc[item_id].last('180D')
    test_ts = test_data.loc[item_id].last('180D')

    ax1.set_title("Train data (past time series values)")
    ax1.plot(train_ts)
    ax2.set_title("Test data (past + future time series values)")
    ax2.plot(test_ts)
    for ax in (ax1, ax2):
        ax.fill_between(
            np.array([train_ts.index[-1], test_ts.index[-1]]),
            test_ts.min(),
            test_ts.max(),
            color="C1",
            alpha=0.3,
            label="Forecast horizon",
        )

    plt.legend()
    plt.show()
    return


@app.cell
def _(PREDICTION_AHEAD, TimeSeriesPredictor, train_data):
    predictor = TimeSeriesPredictor(
        target="sales",
        prediction_length=PREDICTION_AHEAD,
        path="autogluon",
        eval_metric="WQL",
        freq="D",
    )

    # train models (10min limit)
    # fast_training, medium_quality, high_quality, best_quality
    predictor.fit(
        train_data,
        presets="medium_quality",
        num_val_windows=2,
        enable_ensemble=False,
        time_limit=600,  # total training time limit (sec)
    )


    # predictor.fit(
    #     train_data,
    #     hyperparameters={
    #         "TemporalFusionTransformer": {
    #             # sensible starting tweaks
    #             "hidden_dim": 64,
    #             "variable_dim": 64,
    #             "num_heads": 4,
    #             "dropout_rate": 0.1,
    #             # let TFT use all feature types (don’t disable)
    #             "disable_static_features": False,
    #             "disable_known_covariates": False,
    #             "disable_past_covariates": False,
    #             # training
    #             "max_epochs": 50,
    #             "early_stopping_patience": 10,
    #         }
    #     },
    # )
    return (predictor,)


@app.cell
def _(predictor, train_data):
    # get probabilistic forecast (internal test set)
    # in addition to predicting the mean (expected value) of the time series in the future, models also provide the quantiles of the forecast distribution. The quantile forecasts give us an idea about the range of possible outcomes. For example, if the "0.1" quantile is equal to 500.0, it means that the model predicts a 10% chance that the target value will be below 500.0.
    predictions = predictor.predict(train_data)
    predictions.head()
    return (predictions,)


@app.cell
def _(PREDICTION_AHEAD, plt, predictions, predictor, test_data):
    predictor.plot(
        test_data,
        predictions,
        quantile_levels=[0.1, 0.9],
        max_history_length=10*PREDICTION_AHEAD,
        max_num_item_ids=4,
    )

    plt.show()
    return


@app.cell
def _(predictor):
    predictor.leaderboard()
    return


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    import pandas as pd
    from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor
    return TimeSeriesDataFrame, TimeSeriesPredictor, mo, np, pd, plt


if __name__ == "__main__":
    app.run()
