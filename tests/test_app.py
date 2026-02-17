import sys
import pathlib
from urllib.parse import quote

import pytest

# Ensure `src` is on path so we can import `app`
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Known activity
    assert "Chess Club" in data


def test_signup_and_reflects_in_get():
    activity = "Chess Club"
    email = "pytest_student@example.com"
    # Ensure not already present
    resp = client.get("/activities")
    assert resp.status_code == 200
    if email in resp.json()[activity]["participants"]:
        # remove for deterministic test - but app has no delete; skip if present
        pytest.skip("Email already present in initial data")

    # Signup
    path = f"/activities/{quote(activity)}/signup?email={quote(email)}"
    resp = client.post(path)
    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body.get("message", "")

    # Confirm participant appears
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email in resp.json()[activity]["participants"]


def test_duplicate_signup_returns_400():
    activity = "Chess Club"
    email = "pytest_duplicate@example.com"
    path = f"/activities/{quote(activity)}/signup?email={quote(email)}"

    resp = client.post(path)
    assert resp.status_code == 200

    # Second attempt should fail with 400
    resp2 = client.post(path)
    assert resp2.status_code == 400


def test_signup_nonexistent_activity_returns_404():
    activity = "Nonexistent"
    email = "noone@example.com"
    path = f"/activities/{quote(activity)}/signup?email={quote(email)}"
    resp = client.post(path)
    assert resp.status_code == 404
