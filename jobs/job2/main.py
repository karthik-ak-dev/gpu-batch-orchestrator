import sys
import json

if __name__ == "__main__":
    input_json = sys.stdin.read() or "{}"
    data = json.loads(input_json)
    data["job2"] = "done"
    print(json.dumps(data))
