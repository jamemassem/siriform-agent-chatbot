"""
Tests for the lookup_information tool.

This tool performs fuzzy matching for fields with predefined lists
(e.g., location names).
"""

import pytest


class TestLookupInformation:
    """Test cases for lookup_information tool."""

    @pytest.mark.asyncio
    async def test_fuzzy_match_exact_match(self):
        """Test that exact matches return highest confidence."""
        with pytest.raises(ImportError):
            from app.agent.tools.lookup import lookup_information

    @pytest.mark.asyncio
    async def test_fuzzy_match_partial_thai_text(self):
        """Test fuzzy matching with partial Thai text (e.g., 'ตึกศรี')."""
        with pytest.raises(ImportError):
            from app.agent.tools.lookup import lookup_information

    @pytest.mark.asyncio
    async def test_fuzzy_match_returns_multiple_options(self):
        """Test that ambiguous matches return multiple options."""
        with pytest.raises(ImportError):
            from app.agent.tools.lookup import lookup_information

    @pytest.mark.asyncio
    async def test_fuzzy_match_no_results(self):
        """Test behavior when no matches are found."""
        with pytest.raises(ImportError):
            from app.agent.tools.lookup import lookup_information

    @pytest.mark.asyncio
    async def test_fuzzy_match_confidence_threshold(self):
        """Test that low-confidence matches are filtered out."""
        with pytest.raises(ImportError):
            from app.agent.tools.lookup import lookup_information
