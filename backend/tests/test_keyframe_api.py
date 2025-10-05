import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from datetime import datetime
from app.main import app
from app.db.models import User, SessionDB, AnnotatedFrame
from app.services.keyframe_detector import keyframe_detector


# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

def get_test_session():
    with Session(engine) as session:
        yield session

# Override the dependency
app.dependency_overrides[get_test_session] = get_test_session

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_test_db():
    """Set up test database"""
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def test_user(setup_test_db):
    """Create a test user"""
    with Session(engine) as session:
        user = User(
            email="test@example.com",
            full_name="Test User",
            hashed_password="hashed_password"
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


@pytest.fixture
def test_session(test_user):
    """Create a test workout session"""
    with Session(engine) as session:
        workout_session = SessionDB(
            user_id=test_user.id,
            exercise="squat",
            start_ts=datetime.now()
        )
        session.add(workout_session)
        session.commit()
        session.refresh(workout_session)
        return workout_session


class TestKeyframeAPI:
    """Test suite for keyframe API endpoints"""
    
    def test_store_keyframe_success(self, test_session):
        """Test successful keyframe storage"""
        keyframe_data = {
            "session_id": test_session.id,
            "frame_data": "base64_encoded_frame_data",
            "keyframe_type": "bottom",
            "exercise": "squat",
            "pose_landmarks": [
                {"name": "LEFT_HIP", "x": 100, "y": 200},
                {"name": "RIGHT_HIP", "x": 200, "y": 200}
            ]
        }
        
        response = client.post("/keyframes/keyframes", json=keyframe_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == test_session.id
        assert data["keyframe_type"] == "bottom"
        assert data["exercise"] == "squat"
        assert "id" in data
        assert "timestamp" in data
    
    def test_store_keyframe_invalid_session(self):
        """Test keyframe storage with invalid session ID"""
        keyframe_data = {
            "session_id": 99999,  # Non-existent session
            "frame_data": "base64_encoded_frame_data",
            "keyframe_type": "bottom",
            "exercise": "squat",
            "pose_landmarks": []
        }
        
        response = client.post("/keyframes/keyframes", json=keyframe_data)
        
        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]
    
    def test_get_session_keyframes(self, test_session):
        """Test retrieving keyframes for a session"""
        # First, store some keyframes
        keyframes_data = [
            {
                "session_id": test_session.id,
                "frame_data": "frame1_data",
                "keyframe_type": "bottom",
                "exercise": "squat",
                "pose_landmarks": []
            },
            {
                "session_id": test_session.id,
                "frame_data": "frame2_data",
                "keyframe_type": "top",
                "exercise": "squat",
                "pose_landmarks": []
            }
        ]
        
        # Store keyframes
        for keyframe_data in keyframes_data:
            response = client.post("/keyframes/keyframes", json=keyframe_data)
            assert response.status_code == 200
        
        # Retrieve keyframes
        response = client.get(f"/keyframes/sessions/{test_session.id}/keyframes")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 2
        assert len(data["keyframes"]) == 2
        
        # Verify keyframes are ordered by timestamp
        keyframes = data["keyframes"]
        assert keyframes[0]["keyframe_type"] == "bottom"
        assert keyframes[1]["keyframe_type"] == "top"
    
    def test_get_session_keyframes_empty(self, test_session):
        """Test retrieving keyframes for session with no keyframes"""
        response = client.get(f"/keyframes/sessions/{test_session.id}/keyframes")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 0
        assert len(data["keyframes"]) == 0
    
    def test_get_session_keyframes_invalid_session(self):
        """Test retrieving keyframes for invalid session"""
        response = client.get("/keyframes/sessions/99999/keyframes")
        
        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]
    
    def test_clear_session_keyframes(self, test_session):
        """Test clearing keyframes for a session"""
        # First, store some keyframes
        keyframe_data = {
            "session_id": test_session.id,
            "frame_data": "frame_data",
            "keyframe_type": "bottom",
            "exercise": "squat",
            "pose_landmarks": []
        }
        
        response = client.post("/keyframes/keyframes", json=keyframe_data)
        assert response.status_code == 200
        
        # Clear keyframes
        response = client.delete(f"/keyframes/sessions/{test_session.id}/keyframes")
        
        assert response.status_code == 200
        data = response.json()
        assert "Cleared 1 keyframes" in data["message"]
        
        # Verify keyframes are cleared
        response = client.get(f"/keyframes/sessions/{test_session.id}/keyframes")
        data = response.json()
        assert data["total_count"] == 0
    
    def test_clear_session_keyframes_invalid_session(self):
        """Test clearing keyframes for invalid session"""
        response = client.delete("/keyframes/sessions/99999/keyframes")
        
        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]
    
    def test_get_session_rep_count(self, test_session):
        """Test getting rep count for a session"""
        # Set up some rep counting state
        keyframe_detector.rep_counters[test_session.id] = {
            'current_rep_phases': set(),
            'total_reps': 3,
            'last_complete_rep_time': datetime.now()
        }
        
        response = client.get(f"/keyframes/sessions/{test_session.id}/rep-count")
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == test_session.id
        assert data["exercise"] == "squat"
        assert data["rep_count"] == 3
        assert data["counts_reps"] == True
    
    def test_get_session_rep_count_plank(self, test_user):
        """Test getting rep count for plank exercise (doesn't count reps)"""
        with Session(engine) as session:
            plank_session = SessionDB(
                user_id=test_user.id,
                exercise="plank",
                start_ts=datetime.now()
            )
            session.add(plank_session)
            session.commit()
            session.refresh(plank_session)
        
        response = client.get(f"/keyframes/sessions/{plank_session.id}/rep-count")
        
        assert response.status_code == 200
        data = response.json()
        assert data["exercise"] == "plank"
        assert data["counts_reps"] == False
    
    def test_get_session_rep_count_invalid_session(self):
        """Test getting rep count for invalid session"""
        response = client.get("/keyframes/sessions/99999/rep-count")
        
        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]


class TestKeyframeAPIValidation:
    """Test API validation and error handling"""
    
    def test_store_keyframe_missing_fields(self, test_session):
        """Test keyframe storage with missing required fields"""
        # Missing frame_data
        keyframe_data = {
            "session_id": test_session.id,
            "keyframe_type": "bottom",
            "exercise": "squat"
        }
        
        response = client.post("/keyframes/keyframes", json=keyframe_data)
        assert response.status_code == 422  # Validation error
    
    def test_store_keyframe_invalid_keyframe_type(self, test_session):
        """Test keyframe storage with invalid keyframe type"""
        keyframe_data = {
            "session_id": test_session.id,
            "frame_data": "base64_data",
            "keyframe_type": "invalid_type",
            "exercise": "squat",
            "pose_landmarks": []
        }
        
        response = client.post("/keyframes/keyframes", json=keyframe_data)
        # Should still work - validation is not strict on keyframe_type
        assert response.status_code == 200
    
    def test_store_keyframe_invalid_exercise(self, test_session):
        """Test keyframe storage with invalid exercise type"""
        keyframe_data = {
            "session_id": test_session.id,
            "frame_data": "base64_data",
            "keyframe_type": "bottom",
            "exercise": "invalid_exercise",
            "pose_landmarks": []
        }
        
        response = client.post("/keyframes/keyframes", json=keyframe_data)
        # Should still work - validation is not strict on exercise
        assert response.status_code == 200


class TestKeyframeAPIIntegration:
    """Integration tests for keyframe API with detector state"""
    
    def test_keyframe_storage_with_detector_reset(self, test_session):
        """Test that clearing keyframes resets detector state"""
        # Set up detector state
        keyframe_detector.motion_state[test_session.id] = {
            'last_phase': 'bottom',
            'last_keyframe_time': datetime.now(),
            'last_landmarks': []
        }
        keyframe_detector.rep_counters[test_session.id] = {
            'current_rep_phases': {'bottom'},
            'total_reps': 2,
            'last_complete_rep_time': datetime.now()
        }
        
        # Store a keyframe
        keyframe_data = {
            "session_id": test_session.id,
            "frame_data": "base64_data",
            "keyframe_type": "bottom",
            "exercise": "squat",
            "pose_landmarks": []
        }
        response = client.post("/keyframes/keyframes", json=keyframe_data)
        assert response.status_code == 200
        
        # Clear keyframes (should reset detector state)
        response = client.delete(f"/keyframes/sessions/{test_session.id}/keyframes")
        assert response.status_code == 200
        
        # Verify detector state is reset
        assert test_session.id not in keyframe_detector.motion_state
        assert test_session.id not in keyframe_detector.rep_counters
        assert keyframe_detector.get_rep_count(test_session.id) == 0
