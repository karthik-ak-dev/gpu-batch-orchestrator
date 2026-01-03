"""
Example Job 3: Data Aggregation & Output
Demonstrates reading from previous stage and producing final output.
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


def aggregate_data(input_data):
    """
    Simulate GPU-intensive data aggregation.
    Replace this with your actual aggregation logic.
    """
    print("Aggregating data (simulating GPU workload)...")
    time.sleep(2)  # Simulate processing time

    return {
        "stage": "aggregation",
        "input_records": input_data.get("output_records", 0),
        "aggregated_results": {
            "total": input_data.get("output_records", 0),
            "summary": "Processing complete"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    # Read configuration from environment variables
    job_id = os.environ.get("JOB_ID", "default")
    s3_bucket = os.environ.get("S3_BUCKET")

    print(f"=== JOB 3: DATA AGGREGATION ===")
    print(f"Job ID: {job_id}")
    print(f"S3 Bucket: {s3_bucket}")

    # Read input from previous stage
    s3_client = get_s3_client()
    input_key = f"{job_id}/stage2_output.json"
    print(f"Reading input from s3://{s3_bucket}/{input_key}")

    stage2_output = read_from_s3(s3_client, s3_bucket, input_key)

    # Aggregate data
    result = aggregate_data(stage2_output)
    result["job_id"] = job_id
    result["pipeline_status"] = "completed"

    # Write final output
    output_key = f"{job_id}/final_output.json"
    write_to_s3(s3_client, s3_bucket, output_key, result)

    print("Job 3 completed successfully")
    print("Pipeline execution complete!")
