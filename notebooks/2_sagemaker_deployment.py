import marimo

__generated_with = "0.15.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # SageMaker-Core deployment

    - https://github.com/aws/sagemaker-core
    - https://github.com/aws/amazon-sagemaker-examples/
    """
    )
    return


@app.cell
def _():
    import marimo as mo
    import boto3
    from sagemaker_core.helper.session_helper import Session

    boto_session = boto3.session.Session(profile_name="aptimyz-env01")
    sagemaker_session = Session(boto_session=boto_session)
    return (mo,)


if __name__ == "__main__":
    app.run()
