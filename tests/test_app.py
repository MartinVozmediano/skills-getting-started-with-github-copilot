"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestGetActivities:
    """Test cases for the GET /activities endpoint"""

    def test_get_activities_returns_200(self, client):
        """Test that /activities returns a 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self, client):
        """Test that /activities returns known activities"""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Swimming",
            "Debate Club",
            "Robotics Club",
            "Drama Club",
            "Art Studio"
        ]
        
        for activity in expected_activities:
            assert activity in data

    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_info in data.items():
            for field in required_fields:
                assert field in activity_info, f"Activity '{activity_name}' missing field '{field}'"


class TestSignup:
    """Test cases for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_valid_activity(self, client):
        """Test successful signup for a valid activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_duplicate_signup_returns_400(self, client):
        """Test that duplicate signup returns 400 error"""
        # Try to signup with an email that's already registered
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup adds participant to activity list"""
        email = "testuser@mergington.edu"
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_participants = len(initial_response.json()["Programming Class"]["participants"])
        
        # Sign up
        signup_response = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify participant was added
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()["Programming Class"]["participants"]
        
        assert email in updated_participants
        assert len(updated_participants) == initial_participants + 1


class TestRoot:
    """Test cases for the root endpoint"""

    def test_root_redirects(self, client):
        """Test that root endpoint redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
