# Quickstart: SiriForm Agent Chatbot

This guide provides the steps to get the development environment for the SiriForm Agent Chatbot up and running.

## Prerequisites

*   Node.js (v18 or later)
*   pnpm
*   Python (v3.11 or later)
*   Poetry

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/jamemassem/siriform-agent-chatbot.git
    cd siriform-agent-chatbot
    ```

2.  **Install dependencies:**
    This project uses a monorepo managed by pnpm.

    *   **Install frontend and backend dependencies:**
        ```bash
        pnpm install
        ```
    *   **Install Python dependencies for the backend:**
        ```bash
        cd backend
        poetry install
        cd ..
        ```

3.  **Configure Environment Variables:**
    Create a `.env` file in the `backend` directory and add the following:
    ```
    OPENROUTER_API_KEY=your_openrouter_api_key
    LANGCHAIN_API_KEY=your_langsmith_api_key
    LANGCHAIN_TRACING_V2=true
    LANGCHAIN_PROJECT=SiriForm-MVP
    ```

## Running the Application

1.  **Start the backend server:**
    ```bash
    cd backend
    poetry run uvicorn app.main:app --reload
    ```
    The backend will be running at `http://127.0.0.1:8000`.

2.  **Start the frontend development server:**
    In a new terminal:
    ```bash
    cd frontend
    pnpm dev
    ```
    The frontend will be available at `http://localhost:5173`.

## Testing

### Backend Health Check

You can test the backend's health check endpoint with the following cURL command:

```bash
curl http://127.0.0.1:8000/health
```

You should receive a response like:
```json
{"status":"ok"}
```

### Running Tests

*   **Backend tests:**
    ```bash
    cd backend
    poetry run pytest
    ```
*   **Frontend tests:**
    ```bash
    cd frontend
    pnpm test
    ```
