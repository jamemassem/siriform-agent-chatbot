# Data Models for SiriForm Agent Chatbot

## 1. Supabase `form_submissions` Table

This table will store the final, submitted form data.

```sql
CREATE TABLE form_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    form_schema_id VARCHAR(255) NOT NULL,
    submission_data JSONB NOT NULL,
    submitted_at TIMESTAMPTZ DEFAULT now(),
    submitted_by_user_id VARCHAR(255) -- To be linked to a user system in the future
);

-- Example for the MVP
-- form_schema_id would be 'equipment_form_v1'
```

**Rationale**:
*   **`id`**: A unique identifier for each submission.
*   **`form_schema_id`**: A string to identify which form and version this submission corresponds to. This is crucial for the "generalize" capability.
*   **`submission_data`**: A `JSONB` column to store the form data. This is flexible and allows for storing data from any form schema without altering the database structure.
*   **`submitted_at`**: A timestamp to record when the form was submitted.
*   **`submitted_by_user_id`**: A placeholder for future user authentication integration.

## 2. `AgentResponse` JSON Structure

This is the data contract between the backend `SiriAgent` and the frontend. It defines the structure of the JSON object returned by the agent after each conversational turn.

```json
{
  "response_type": {
    "type": "string",
    "enum": ["clarification", "update", "error"],
    "description": "Indicates the primary action taken by the agent."
  },
  "message": {
    "type": "string",
    "description": "The natural language response from Siri to be displayed in the chat."
  },
  "form_data": {
    "type": "object",
    "description": "The complete, current state of the form data as understood by the agent."
  },
  "confidence_scores": {
    "type": "object",
    "description": "A dictionary of confidence scores for the data extracted in the last turn."
  },
  "missing_fields": {
    "type": "array",
    "items": {
      "type": "string"
    },
    "description": "A list of required fields that are still empty."
  },
  "error_details": {
    "type": "string",
    "description": "Details about an error if the response_type is 'error'."
  }
}
```
