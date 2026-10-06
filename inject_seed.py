"""
inject_seed.py
Reads seed_data.json and writes a clean server.py with proper DB initialization.
"""
import json, re

with open("seed_data.json", encoding="utf-8") as f:
    seed = json.load(f)

with open("server.py", encoding="utf-8") as f:
    content = f.read()

# Build the DB block as a Python literal string
db_block = f"DB = {json.dumps(seed, indent=4, ensure_ascii=False)}\n"

# Replace from "DB = {" to just before "class IncidentRequest"
new_content = re.sub(
    r'# --- In-Memory Database ---\nDB = \{.*?\n\nclass IncidentRequest',
    f"# --- In-Memory Database (seeded from theft_case_output.json) ---\n{db_block}\nclass IncidentRequest",
    content,
    flags=re.DOTALL
)

if new_content == content:
    print("Pattern not matched — trying alternate replacement")
    # fallback: find DB = { up to } followed by class
    new_content = re.sub(
        r'DB = \{.*?\n(?=class IncidentRequest)',
        f"{db_block}\n",
        content,
        flags=re.DOTALL
    )

with open("server.py", "w", encoding="utf-8") as f:
    f.write(new_content)

print("server.py injected with 5-case seed DB.")
