import sys
import json


def get_json():
    json_data = sys.stdin.read()
    try:
        json.loads(json_data)
    except json.JSONDecodeError:
        print("Invalid JSON")
        sys.exit(1)
    return json.loads(json_data)


def convert(json_data: dict):
    payload = {
        "source": {
            "name": "textlint",
            "url": "https://github.com/textlint/textlint",
        },
        "severity": "WARNING",
        "diagnostics": [],
    }
    for data in json_data:
        messages = data["messages"]
        if messages == []:
            continue
        filepath = data["filePath"]
        for message in messages:
            diag = {
                "message": message["message"],
                "location": {
                    "path": filepath,
                    "range": {
                        "start": {"line": message["line"], "column": message["column"]},
                    },
                },
                "severity": "ERROR",
                "code": {
                    "value": message["ruleId"],
                },
            }
            payload["diagnostics"].append(diag)
    return payload


def main():
    json_data = get_json()
    payload = convert(json_data)
    if payload["diagnostics"] == []:
        sys.exit(0)
    else:
        print(json.dumps(payload))


if __name__ == "__main__":
    main()
