import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import get_session
from sqlmodel import Session as SQLSession, create_engine
from app.db.models import SessionDB, SessionMetric
from datetime import datetime, timezone
import json

# Create test database
engine = create_engine("sqlite:///:memory:")
SQLModel.metadata.create_all(engine)

def get_test_session():
    with Session(engine) as session:
        yield session

app.dependency_overrides[get_session] = get_test_session
client = TestClient(app)

def test_metrics_endpoint():
    """Test the metrics endpoint with correct data format"""
    
    # Create a test session
    session_data = {
        "exercise": "squat",
        "user_id": 1
    }
    
    response = client.post("/sessions/start", json=session_data)
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    
    # Test metrics endpoint with correct format
    metrics_data = {
        "reps": 5,
        "avg_score": 0.8,
        "duration_sec": 120,
        "ts": datetime.now(timezone.utc).isoformat()
    }
    
    response = client.post(f"/sessions/{session_id}/metrics", json=metrics_data)
    assert response.status_code == 200
    assert response.json() == {"ok": True}

def test_metrics_endpoint_wrong_format():
    """Test the metrics endpoint with wrong data format (should fail)"""
    
    # Create a test session
    session_data = {
        "exercise": "squat",
        "user_id": 1
    }
    
    response = client.post("/sessions/start", json=session_data)
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    
    # Test with wrong format (missing required fields)
    wrong_metrics_data = {
        "reps": 5,
        "durationSec": 120,  # Wrong field name
        "timestamp": datetime.now(timezone.utc).isoformat()  # Wrong field name
    }
    
    response = client.post(f"/sessions/{session_id}/metrics", json=wrong_metrics_data)
    assert response.status_code == 422  # Unprocessable Entity

def test_analysis_endpoint_no_session():
    """Test analysis endpoint with non-existent session"""
    
    response = client.post("/analysis/analyze-and-cleanup/999")
    assert response.status_code == 404

def test_analysis_endpoint_active_session():
    """Test analysis endpoint with active session (should fail)"""
    
    # Create a test session
    session_data = {
        "exercise": "squat",
        "user_id": 1
    }
    
    response = client.post("/sessions/start", json=session_data)
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    
    # Try to analyze active session (should fail)
    response = client.post(f"/analysis/analyze-and-cleanup/{session_id}")
    assert response.status_code == 400  # Bad Request - session not ended
