import json
file_path = "C:/Workspace/ThesisMate/ThesisMate/chat_history.txt"
with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        last_line = lines[-1]  # or lines[-1:]
        print(last_line)