# AutoML Job

https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-create-experiment-timeseries-forecasting.html
https://docs.aws.amazon.com/sagemaker/latest/dg/timeseries-forecasting-algorithms.html
https://sagemaker.readthedocs.io/en/v2.125.0/experiments/index.html
https://github.com/aws/amazon-sagemaker-examples/blob/main/autopilot/autopilot_time_series.ipynb

https://docs.aws.amazon.com/sagemaker/latest/dg/pre-built-docker-containers-scikit-learn-spark.html

```bash
s3://sagemaker-forecasting-aptimyz-data/train.csv
```

```bash
aws s3 mb sagemaker-forecasting-aptimyz-data

```

## Prerequisites
Basic AWS Setup

```bash
aws-vault exec aptimyz-env01
export AWS_REGION=eu-central-1
export AWS_DEFAULT_REGION=eu-central-1

# Create IAM roles and policies
just iam-update-pipeline-policy
just iam-update-training-policy

# Create S3 buckets
aws s3 mb s3://sagemaker-forecasting-aptimyz-input
aws s3 mb s3://sagemaker-forecasting-aptimyz-output

# Move training data and scripts
aws s3 cp ./data/train.csv s3://sagemaker-forecasting-aptimyz-input/train/train.csv
aws s3 sync ./automl/scripts s3://sagemaker-forecasting-aptimyz-input/scripts --exclude "*" --include "*.py"
```

## SageMaker Pipeline Management

https://docs.aws.amazon.com/sagemaker/latest/dg/define-pipeline.html

```bash
# Create pipeline (uses Pipeline Service Role for orchestration)
aws sagemaker create-pipeline \
  --pipeline-name "forecast-training-pipeline" \
  --pipeline-display-name "Forecasting-Training" \
  --pipeline-definition file://automl/pipelines/training_pipeline_definition.json \
  --role-arn arn:aws:iam::283674368847:role/SageMakerPipelineServiceRole

# Update pipeline
aws sagemaker update-pipeline \
  --pipeline-name "forecast-training-pipeline" \
  --pipeline-definition file://automl/pipelines/training_pipeline_definition.json

# List pipelines
aws sagemaker list-pipelines --sort-by "CreationTime" --sort-order "Descending"

# Start pipeline execution
aws sagemaker start-pipeline-execution \
  --pipeline-name "forecast-training-pipeline" \
  --pipeline-execution-display-name "Run-$(date +%Y%m%d-%H%M%S)"

# List pipeline executions
aws sagemaker list-pipeline-executions --pipeline-name "forecast-training-pipeline"

# Delete pipeline
aws sagemaker delete-pipeline --pipeline-name "forecast-training-pipeline"
```

## Training

```bash
aws sagemaker list-candidates-for-auto-ml-job \
  --auto-ml-job-name forecast-20250918-113854 \
  --output json | jq -r '.Candidates
  | sort_by(.FinalAutoMLJobObjectiveMetric.Value)
  | .[] | [.CandidateName, .FinalAutoMLJobObjectiveMetric.Value]
  | @tsv'

# https://docs.aws.amazon.com/cli/latest/reference/sagemaker/create-auto-ml-job-v2.html
aws sagemaker create-auto-ml-job-v2 \
  --role-arn arn:aws:iam::283674368847:role/SageMakerTrainingExecutionRole \
  --auto-ml-job-name "forecast-$(date +%Y%m%d-%H%M%S)" \
  --auto-ml-job-input-data-config '[{
    "ChannelType": "training",
    "ContentType": "text/csv;header=present",
    "CompressionType": "None",
    "DataSource": {
      "S3DataSource": {
        "S3DataType": "S3Prefix",
        "S3Uri": "s3://sagemaker-forecasting-aptimyz-input/train"
      }
    }
  }]' \
  --output-data-config '{"S3OutputPath":"s3://sagemaker-forecasting-aptimyz-output/"}' \
  --auto-ml-problem-type-config '{
    "TimeSeriesForecastingJobConfig": {
      "ForecastFrequency": "1D",
      "ForecastHorizon": 7,
      "ForecastQuantiles": ["p10","p50","p90"],
      "TimeSeriesConfig": {
        "TargetAttributeName": "sales",
        "TimestampAttributeName": "date",
        "ItemIdentifierAttributeName": "item",
        "GroupingAttributeNames": ["store"]
      },
      "CompletionCriteria": {
        "MaxCandidates": 1,
        "MaxAutoMLJobRuntimeInSeconds": 3600,
        "MaxRuntimePerTrainingJobInSeconds": 60
      }
    }
  }'
```

```bash
# check job training status
aws sagemaker describe-auto-ml-job-v2 --auto-ml-job-name forecast-20250918-113854

# candidates (leaderboard)
aws sagemaker list-candidates-for-auto-ml-job --auto-ml-job-name forecast-20250918-113854

# all training jobs
aws sagemaker list-training-jobs | jq '[.TrainingJobSummaries[] | {TrainingJobName, CreationTime, TrainingJobStatus}]'
```
