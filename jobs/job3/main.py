import sys
import json

if __name__ == "__main__":
    input_json = sys.stdin.read() or "[]"
    arr = json.loads(input_json)
    result = {}
    for d in arr:
        if "job1_s3_output" in d:
            result["job1_s3_output"] = d["job1_s3_output"]
        if "job2_s3_output" in d:
            result["job2_s3_output"] = d["job2_s3_output"]
    # Simulate writing merged output to S3
    result["job3_s3_output"] = "s3://dummy-bucket/job3.json"
    print(json.dumps(result))
