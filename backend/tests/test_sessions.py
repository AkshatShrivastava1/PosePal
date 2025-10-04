from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime, timezone

client = TestClient(app)

def test_session_flow():
    r = client.post("/sessions/start", json={"exercise":"squat"})
    assert r.status_code == 200
    sid = r.json()["session_id"]

    now = datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
    m = {"reps": 8, "avg_score": 0.8, "flags": ["knees_in"], "duration_sec": 40, "ts": now}
    r = client.post(f"/sessions/{sid}/metrics", json=m)
    assert r.status_code == 200

    r = client.post(f"/sessions/{sid}/stop", json={"ts": now})
    assert r.status_code == 200

    r = client.get(f"/sessions/{sid}/summary")
    assert r.status_code == 200
    data = r.json()
    assert data["total_reps"] >= 8
    assert data["exercise"] == "squat"
