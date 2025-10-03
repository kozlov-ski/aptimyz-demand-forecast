import marimo

__generated_with = "0.15.2"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md(
        r"""
    # Time Series Forecasting
    ## SageMaker-Core, AutoMLV2

    - https://github.com/aws/sagemaker-core
    - https://github.com/aws/amazon-sagemaker-examples/
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""# Pipelines""")
    return


@app.cell
def _():
    from sagemaker_core.resources import Pipeline

    # get all pipelines
    for p in Pipeline.get_all():
        print(p.pipeline_name)
    return


@app.cell
def _():
    import marimo as mo
    import boto3
    import train_sagemaker
    from sagemaker_core.helper.session_helper import Session, get_execution_role

    boto_session = boto3.session.Session(
        profile_name="aptimyz-env01", region_name="eu-central-1"
    )

    sagemaker_session = Session(boto_session=boto_session)

    region = sagemaker_session.boto_region_name
    role = get_execution_role(sagemaker_session=sagemaker_session)

    print(f"AWS region: {region}")
    print(f"Execution role: {role}")
    return (mo,)


if __name__ == "__main__":
    app.run()
