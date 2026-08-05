import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

original_activities = copy.deepcopy(activities)
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(original_activities))
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert payload["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_for_activity():
    test_email = "newstudent@mergington.edu"
    response = client.post("/activities/Chess%20Club/signup", params={"email": test_email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {test_email} for Chess Club"
    assert test_email in activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    test_email = "duplicate@mergington.edu"
    first_response = client.post("/activities/Chess%20Club/signup", params={"email": test_email})
    assert first_response.status_code == 200

    second_response = client.post("/activities/Chess%20Club/signup", params={"email": test_email})

    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up for this activity"


def test_delete_participant():
    email_to_remove = "michael@mergington.edu"
    response = client.delete("/activities/Chess%20Club/participants", params={"email": email_to_remove})

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email_to_remove} from Chess Club"
    assert email_to_remove not in activities["Chess Club"]["participants"]


def test_delete_nonexistent_participant_returns_404():
    response = client.delete("/activities/Chess%20Club/participants", params={"email": "missing@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_root_redirects_to_static_index():
    response = client.get("/", allow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"
