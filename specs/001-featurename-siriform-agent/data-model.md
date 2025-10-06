# Data Model for SiriForm Agent Chatbot

This document outlines the data models for the entities required by the feature.

## Entities

### FormSubmission
Represents a single instance of a user's interaction with a form.

-   **`id`**: `UUID` (Primary Key) - Unique identifier for the submission.
-   **`user_id`**: `UUID` (Foreign Key to `auth.users`) - The authenticated user who initiated the submission.
-   **`session_id`**: `TEXT` - An anonymous identifier for the session, used for privacy-preserving history.
-   **`form_schema_id`**: `UUID` (Foreign Key to `FormSchema`) - The specific form schema being filled out.
-   **`submitted_at`**: `TIMESTAMPZ` - The timestamp when the form was successfully submitted.
-   **`data`**: `JSONB` - The actual data collected from the user for the form fields.

### FormSchema
Represents the structure and rules of a form that the agent can process.

-   **`id`**: `UUID` (Primary Key) - Unique identifier for the form schema.
-   **`name`**: `TEXT` - A human-readable name for the form (e.g., "Computer Equipment Request Form").
-   **`version`**: `TEXT` - The version of the form schema (e.g., "1.0.0").
-   **`schema_definition`**: `JSONB` - The complete JSON schema definition of the form, including fields, types, and validation rules.
