"""Tests for the Mergington High School Activities API"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestGetActivities:
    """Tests for getting activities"""
    
    def test_get_activities_returns_200(self):
        """Test that GET /activities returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)
    
    def test_get_activities_contains_expected_activities(self):
        """Test that activities contain expected keys"""
        response = client.get("/activities")
        activities = response.json()
        
        # Check that we have activities
        assert len(activities) > 0
        
        # Check that expected activities are present
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        for activity in expected_activities:
            assert activity in activities
    
    def test_activity_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignup:
    """Tests for signing up for activities"""
    
    def test_signup_valid_user(self):
        """Test signing up a valid user for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
    
    def test_signup_nonexistent_activity(self):
        """Test signing up for a non-existent activity"""
        response = client.post(
            "/activities/Fake%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_email(self):
        """Test that duplicate signup is rejected"""
        email = "duplicate-test@mergington.edu"
        
        # Sign up the first time
        response1 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Try to sign up again with same email
        response2 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_different_activities(self):
        """Test that same user can sign up for different activities"""
        email = "multi-activity@mergington.edu"
        
        response1 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        response2 = client.post(
            f"/activities/Programming%20Class/signup?email={email}"
        )
        assert response2.status_code == 200


class TestUnregister:
    """Tests for unregistering from activities"""
    
    def test_unregister_valid_participant(self):
        """Test unregistering a valid participant"""
        email = "remove-test@mergington.edu"
        
        # First sign up
        client.post(f"/activities/Chess%20Club/signup?email={email}")
        
        # Then unregister
        response = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
    
    def test_unregister_nonexistent_activity(self):
        """Test unregistering from a non-existent activity"""
        response = client.delete(
            "/activities/Fake%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_not_registered_user(self):
        """Test unregistering a user who is not registered"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=not-registered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_removes_participant(self):
        """Test that unregister actually removes the participant"""
        email = "verify-removal@mergington.edu"
        
        # Sign up
        client.post(f"/activities/Debate%20Club/signup?email={email}")
        
        # Get activities and verify participant is there
        response1 = client.get("/activities")
        activities1 = response1.json()
        assert email in activities1["Debate Club"]["participants"]
        
        # Unregister
        client.delete(f"/activities/Debate%20Club/unregister?email={email}")
        
        # Get activities and verify participant is removed
        response2 = client.get("/activities")
        activities2 = response2.json()
        assert email not in activities2["Debate Club"]["participants"]


class TestRoot:
    """Tests for the root endpoint"""
    
    def test_root_redirects(self):
        """Test that root endpoint redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
