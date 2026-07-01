"""
Tests for the POST /activities/{activity_name}/signup endpoint
"""
import pytest
from fastapi.testclient import TestClient


def test_signup_successful(client: TestClient):
    """Test successful signup for an activity"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Signed up newstudent@mergington.edu for Chess Club"
    
    # Verify the participant was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_activity_not_found(client: TestClient):
    """Test signup fails when activity doesn't exist"""
    response = client.post(
        "/activities/Nonexistent Activity/signup",
        params={"email": "student@mergington.edu"}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_signup_student_already_registered(client: TestClient):
    """Test signup fails when student is already registered"""
    # michael@mergington.edu is already in Chess Club
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student already signed up for this activity"


def test_signup_adds_to_participants_list(client: TestClient):
    """Test that signup correctly adds email to participants list"""
    # Get initial count
    initial_response = client.get("/activities")
    initial_count = len(initial_response.json()["Basketball Team"]["participants"])
    
    # Sign up new student
    client.post(
        "/activities/Basketball Team/signup",
        params={"email": "newplayer@mergington.edu"}
    )
    
    # Get updated count
    updated_response = client.get("/activities")
    updated_count = len(updated_response.json()["Basketball Team"]["participants"])
    
    assert updated_count == initial_count + 1


def test_signup_multiple_students_same_activity(client: TestClient):
    """Test multiple students can sign up for the same activity"""
    students = [
        "student1@mergington.edu",
        "student2@mergington.edu",
        "student3@mergington.edu"
    ]
    
    for email in students:
        response = client.post(
            "/activities/Art Studio/signup",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # Verify all students were added
    activities_response = client.get("/activities")
    participants = activities_response.json()["Art Studio"]["participants"]
    
    for email in students:
        assert email in participants


def test_signup_different_activities_same_student(client: TestClient):
    """Test same student can sign up for different activities"""
    email = "multitalented@mergington.edu"
    
    activities = ["Chess Club", "Drama Club", "Math Olympiad"]
    
    for activity in activities:
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # Verify student is in all activities
    all_activities = client.get("/activities").json()
    for activity in activities:
        assert email in all_activities[activity]["participants"]


def test_signup_preserves_existing_participants(client: TestClient):
    """Test that signing up doesn't remove existing participants"""
    # Get initial participants
    initial_response = client.get("/activities")
    initial_participants = initial_response.json()["Tennis Club"]["participants"].copy()
    
    # Sign up new student
    client.post(
        "/activities/Tennis Club/signup",
        params={"email": "newcomer@mergington.edu"}
    )
    
    # Get updated participants
    updated_response = client.get("/activities")
    updated_participants = updated_response.json()["Tennis Club"]["participants"]
    
    # All initial participants should still be there
    for participant in initial_participants:
        assert participant in updated_participants
    
    # New participant should also be there
    assert "newcomer@mergington.edu" in updated_participants
