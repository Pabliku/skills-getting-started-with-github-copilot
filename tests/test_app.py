from fastapi.testclient import TestClient

from src import app as app_module


client = TestClient(app_module.app)


def test_unregister_participant_removes_email_from_activity():
    app_module.activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu"],
        }
    }

    signup_response = client.post(
        "/activities/Chess Club/signup?email=test@mergington.edu"
    )
    assert signup_response.status_code == 200

    unregister_response = client.delete(
        "/activities/Chess Club/signup?email=test@mergington.edu"
    )
    assert unregister_response.status_code == 200
    assert "unregistered" in unregister_response.json()["message"].lower()

    activities_response = client.get("/activities")
    assert activities_response.status_code == 200
    assert "test@mergington.edu" not in activities_response.json()["Chess Club"]["participants"]
