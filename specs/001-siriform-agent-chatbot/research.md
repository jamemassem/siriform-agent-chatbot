# Research for SiriForm Agent Chatbot (Core MVP)

## 1. External Thai Mapping API

**Decision**: Use the **Longdo Map API**.

**Rationale**:
*   **Free Tier**: Offers a generous free tier suitable for the MVP's expected usage.
*   **Good Documentation**: The API documentation is clear and provides examples for geolocation and search.
*   **Thai Language Support**: Natively supports Thai language queries and provides accurate results for locations within Thailand.
*   **No API Key Required for Basic Search**: Some basic search functionalities can be used without an API key, which simplifies initial development and testing.

**Alternatives Considered**:
*   **OpenStreetMap (Nominatim)**: While powerful and free, the Thai language support can be less consistent than a dedicated local service. It's a viable fallback option.
*   **Google Maps API**: Powerful but requires a credit card and has a more complex pricing structure. Overkill for the MVP.

## 2. AgentResponse JSON Structure

**Decision**: The `SiriAgent` will return the following JSON structure to the frontend after each turn.

```json
{
  "response_type": "clarification" | "update" | "error",
  "message": "The natural language response from Siri.",
  "form_data": {
    "field_name_1": "value1",
    "field_name_2": "value2"
  },
  "confidence_scores": {
    "field_name_1": 0.95
  },
  "missing_fields": ["field_name_3", "field_name_4"],
  "error_details": "Details about the error if response_type is 'error'."
}
```

**Rationale**:
*   **`response_type`**: Clearly indicates the agent's primary action, allowing the frontend to react accordingly (e.g., display a clarifying question, update the form).
*   **`message`**: The user-facing text to be displayed in the chat interface.
*   **`form_data`**: The complete, current state of the form data as understood by the agent. This allows the frontend to re-render the form with the latest information.
*   **`confidence_scores`**: Provides transparency into the agent's decision-making process. Can be used for debugging or future UI enhancements.
*   **`missing_fields`**: Informs the frontend about which required fields are still empty, enabling features like the progress bar.
*   **`error_details`**: Provides specific error information for logging and debugging.

## 3. LangGraph Best Practices

**Decision**:
*   **State Management**: The primary state will be a dictionary representing the form data. Each node in the graph will receive and return this state object.
*   **Tool Invocation**: Use LangGraph's built-in tool invocation capabilities. Tools will be simple Python functions that are decorated to be available to the agent.
*   **Conditional Edges**: Use conditional edges to implement the "No Guessing" rule. After the `analyze_user_request` node, a conditional edge will check the confidence scores. If any score is below the threshold, it will route to the `ask_clarifying_question` tool. Otherwise, it will route to the `update_form_data` tool.

**Rationale**:
*   This approach leverages LangGraph's core strengths for building stateful, multi-step agents.
*   It provides a clear and maintainable way to implement the agent's logic, with a visible flow of control through the graph.
*   Conditional edges are the ideal mechanism for implementing the agent's decision-making logic based on confidence scores.
