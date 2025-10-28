import json
import os

file_path = "C:/Workspace/ThesisMate/chat_history.txt"

if os.path.exists(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        if lines:
            last_line = lines[-1].strip()
            print("Debug Raw:", last_line)

            # Parse the JSON safely
            try:
                data = json.loads(last_line)
                print("Debug Parsed JSON:", data)
            except json.JSONDecodeError as e:
                print("JSON Decode Error:", e)
                data = {}

            # Extract context if it exists
            context_str = data.get("answer", "") if isinstance(data, dict) else ""
            print("Context:", context_str)

        else:
            context_str = ""
            print("Debug: File empty")
else:
    context_str = ""
    print("Debug: File not found")
