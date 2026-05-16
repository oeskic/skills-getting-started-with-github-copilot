import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def restore_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


def encode_activity_name(activity_name: str) -> str:
    return quote(activity_name, safe="")


def test_get_activities_returns_activities():
    # Arrange
    expected_activities = {"Chess Club", "Programming Class", "Gym Class"}

    # Act
    response = client.get("/activities")
    json_data = response.json()

    # Assert
    assert response.status_code == 200
    assert expected_activities.issubset(set(json_data.keys()))
    assert isinstance(json_data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "teststudent@mergington.edu"
    path = f"/activities/{encode_activity_name(activity_name)}/signup?email={email}"

    # Act
    response = client.post(path)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_for_unknown_activity_returns_404():
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"
    path = f"/activities/{encode_activity_name(activity_name)}/signup?email={email}"

    # Act
    response = client.post(path)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_unsubscribes():
    # Arrange
    activity_name = "Gym Class"
    email = "remove-test@mergington.edu"
    signup_path = f"/activities/{encode_activity_name(activity_name)}/signup?email={email}"
    client.post(signup_path)
    delete_path = f"/activities/{encode_activity_name(activity_name)}/signup?email={email}"

    # Act
    response = client.delete(delete_path)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_remove_missing_participant_returns_404():
    # Arrange
    activity_name = "Programming Class"
    email = "ghost@mergington.edu"
    delete_path = f"/activities/{encode_activity_name(activity_name)}/signup?email={email}"

    # Act
    response = client.delete(delete_path)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
