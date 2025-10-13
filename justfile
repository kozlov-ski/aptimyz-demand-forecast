init:
    uv sync

clean:
    rm -rf data/*

[working-directory: 'data']
data:
    uv run kaggle competitions download -c demand-forecasting-kernels-only
    unzip -q demand-forecasting-kernels-only.zip

jupyter:
    uv run jupyter lab

iam-update-pipeline-policy:
    ./scripts/update_iam_policy.sh SageMakerPipelineServicePolicy SageMakerPipelineServiceRole automl/security/pipeline-service-role-policy.json

iam-update-training-policy:
    ./scripts/update_iam_policy.sh SageMakerTrainingExecutionPolicy SageMakerTrainingExecutionRole automl/security/training-execution-role-policy.json
