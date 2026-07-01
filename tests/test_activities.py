"""
Tests for the GET /activities endpoint
"""
import pytest
from fastapi.testclient import TestClient


def test_get_activities_returns_all_activities(client: TestClient):
    """Test that GET /activities returns all available activities"""
    response = client.get("/activities")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify we get all 9 activities
    assert len(data) == 9
    
    # Verify some expected activities exist
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    assert "Basketball Team" in data


def test_get_activities_structure(client: TestClient):
    """Test that each activity has the correct structure"""
    response = client.get("/activities")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check that each activity has required fields
    for activity_name, activity_data in data.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        
        # Verify data types
        assert isinstance(activity_data["description"], str)
        assert isinstance(activity_data["schedule"], str)
        assert isinstance(activity_data["max_participants"], int)
        assert isinstance(activity_data["participants"], list)


def test_get_activities_chess_club_details(client: TestClient):
    """Test that Chess Club has correct initial data"""
    response = client.get("/activities")
    
    assert response.status_code == 200
    data = response.json()
    
    chess_club = data["Chess Club"]
    assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
    assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert chess_club["max_participants"] == 12
    assert "michael@mergington.edu" in chess_club["participants"]
    assert "daniel@mergington.edu" in chess_club["participants"]


def test_get_activities_programming_class_details(client: TestClient):
    """Test that Programming Class has correct initial data"""
    response = client.get("/activities")
    
    assert response.status_code == 200
    data = response.json()
    
    programming = data["Programming Class"]
    assert programming["description"] == "Learn programming fundamentals and build software projects"
    assert programming["schedule"] == "Tuesdays and Thursdays, 3:30 PM - 4:30 PM"
    assert programming["max_participants"] == 20
    assert "emma@mergington.edu" in programming["participants"]
    assert "sophia@mergington.edu" in programming["participants"]


def test_get_activities_participants_are_lists(client: TestClient):
    """Test that participants field is always a list"""
    response = client.get("/activities")
    
    assert response.status_code == 200
    data = response.json()
    
    for activity_name, activity_data in data.items():
        participants = activity_data["participants"]
        assert isinstance(participants, list), f"{activity_name} participants should be a list"
        
        # All participants should be strings (emails)
        for participant in participants:
            assert isinstance(participant, str)
            assert "@" in participant  # Basic email validation
