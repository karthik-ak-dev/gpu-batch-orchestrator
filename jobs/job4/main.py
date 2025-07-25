import json
import os
import sys
import boto3
from botocore.exceptions import ClientError


def get_s3_client():
    """Get S3 client."""
    return boto3.client("s3")


def read_from_s3(s3_client, bucket, key):
    """Read JSON data from S3."""
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        data = json.loads(response["Body"].read().decode("utf-8"))
        print(f"Successfully read from s3://{bucket}/{key}", file=sys.stderr)
        return data
    except ClientError as e:
        print(f"Error reading from S3: {e}", file=sys.stderr)
        return None


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

    print("=== JOB4 DEBUG ===", file=sys.stderr)
    print(f"Execution ID: {execution_id}", file=sys.stderr)
    print(f"S3 Bucket: {s3_bucket}", file=sys.stderr)
    print(f"Job Name: {job_name}", file=sys.stderr)
    print("==================", file=sys.stderr)

    s3_client = get_s3_client()

    # Read Job3 result
    job3_key = f"{execution_id}/job3-result.json"
    job3_data = read_from_s3(s3_client, s3_bucket, job3_key)

    if job3_data is None:
        print("Failed to read Job3 data from S3", file=sys.stderr)
        exit(1)

    print("Job3 Data:", file=sys.stderr)
    print(json.dumps(job3_data, indent=2), file=sys.stderr)
    print("==================", file=sys.stderr)

    # Process the data (Job4's logic - final processing)
    result = {
        "job3_data": job3_data,
        "final_result": {
            "total_jobs_processed": 4,
            "execution_id": execution_id,
            "pipeline_status": "completed",
            "final_processed_at": "2025-01-25T12:10:00Z",  # Real: now()
        },
        "status": "completed",
    }

    # Write result to S3
    s3_key = f"{execution_id}/job4-result.json"

    if write_to_s3(s3_client, s3_bucket, s3_key, result):
        print("Job4 completed successfully", file=sys.stderr)
    else:
        print("Job4 failed to write output", file=sys.stderr)
        exit(1)
