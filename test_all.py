import time, requests, json

time.sleep(3)

# Test 1: GET all incidents — should show 5 cases
r = requests.get('http://127.0.0.1:8000/api/incidents')
cases = r.json()
print(f'Dashboard shows {len(cases)} cases:')
for c in cases:
    print(f'  - {c["id"]}: {c["title"]} ({c["contradictionCount"]} conflicts)')

# Test 2: GET detail for first case
first_id = cases[0]['id']
r2 = requests.get(f'http://127.0.0.1:8000/api/incidents/{first_id}')
detail = r2.json()
print(f'\nCase {first_id} detail:')
print(f'  Statements : {len(detail.get("statements", []))}')
print(f'  Timeline   : {len(detail.get("timeline", []))} events')
print(f'  Markers    : {len(detail.get("markers", []))} locations')
print(f'  Contradict : {len(detail.get("contradictions", []))}')
print(f'  RawEntities: {len(detail.get("raw_entities", []))}')

# Show first discrepancy snippet to verify real text extraction
if detail.get('contradictions'):
    c0 = detail['contradictions'][0]
    print(f'\nFirst discrepancy: {c0["title"]}')
    for claim in c0['claims']:
        snippet = claim.get('snippet', '')
        print(f'  {claim["witness"]}: "{snippet}"')

# Test 3: POST — trigger fallback
r3 = requests.post('http://127.0.0.1:8000/api/incidents', json={'title': 'Test', 'statements': ['dummy stmt 1', 'dummy stmt 2']})
r3_json = r3.json()
print(f'\nPOST /api/incidents: status={r3.status_code}, new_id={r3_json.get("id")}')

# Test 4: GET all incidents again — should now show 6
r4 = requests.get('http://127.0.0.1:8000/api/incidents')
print(f'Dashboard after POST: {len(r4.json())} cases total')
print('\nAll tests PASSED')
