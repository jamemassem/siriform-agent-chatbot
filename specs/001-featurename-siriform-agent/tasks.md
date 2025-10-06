# Tasks: SiriForm Agent Chatbot (Core MVP)

**Input**: Design documents from `D:\Users\User\Documents\GitHub\siriform-agent-chatbot\specs\001-featurename-siriform-agent\`

| ID   | P? | Phase     | Task Description                                                                                             |
|------|----|-----------|--------------------------------------------------------------------------------------------------------------|
| T001 |    | Setup     | Initialize the Monorepo structure with `pnpm-workspace.yaml` and create `/frontend` and `/backend` directories. |
| T002 |    | Setup     | In the `/backend` directory, initialize a Python project with `poetry` and add FastAPI, LangChain, and LangGraph. |
| T003 |    | Setup     | In the `/frontend` directory, initialize a React + TypeScript project using Vite.                             |
| T004 |    | Backend   | Create the `equipment_form.json` schema file in `/backend/app/schemas/` by manually converting the format from `/source_files/legacy_equipment_form.ts`. |
| T005 | [P] | Backend   | Define Pydantic models in `/backend/app/models.py` for API request and response bodies.                      |
| T006 | [P] | Testing   | Write failing unit tests for the agent's tools.                                                              |
| T007 | [P] | Backend   | Implement the `lookup_user_history` tool in `/backend/app/agent/tools/history.py`.                           |
| T008 | [P] | Backend   | Implement the `analyze_user_request` tool in `/backend/app/agent/tools/analyzer.py`.                         |
| T009 | [P] | Backend   | Implement the `lookup_information` tool for fuzzy matching in `/backend/app/agent/tools/lookup.py`.            |
| T010 | [P] | Backend   | Implement the `update_form_data` tool in `/backend/app/agent/tools/form_writer.py`.                          |
| T011 | [P] | Backend   | Implement the `validate_field` tool in `/backend/app/agent/tools/validator.py`.                              |
| T012 | [P] | Backend   | Implement the `ask_clarifying_question` tool in `/backend/app/agent/tools/question_asker.py`.                |
| T013 |    | Testing   | Write failing contract tests for the API endpoints.                                                          |
| T014 |    | Backend   | Create the FastAPI endpoints (`/api/v1/chat`, `/api/v1/form-schema/{form_name}`) in `/backend/app/main.py`.     |
| T015 |    | Backend   | Implement the core `SiriAgent` logic in `/backend/app/agent/SiriAgent.py` using LangGraph to orchestrate the tools. |
| T016 |    | Backend   | Configure LangSmith observability for the agent.                                                              |
| T017 | [P] | Frontend  | Implement the `DynamicFormRenderer.tsx` component to render a form from a JSON schema.                        |
| T018 | [P] | Frontend  | Implement the `ProgressBar.tsx` component with gradient fill and smooth animations.                           |
| T019 | [P] | Frontend  | Implement the main two-column chat interface in `App.tsx`.                                                    |
| T020 |    | Integration| Connect the frontend to the backend `/api/v1/chat` endpoint.                                                  |
| T021 |    | Integration| Connect to Supabase Postgres and implement the `form_submissions` table access for user history.              |
| T022 |    | Testing   | Write a backend integration test in `/backend/tests/test_agent_generalization.py` to verify the agent's ability to process a different schema (`RoomBooking.json`). |
| T023 |    | Polish    | Implement JWT verification using Supabase Auth for securing the backend API.                                  |

## Dependencies
- **T001-T003** must be completed before all other tasks.
- **T004** must be completed before agent tool implementation (T007-T012).
- **T006** (Unit Tests) must be completed before **T007-T012**.
- **T007-T012** can be done in parallel but must be completed before **T015**.
- **T013** (Contract Tests) must be completed before **T014**.
- **T015** depends on **T007-T012**.
- **T017-T019** can be done in parallel.
- **T014** and **T017-T019** must be completed before **T020**.
- **T021** depends on **T007**.
- **T022** depends on **T015**.

## Parallel Execution Example
The following tasks can be executed in parallel after the initial setup:
- `Task: "T005 [P] Define Pydantic models..."`
- `Task: "T006 [P] Write failing unit tests..."`
- `Task: "T007 [P] Implement the lookup_user_history tool..."`
- `Task: "T008 [P] Implement the analyze_user_request tool..."`
- `Task: "T009 [P] Implement the lookup_information tool..."`
- `Task: "T010 [P] Implement the update_form_data tool..."`
- `Task: "T011 [P] Implement the validate_field tool..."`
- `Task: "T012 [P] Implement the ask_clarifying_question tool..."`
- `Task: "T017 [P] Implement the DynamicFormRenderer.tsx component..."`
- `Task: "T018 [P] Implement the ProgressBar.tsx component..."`
- `Task: "T019 [P] Implement the main two-column chat interface..."`
