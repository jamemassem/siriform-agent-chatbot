# Quickstart Guide: SiriForm Agent Chatbot

This guide provides manual steps to validate the core user scenarios.

## Scenario 1: Conversational Form Filling

1.  **Action**: Open the application.
2.  **Action**: In the chat input on the left, type: `I need 2 laptops tomorrow morning in room A304.`
3.  **Verify**: The form on the right updates:
    -   `quantity` field shows `2`.
    -   `start_date` field shows tomorrow's date.
    -   `location` field shows `A304`.
4.  **Verify**: The agent responds with a question asking for the next required piece of information (e.g., "What is the purpose of this request?").

## Scenario 2: Intelligent Clarification

1.  **Action**: Start a new session.
2.  **Action**: In the chat input, type: `I need the equipment at 'ตึกศรี'.`
3.  **Verify**: The agent responds with the clarifying question: "ได้ค่ะ สำหรับสถานที่ 'ตึกศรี' ไม่ทราบว่าหมายถึง 'ตึกศรีสังวาลย์' หรือ 'อาคาร 100 ปี สมเด็จพระศรีนครินทร์' คะ?".
4.  **Action**: Respond with one of the options.
5.  **Verify**: The `location` field in the form is correctly populated with the full name of the chosen location.

## Scenario 3: Proactive Assistant (Memory)

*Prerequisite: At least one previous form submission exists for the current user/session where the quantity was "2 laptops".*

1.  **Action**: Start a new session.
2.  **Action**: In the chat input, type: `I'd like to borrow a laptop.`
3.  **Verify**: The agent responds with the proactive question: "สวัสดีค่ะ ปกติจะยืมโน้ตบุ๊ก 2 เครื่องใช่ไหมคะ รับเป็น 2 เครื่องเหมือนเดิมเลยไหมคะ?".
4.  **Action**: Respond "Yes".
5.  **Verify**: The `quantity` field in the form is set to `2`.
