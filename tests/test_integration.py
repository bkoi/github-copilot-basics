"""
Integration tests for FastAPI endpoints.
Tests full HTTP layer with client making requests to endpoints.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_200(self, client, fresh_activities):
        """Test that GET /activities returns HTTP 200."""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client, fresh_activities):
        """Test that GET /activities returns a dictionary."""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)

    def test_get_activities_contains_all_activities(self, client, fresh_activities):
        """Test that response contains all expected activities."""
        response = client.get("/activities")
        data = response.json()
        
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert len(data) == 9

    def test_get_activities_includes_activity_details(self, client, fresh_activities):
        """Test that each activity includes required fields."""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club

    def test_get_activities_participants_field_is_list(self, client, fresh_activities):
        """Test that participants field is a list."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_reflects_initial_participants(self, client, fresh_activities):
        """Test that GET /activities shows initial participant count."""
        response = client.get("/activities")
        data = response.json()
        
        # Chess Club should start with 2 participants
        assert len(data["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]


class TestRootRedirect:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """Test that GET / redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert "/static/index.html" in response.headers["location"]

    def test_root_redirect_with_follow(self, client):
        """Test that following root redirect works."""
        response = client.get("/", follow_redirects=True)
        assert response.status_code == 200


class TestSignupSuccess:
    """Tests for successful POST /activities/{activity_name}/signup."""

    def test_signup_returns_200(self, client, fresh_activities):
        """Test that successful signup returns HTTP 200."""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200

    def test_signup_returns_success_message(self, client, fresh_activities):
        """Test that signup response includes success message."""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_adds_participant(self, client, fresh_activities):
        """Test that signup actually adds participant to activity."""
        # Get initial state
        response_before = client.get("/activities")
        data_before = response_before.json()
        initial_count = len(data_before["Chess Club"]["participants"])
        
        # Sign up
        client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        # Check new state
        response_after = client.get("/activities")
        data_after = response_after.json()
        new_count = len(data_after["Chess Club"]["participants"])
        
        assert new_count == initial_count + 1
        assert "newstudent@mergington.edu" in data_after["Chess Club"]["participants"]

    def test_signup_with_email_format(self, client, fresh_activities):
        """Test signup with various email formats."""
        emails = [
            "test.user@mergington.edu",
            "student123@mergington.edu",
            "a.b.c@mergington.edu"
        ]
        
        for i, email in enumerate(emails):
            response = client.post(
                "/activities/Programming%20Class/signup",
                params={"email": email}
            )
            assert response.status_code == 200


class TestSignupErrors:
    """Tests for error cases in POST /activities/{activity_name}/signup."""

    def test_signup_nonexistent_activity_returns_404(self, client, fresh_activities):
        """Test that signup for nonexistent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_email_returns_400(self, client, fresh_activities):
        """Test that duplicate signup returns 400 error."""
        # Try to sign up with email already in Chess Club
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_duplicate_error_includes_detail(self, client, fresh_activities):
        """Test that duplicate signup error has descriptive message."""
        response = client.post(
            "/activities/Programming%20Class/signup",
            params={"email": "emma@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_signup_same_activity_twice_fails(self, client, fresh_activities):
        """Test that same email cannot sign up twice for same activity."""
        # First signup should succeed
        response1 = client.post(
            "/activities/Debate%20Team/signup",
            params={"email": "testuser@mergington.edu"}
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            "/activities/Debate%20Team/signup",
            params={"email": "testuser@mergington.edu"}
        )
        assert response2.status_code == 400

    def test_signup_special_characters_in_activity_name(self, client, fresh_activities):
        """Test signup with special characters in activity name."""
        # Activity names with spaces should be URL encoded
        response = client.post(
            "/activities/Soccer%20Team/signup",
            params={"email": "player@mergington.edu"}
        )
        assert response.status_code == 200

    def test_signup_email_with_special_characters(self, client, fresh_activities):
        """Test signup with special characters in email."""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "user+tag@mergington.edu"}
        )
        assert response.status_code == 200


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint."""

    def test_remove_participant_returns_200(self, client, fresh_activities):
        """Test that removing participant returns HTTP 200."""
        response = client.delete(
            "/activities/Chess%20Club/participants",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200

    def test_remove_participant_returns_success_message(self, client, fresh_activities):
        """Test that removal response includes success message."""
        response = client.delete(
            "/activities/Chess%20Club/participants",
            params={"email": "michael@mergington.edu"}
        )
        data = response.json()
        assert "message" in data
        assert "Removed" in data["message"]
        assert "michael@mergington.edu" in data["message"]

    def test_remove_participant_actually_removes(self, client, fresh_activities):
        """Test that participant is actually removed from activity."""
        # Get initial state
        response_before = client.get("/activities")
        data_before = response_before.json()
        initial_count = len(data_before["Chess Club"]["participants"])
        
        # Remove participant
        client.delete(
            "/activities/Chess%20Club/participants",
            params={"email": "michael@mergington.edu"}
        )
        
        # Check new state
        response_after = client.get("/activities")
        data_after = response_after.json()
        new_count = len(data_after["Chess Club"]["participants"])
        
        assert new_count == initial_count - 1
        assert "michael@mergington.edu" not in data_after["Chess Club"]["participants"]

    def test_remove_participant_nonexistent_activity_returns_404(self, client, fresh_activities):
        """Test that removing from nonexistent activity returns 404."""
        response = client.delete(
            "/activities/Nonexistent%20Activity/participants",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404

    def test_remove_nonexistent_participant_returns_404(self, client, fresh_activities):
        """Test that removing nonexistent participant returns 404."""
        response = client.delete(
            "/activities/Chess%20Club/participants",
            params={"email": "nonexistent@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_remove_participant_with_special_characters(self, client, fresh_activities):
        """Test removing participant with special characters in email."""
        # First add a participant with special characters
        client.post(
            "/activities/Art%20Club/signup",
            params={"email": "user+special@mergington.edu"}
        )
        
        # Then remove them
        response = client.delete(
            "/activities/Art%20Club/participants",
            params={"email": "user+special@mergington.edu"}
        )
        assert response.status_code == 200

    def test_remove_participant_different_activities_independent(self, client, fresh_activities):
        """Test that removing from one activity doesn't affect others."""
        email = "shared@mergington.edu"
        
        # Sign up for two activities
        client.post("/activities/Chess%20Club/signup", params={"email": email})
        client.post("/activities/Programming%20Class/signup", params={"email": email})
        
        # Remove from Chess Club
        response = client.delete(
            "/activities/Chess%20Club/participants",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify still in Programming Class
        response_activities = client.get("/activities")
        data = response_activities.json()
        assert email in data["Programming Class"]["participants"]
        assert email not in data["Chess Club"]["participants"]


class TestIntegrationScenarios:
    """End-to-end integration test scenarios."""

    def test_signup_then_view_participant_in_list(self, client, fresh_activities):
        """Test full flow: sign up, then view participant in activity list."""
        new_email = "integration@test.edu"
        
        # Sign up
        signup_response = client.post(
            "/activities/Basketball%20Club/signup",
            params={"email": new_email}
        )
        assert signup_response.status_code == 200
        
        # View activities
        activities_response = client.get("/activities")
        data = activities_response.json()
        
        # Verify new participant is in list
        assert new_email in data["Basketball Club"]["participants"]

    def test_signup_remove_signup_flow(self, client, fresh_activities):
        """Test flow: sign up, remove, then sign up again."""
        email = "flow@test.edu"
        activity = "Robotics%20Club"
        
        # First signup
        response1 = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert response1.status_code == 200
        
        # Remove
        response2 = client.delete(f"/activities/{activity}/participants", params={"email": email})
        assert response2.status_code == 200
        
        # Sign up again (should succeed now)
        response3 = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert response3.status_code == 200

    def test_multiple_signups_different_activities(self, client, fresh_activities):
        """Test signing up for multiple different activities."""
        email = "multi@test.edu"
        activities = ["Drama%20Club", "Art%20Club", "Debate%20Team"]
        
        for activity in activities:
            response = client.post(f"/activities/{activity}/signup", params={"email": email})
            assert response.status_code == 200
        
        # Verify in all activities
        response_data = client.get("/activities")
        data = response_data.json()
        
        for activity_name in ["Drama Club", "Art Club", "Debate Team"]:
            assert email in data[activity_name]["participants"]
