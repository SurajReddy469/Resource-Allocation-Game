import urllib.request
import json

BASE_URL = "http://127.0.0.1:5000"

def test_endpoint(method, path, data=None):
    url = BASE_URL + path
    try:
        req = urllib.request.Request(url, method=method)
        if data:
            req.add_header('Content-Type', 'application/json')
            req.data = json.dumps(data).encode('utf-8')
        
        response = urllib.request.urlopen(req)
        return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return {"error": str(e)}

print("Starting game...")
test_endpoint("POST", "/api/game/start", {"map": "standard", "total_turns": 3})

print("Playing turn 1...")
test_endpoint("POST", "/api/game/play", {"allocations": [10, 10, 10, 10, 10]})

print("\n--- Testing Admin ---")
admin_logs = test_endpoint("GET", "/api/admin/reasoning-logs")
print(f"Admin Logs Type: {type(admin_logs)}, Contains error: {'error' in admin_logs}")

fairness = test_endpoint("GET", "/api/admin/fairness")
print(f"Fairness Type: {type(fairness)}, Contains error: {'error' in fairness}")

print("\n--- Testing Analytics ---")
analytics = test_endpoint("GET", "/api/analytics/live")
print(f"Analytics Type: {type(analytics)}, Contains error: {'error' in analytics}")

print("\n--- Testing Reasoning ---")
reasoning = test_endpoint("GET", "/api/reasoning/traces")
print(f"Reasoning Type: {type(reasoning)}, Contains error: {'error' in reasoning if isinstance(reasoning, dict) else False}")
