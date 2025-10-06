# Feature Specification: SiriForm Agent Chatbot (Core MVP)

**Feature Branch**: `001-featurename-siriform-agent`
**Created**: 2025-10-06
**Status**: Draft

## User Scenarios & Testing

### Primary User Story
As a general staff member, I want to request computer equipment by having a natural conversation with an intelligent assistant named "Siri," so that I can complete the process quickly and accurately without having to manually fill out a complex form.

### Acceptance Scenarios
1.  **Given** the user opens the application, **When** they type "I need 2 laptops tomorrow morning in room A304," **Then** Siri extracts "2" for quantity, "tomorrow morning" for the start date/time, and "A304" for the location, fills these fields in the form on the right, and asks for the next required piece of information.
2.  **Given** the form requires a location from a predefined list, **When** the user types "I need the equipment at 'ตึกศรี'," **Then** Siri asks for clarification with options: "ได้ค่ะ สำหรับสถานที่ 'ตึกศรี' ไม่ทราบว่าหมายถึง 'ตึกศรีสังวาลย์' หรือ 'อาคาร 100 ปี สมเด็จพระศรีนครินทร์' คะ?".
3.  **Given** a user has previously borrowed "2 laptops," **When** they start a new request by typing "I'd like to borrow a laptop," **Then** Siri proactively asks, "สวัสดีค่ะ ปกติจะยืมโน้ตบุ๊ก 2 เครื่องใช่ไหมคะ รับเป็น 2 เครื่องเหมือนเดิมเลยไหมคะ?".
4.  **Given** the AI assistant is unavailable, **When** the user opens the application, **Then** a message is displayed indicating the assistant is offline, and the user can still fill out and submit the form manually.

### Edge Cases
-   **What happens when the user provides conflicting information?**
    > The agent will prioritize the most recent information provided in the sentence (e.g., in "I need 1, no, 2 laptops," it will use "2"). It may then ask for confirmation: "Just to confirm, you need 2 laptops, is that correct?".
-   **How does the system handle requests for equipment not on the list?**
    > Siri will inform the user that the requested item is not standard and ask for confirmation before proceeding, logging it as a custom request.
-   **What is the behavior if the user's requested date/time is in the past?**
    > Siri will detect that the date is in the past and politely ask the user for a future date: "It looks like that date has already passed. Could you please provide a future date for the request?".

## Requirements

### Functional Requirements
-   **FR-001**: The system MUST provide a two-column layout with a chat interface on the left and the form workspace on the right.
-   **FR-002**: The AI agent, "Siri," MUST be able to read a given form schema and guide the user through filling it out conversationally.
-   **FR-003**: All AI-generated language MUST align with the defined "Siri" persona (Intelligent, Empathetic, Friendly, Professional).
-   **FR-004**: The system MUST display a real-time progress bar indicating the completion percentage of the form's required fields.
-   **FR-005**: Fields populated by the AI MUST be visually highlighted until the user interacts with them.
-   **FR-006**: The agent MUST ask for clarification if user input is ambiguous or has low confidence, based on the form's schema and predefined lists.
-   **FR-007**: The agent MUST be able to query a user's submission history to offer shortcuts for recurring requests.
-   **FR-008**: The backend MUST include a test proving the agent can process a different form schema without code changes to the agent itself.
-   **FR-009**: The entire reasoning lifecycle of the agent MUST be traceable through LangSmith.
-   **FR-010**: The application MUST remain fully functional for manual form entry if the AI assistant (OpenRouter API) is unavailable.

### Key Entities
-   **User:** Represents the person interacting with the system.
-   **Form Submission:** Represents a single instance of a completed (or in-progress) equipment request form, including all field values.
-   **Form Schema:** A structured definition of a form, including fields, types, validation rules, and options.

## Constitution Alignment

- [x] **Principle 1: Persona-Driven, Flawless User Experience**: The entire specification is centered around the "Siri" persona and creating a seamless, conversational experience.
- [x] **Principle 2: Radical Engineering Excellence and Code Quality**: The requirement for a generalized agent that can handle any schema promotes a clean, non-repetitive design.
- [x] **Principle 3: Performance as a Core Feature**: The UI/UX requirements for real-time updates (progress bar, highlighting) imply a need for a responsive system.
- [x] **Principle 4: Measurable and Verifiable Quality**: The critical test case (FR-008) and the requirement for LangSmith tracing (FR-009) ensure the agent's quality is verifiable and observable.
- [x] **Principle 5: Clear Contracts and Boundaries**: The two-panel layout and the separation of the AI agent (backend) from the UI (frontend) naturally enforce this principle.

## Clarifications

### Session 2025-10-06
- Q: User confirmed that all requirements are clear and no ambiguities need to be addressed at this stage. → A: Proceed with planning.

---
*Based on Constitution v1.0.0 - See `../memory/constitution.md`*
