import json
import os
import sys
import boto3
from botocore.exceptions import ClientError


def get_s3_client():
    """Get S3 client."""
    return boto3.client("s3")


def read_from_s3(s3_client, bucket, key):
    """Read data from S3."""
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        return response['Body'].read()
    except ClientError as e:
        print(f"Error reading from S3: {e}")
        return None


def write_to_s3(s3_client, bucket, key, data, content_type="application/json"):
    """Write data to S3."""
    try:
        if isinstance(data, str):
            body = data
        else:
            body = json.dumps(data, indent=2)

        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=body,
            ContentType=content_type,
        )
        print(f"Successfully wrote to s3://{bucket}/{key}")
        return True
    except ClientError as e:
        print(f"Error writing to S3: {e}")
        return False


if __name__ == "__main__":
    # Get environment variables
    edf_id = os.environ.get("EDF_ID")
    s3_bucket = os.environ.get("S3_BUCKET")
    redis_host = os.environ.get("REDIS_HOST")
    redis_port = os.environ.get("REDIS_PORT")
    input_data_str = os.environ.get("INPUT_DATA", "{}")

    print("=== JOB4_PQST DEBUG ===")
    print(f"EDF ID: {edf_id}")
    print(f"S3 Bucket: {s3_bucket}")
    print(f"Redis Host: {redis_host}")
    print(f"Redis Port: {redis_port}")
    print(f"Input Data: {input_data_str}")
    print("=======================")

    # Parse input data
    try:
        input_data = json.loads(input_data_str)
        edf_id = input_data.get("edf_id") or edf_id
    except json.JSONDecodeError:
        print("Warning: Could not parse input data")
        exit(1)

    if not edf_id:
        print("Error: EDF_ID is required")
        exit(1)

    s3_client = get_s3_client()

    # Read beats.json from S3
    beats_s3_key = f"{edf_id}/beats.json"
    print(f"Reading beats.json from s3://{s3_bucket}/{beats_s3_key}")

    # TODO: Add your PQST processing logic here
    # beats_data = read_from_s3(s3_client, s3_bucket, beats_s3_key)
    # if beats_data is None:
    #     print("Error: Could not read beats.json from S3")
    #     exit(1)
    # Process the beats data for PQST analysis

    # Write pqst.json back to S3
    pqst_s3_key = f"{edf_id}/pqst.json"
    print(f"Writing pqst.json to s3://{s3_bucket}/{pqst_s3_key}")

    # Write dummy data (empty JSON object for now)
    pqst_data = {
        "edf_id": edf_id,
        "processed_at": "2025-01-25T12:00:00Z",
        "status": "completed",
        "pqst_analyzed": True
    }
    write_to_s3(s3_client, s3_bucket, pqst_s3_key, pqst_data)

    print("Job4_pqst completed successfully") 