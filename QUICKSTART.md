# Quick Start Guide

## Installation

### 1. Install System Prerequisites

#### Python 3.11+
Download from [python.org](https://www.python.org/downloads/) or use:
```powershell
# Windows (using winget)
winget install Python.Python.3.11
```

#### Poetry (Python Package Manager)
```powershell
# Windows PowerShell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

#### Node.js 18+ and pnpm
```powershell
# Install Node.js
winget install OpenJS.NodeJS.LTS

# Install pnpm
npm install -g pnpm
```

### 2. Backend Setup

```powershell
# Navigate to backend
cd backend

# Install dependencies
poetry install

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
notepad .env
```

### 3. Frontend Setup

```powershell
# Navigate to frontend
cd ../frontend

# Install dependencies
pnpm install
```

## Running the Application

### Start Backend Server
```powershell
cd backend
poetry run uvicorn app.main:app --reload
```
API will be available at: http://localhost:8000  
API docs: http://localhost:8000/docs

### Start Frontend Dev Server
```powershell
cd frontend
pnpm dev
```
Frontend will be available at: http://localhost:5173

## Running Tests

### Backend Tests
```powershell
cd backend

# Run all tests
poetry run pytest -v

# Run with coverage
poetry run pytest --cov=app tests/

# Run specific test file
poetry run pytest tests/test_lookup_user_history.py -v
```

### Test Results
Currently implemented:
- ✅ 30 unit tests for agent tools
- ✅ 8 contract tests for API endpoints
- Total: **38 test cases**

## Environment Variables

Required environment variables in `backend/.env`:

```bash
# OpenRouter API (for LLM access)
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=anthropic/claude-3-sonnet

# Supabase (for user history)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# LangSmith (optional, for observability)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_PROJECT=siriform-agent
```

## API Endpoints

### Health Check
```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

### Get Form Schema
```http
GET /api/v1/form-schema/{form_name}
```

Example:
```bash
curl http://localhost:8000/api/v1/form-schema/equipment_form
```

Response:
```json
{
  "name": "equipment_form",
  "version": "1.0.0",
  "schema": { ... }
}
```

### Chat Interaction
```http
POST /api/v1/chat
Content-Type: application/json
```

Request body:
```json
{
  "message": "I need 2 laptops for tomorrow morning",
  "session_id": "sess_12345",
  "form_data": {}
}
```

Response:
```json
{
  "response": "เข้าใจแล้วครับ คุณต้องการ Notebook จำนวน 2 เครื่อง",
  "form_data": {
    "equipments": [
      {
        "type": "Notebook",
        "quantity": 2,
        "detail": ""
      }
    ]
  },
  "highlighted_fields": ["equipments"],
  "confidence": 0.9
}
```

## Project Structure

```
siriform-agent-chatbot/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── agent/          # AI agent and tools
│   │   ├── schemas/        # Form JSON schemas
│   │   ├── main.py         # FastAPI app
│   │   └── models.py       # Pydantic models
│   ├── tests/              # Test suite
│   ├── pyproject.toml      # Poetry config
│   └── .env               # Environment variables
├── frontend/               # React + TypeScript frontend
│   ├── src/
│   │   ├── components/    # React components (TODO)
│   │   ├── services/      # API client (TODO)
│   │   └── types/         # TypeScript types (TODO)
│   └── package.json
├── pnpm-workspace.yaml     # Monorepo config
└── PROGRESS.md            # Implementation status
```

## Development Workflow

1. **Backend Development**
   - Write tests first (TDD)
   - Implement feature
   - Run tests: `poetry run pytest`
   - Format code: `poetry run black app/ tests/`
   - Check types: `poetry run mypy app/`

2. **Frontend Development** (Coming soon)
   - Component development in Storybook
   - Type-safe API calls
   - E2E testing with Playwright

## Troubleshooting

### Poetry command not found
Add Poetry to PATH:
```powershell
$Env:Path += ";$Env:APPDATA\Python\Scripts"
```

### Python not found
Verify installation:
```powershell
python --version  # Should show 3.11+
```

### Module import errors in tests
Ensure you're running tests through Poetry:
```powershell
poetry run pytest  # Correct
pytest             # May fail if virtualenv not activated
```

### CORS errors in frontend
Verify backend CORS configuration in `app/main.py`:
```python
allow_origins=[
    "http://localhost:5173",  # Vite dev server
    # Add your frontend URL here
]
```

## Next Steps

1. **Install prerequisites** (Python, Poetry, Node.js, pnpm)
2. **Run backend tests** to verify setup
3. **Configure LangSmith** for observability (T016)
4. **Implement frontend** components (T017-T020)
5. **Connect to Supabase** for user history (T021)
6. **Add authentication** with JWT (T023)

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Supabase Documentation](https://supabase.com/docs)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## Support

For issues or questions:
1. Check `PROGRESS.md` for implementation status
2. Review test files in `backend/tests/` for usage examples
3. Check API documentation at http://localhost:8000/docs
