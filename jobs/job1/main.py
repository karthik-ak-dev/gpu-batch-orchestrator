import json
import sys

if __name__ == "__main__":
    input_json = sys.stdin.read() or "{}"
    print(f"job1 received input: {input_json}")
    # Simulate writing to S3 and outputting the S3 URL, include input in output
    print(
        json.dumps(
            {
                "job1_s3_output": "s3://dummy-bucket/job1.json",
                "job1_input": input_json,  # noqa: E501
            }
        )
    )
