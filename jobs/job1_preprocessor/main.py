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

    print("=== JOB1_PREPROCESSOR DEBUG ===")
    print(f"EDF ID: {edf_id}")
    print(f"S3 Bucket: {s3_bucket}")
    print(f"Redis Host: {redis_host}")
    print(f"Redis Port: {redis_port}")
    print(f"Input Data: {input_data_str}")
    print("================================")

    # Parse input data
    try:
        input_data = json.loads(input_data_str)
        edf_file = input_data.get("edf_file")  # S3 URL of the EDF file
        edf_id = input_data.get("edf_id") or edf_id
    except json.JSONDecodeError:
        print("Warning: Could not parse input data")
        exit(1)

    if not edf_id:
        print("Error: EDF_ID is required")
        exit(1)

    s3_client = get_s3_client()

    # Read EDF file from S3
    edf_s3_key = f"{edf_id}/{edf_id}.edf"
    print(f"Reading EDF file from s3://{s3_bucket}/{edf_s3_key}")

    # TODO: Add your EDF processing logic here
    # edf_data = read_from_s3(s3_client, s3_bucket, edf_s3_key)
    # if edf_data is None:
    #     print("Error: Could not read EDF file from S3")
    #     exit(1)

    # Process the EDF data and create AI_resampled files
    # TODO: Add your preprocessing logic here
    # This would include:
    # - Resampling the EDF data
    # - Creating day001, day002, day003, day004 files
    # - Creating denoised.npy
    # - Creating metadata.json

    # Write AI_resampled files back to S3
    ai_resampled_files = [
        f"{edf_id}_250_day001.npz",
        f"{edf_id}_250_day002.npz",
        f"{edf_id}_250_day003.npz",
        f"{edf_id}_250_day004.npz"
    ]

    for filename in ai_resampled_files:
        s3_key = f"{edf_id}/AI_resampled/{filename}"
        print(f"Writing AI_resampled file to s3://{s3_bucket}/{s3_key}")
        # Write dummy data (empty file for now)
        write_to_s3(s3_client, s3_bucket, s3_key, "",
                   content_type="application/octet-stream")

    # Write denoised.npy
    denoised_s3_key = f"{edf_id}/denoised.npy"
    print(f"Writing denoised.npy to s3://{s3_bucket}/{denoised_s3_key}")
    write_to_s3(s3_client, s3_bucket, denoised_s3_key, "",
               content_type="application/octet-stream")

    # Write metadata.json
    metadata = {
        "edf_id": edf_id,
        "processed_at": "2025-01-25T12:00:00Z",
        "status": "completed",
        "ai_resampled_files": ai_resampled_files
    }
    metadata_s3_key = f"{edf_id}/metadata.json"
    print(f"Writing metadata.json to s3://{s3_bucket}/{metadata_s3_key}")
    write_to_s3(s3_client, s3_bucket, metadata_s3_key, metadata)

    print("Job1_preprocessor completed successfully") 