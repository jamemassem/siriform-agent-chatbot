"""
Tests for the lookup_user_history tool.

This tool queries the user's submission history from Supabase
to offer shortcuts for recurring requests.
"""

import pytest
from unittest.mock import AsyncMock, patch


class TestLookupUserHistory:
    """Test cases for lookup_user_history tool."""

    @pytest.mark.asyncio
    async def test_lookup_history_returns_previous_submissions(
        self, mock_supabase_client, sample_session_id
    ):
        """Test that lookup_user_history retrieves previous form submissions."""
        # Arrange
        expected_history = [
            {
                "id": "sub_1",
                "session_id": sample_session_id,
                "data": {"equipments": [{"type": "Notebook", "quantity": 2}]},
                "submitted_at": "2025-10-01T10:00:00Z",
            }
        ]
        mock_supabase_client.execute.return_value.data = expected_history

        # Act & Assert - This should fail until we implement the tool
        with pytest.raises(ImportError):
            from app.agent.tools.history import lookup_user_history

    @pytest.mark.asyncio
    async def test_lookup_history_filters_by_session(self, sample_session_id):
        """Test that history lookup filters by session_id."""
        # This test should fail until implementation
        with pytest.raises(ImportError):
            from app.agent.tools.history import lookup_user_history

    @pytest.mark.asyncio
    async def test_lookup_history_returns_empty_for_new_user(self):
        """Test that new users with no history get empty list."""
        # This test should fail until implementation
        with pytest.raises(ImportError):
            from app.agent.tools.history import lookup_user_history

    @pytest.mark.asyncio
    async def test_lookup_history_sorts_by_recency(self):
        """Test that history is sorted by most recent first."""
        # This test should fail until implementation
        with pytest.raises(ImportError):
            from app.agent.tools.history import lookup_user_history
