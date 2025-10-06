
# Implementation Plan: SiriForm Agent Chatbot (Core MVP)

**Branch**: `001-featurename-siriform-agent` | **Date**: 2025-10-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `D:\Users\User\Documents\GitHub\siriform-agent-chatbot\specs\001-featurename-siriform-agent\spec.md`

## Summary
This plan outlines the technical approach for building the core MVP of the SiriForm Agent Chatbot. The primary goal is to create a conversational AI agent, "Siri," that can guide users through filling out a complex form (the Computer Equipment Request Form) using natural language. The architecture is a Python/FastAPI backend with a React frontend, following a Monorepo structure.

## Technical Context
**Language/Version**: Python 3.11, TypeScript 5.x
**Primary Dependencies**: FastAPI, LangChain/LangGraph, React, Vite, Supabase
**Storage**: Supabase (Postgres) for `form_submissions`
**Testing**: Pytest for backend, Vitest/RTL for frontend
**Target Platform**: Web Browser
**Project Type**: Web Application (Monorepo: `/frontend`, `/backend`)
**Performance Goals**: UI must be responsive; AI agent latency should be minimized.
**Constraints**: The agent must not guess; it must ask for clarification if confidence is low.
**Scale/Scope**: MVP is focused on a single form (Computer Equipment Request) and a single user type.

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Principle 1 (Persona-Driven UX):** PASS. The plan is centered on the "Siri" persona and conversational interaction.
- [x] **Principle 2 (Engineering Excellence):** PASS. The Monorepo structure, generalized agent design, and clear separation of concerns adhere to this principle.
- [x] **Principle 3 (Performance):** PASS. The tech stack is chosen for performance, and UI responsiveness is a stated goal.
- [x] **Principle 4 (Measurable Quality):** PASS. LangSmith integration and the architectural extensibility test provide clear verification paths.
- [x] **Principle 5 (Clear Boundaries):** PASS. The frontend/backend split with a defined API contract is a core part of the architecture.

## Project Structure

### Documentation (this feature)
```
specs/001-featurename-siriform-agent/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── openapi.json
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)
```
/
├── backend/
│   ├── app/
│   │   ├── schemas/
│   │   │   └── equipment_form.json
│   │   ├── agent/
│   │   │   ├── SiriAgent.py
│   │   │   └── tools/
│   │   └── main.py
│   └── tests/
│       └── test_agent_generalization.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DynamicFormRenderer.tsx
│   │   │   └── ProgressBar.tsx
│   │   └── App.tsx
│   └── tests/
└── pnpm-workspace.yaml
```

**Structure Decision**: A Monorepo managed by `pnpm workspaces` is chosen to facilitate development and ensure clear separation between the frontend and backend applications, aligning with Principle 5.

## Form Schema Management
**Form Schema Management:** The structure of the primary Computer Equipment Request Form will be created by **manually converting the original `.ts` format from `/source_files/legacy_equipment_form.ts`** into an `equipment_form.json` schema file by hand. This file will reside in a `/backend/app/schemas` directory.

## Phase 0: Outline & Research
1.  **Extract unknowns from Technical Context**: All major technical decisions have been made in the provided plan. No further research is required.
2.  **Consolidate findings** in `research.md`: Document the chosen technology stack and architecture.

**Output**: `research.md` confirming the tech stack.

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1.  **Extract entities from feature spec** → `data-model.md`:
    -   **FormSubmission**: `id`, `user_id`, `session_id`, `form_schema_id`, `submitted_at`, `data` (JSONB).
    -   **FormSchema**: `id`, `name`, `version`, `schema_definition` (JSONB).
2.  **Generate API contracts** → `/contracts/openapi.json`:
    -   `POST /api/v1/chat`: Endpoint for the frontend to send user messages to the agent.
    -   `GET /api/v1/form-schema/{form_name}`: Endpoint to retrieve the form schema for rendering.
3.  **Generate contract tests**: Create failing contract tests for the defined endpoints.
4.  **Extract test scenarios** → `quickstart.md`:
    -   Document the steps for the three primary user scenarios from the spec.

**Output**: `data-model.md`, `/contracts/openapi.json`, failing contract tests, `quickstart.md`.

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do.*

**Task Generation Strategy**:
-   Generate tasks based on the development phases outlined in the technical plan.
-   **Phase 1 (Backend)**: Tasks for setting up FastAPI, creating the `SiriAgent` and its tools, and converting the form schema.
-   **Phase 2 (Frontend)**: Tasks for setting up React/Vite and building the UI components.
-   **Phase 3 (Integration)**: Tasks for connecting the two, implementing user history, and writing the critical generalization test.

**Ordering Strategy**:
-   Backend foundation tasks will be prioritized to allow the frontend to connect to a working API early.
-   TDD will be followed where applicable (e.g., writing failing contract tests first).

**Estimated Output**: A detailed `tasks.md` file with ~20-25 ordered tasks.

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [ ] Phase 0: Research complete
- [ ] Phase 1: Design complete
- [ ] Phase 2: Task planning complete (approach described)

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [ ] Post-Design Constitution Check: PENDING
- [x] All NEEDS CLARIFICATION resolved

---
*Based on Constitution v1.0.0 - See `../memory/constitution.md`*
