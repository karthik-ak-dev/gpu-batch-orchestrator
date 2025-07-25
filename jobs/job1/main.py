import json
import sys

if __name__ == "__main__":
    input_json = sys.stdin.read() or "{}"
    print("=== JOB1 DEBUG ===")
    print(f"Raw input received: {input_json}")
    print(f"Input type: {type(input_json)}")
    print(f"Input length: {len(input_json)}")
    print("==================")

    # Simulate writing to S3 and outputting the S3 URL, include input in output
    print(
        json.dumps(
            {
                "job1_s3_output": "s3://dummy-bucket/job1.json",
                "job1_input": input_json,  # noqa: E501
            }
        )
    )
