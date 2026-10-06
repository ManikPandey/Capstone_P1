"""
build_seed_db.py
Generates a full 5-case seeded DB for server.py using theft_case_output.json as the
canonical ML output. Run once: python build_seed_db.py > seed_data.json
"""
import json, hashlib, datetime, copy, random

BASE_DATE = datetime.datetime(2024, 11, 3, 14, 0, 0)

# ---------- Real witness statements (no padding) ----------
HEIST_STATEMENTS = [
    "I was stationed by the glass doors of the Tanishq showroom on MG Road. Two masked robbers stormed inside. The robbers ordered all customers to lie flat on the floor. The primary robber was wearing a dark leather jacket and blue jeans.",
    "I run a café just across from the Tanishq store. I saw three robbers sprinted out of the store entrance carrying heavy duffel bags. Then the robbers pushed past frightened pedestrians on the sidewalk as people screamed for police assistance.",
    "On MG Road when the commotion erupted. The primary robber wore a dark leather jacket. The primary robber fled and then revved a motorcycle. The primary robber headed north toward the flyover.",
    "I was walking along MG Road. Suddenly the thieves dashed from the store. The primary robber was wearing a bright red hoodie with beige cargo pants.",
    "I was inside securing the cash register when I heard the alarm. The thieves took fifty lakhs worth of diamond necklaces and luxury watches from the vault counters. Emergency sirens began blaring within minutes."
]

with open("theft_case_output.json", encoding="utf-8") as f:
    ML_OUTPUT = json.load(f)

# ---------- Helper: map raw ML output to UI data for a set of statements ----------
def map_ml_to_ui(inc_id, title, case_type, date_str, status, statements, ml_output):
    ui_statements = [
        {"id": f"stmt_{i}", "witness": f"Witness {chr(65+i)}", "text": text, "status": "Processed"}
        for i, text in enumerate(statements)
    ]

    # Contradictions
    ui_contradictions = []
    for i, d in enumerate(ml_output.get("contradictions", [])):
        claims = []
        for span_info in d.get("source_span", []):
            stmt_id_str = span_info[0]   # e.g. "stmt_0"
            span_range = span_info[1]    # e.g. [28, 41]
            try:
                stmt_idx = int(stmt_id_str.split("_")[-1])
            except Exception:
                stmt_idx = 0
            if stmt_idx >= len(statements):
                stmt_idx = 0
            full_text = statements[stmt_idx]
            start, end = span_range[0], span_range[1]
            start = max(0, min(start, len(full_text)))
            end   = max(0, min(end,   len(full_text)))
            snippet = full_text[start:end] if end > start else full_text[:30]
            claims.append({
                "witness":  f"Witness {chr(65+stmt_idx)}",
                "snippet":  snippet,
                "fullText": full_text,
                "span":     [start, end]
            })
        ui_contradictions.append({
            "id":       f"c_{i}",
            "type":     d.get("type", "semantic"),
            "title":    f"Flagged Discrepancy #{i+1}",
            "rationale": d.get("rationale", "Statements conflict."),
            "claims":   claims
        })

    # Timeline — derive from events
    COLORS = ["border-blue-500","border-red-500","border-green-500","border-purple-500","border-yellow-500"]
    ui_timeline = []
    base_dt = datetime.datetime.fromisoformat(date_str + "T14:00:00")
    for i, ev in enumerate(ml_output.get("events", [])):
        try:
            stmt_idx = int(ev.get("source_statement_id","stmt_0").split("_")[-1])
        except Exception:
            stmt_idx = 0
        if stmt_idx >= len(statements): stmt_idx = 0
        t = base_dt + datetime.timedelta(minutes=i)
        subj   = ev.get("subject","") or ""
        action = ev.get("action","") or ""
        obj    = ev.get("object","") or ""
        content = f"{subj} {action} {obj}".strip()
        if len(content) > 90:
            content = content[:87] + "..."
        ui_timeline.append({
            "id":        f"ev_{i}",
            "content":   content,
            "start":     t.isoformat(),
            "witness":   f"Witness {chr(65+stmt_idx)}",
            "className": f"border-l-4 {COLORS[stmt_idx % len(COLORS)]} bg-[var(--bg-surface)] text-[var(--text-primary)]"
        })

    # Map markers — LOCATION entities with Bangalore coords
    # MG Road, Bengaluru: ~12.9750, 77.6069
    BASE_LAT, BASE_LNG = 12.9750, 77.6069
    ui_markers = []
    seen = set()
    for i, ent in enumerate(ml_output.get("entities", [])):
        if ent.get("label") not in ["LOCATION","FACILITY","GPE"]:
            continue
        label = ent.get("text","Location")
        if label in seen:
            continue
        seen.add(label)
        try:
            stmt_idx = int(ent.get("source_statement_id","stmt_0").split("_")[-1])
        except Exception:
            stmt_idx = 0
        offset = len(ui_markers)
        ui_markers.append({
            "id":      f"m_{i}",
            "lat":     round(BASE_LAT + offset * 0.0004, 6),
            "lng":     round(BASE_LNG + offset * 0.0003, 6),
            "label":   label,
            "witness": f"Witness {chr(65+stmt_idx)}",
            "color":   "blue"
        })

    # raw data for relationship graph
    raw_entities   = ml_output.get("entities", [])
    raw_events     = ml_output.get("events", [])

    summary = {
        "id":               inc_id,
        "title":            title,
        "type":             case_type,
        "date":             date_str,
        "status":           status,
        "witnessCount":     len(statements),
        "contradictionCount": len(ui_contradictions)
    }

    data = {
        "statements":    ui_statements,
        "markers":       ui_markers,
        "timeline":      ui_timeline,
        "contradictions": ui_contradictions,
        "raw_entities":  raw_entities,
        "raw_events":    raw_events
    }

    return summary, data


# ---------- Build 5 cases ----------
CASES = [
    # (id, title, type, date, status, statements — use HEIST data or variants)
    (
        "inc-demo01",
        "Tanishq Jewelry Heist — MG Road",
        "Armed Robbery",
        "2024-11-03",
        "Reviewing",
        HEIST_STATEMENTS
    ),
    (
        "inc-demo02",
        "Gold Vault Break-In — Commercial Street",
        "Burglary",
        "2024-11-10",
        "Active",
        [
            "I was the night guard at the Malabar Gold vault on Commercial Street. Around midnight two masked men cut through the rear shutter.",
            "I live above the shop. I heard drilling sounds late at night. Two men fled through the back alley carrying what looked like gold bars.",
            "I was watching from my window and saw one masked man wearing a blue hoodie. He revved a scooter before speeding away.",
            "I run a tea stall nearby. Three men, not two, ran past me toward the auto stand — the lead man had a bright orange jacket.",
            "I was the CCTV operator. The footage shows the vault door forced open at 00:13. The robbers took twelve kilograms of gold biscuits from safe #4."
        ]
    ),
    (
        "inc-demo03",
        "ATM Cash Heist — Indiranagar",
        "Theft",
        "2024-10-22",
        "Active",
        [
            "I was the ATM security guard on duty. At approximately 1 AM a black SUV rammed the ATM kiosk and three men jumped out with hydraulic cutters.",
            "I was passing by in an auto when I saw two men prying open the ATM. They escaped in a white sedan towards the 100 Feet Road.",
            "I live across the street. The vehicle was black — definitely an SUV, not a sedan. One of the men was wearing a red jacket.",
            "I am the bank branch manager. CCTV confirmed the incident at 01:07. Two crore rupees in cash was removed from the ATM cassettes.",
            "I witnessed the getaway from the adjacent parking lot. The car was silver — I am certain because it passed under the street light."
        ]
    ),
    (
        "inc-demo04",
        "Diamond Merchant Robbery — Chickpet",
        "Armed Robbery",
        "2024-09-14",
        "Archived",
        [
            "I am the shop owner. Two armed men walked in posing as buyers and held my staff at gunpoint. They took diamonds worth eighty lakhs.",
            "I was a customer inside the shop. I saw three robbers — one stayed at the door, two went behind the counter.",
            "I am a vendor next door. I heard shouting and saw one man run out without a weapon. He wore a grey tracksuit.",
            "I was on the street opposite. The man I saw fleeing wore a black kurta, not a tracksuit.",
            "I am the investigating officer. Forensics confirmed two distinct sets of boot prints inside. Witness accounts conflict on the number of robbers — two vs three."
        ]
    ),
    (
        "inc-demo05",
        "Bank Locker Fraud — Koramangala",
        "Financial Fraud",
        "2024-08-30",
        "Active",
        [
            "I am the bank manager. An individual presenting forged KYC documents accessed locker #112 and removed gold worth thirty lakhs.",
            "I am the customer whose locker was accessed. I had last visited on 10th August. The signatures on the access register do not match mine.",
            "I am the bank teller who processed the access request. The individual appeared nervous and left in a hurry after 15 minutes.",
            "I am the security guard at the entrance. The individual who entered that day was a woman in a blue saree, not a man.",
            "I am the CCTV review officer. The footage from camera 3 clearly shows a woman in blue entering the locker area at 11:42 AM."
        ]
    )
]

all_summaries = []
all_data = {}

for inc_id, title, case_type, date_str, status, stmts in CASES:
    summary, data = map_ml_to_ui(inc_id, title, case_type, date_str, status, stmts, ML_OUTPUT)
    all_summaries.append(summary)
    all_data[inc_id] = data

result = {"incidents": all_summaries, "incident_data": all_data}
with open("seed_data.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"Done — {len(all_summaries)} cases written to seed_data.json")
