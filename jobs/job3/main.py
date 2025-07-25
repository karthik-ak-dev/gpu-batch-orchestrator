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

    print("=== JOB3 DEBUG ===", file=sys.stderr)
    print(f"Execution ID: {execution_id}", file=sys.stderr)
    print(f"S3 Bucket: {s3_bucket}", file=sys.stderr)
    print(f"Job Name: {job_name}", file=sys.stderr)
    print("==================", file=sys.stderr)

    s3_client = get_s3_client()

    # Read Job1 result
    job1_key = f"{execution_id}/job1-result.json"
    job1_data = read_from_s3(s3_client, s3_bucket, job1_key)

    # Read Job2 result
    job2_key = f"{execution_id}/job2-result.json"
    job2_data = read_from_s3(s3_client, s3_bucket, job2_key)

    if job1_data is None or job2_data is None:
        print("Failed to read input data from S3", file=sys.stderr)
        exit(1)

    print("Job1 Data:", file=sys.stderr)
    print(json.dumps(job1_data, indent=2), file=sys.stderr)
    print("Job2 Data:", file=sys.stderr)
    print(json.dumps(job2_data, indent=2), file=sys.stderr)
    print("==================", file=sys.stderr)

    # Process the data (Job3's logic - merge Job1 and Job2 results)
    result = {
        "job1_data": job1_data,
        "job2_data": job2_data,
        "merged_result": {
            "job1_status": job1_data.get("status"),
            "job2_status": job2_data.get("status"),
            "combined_at": "2025-01-25T12:05:00Z",  # Real: datetime.now()
        },
        "status": "completed",
    }

    # Write result to S3
    s3_key = f"{execution_id}/job3-result.json"

    if write_to_s3(s3_client, s3_bucket, s3_key, result):
        print("Job3 completed successfully", file=sys.stderr)
    else:
        print("Job3 failed to write output", file=sys.stderr)
        exit(1)
