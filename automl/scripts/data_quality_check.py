import argparse
import boto3
import pandas as pd
import json
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-data", type=str, required=True)
    parser.add_argument("--output-data", type=str, required=True)
    parser.add_argument("--target", type=str, default="sales")
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
    report = {}

    # Check missing values
    if df["timestamp"].isnull().any() or df[args.target].isnull().any():
        quality_pass = False
        report["missing_values"] = "Found missing values in timestamp or target"

    # Check cadence (assume timestamp is date)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    diffs = df["timestamp"].diff().dt.days
    if (diffs > 1).any():
        quality_pass = False
        report["cadence"] = "Gaps in daily data"

    # Schema check
    required_cols = ["timestamp", args.target]
    if not all(col in df.columns for col in required_cols):
        quality_pass = False
        report["schema"] = "Missing required columns"

    # Output report
    os.makedirs("/opt/ml/processing/output/report", exist_ok=True)
    report_path = "/opt/ml/processing/output/report/quality_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f)

    if not quality_pass:
        raise Exception("Data quality check failed")


def parse_s3_path(s3_path):
    # s3://bucket/key
    parts = s3_path.replace("s3://", "").split("/")
    bucket = parts[0]
    key = "/".join(parts[1:])
    return bucket, key


if __name__ == "__main__":
    main()
