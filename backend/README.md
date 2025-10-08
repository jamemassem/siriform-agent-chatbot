# SiriForm Backend

Backend API for the SiriForm Agent Chatbot.

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

3. Run the development server:
```bash
poetry run uvicorn app.main:app --reload
```

## Running Tests

```bash
poetry run pytest
```

## Project Structure

```
app/
├── agent/          # AI agent logic and tools
│   └── tools/      # Agent tools (6 implemented)
│       ├── history.py          # lookup_user_history - retrieves past submissions
│       ├── analyzer.py         # analyze_user_request - extracts structured data
│       ├── lookup.py           # lookup_information - fuzzy matching for fields
│       ├── form_writer.py      # update_form_data - updates form state
│       ├── validator.py        # validate_field - validates against JSON Schema
│       └── question_asker.py   # ask_clarifying_question - generates questions
├── schemas/        # Form schemas (JSON)
│   └── equipment_form.json
├── main.py         # FastAPI application (TODO)
└── models.py       # Pydantic models
tests/
├── conftest.py     # Test fixtures
├── test_lookup_user_history.py
├── test_analyze_user_request.py
├── test_lookup_information.py
├── test_update_form_data.py
├── test_validate_field.py
└── test_ask_clarifying_question.py
```

## Agent Tools

The backend implements 6 specialized tools for the ReAct agent:

1. **lookup_user_history** - Retrieves user's previous form submissions from Supabase
2. **analyze_user_request** - Extracts structured data from natural language (Thai/English)
3. **lookup_information** - Performs fuzzy matching for field values
4. **update_form_data** - Updates form data with validation
5. **validate_field** - Validates fields against JSON Schema
6. **ask_clarifying_question** - Generates contextual clarifying questions

## Testing

All tools have comprehensive unit tests following TDD principles. To run tests:

```bash
poetry run pytest -v                    # Run all tests
poetry run pytest tests/test_*.py -v    # Run specific test
poetry run pytest --cov=app tests/      # With coverage
```

## Prerequisites

- Python 3.11+
- Poetry (Python package manager)
- Supabase account (for user history storage)
- OpenRouter API key (for LLM access)
