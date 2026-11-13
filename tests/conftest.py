import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app

# Template for fresh activity data for each test
INITIAL_ACTIVITIES = {
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
    "Basketball Team": {
        "description": "Practice basketball skills and compete in team games",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": []
    },
    "Soccer Club": {
        "description": "Develop soccer skills and play friendly matches",
        "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 22,
        "participants": []
    }
}


@pytest.fixture
def client():
    """Provides a TestClient for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def fresh_activities():
    """Provides fresh activity data and resets the app's activities for each test"""
    from src.app import activities
    
    # Store the original data
    original_data = deepcopy(activities)
    
    # Reset with fresh data
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))
    
    yield activities
    
    # Restore original data after test
    activities.clear()
    activities.update(original_data)
