import requests
import json
import sys

url = "http://127.0.0.1:8000/api/incidents"
data = {
    "title": "Jewelry Store Heist (Demo)",
    "statements": ["dummy"] * 5
}
try:
    res = requests.post(url, json=data)
    incident_id = res.json()["id"]
    
    # Now get the generated data
    res_data = requests.get(f"http://127.0.0.1:8000/api/incidents/{incident_id}").json()
    
    # Get the summary list
    res_summary = requests.get("http://127.0.0.1:8000/api/incidents").json()
    summary = next(s for s in res_summary if s["id"] == incident_id)
    
    with open("demo_db.json", "w") as f:
        json.dump({"summary": summary, "data": res_data}, f, indent=2)
    print("Demo DB saved.")
except Exception as e:
    print(e)
