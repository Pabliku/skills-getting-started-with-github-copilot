import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)


def default_activities():
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        },
    }


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities = copy.deepcopy(default_activities())


def test_get_activities_returns_available_activities():
    # Arrange: baseline activities are loaded through the fixture.

    # Act
    response = client.get("/activities")
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in payload
    assert payload["Chess Club"]["max_participants"] == 12
    assert payload["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_new_participant():
    # Arrange
    new_email = "test@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": new_email},
    )

    # Assert
    assert response.status_code == 200
    assert new_email in app_module.activities["Chess Club"]["participants"]
    assert "Signed up" in response.json()["message"]


def test_signup_duplicate_returns_400():
    # Arrange
    existing_email = "michael@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": existing_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_for_unknown_activity_returns_404():
    # Arrange
    new_email = "student@mergington.edu"

    # Act
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": new_email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_unregistered_participant_returns_404():
    # Arrange
    missing_email = "missing@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": missing_email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_delete_registered_participant_removes_them():
    # Arrange
    registered_email = "daniel@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": registered_email},
    )

    # Assert
    assert response.status_code == 200
    assert registered_email not in app_module.activities["Chess Club"]["participants"]
    assert "Unregistered" in response.json()["message"]
