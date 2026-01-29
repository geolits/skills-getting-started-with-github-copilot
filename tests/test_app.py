import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestActivities:
    """Test activity endpoints"""

    def test_get_activities(self):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Basketball" in data
        assert "Chess Club" in data

    def test_activity_structure(self):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Basketball"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity

    def test_activity_participants_initial(self):
        """Test that some activities have initial participants"""
        response = client.get("/activities")
        data = response.json()
        
        # Chess Club should have participants
        assert len(data["Chess Club"]["participants"]) > 0
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]


class TestSignup:
    """Test signup functionality"""

    def test_signup_for_activity(self):
        """Test signing up for an activity"""
        response = client.post(
            "/activities/Basketball/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]

    def test_signup_already_registered(self):
        """Test that duplicate signup is rejected"""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/Tennis Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            f"/activities/Tennis Club/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_nonexistent_activity(self):
        """Test signing up for non-existent activity"""
        response = client.post(
            "/activities/Fake Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestUnregister:
    """Test unregister functionality"""

    def test_unregister_participant(self):
        """Test unregistering a participant"""
        email = "unregister@mergington.edu"
        
        # First sign up
        client.post(f"/activities/Art Studio/signup?email={email}")
        
        # Then unregister
        response = client.delete(
            f"/activities/Art Studio/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
        
        # Verify participant is removed
        activities = client.get("/activities").json()
        assert email not in activities["Art Studio"]["participants"]

    def test_unregister_not_registered(self):
        """Test unregistering someone not registered"""
        response = client.delete(
            "/activities/Drama Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_nonexistent_activity(self):
        """Test unregistering from non-existent activity"""
        response = client.delete(
            "/activities/Fake Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_existing_participant(self):
        """Test unregistering an existing participant"""
        # Unregister from Chess Club which has participants
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify participant is removed
        activities = client.get("/activities").json()
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
