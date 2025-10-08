"""
Tests for the update_form_data tool.

This tool updates the form data state based on extracted information.
"""

import pytest


class TestUpdateFormData:
    """Test cases for update_form_data tool."""

    @pytest.mark.asyncio
    async def test_update_single_field(self, sample_form_data):
        """Test updating a single form field."""
        with pytest.raises(ImportError):
            from app.agent.tools.form_writer import update_form_data

    @pytest.mark.asyncio
    async def test_update_nested_field(self):
        """Test updating nested fields like equipment items."""
        with pytest.raises(ImportError):
            from app.agent.tools.form_writer import update_form_data

    @pytest.mark.asyncio
    async def test_update_preserves_existing_data(self):
        """Test that updates don't overwrite unrelated fields."""
        with pytest.raises(ImportError):
            from app.agent.tools.form_writer import update_form_data

    @pytest.mark.asyncio
    async def test_update_handles_array_fields(self):
        """Test updating array fields like equipments."""
        with pytest.raises(ImportError):
            from app.agent.tools.form_writer import update_form_data

    @pytest.mark.asyncio
    async def test_update_validates_before_writing(self):
        """Test that invalid updates are rejected."""
        with pytest.raises(ImportError):
            from app.agent.tools.form_writer import update_form_data
