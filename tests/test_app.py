"""
FastAPI backend tests using AAA (Arrange-Act-Assert) pattern
Tests for the Mergington High School Activities API
"""
from urllib.parse import quote


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_success(self, client, fresh_activities):
        """
        Arrange: No setup needed, just have fresh activities
        Act: Call GET /activities
        Assert: Returns 200 with all activities
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_includes_participants(self, client, fresh_activities):
        """
        Arrange: Know which activities have existing participants
        Act: Call GET /activities
        Assert: Response includes participants list for each activity
        """
        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert "participants" in data["Chess Club"]
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]

    def test_get_activities_correct_count(self, client, fresh_activities):
        """
        Arrange: Know total number of activities in fixture
        Act: Call GET /activities
        Assert: Response contains exactly the expected number of activities
        """
        # Arrange
        expected_count = 5

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert len(data) == expected_count

    def test_get_activities_has_required_fields(self, client, fresh_activities):
        """
        Arrange: Know the required structure for each activity
        Act: Call GET /activities
        Assert: Each activity has all required fields
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for activity_name, activity_data in data.items():
            for field in required_fields:
                assert field in activity_data, f"Missing field '{field}' in {activity_name}"


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client, fresh_activities):
        """
        Arrange: Select an activity and a new email
        Act: POST to signup endpoint with valid data
        Assert: Returns 200 and success message
        """
        # Arrange
        activity_name = "Basketball Team"
        new_email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_updates_participant_list(self, client, fresh_activities):
        """
        Arrange: Select an activity and know a new email
        Act: POST to signup endpoint
        Assert: Email is added to the activity's participants list
        """
        # Arrange
        activity_name = "Soccer Club"
        new_email = "soccer_fan@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )

        # Assert
        assert response.status_code == 200
        assert new_email in fresh_activities[activity_name]["participants"]

    def test_signup_duplicate_email(self, client, fresh_activities):
        """
        Arrange: Sign up an email first, then try again
        Act: Attempt to signup the same email twice
        Assert: Second attempt returns 400 with error message
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={existing_email}"
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_activity_not_found(self, client, fresh_activities):
        """
        Arrange: Use an activity name that doesn't exist
        Act: POST with invalid activity name
        Assert: Returns 404 with error message
        """
        # Arrange
        invalid_activity = "Nonexistent Club"
        test_email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup?email={test_email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_activity_full(self, client, fresh_activities):
        """
        Arrange: Create an activity with only 1 spot, fill it
        Act: Attempt to signup when activity is at capacity
        Assert: Returns 400 with error message about capacity
        """
        # Arrange
        # Set max_participants to 2 for Chess Club and it already has 2 participants
        fresh_activities["Chess Club"]["max_participants"] = 2
        new_email = "another_chess_fan@mergington.edu"

        # Act
        response = client.post(
            f"/activities/Chess Club/signup?email={new_email}"
        )

        # Assert
        assert response.status_code == 400
        assert "full" in response.json()["detail"]

    def test_signup_updates_availability(self, client, fresh_activities):
        """
        Arrange: Get initial spots available in an activity
        Act: Sign up a participant
        Assert: Spots available decreases by 1 after signup
        """
        # Arrange
        activity_name = "Basketball Team"
        initial_spots = (
            fresh_activities[activity_name]["max_participants"]
            - len(fresh_activities[activity_name]["participants"])
        )
        new_email = "basketball_player@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )

        # Assert
        assert response.status_code == 200
        updated_spots = (
            fresh_activities[activity_name]["max_participants"]
            - len(fresh_activities[activity_name]["participants"])
        )
        assert updated_spots == initial_spots - 1

    def test_signup_with_special_characters_in_email(self, client, fresh_activities):
        """
        Arrange: Use an email with special characters (properly URL encoded)
        Act: Signup with special character email
        Assert: Signup succeeds and email is in participants
        """
        # Arrange
        activity_name = "Soccer Club"
        special_email = "student+test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={quote(special_email, safe='')}"
        )

        # Assert
        assert response.status_code == 200
        assert special_email in fresh_activities[activity_name]["participants"]


class TestDeleteParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_delete_participant_success(self, client, fresh_activities):
        """
        Arrange: Pick an activity with an existing participant
        Act: DELETE the participant from the activity
        Assert: Returns 200 and success message
        """
        # Arrange
        activity_name = "Chess Club"
        participant_email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{participant_email}"
        )

        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]

    def test_delete_removes_from_list(self, client, fresh_activities):
        """
        Arrange: Know an activity with participants
        Act: DELETE a specific participant
        Assert: Email is removed from the activity's participants list
        """
        # Arrange
        activity_name = "Programming Class"
        participant_email = "emma@mergington.edu"
        initial_count = len(fresh_activities[activity_name]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{participant_email}"
        )

        # Assert
        assert response.status_code == 200
        assert participant_email not in fresh_activities[activity_name]["participants"]
        assert len(fresh_activities[activity_name]["participants"]) == initial_count - 1

    def test_delete_participant_not_found(self, client, fresh_activities):
        """
        Arrange: Use an activity and an email not in its participants
        Act: DELETE with non-existent participant
        Assert: Returns 404 with error message
        """
        # Arrange
        activity_name = "Gym Class"
        nonexistent_email = "ghost@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{nonexistent_email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_delete_activity_not_found(self, client, fresh_activities):
        """
        Arrange: Use an activity name that doesn't exist
        Act: DELETE with invalid activity name
        Assert: Returns 404 with error message
        """
        # Arrange
        invalid_activity = "Fake Club"
        test_email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/participants/{test_email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_delete_updates_availability(self, client, fresh_activities):
        """
        Arrange: Get initial spots available before delete
        Act: Remove a participant
        Assert: Spots available increases by 1 after removal
        """
        # Arrange
        activity_name = "Chess Club"
        participant_email = "michael@mergington.edu"
        initial_spots = (
            fresh_activities[activity_name]["max_participants"]
            - len(fresh_activities[activity_name]["participants"])
        )

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{participant_email}"
        )

        # Assert
        assert response.status_code == 200
        updated_spots = (
            fresh_activities[activity_name]["max_participants"]
            - len(fresh_activities[activity_name]["participants"])
        )
        assert updated_spots == initial_spots + 1

    def test_delete_with_special_characters(self, client, fresh_activities):
        """
        Arrange: Add an email with special characters, then delete it
        Act: DELETE with special character email
        Assert: Deletion succeeds and email is removed
        """
        # Arrange
        activity_name = "Soccer Club"
        special_email = "coach+soccer@mergington.edu"
        # First signup with properly encoded email
        client.post(f"/activities/{activity_name}/signup?email={quote(special_email, safe='')}")

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{quote(special_email, safe='')}"
        )

        # Assert
        assert response.status_code == 200
        assert special_email not in fresh_activities[activity_name]["participants"]


class TestIntegration:
    """Integration tests combining multiple operations"""

    def test_signup_then_delete_flow(self, client, fresh_activities):
        """
        Arrange: Have an empty activity
        Act: Signup, verify in list, then delete, verify removed
        Assert: Both operations succeed and state is correct
        """
        # Arrange
        activity_name = "Basketball Team"
        test_email = "player@mergington.edu"

        # Act - Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )

        # Assert signup
        assert signup_response.status_code == 200
        assert test_email in fresh_activities[activity_name]["participants"]

        # Act - Delete
        delete_response = client.delete(
            f"/activities/{activity_name}/participants/{test_email}"
        )

        # Assert delete
        assert delete_response.status_code == 200
        assert test_email not in fresh_activities[activity_name]["participants"]

    def test_multiple_signups_and_deletions(self, client, fresh_activities):
        """
        Arrange: Have an empty activity
        Act: Add multiple participants, delete some, verify list integrity
        Assert: All operations succeed with correct final state
        """
        # Arrange
        activity_name = "Soccer Club"
        emails = ["player1@mergington.edu", "player2@mergington.edu", "player3@mergington.edu"]

        # Act - Signup all
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup?email={email}"
            )
            assert response.status_code == 200

        # Assert all signed up
        assert len(fresh_activities[activity_name]["participants"]) == 3

        # Act - Delete middle one
        delete_response = client.delete(
            f"/activities/{activity_name}/participants/{emails[1]}"
        )

        # Assert middle one deleted
        assert delete_response.status_code == 200
        assert emails[1] not in fresh_activities[activity_name]["participants"]
        assert emails[0] in fresh_activities[activity_name]["participants"]
        assert emails[2] in fresh_activities[activity_name]["participants"]
        assert len(fresh_activities[activity_name]["participants"]) == 2
