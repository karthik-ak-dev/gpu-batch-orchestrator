"""
Example Job 2: Data Transformation
Demonstrates reading from previous stage and transforming data.
"""
import json
import os
import time
import boto3
from datetime import datetime


def get_s3_client():
    """Initialize S3 client."""
    return boto3.client("s3")


def read_from_s3(s3_client, bucket, key):
    """Read JSON data from S3."""
    response = s3_client.get_object(Bucket=bucket, Key=key)
    return json.loads(response["Body"].read().decode("utf-8"))


def write_to_s3(s3_client, bucket, key, data):
    """Write JSON data to S3."""
    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(data, indent=2),
        ContentType="application/json"
    )
    print(f"Wrote output to s3://{bucket}/{key}")


def transform_data(input_data):
    """
    Simulate GPU-intensive data transformation.
    Replace this with your actual transformation logic.
    """
    print("Transforming data (simulating GPU workload)...")
    time.sleep(2)  # Simulate processing time

    return {
        "stage": "transformation",
        "input_records": input_data.get("records_processed", 0),
        "output_records": input_data.get("records_processed", 0) * 2,
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    # Read configuration from environment variables
    job_id = os.environ.get("JOB_ID", "default")
    s3_bucket = os.environ.get("S3_BUCKET")

    print(f"=== JOB 2: DATA TRANSFORMATION ===")
    print(f"Job ID: {job_id}")
    print(f"S3 Bucket: {s3_bucket}")

    # Read input from previous stage
    s3_client = get_s3_client()
    input_key = f"{job_id}/stage1_output.json"
    print(f"Reading input from s3://{s3_bucket}/{input_key}")

    stage1_output = read_from_s3(s3_client, s3_bucket, input_key)

    # Transform data
    result = transform_data(stage1_output)
    result["job_id"] = job_id

    # Write output for next stage
    output_key = f"{job_id}/stage2_output.json"
    write_to_s3(s3_client, s3_bucket, output_key, result)

    print("Job 2 completed successfully")
