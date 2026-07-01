"""
Tests for the DELETE /activities/{activity_name}/participants/{email} endpoint
"""
import pytest
from fastapi.testclient import TestClient


def test_remove_participant_successful(client: TestClient):
    """Test successful removal of a participant from an activity"""
    response = client.delete("/activities/Chess Club/participants/michael@mergington.edu")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Removed michael@mergington.edu from Chess Club"
    
    # Verify the participant was removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_remove_participant_activity_not_found(client: TestClient):
    """Test removal fails when activity doesn't exist"""
    response = client.delete("/activities/Nonexistent Activity/participants/student@mergington.edu")
    
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_remove_participant_not_in_activity(client: TestClient):
    """Test removal fails when participant is not in the activity"""
    response = client.delete("/activities/Chess Club/participants/notregistered@mergington.edu")
    
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Participant not found in this activity"


def test_remove_participant_reduces_count(client: TestClient):
    """Test that removing a participant reduces the count by one"""
    # Get initial count
    initial_response = client.get("/activities")
    initial_count = len(initial_response.json()["Programming Class"]["participants"])
    
    # Remove a participant
    client.delete("/activities/Programming Class/participants/emma@mergington.edu")
    
    # Get updated count
    updated_response = client.get("/activities")
    updated_count = len(updated_response.json()["Programming Class"]["participants"])
    
    assert updated_count == initial_count - 1


def test_remove_participant_preserves_others(client: TestClient):
    """Test that removing one participant doesn't affect others"""
    # Get initial participants
    initial_response = client.get("/activities")
    initial_participants = initial_response.json()["Gym Class"]["participants"].copy()
    
    # Remove one participant
    removed_email = "john@mergington.edu"
    client.delete(f"/activities/Gym Class/participants/{removed_email}")
    
    # Get updated participants
    updated_response = client.get("/activities")
    updated_participants = updated_response.json()["Gym Class"]["participants"]
    
    # Removed participant should be gone
    assert removed_email not in updated_participants
    
    # Other participants should still be there
    for participant in initial_participants:
        if participant != removed_email:
            assert participant in updated_participants


def test_remove_all_participants_one_by_one(client: TestClient):
    """Test removing all participants from an activity"""
    # Get initial participants
    initial_response = client.get("/activities")
    participants = initial_response.json()["Basketball Team"]["participants"].copy()
    
    # Remove all participants
    for email in participants:
        response = client.delete(f"/activities/Basketball Team/participants/{email}")
        assert response.status_code == 200
    
    # Verify list is empty
    final_response = client.get("/activities")
    final_participants = final_response.json()["Basketball Team"]["participants"]
    assert len(final_participants) == 0


def test_remove_and_signup_again(client: TestClient):
    """Test that a removed participant can sign up again"""
    email = "daniel@mergington.edu"
    activity = "Chess Club"
    
    # Remove participant
    response = client.delete(f"/activities/{activity}/participants/{email}")
    assert response.status_code == 200
    
    # Verify removed
    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]
    
    # Sign up again
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Verify added back
    activities = client.get("/activities").json()
    assert email in activities[activity]["participants"]


def test_remove_participant_case_sensitive(client: TestClient):
    """Test that participant removal is case-sensitive"""
    # Try to remove with different case
    response = client.delete("/activities/Chess Club/participants/MICHAEL@MERGINGTON.EDU")
    
    # Should fail because email case doesn't match
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Participant not found in this activity"


def test_remove_participant_from_multiple_activities(client: TestClient):
    """Test removing same participant from multiple activities"""
    email = "versatile@mergington.edu"
    
    # Sign up for multiple activities
    activities = ["Drama Club", "Debate Team"]
    for activity in activities:
        client.post(f"/activities/{activity}/signup", params={"email": email})
    
    # Remove from one activity
    response = client.delete(f"/activities/Drama Club/participants/{email}")
    assert response.status_code == 200
    
    # Verify removed from Drama Club but still in Debate Team
    all_activities = client.get("/activities").json()
    assert email not in all_activities["Drama Club"]["participants"]
    assert email in all_activities["Debate Team"]["participants"]
