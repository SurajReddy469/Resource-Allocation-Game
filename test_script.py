import urllib.request
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_endpoint(name, method, path, data=None):
    url = BASE_URL + path
    try:
        req = urllib.request.Request(url, method=method)
        if data:
            req.add_header('Content-Type', 'application/json')
            req.data = json.dumps(data).encode('utf-8')
        
        response = urllib.request.urlopen(req)
        body = response.read().decode('utf-8')
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return body
    except urllib.error.HTTPError as e:
        print(f"[{name}] FAILED - HTTP Error {e.code}: {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"[{name}] FAILED - Exception: {e}")
        return None

def run_tests():
    print("Testing CFAI application (Edge Cases)...")
    
    # 3. Start Game
    start_payload = {
        "map": "standard",
        "total_turns": 3,
        "starting_resources": 50,
        "regen": 10,
        "ai_mode": "auto"
    }
    state = test_endpoint("Start Game", "POST", "/api/game/start", start_payload)
    print("Game Started!")
    
    # Edge case 1: play without allocations
    res1 = test_endpoint("Play Turn without allocations", "POST", "/api/game/play", {})
    if res1 is None:
        print("Empty payload failed gracefully via HTTP error")
    elif "error" in res1:
        print("Empty payload handled. Result:", res1)
        
    # Edge case 2: overspending resources
    res2 = test_endpoint("Play Turn overspend", "POST", "/api/game/play", {"allocations": [100, 100, 100, 100, 100]})
    if res2 is None:
        print("Overspend payload failed gracefully via HTTP error")
    elif "error" in res2:
        print("Overspend payload handled. Result:", res2)

    # Edge case 3: negative allocations
    res3 = test_endpoint("Play Turn negative", "POST", "/api/game/play", {"allocations": [-10, -20, 0, 0, 0]})
    if res3 is None:
        print("Negative payload failed gracefully via HTTP error")
    elif "error" in res3:
        print("Negative payload handled. Result:", res3)

    # Edge case 4: invalid map
    res4 = test_endpoint("Start Game invalid map", "POST", "/api/game/start", {"map": "nonexistent_map"})
    if res4 is None:
        print("Invalid map failed gracefully via HTTP error")
    elif "error" in res4:
        print("Invalid map payload handled. Result:", res4)

if __name__ == "__main__":
    run_tests()
