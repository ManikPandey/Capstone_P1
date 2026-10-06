import json
import re

with open("demo_db.json", "r") as f:
    demo_db = json.load(f)

summary = demo_db["summary"]
data = demo_db["data"]

with open("server.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the DB dict in server.py
# Find everything between DB = { and class IncidentRequest
new_db_str = "DB = {\n"
new_db_str += f'    "incidents": [\n{json.dumps(summary, indent=8)}],\n'
new_db_str += f'    "incident_data": {{\n        "{summary["id"]}": {json.dumps(data, indent=8)}\n    }}\n'
new_db_str += "}\n\n"

content = re.sub(r'DB = \{.*?\n\nclass IncidentRequest', new_db_str + "class IncidentRequest", content, flags=re.DOTALL)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(content)

print("server.py updated with new DB.")
