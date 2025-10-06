<!--
Sync Impact Report:
- Version change: None -> 1.0.0
- Added sections: Preamble, Principles, Governance
- Removed sections: None
- Templates requiring updates:
  - ✅ .specify/templates/plan-template.md
  - ✅ .specify/templates/spec-template.md
  - ✅ .specify/templates/tasks-template.md
  - ✅ .specify/templates/commands/constitution.md
- Follow-up TODOs: None
-->

# Constitution of the Siriform Agent Chatbot

**Version**: 1.0.0
**Ratification Date**: 2025-10-06
**Last Amended Date**: 2025-10-06

## Preamble

These are the governing principles for the "Siriform Agent Chatbot" project. All development, design, and testing activities must adhere to these standards to ensure the creation of a world-class, intelligent assistant.

## Principles

### Principle 1: Persona-Driven, Flawless User Experience

The core of this project is an interaction with "Siri," a helpful and highly competent female IT staff member. Every decision must prioritize a seamless, intuitive, and consistent user experience that is always aligned with this persona.

*   **Mandates:**
    *   **Persona Consistency:** All AI-generated language must reflect the helpful, polite, and efficient persona of a female Thai IT professional.
    *   **Interaction Cohesion:** The agent's conversational actions and the system's state changes must be seamlessly integrated.
    *   **Clarity and Feedback:** The user must always have clear, immediate, and intuitive feedback on the agent's actions.

### Principle 2: Radical Engineering Excellence and Code Quality

We write software that is not merely functional, but is demonstrably clean, efficient, and supremely maintainable. Our code is a professional asset; its quality is a direct reflection of our engineering discipline.

*   **Mandates:**
    *   **Meaningful Names:** All identifiers must clearly describe their purpose.
    *   **DRY (Don't Repeat Yourself):** Logic must never be duplicated.
    *   **KISS (Keep It Simple, Stupid):** The simplest solution is the preferred solution.
    *   **Single Responsibility Principle (SRP):** Every component must have one primary responsibility.
    *   **YAGNI (You Ain't Gonna Need It):** We will not implement features on the assumption they "might be needed in the future."
    *   **Zero Hard-Coding and High Configurability:** There is a zero-tolerance policy for hard-coded values.
    *   **Purposeful Commenting:** Comments will explain the "why," not the "what."
    *   **Consistent Formatting:** The entire codebase will be automatically formatted.

### Principle 3: Performance as a Core Feature

Application speed is a critical feature. The system must feel responsive and fluid at all times.

*   **Mandates:**
    *   **UI Responsiveness:** The frontend must be optimized for fast loads and interactions.
    *   **Low-Latency Agent:** The AI agent must respond with minimal latency.
    *   **Efficient State Management:** Application state will be managed efficiently.

### Principle 4: Measurable and Verifiable Quality

Quality is not assumed; it is verified through rigorous, repeatable, and efficient testing. The agent's behavior must be observable and its performance measurable.

*   **Mandates:**
    *   **Verifiable Agent Behavior:** The agent's logic must be testable through a standardized evaluation framework.
    *   **Full Observability:** The internal workings of the agent must be fully traceable.
    *   **Data-Driven Improvement:** Agent quality will be measured against defined success metrics to guide improvement.

### Principle 5: Clear Contracts and Boundaries

In our Monorepo architecture, the Frontend and Backend are distinct applications. They communicate exclusively through well-defined API contracts, ensuring each can evolve independently.

*   **Mandates:**
    *   **API-First Design:** All communication between Frontend and Backend MUST occur through a formally defined API.
    *   **Backend as the Source of Truth:** The Backend (Python) is the single source of truth for all business logic and data models.
    *   **Clear Separation of Responsibilities:** The Backend handles all business logic; the Frontend's primary responsibility is presentation.

## Governance

### Development Workflow
All development must follow the explicit, sequential workflow of the `spec-kit` methodology (`/constitution` -> `/specify` -> `/clarify` -> `/plan` -> `/tasks` -> `/analyze` -> `/implement`).

*   **Strict Sequential Execution:** The AI Agent MUST complete one command and wait for the next explicit command from the user before proceeding. It is strictly forbidden to proactively execute the next command in the sequence (e.g., automatically running `/plan` after `/specify` is complete). Each step requires human review and a direct instruction to continue.

### Versioning
This constitution follows semantic versioning (vX.Y.Z):
*   **MAJOR**: Backward-incompatible changes (e.g., removing a principle).
*   **MINOR**: Backward-compatible additions (e.g., adding a new principle).
*   **PATCH**: Clarifications, typo fixes, and non-semantic updates.

### Compliance
All project artifacts, including code, specifications, and plans, must be reviewed for compliance with this constitution before being finalized.
