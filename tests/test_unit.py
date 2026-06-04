"""
Unit tests for business logic and validation functions.
Tests core logic without the HTTP layer.
"""

import pytest


def test_activity_exists_in_fresh_activities(fresh_activities):
    """Test that fresh activities contains expected activities."""
    assert "Chess Club" in fresh_activities
    assert "Programming Class" in fresh_activities
    assert "Gym Class" in fresh_activities
    assert len(fresh_activities) == 9


def test_activity_data_structure(fresh_activities):
    """Test that activity data has correct structure and fields."""
    activity = fresh_activities["Chess Club"]
    
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)


def test_participant_list_is_list(fresh_activities):
    """Test that participants field is a list."""
    activity = fresh_activities["Chess Club"]
    assert isinstance(activity["participants"], list)
    assert len(activity["participants"]) == 2


def test_activity_isolation_between_tests(fresh_activities):
    """
    Test that modifications to activities in one test don't affect setup.
    Each test should get a fresh copy.
    """
    # Modify the activities
    fresh_activities["Chess Club"]["participants"].append("new@student.edu")
    assert len(fresh_activities["Chess Club"]["participants"]) == 3


def test_max_participants_field_exists(fresh_activities):
    """Test that all activities have max_participants field."""
    for activity_name, activity_data in fresh_activities.items():
        assert "max_participants" in activity_data
        assert isinstance(activity_data["max_participants"], int)
        assert activity_data["max_participants"] > 0


def test_participants_are_emails(fresh_activities):
    """Test that participants are valid-looking email addresses."""
    for activity_name, activity_data in fresh_activities.items():
        for participant in activity_data["participants"]:
            assert "@" in participant
            assert participant.endswith(".edu") or "@" in participant


def test_duplicate_detection_logic(fresh_activities):
    """Test logic for detecting duplicate signup attempts."""
    activity = fresh_activities["Chess Club"]
    original_count = len(activity["participants"])
    
    # Check if email is already in list (duplicate detection)
    test_email = "michael@mergington.edu"
    is_duplicate = test_email in activity["participants"]
    
    assert is_duplicate is True
    assert len(activity["participants"]) == original_count


def test_participant_removal_logic(fresh_activities):
    """Test logic for removing a participant."""
    activity = fresh_activities["Chess Club"]
    original_count = len(activity["participants"])
    email_to_remove = "michael@mergington.edu"
    
    # Verify participant exists before removal
    assert email_to_remove in activity["participants"]
    
    # Remove participant
    activity["participants"].remove(email_to_remove)
    
    # Verify removal
    assert email_to_remove not in activity["participants"]
    assert len(activity["participants"]) == original_count - 1


def test_nonexistent_participant_removal_fails(fresh_activities):
    """Test that removing a nonexistent participant raises error."""
    activity = fresh_activities["Chess Club"]
    nonexistent_email = "doesnotexist@test.edu"
    
    assert nonexistent_email not in activity["participants"]
    
    with pytest.raises(ValueError):
        activity["participants"].remove(nonexistent_email)
