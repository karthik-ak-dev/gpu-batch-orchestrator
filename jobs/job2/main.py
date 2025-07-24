import json
import sys

if __name__ == "__main__":
    input_json = sys.stdin.read() or "{}"
    print(f"job2 received input: {input_json}")
    # Simulate writing to S3 and outputting the S3 URL, include input in output
    print(
        json.dumps(
            {
                "job2_s3_output": "s3://dummy-bucket/job2.json",
                "job2_input": input_json,
            }
        )
    )
