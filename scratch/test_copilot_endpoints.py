import httpx

base_url = "http://localhost:8010/api/v1/copilot"

# 1. Start a chat session
try:
    resp = httpx.post(f"{base_url}/chat/sessions", json={"title": "EGFR Test Session"})
    session_id = resp.json()["id"]
    print("Created Chat Session:", session_id)
    
    # 2. Query Chat respond
    print("\n--- Testing Chat Response for 'Show top 10 EGFR compounds' ---")
    payload = {"message": "Show top 10 EGFR compounds"}
    chat_resp = httpx.post(f"{base_url}/chat/sessions/{session_id}/respond", json=payload, timeout=5.0)
    print("Status:", chat_resp.status_code)
    print("Content Preview:")
    print(chat_resp.json()["content"][:500] + "...")
    print("Citations:")
    print(chat_resp.json()["citations_json"])
    
    # 3. Query Plan
    print("\n--- Testing Query Plan for 'Show top 10 EGFR compounds' ---")
    plan_resp = httpx.post(f"{base_url}/query-plan", json={"query": "Show top 10 EGFR compounds"}, timeout=5.0)
    print("Status:", plan_resp.status_code)
    print("Plan:", plan_resp.json())
    
    # 4. Dashboard
    print("\n--- Testing Dashboard for 'Show top 10 EGFR compounds' ---")
    dash_resp = httpx.post(f"{base_url}/dashboard", json={"prompt": "Show top 10 EGFR compounds"}, timeout=5.0)
    print("Status:", dash_resp.status_code)
    print("Dashboard Title:", dash_resp.json()["title"])
    print("Widgets count:", len(dash_resp.json()["widgets"]))
    print("Widget 1 X values:", dash_resp.json()["widgets"][0]["plotly_data"][0]["x"])
    print("Widget 1 Y values:", dash_resp.json()["widgets"][0]["plotly_data"][0]["y"])
    
except Exception as e:
    print("Error:", e)
