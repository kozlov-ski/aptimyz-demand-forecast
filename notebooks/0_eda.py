import marimo

__generated_with = "0.15.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# Forecasting EDA""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Statistics""")
    return


@app.cell
def _(train_df):
    train_df.describe()
    return


@app.cell(hide_code=True)
def _(plt, sns, train_df):
    _ax = sns.histplot(train_df['sales'], kde=True, stat="density")
    _ax.set_title("Sales Distribution")
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Sales""")
    return


@app.cell(hide_code=True)
def _(mticker, plt, sales_total_df, sns):
    _ax = sns.barplot(data=sales_total_df, x="year", y="sales")
    _ax.set_title("Yearly Sales Totals")
    _ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    plt.show()
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mticker, plt, sales_store_df, sns):
    plt.figure(figsize=(14, 6))
    _ax = sns.lineplot(data=sales_store_df, x="month", y="sales", hue="store")
    _ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    _ax.set_title("Sales by Store")
    plt.show()
    return


@app.cell(hide_code=True)
def _(plt, sales_store_daily_df, sns):
    plt.figure(figsize=(14, 6))
    _ax = sns.boxplot(data=sales_store_daily_df, x="store", y="sales")
    _ax.set_title("Daily Store Sales (all products)")
    plt.show()
    return


@app.cell
def _(mo, train):
    sales_store_daily_df = mo.sql(
        f"""
        SELECT
        	DATE_TRUNC('day', date) AS day,
            store,
            SUM(sales) AS sales
        FROM train
        GROUP BY 1,2
        """,
        output=False
    )
    return (sales_store_daily_df,)


@app.cell
def _(mo, train):
    sales_store_df = mo.sql(
        f"""
        SELECT
            DATE_TRUNC('month', date) AS month,
            CAST(store AS VARCHAR) AS store,
            SUM(sales) AS sales
        FROM train
        GROUP BY 1, 2
        ORDER BY 1;
        """,
        output=False
    )
    return (sales_store_df,)


@app.cell
def _(mo, train):
    sales_total_df = mo.sql(
        f"""
        SELECT
            DATE_TRUNC('year', date) AS year,
            SUM(sales) AS sales
        FROM train
        GROUP BY 1
        ORDER BY 1;
        """,
        output=False
    )
    return (sales_total_df,)


@app.cell
def _(mo, train):
    train_df = mo.sql(
        f"""
        SELECT * FROM train;
        """,
        output=False
    )
    return (train_df,)


@app.cell
def _(mo):
    _df = mo.sql(
        f"""
        CREATE VIEW train AS
        SELECT * FROM READ_CSV('data/train.csv');
        """
    )
    return (train,)


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    import seaborn as sns
    return mo, mticker, plt, sns


if __name__ == "__main__":
    app.run()
