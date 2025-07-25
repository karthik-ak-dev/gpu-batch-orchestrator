import json
import os
import sys
import boto3
from botocore.exceptions import ClientError


def get_s3_client():
    """Get S3 client."""
    return boto3.client("s3")


def write_to_s3(s3_client, bucket, key, data):
    """Write data to S3."""
    try:
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(data, indent=2),
            ContentType="application/json",
        )
        print(f"Successfully wrote to s3://{bucket}/{key}", file=sys.stderr)
        return True
    except ClientError as e:
        print(f"Error writing to S3: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    # Get environment variables
    execution_id = os.environ.get("EXECUTION_ID")
    s3_bucket = os.environ.get("S3_BUCKET")
    job_name = os.environ.get("JOB_NAME")
    input_data_str = os.environ.get("INPUT_DATA", "{}")

    print("=== JOB2 DEBUG ===", file=sys.stderr)
    print(f"Execution ID: {execution_id}", file=sys.stderr)
    print(f"S3 Bucket: {s3_bucket}", file=sys.stderr)
    print(f"Job Name: {job_name}", file=sys.stderr)
    print(f"Input Data: {input_data_str}", file=sys.stderr)
    print("==================", file=sys.stderr)

    # Parse input data
    try:
        input_data = json.loads(input_data_str)
    except json.JSONDecodeError:
        input_data = {}
        print(
            "Warning: Could not parse input data, using empty dict",
            file=sys.stderr
        )

    # Process the data (Job2's logic)
    result = {
        "job2_input": input_data,
        "processed_at": "2025-01-25T12:00:00Z",  # Real: datetime.now()
        "status": "completed",
    }

    # Write result to S3
    s3_client = get_s3_client()
    s3_key = f"{execution_id}/job2-result.json"

    if write_to_s3(s3_client, s3_bucket, s3_key, result):
        print("Job2 completed successfully", file=sys.stderr)
    else:
        print("Job2 failed to write output", file=sys.stderr)
        exit(1)
