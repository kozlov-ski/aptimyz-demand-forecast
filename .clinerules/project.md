# Project Description

The purpose of the project is to deploy AWS SageMaker pipelines for training a AutoML timeseries forecasting job. The data is about demand prediction in retail store.

The project is delivered one step at a time. Do not rush with the next steps until explicitly asked.

Global rules:
- The JSONSchema for pipelines files is defined in schema-pipeline.json file.
- Commonly used CLI commands are located in README_Sagemaker.md file
- Do not try to run justfile recipies, if they are needed ask me to do so manually
- Assume I'm a power user who need to create automated and scalable solutions

## Training dataset
The training dataset is located on S3 storage and follows the following format

```csv
date,store,item,sales
2013-01-01,1,1,13
2013-01-02,1,1,11
2013-01-03,1,1,14
2013-01-04,1,1,13
```

- The series id is a composite key of (store, item)
- Target is the sales column

## Training pipeline
This pipeline focuses on retraining, validation, and conditional registration. If the new model isn't better, it skips registration to avoid overwriting.

### Step 1: Data Quality Check (ProcessingStep)

**Input**: training_data_s3 parameter.
Processor: SKLearnProcessor or ScriptProcessor with a custom Python script.
**Script**: Load data from S3, check completeness (e.g., no missing values in key columns like timestamp, target), cadence (e.g., daily frequency via timestamp gaps), schema validation.
**Output**: Quality report to S3; fail pipeline if checks don't pass (use PropertyFile for pass/fail flag).
Instance: ml.t3.medium (cost-effective for checks).


### Step 2: Model Training (AutoMLStep)

Depends on: Step 1 success.
**Config**: Mirrors the provided CLI command – TimeSeriesForecastingJobConfig with parameters for horizon, frequency, quantiles, attributes, completion criteria (max candidates/runtime).
**Input**: Training channel from training_data_s3 (CSV, no compression).
**Output**: Model artifacts and inference container to output_s3.
Instance: Auto-selected by AutoML, with runtime limits.


### Step 3: Model Benchmarking/Evaluation (ProcessingStep)

Depends on: Step 2.
Input: Model from Step 2, validation_data_s3.
Processor: ScriptProcessor with custom script.
Script: Deploy temporary inference (e.g., via batch transform or local predict), forecast on validation data, compute metrics (e.g., RMSE, MASE per quantile/group).
Output: Metrics JSON to S3 (use PropertyFile to extract key metrics for downstream conditions).


### Step 4: Record Metrics (TuningStep or Custom LambdaStep)

Depends on: Step 3.
Action: Log evaluation metrics to SageMaker Experiments (via SDK in a script or Lambda). Track run details like job name, parameters, metrics.


### Step 5: Metrics Comparison (ConditionStep)

Depends on: Step 4.
**Input**: Current metrics from Step 3 PropertyFile; fetch previous best metrics via Experiment query (use LambdaStep or ProcessingStep to query/compare).
**Condition**: If new metrics > threshold improvement (e.g., lower RMSE), proceed to registration; else, end pipeline.


### Step 6: Deploy to Model Registry (RegisterModelStep)

Depends on: Condition true.
**Action**: Register model package to model_package_group with artifacts from Step 2, metrics from Step 3, and approval status (e.g., "PendingManualApproval" or auto-approve if confident).
**Inference**: Specify container from AutoML output for time series forecasting.

## Inference pipeline
