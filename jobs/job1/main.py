"""
Example Job 1: Data Ingestion
Demonstrates reading input data and writing to S3 for the next stage.
"""
import json
import os
import time
import boto3
from datetime import datetime


def get_s3_client():
    """Initialize S3 client."""
    return boto3.client("s3")


def write_to_s3(s3_client, bucket, key, data):
    """Write JSON data to S3."""
    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(data, indent=2),
        ContentType="application/json"
    )
    print(f"Wrote output to s3://{bucket}/{key}")


def process_data(input_data):
    """
    Simulate GPU-intensive data processing.
    Replace this with your actual processing logic.
    """
    print("Processing data (simulating GPU workload)...")
    time.sleep(2)  # Simulate processing time

    return {
        "stage": "ingestion",
        "records_processed": 1000,
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    # Read configuration from environment variables
    job_id = os.environ.get("JOB_ID", "default")
    s3_bucket = os.environ.get("S3_BUCKET")
    input_data = os.environ.get("INPUT_DATA", "{}")

    print(f"=== JOB 1: DATA INGESTION ===")
    print(f"Job ID: {job_id}")
    print(f"S3 Bucket: {s3_bucket}")

    # Parse input
    try:
        config = json.loads(input_data)
    except json.JSONDecodeError:
        config = {}

    # Process data
    result = process_data(config)
    result["job_id"] = job_id

    # Write output for next stage
    s3_client = get_s3_client()
    output_key = f"{job_id}/stage1_output.json"
    write_to_s3(s3_client, s3_bucket, output_key, result)

    print("Job 1 completed successfully")
