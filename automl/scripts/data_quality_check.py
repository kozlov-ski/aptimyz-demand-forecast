# uv run automl/scripts/data_quality_check.py --input-data s3://sagemaker-forecasting-aptimyz-input/train/train.csv --output-data s3://sagemaker-forecasting-aptimyz-output --report-path /tmp / report

import argparse
import boto3
import pandas as pd
import json
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-data", type=str, required=True)
    parser.add_argument("--output-data", type=str, required=True)
    parser.add_argument(
        "--report-path",
        type=str,
        default="/opt/ml/processing/output/report/quality_report.json",
    )
    args = parser.parse_args()

    # Download data from S3
    s3 = boto3.client("s3")
    bucket, key = parse_s3_path(args.input_data)
    local_file = "/tmp/data.csv"
    s3.download_file(bucket, key, local_file)

    # Load data
    df = pd.read_csv(local_file)

    # Checks
    quality_pass = True
    report = {"status": "PASS", "details": {}}

    # Schema check
    required_cols = ["date", "store", "item", "sales"]
    if not all(col in df.columns for col in required_cols):
        quality_pass = False
        report["details"]["schema"] = "Missing required columns"

    if quality_pass:
        # Convert date
        df["date"] = pd.to_datetime(df["date"])

        # Check no null values in sales
        if df["sales"].isnull().any():
            quality_pass = False
            report["details"]["missing_values"] = "Found missing values in sales"

        # Check cadence per series
        grouped = df.groupby(["store", "item"])
        for name, group in grouped:
            group = group.sort_values("date")
            diffs = group["date"].diff().dt.days
            if (diffs > 1).any():
                quality_pass = False
                report["details"]["cadence"] = (
                    f"Gaps in daily data for store {name[0]}, item {name[1]}"
                )
                break

    if not quality_pass:
        report["status"] = "FAIL"

    # Output report
    report_dir = os.path.dirname(args.report_path)
    os.makedirs(report_dir, exist_ok=True)
    report_path = args.report_path
    with open(report_path, "w") as f:
        json.dump(report, f)

    if not quality_pass:
        error_details = "; ".join([f"{k}: {v}" for k, v in report["details"].items()])
        raise Exception(f"Data quality check failed: {error_details}")


def parse_s3_path(s3_path):
    # s3://bucket/key
    parts = s3_path.replace("s3://", "").split("/")
    bucket = parts[0]
    key = "/".join(parts[1:])
    return bucket, key


if __name__ == "__main__":
    main()
