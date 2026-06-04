"""
Shared pytest fixtures for test setup and teardown.
Provides TestClient and fresh activity database for each test.
"""

import copy
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """
    Provides a TestClient for making HTTP requests to the FastAPI app.
    """
    return TestClient(app)


@pytest.fixture
def fresh_activities(monkeypatch):
    """
    Provides a fresh copy of activities for each test to ensure isolation.
    Resets the global activities dict before each test.
    """
    # Create a deep copy of the original activities
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Team-based soccer training and matches",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["isaac@mergington.edu", "lina@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Practice basketball skills and play friendly games",
            "schedule": "Wednesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["nate@mergington.edu", "mia@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore drawing, painting, and mixed media projects",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["zoe@mergington.edu", "hannah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Rehearse scenes, improvise, and prepare for performances",
            "schedule": "Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["ryan@mergington.edu", "bella@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["alex@mergington.edu", "sara@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Design, build, and program robots for challenges",
            "schedule": "Mondays and Fridays, 3:30 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["carter@mergington.edu", "maya@mergington.edu"]
        }
    }

    # Replace the global activities with a deep copy for this test
    fresh_copy = copy.deepcopy(original_activities)
    monkeypatch.setattr("app.activities", fresh_copy)

    return fresh_copy
