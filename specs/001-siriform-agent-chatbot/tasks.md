# Tasks: SiriForm Agent Chatbot (Core MVP)

**Input**: Design documents from `specs/001-siriform-agent-chatbot/`
**Prerequisites**: `plan.md`, `research.md`, `data-model.md`, `contracts/openapi.json`

## Phase 1: Project Setup & Backend Foundation
| ID   | P? | Description                                                                                                                            |
|------|----|----------------------------------------------------------------------------------------------------------------------------------------|
| T001 |    | Initialize the monorepo using `pnpm workspaces` and create the `backend` and `frontend` directories.                                   |
| T002 |    | In `backend/`, initialize a new Python project with Poetry and add FastAPI, Uvicorn, and LangGraph as dependencies.                     |
| T003 |    | In `backend/app/schemas/`, manually create `equipment_form.json` by converting the structure from the original `.ts` format.            |
| T004 |    | In `backend/app/`, define Pydantic models for the API request (`AgentInvokeRequest`) and response (`AgentResponse`).                     |
| T005 |    | Set up the `form_submissions` table in Supabase Postgres as defined in `data-model.md`.                                                |
| T006 |    | Create a health check endpoint `/health` in `backend/app/main.py` to confirm the server is running.                                    |

## Phase 2: Core Agent Implementation (Backend)
| ID   | P? | Description                                                                                                                            |
|------|----|----------------------------------------------------------------------------------------------------------------------------------------|
| T007 |    | In `backend/app/services/SiriAgent.py`, create the basic structure for the `SiriAgent` class.                                          |
| T008 | [P]| Implement the `analyze_user_request` tool as a Python function.                                                                        |
| T009 | [P]| Implement the `update_form_data` tool as a Python function.                                                                            |
| T010 | [P]| Implement the `validate_field` tool as a Python function.                                                                              |
| T011 | [P]| Implement the `ask_clarifying_question` tool, ensuring it uses the "Siri" persona.                                                     |
| T012 |    | Implement the `lookup_information` tool, including the internal fuzzy matching against a list of Siriraj buildings.                    |
| T013 |    | Integrate the Longdo Map API into the `lookup_information` tool as the fallback for location validation.                               |
| T014 |    | Implement the API failure handling within the `lookup_information` tool as per the plan.                                               |
| T015 |    | Assemble the tools into a LangGraph agent within `SiriAgent.py`.                                                                       |
| T016 |    | Implement the "No Guessing" rule using conditional edges in the LangGraph agent based on confidence scores.                            |
| T017 |    | Integrate the OpenRouter API client into the agent to call the LLM.                                                                    |
| T018 |    | Configure LangSmith tracing for the agent's entire execution path.                                                                     |
| T019 |    | In `backend/app/main.py`, create the `/agent/invoke` endpoint that passes requests to the `SiriAgent`.                                  |

## Phase 3: Backend Testing
| ID   | P? | Description                                                                                                                            |
|------|----|----------------------------------------------------------------------------------------------------------------------------------------|
| T020 | [P]| Write a unit test for the `analyze_user_request` tool in `backend/tests/unit/`.                                                        |
| T021 | [P]| Write a unit test for the `lookup_information` tool, mocking the external API call.                                                    |
| T022 | [P]| Write a unit test for the `validate_field` tool.                                                                                       |
| T023 |    | Write an integration test in `backend/tests/integration/` for the full `SiriAgent` ReAct cycle with the `equipment_form.json` schema.   |
| T024 |    | Create the `RoomBooking.json` schema in `backend/app/schemas/` for the generalization test.                                            |
| T025 |    | Write the critical backend-only integration test to prove the agent's "generalize" capability using the `RoomBooking.json` schema.     |

## Phase 4: Frontend Foundation
| ID   | P? | Description                                                                                                                            |
|------|----|----------------------------------------------------------------------------------------------------------------------------------------|
| T026 |    | In `frontend/`, initialize a new React + TypeScript project using Vite.                                                                |
| T027 |    | Implement the main two-column layout (`ChatPanel` on the left, `FormPanel` on the right).                                              |
| T028 |    | Create the `DynamicFormRenderer.tsx` component that can render a form from a JSON schema.                                              |
| T029 |    | Hard-wire the `DynamicFormRenderer.tsx` to render the `equipment_form.json` for the MVP.                                               |
| T030 | [P]| Create the `ProgressBar.tsx` component with a modern gradient fill and smooth animations.                                              |
| T031 | [P]| Implement the persistent highlighting logic for fields populated by the AI.                                                            |

## Phase 5: Frontend-Backend Integration
| ID   | P? | Description                                                                                                                            |
|------|----|----------------------------------------------------------------------------------------------------------------------------------------|
| T032 |    | In `frontend/src/services/`, create an API service to communicate with the backend's `/agent/invoke` endpoint.                          |
| T033 |    | Connect the chat input component to the API service to send user messages to the backend.                                              |
| T034 |    | Update the `DynamicFormRenderer.tsx` to reflect the `form_data` received in the `AgentResponse` from the backend.                      |
| T035 |    | Implement the UI logic to display clarifying questions from Siri and send the user's answer back to the agent.                         |
| T036 |    | Implement UI logic to display error messages from the agent in a user-friendly way.                                                    |
| T037 |    | Connect the `ProgressBar.tsx` component to the `missing_fields` array from the `AgentResponse`.                                        |

## Phase 6: Polish & Finalization
| ID   | P? | Description                                                                                                                            |
|------|----|----------------------------------------------------------------------------------------------------------------------------------------|
| T038 |    | Conduct end-to-end testing of the full conversational form-filling flow.                                                                 |
| T039 | [P]| Review and refine all of Siri's conversational prompts in `ask_clarifying_question` to ensure they match the persona.                  |
| T040 | [P]| Update `quickstart.md` and the main `README.md` with final setup and usage instructions.                                               |
| T041 |    | Perform a final code review and refactoring pass on both the frontend and backend.                                                     |

## Dependencies
- **Phase 1** must be completed before **Phase 2**.
- **Phase 2** must be completed before **Phase 3** and **Phase 5**.
- **Phase 4** can run in parallel with **Phase 2 & 3**.
- **Phase 5** requires both **Phase 2** and **Phase 4** to be complete.
- **Phase 6** is the final phase.

## Parallel Execution Example
```
# The following tasks can be started after Phase 1 is complete:
Task: "T008 [P] Implement the `analyze_user_request` tool as a Python function."
Task: "T026 In `frontend/`, initialize a new React + TypeScript project using Vite."
Task: "T027 Implement the main two-column layout (`ChatPanel` on the left, `FormPanel` on the right)."
```
