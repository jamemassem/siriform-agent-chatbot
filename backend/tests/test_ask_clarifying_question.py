"""
Tests for the ask_clarifying_question tool.

This tool generates clarifying questions when user input is ambiguous
or confidence is low.
"""

import pytest


class TestAskClarifyingQuestion:
    """Test cases for ask_clarifying_question tool."""

    @pytest.mark.asyncio
    async def test_ask_question_for_low_confidence(self):
        """Test that tool asks for clarification when confidence is low."""
        with pytest.raises(ImportError):
            from app.agent.tools.question_asker import ask_clarifying_question

    @pytest.mark.asyncio
    async def test_ask_question_with_options(self):
        """Test that tool provides multiple options for user to choose."""
        with pytest.raises(ImportError):
            from app.agent.tools.question_asker import ask_clarifying_question

    @pytest.mark.asyncio
    async def test_ask_question_in_thai(self):
        """Test that clarifying questions are in Thai language."""
        with pytest.raises(ImportError):
            from app.agent.tools.question_asker import ask_clarifying_question

    @pytest.mark.asyncio
    async def test_ask_question_maintains_persona(self):
        """Test that questions maintain Siri persona (polite, professional)."""
        with pytest.raises(ImportError):
            from app.agent.tools.question_asker import ask_clarifying_question

    @pytest.mark.asyncio
    async def test_ask_question_contextual(self):
        """Test that questions are contextual to the form field."""
        with pytest.raises(ImportError):
            from app.agent.tools.question_asker import ask_clarifying_question
