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
├── schemas/        # Form schemas (JSON)
├── main.py         # FastAPI application
└── models.py       # Pydantic models
```
