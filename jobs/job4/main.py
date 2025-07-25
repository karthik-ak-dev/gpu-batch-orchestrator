import sys
import json

if __name__ == "__main__":
    input_json = sys.stdin.read() or "{}"
    print("=== JOB4 DEBUG ===")
    print(f"Raw input received: {input_json}")
    print(f"Input type: {type(input_json)}")
    print(f"Input length: {len(input_json)}")
    print("==================")

    data = json.loads(input_json)
    # Simulate writing final output to S3
    data["job4_s3_output"] = "s3://dummy-bucket/job4.json"
    print(json.dumps(data))
