# SageMaker CLI

```bash
aws-vault exec aptimyz-env01
export AWS_REGION=eu-central-1
```

## Domains

```bash
# List SageMaker domains
aws sagemaker list-domains

# Describe domain details
aws sagemaker describe-domain --domain-id d-07vfaf2bekk7

# Create a user profile
aws sagemaker create-user-profile \
 --domain-id d-07vfaf2bekk7 \
 --user-profile-name <username> \
 --user-settings file://user-settings.json

# List users in domain
aws sagemaker list-user-profiles --domain-id d-07vfaf2bekk7
```

## Training jobs

```bash
# Create training job
aws sagemaker create-training-job \
  --training-job-name "ml-training-$(date +%Y%m%d-%H%M%S)" \
  --algorithm-specification TrainingImage=<ecr-image>,TrainingInputMode=File \
  --role-arn <role-arn> \
  --input-data-config file://input-config.json \
  --output-data-config S3OutputPath=s3://bucket/output/ \
  --resource-config file://resource-config.json \
  --stopping-condition MaxRuntimeInSeconds=86400

# List training jobs
aws sagemaker list-training-jobs | jq '[.TrainingJobSummaries[] | {TrainingJobName, CreationTime, TrainingJobStatus}]'

aws sagemaker list-training-jobs \
  --status-equals "Completed" \
  --sort-by "CreationTime" \
  --sort-order "Descending" \
  --max-results 50

# Describe training job
aws sagemaker describe-training-job \
  --training-job-name Canvas1757048433409-qb-backtest-1-1-3cdbfcdf02404d078ca855da3da

# Stop training job
aws sagemaker stop-training-job \
  --training-job-name <job-name>
```
