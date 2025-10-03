
# Implementation Plan: SiriForm Agent Chatbot (Core MVP)

**Branch**: `001-siriform-agent-chatbot` | **Date**: 2025-10-03 | **Spec**: [specs/001-siriform-agent-chatbot/spec.md](specs/001-siriform-agent-chatbot/spec.md)
**Input**: Feature specification from `specs/001-siriform-agent-chatbot/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code, or `AGENTS.md` for all other agents).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
This plan outlines the implementation of the SiriForm Agent Chatbot MVP. The core of the project is a Python-based AI agent using LangGraph, which provides a conversational interface for filling out forms. The frontend will be a React application with a two-column layout, and the backend will be a FastAPI server. The agent's "generalized" skill will be tested to ensure it can handle different form schemas without code changes.

## Technical Context
**Language/Version**: Python 3.11, TypeScript (React)
**Primary Dependencies**: FastAPI, LangGraph, React, Vite, pnpm
**Storage**: Supabase (Postgres) for form submissions only.
**Testing**: Pytest for backend, Vitest/React Testing Library for frontend.
**Target Platform**: Web
**Project Type**: Web application (Monorepo: `/frontend`, `/backend`)
**Performance Goals**: Agent response latency < 3 seconds.
**Constraints**: Must use OpenRouter API for LLM access and LangSmith for observability.
**Scale/Scope**: MVP focused on a single, complex form (Computer Equipment Request).

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle 1 (Persona-Driven UX):** PASS. The agent's tool design (`ask_clarifying_question`) and "No Guessing" rule directly support the Siri persona.
- **Principle 2 (Engineering Excellence):** PASS. The monorepo structure with a clear separation between frontend and backend, along with the use of a JSON schema for the form, adheres to SRP and DRY.
- **Principle 3 (Performance):** PASS. The architecture is designed for low latency, with the agent's core logic in a compiled Python backend.
- **Principle 4 (Verifiable Quality):** PASS. The plan includes a critical backend test to verify the agent's generalized capability and mandates LangSmith for observability.
- **Principle 5 (Clear Contracts):** PASS. The frontend and backend communicate via a well-defined API, and the backend is the source of truth for agent logic.

## Project Structure

### Documentation (this feature)
```
specs/001-siriform-agent-chatbot/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
backend/
├── app/
│   ├── schemas/
│   │   └── equipment_form.json
│   ├── services/
│   │   └── SiriAgent.py
│   └── main.py
└── tests/

frontend/
├── src/
│   ├── components/
│   │   └── DynamicFormRenderer.tsx
│   ├── pages/
│   └── services/
└── tests/
```

**Structure Decision**: A monorepo with `pnpm workspaces` will be used to manage the `frontend` and `backend` projects, ensuring clear separation of concerns as per the constitution.

## Phase 0: Outline & Research
1. **Identify external mapping API**: Research and select a free, reliable Thai mapping API (e.g., Longdo Map, OpenStreetMap/Nominatim) for the `lookup_information` tool.
2. **Finalize `AgentResponse` structure**: Define the JSON structure the agent will use to communicate its state and results to the frontend.
3. **LangGraph Best Practices**: Research best practices for state management and tool invocation within LangGraph to ensure an efficient ReAct cycle.

**Output**: `research.md` with decisions on the mapping API and agent response format.

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1.  **Data Model (`data-model.md`):**
    *   Define the schema for the `form_submissions` table in Supabase.
    *   Formalize the `AgentResponse` JSON structure.
2.  **API Contracts (`/contracts/`):**
    *   Define the OpenAPI specification for the backend, including the endpoint for interacting with the `SiriAgent`.
3.  **Quickstart Guide (`quickstart.md`):**
    *   Write a step-by-step guide for setting up the development environment (both frontend and backend).
    *   Include a simple cURL command to test the agent's health check endpoint.
4.  **Agent File (`.github/copilot-instructions.md`):**
    *   Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType copilot` to update the agent context with the new technologies.

**Output**: `data-model.md`, `/contracts/openapi.json`, `quickstart.md`, and an updated `.github/copilot-instructions.md`.

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- **Backend First**: Prioritize building the core agent and its tools.
- **TDD for Agent**: Write failing tests for each agent tool before implementation.
- **Frontend after Backend**: Start frontend development once the backend API contract is stable.
- **Integration Last**: Connect the frontend and backend and perform end-to-end testing.

**Ordering Strategy**:
1.  **Phase 1 (Backend & Core Agent):** Monorepo setup, FastAPI app, `equipment_form.json` creation, `SiriAgent` implementation with all tools, LangSmith integration.
2.  **Phase 2 (Frontend UI):** React app setup, `DynamicFormRenderer` implementation.
3.  **Phase 3 (Integration & Evaluation):** Connect frontend to backend, end-to-end testing, and write the critical backend test for the agent's "generalize" capability.

**Estimated Output**: 30-40 ordered tasks in `tasks.md`.

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*No constitutional violations identified that require justification.*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A       | N/A        | N/A                                 |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*