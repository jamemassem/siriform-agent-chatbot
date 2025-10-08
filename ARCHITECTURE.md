# SiriAgent Architecture

## System Overview

```
┌─────────────────┐
│   User (Thai)   │
│  "ขอ laptop 2"  │
│      "เครื่อง"   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│            Frontend (React)                     │
│  ┌─────────────────┐  ┌────────────────────┐  │
│  │  Chat Interface │  │  DynamicFormRenderer│  │
│  │                 │  │  (Progress: 45%)   │  │
│  │  Message List   │  │  ✓ Name            │  │
│  │  Input Field    │  │  ✓ Equipment       │  │
│  │  Send Button    │  │  ⚠ Date (pending)  │  │
│  └─────────────────┘  └────────────────────┘  │
└────────────┬────────────────────────────────────┘
             │ HTTP POST /api/v1/chat
             ▼
┌───────────────────────────────────────────────────┐
│         Backend (FastAPI)                         │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │          SiriAgent (LangGraph)              │ │
│  │                                             │ │
│  │  ┌──────────┐      ┌──────────────────┐   │ │
│  │  │ Analyze  │─────▶│ Lookup History   │   │ │
│  │  │ Request  │      │ (Supabase)       │   │ │
│  │  └──────────┘      └──────────────────┘   │ │
│  │       │                     │              │ │
│  │       ▼                     ▼              │ │
│  │  ┌──────────────┐    ┌─────────────────┐  │ │
│  │  │ Update Form  │◀───│   Validate      │  │ │
│  │  │    Data      │───▶│    Fields       │  │ │
│  │  └──────────────┘    └─────────────────┘  │ │
│  │       │                     │              │ │
│  │       │         ┌───────────┘              │ │
│  │       ▼         ▼                          │ │
│  │  ┌─────────────────────────────┐          │ │
│  │  │  Ask Clarifying Question?   │          │ │
│  │  │  (if confidence < 0.7)      │          │ │
│  │  └─────────────────────────────┘          │ │
│  │                                             │ │
│  └─────────────────────────────────────────────┘ │
│                                                   │
│  Agent Tools:                                     │
│  ✅ lookup_user_history                           │
│  ✅ analyze_user_request                          │
│  ✅ lookup_information                            │
│  ✅ update_form_data                              │
│  ✅ validate_field                                │
│  ✅ ask_clarifying_question                       │
└───────────────────────────────────────────────────┘
             │
             ▼
┌───────────────────────────────────────────────────┐
│         External Services                         │
│                                                   │
│  ┌────────────────┐    ┌────────────────────┐   │
│  │   Supabase     │    │   OpenRouter       │   │
│  │   (Postgres)   │    │   (LLM API)        │   │
│  │                │    │                    │   │
│  │  form_         │    │  Claude 3 Sonnet   │   │
│  │  submissions   │    │  GPT-4             │   │
│  └────────────────┘    └────────────────────┘   │
│                                                   │
│  ┌────────────────┐                              │
│  │   LangSmith    │                              │
│  │   (Observability)                             │
│  │                │                              │
│  │  Trace Agent   │                              │
│  │  Execution     │                              │
│  └────────────────┘                              │
└───────────────────────────────────────────────────┘
```

## Agent Workflow (LangGraph State Machine)

```
START
  │
  ▼
┌─────────────────────────────────────────────────┐
│ 1. ANALYZE NODE                                 │
│                                                 │
│ • Parse user message (Thai/English)            │
│ • Extract: quantities, dates, times, locations │
│ • Calculate confidence score                   │
│                                                 │
│ Input:  "ขอ laptop 2 เครื่อง พรุ่งนี้เช้า"         │
│ Output: {                                      │
│   equipments: [{type: "Notebook", qty: 2}],   │
│   requestDate: "2024-01-15",                  │
│   requestTime: "09:00",                       │
│   confidence: 0.85                            │
│ }                                              │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ 2. LOOKUP HISTORY NODE                          │
│                                                 │
│ • Query Supabase for user's past submissions   │
│ • Filter by session_id or user_id             │
│ • Add context to conversation                  │
│                                                 │
│ Query: session_id = "sess_12345"               │
│ Result: [                                      │
│   { submitted_at: "2024-01-10", ... },        │
│   { submitted_at: "2024-01-05", ... }         │
│ ]                                              │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ 3. UPDATE FORM NODE                             │
│                                                 │
│ • Merge extracted data into form_data          │
│ • Handle nested paths (e.g., equipments[0])   │
│ • Track highlighted fields                     │
│                                                 │
│ Before: {}                                     │
│ After: {                                       │
│   equipments: [{type: "Notebook", qty: 2}],   │
│   requestDate: "2024-01-15",                  │
│   requestTime: "09:00"                        │
│ }                                              │
│ Highlighted: ["equipments", "requestDate"]    │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ 4. VALIDATE NODE                                │
│                                                 │
│ • Validate each field against JSON Schema      │
│ • Check: required, patterns, enums, ranges    │
│ • Adjust confidence based on validation        │
│                                                 │
│ Checks:                                        │
│ ✓ equipments: array with minItems=1           │
│ ✓ requestDate: format="date" (YYYY-MM-DD)     │
│ ✓ requestTime: format="time" (HH:MM)          │
│ ✗ phoneNumber: missing (required)             │
│                                                 │
│ confidence: 0.85 → 0.85 (no errors in updated) │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
         ┌───────┴────────┐
         │  Should Ask    │
         │  Question?     │
         │                │
         │ • confidence   │
         │   < 0.7?       │
         │ • ambiguous    │
         │   fields?      │
         │ • validation   │
         │   errors?      │
         └───┬────────┬───┘
             │        │
      Yes    │        │ No
             │        │
             ▼        ▼
    ┌────────────┐  END
    │ 5. ASK     │   │
    │ QUESTION   │   │
    │ NODE       │   │
    │            │   │
    │ Generate   │   │
    │ clarifying │   │
    │ question   │   │
    │            │   │
    │ "กรุณาระบุ │   │
    │ เบอร์โทรฯ" │   │
    └─────┬──────┘   │
          │          │
          ▼          │
         END ◄───────┘
```

## Tool Descriptions

### 1. `lookup_user_history`
**Purpose**: Retrieve user's previous form submissions for context

**Function**:
```python
async def lookup_user_history(
    supabase_client,
    session_id: str,
    user_id: str = None,
    limit: int = 5
) -> List[Dict]
```

**Example**:
```python
history = await lookup_user_history(
    supabase_client=supabase,
    session_id="sess_12345",
    limit=3
)
# Returns:
[
  {
    "id": "uuid-1",
    "submitted_at": "2024-01-10T10:30:00Z",
    "data": { "department": "Engineering", ... }
  },
  ...
]
```

---

### 2. `analyze_user_request`
**Purpose**: Extract structured data from natural language

**Function**:
```python
async def analyze_user_request(
    user_message: str,
    form_schema: Dict,
    llm_client = None
) -> Dict
```

**Example**:
```python
result = await analyze_user_request(
    user_message="ขอ laptop 2 เครื่อง พรุ่งนี้เช้า",
    form_schema=equipment_schema
)
# Returns:
{
  "extracted_data": {
    "equipments": [{"type": "Notebook", "quantity": 2}],
    "requestDate": "2024-01-15",
    "requestTime": "09:00"
  },
  "confidence": 0.85,
  "ambiguities": ["deliveryLocation"]
}
```

**Pattern Matching**:
- Quantities: `(\d+)\s*(laptop|notebook|เครื่อง)`
- Dates: `tomorrow|พรุ่งนี้` → +1 day
- Times: `morning|เช้า` → "09:00"
- Buildings: `(building|ตึก|อาคาร)\s*([A-Z]|\w+)`

---

### 3. `lookup_information`
**Purpose**: Fuzzy match user input to valid field options

**Function**:
```python
async def lookup_information(
    query: str,
    form_schema: Dict,
    field_name: str,
    threshold: float = 0.6
) -> List[Dict]
```

**Example**:
```python
matches = await lookup_information(
    query="ตึกศรี",
    form_schema=equipment_schema,
    field_name="deliveryLocation"
)
# Returns:
[
  {
    "value": "ตึกศรีจันทร์ (Srichand Building)",
    "confidence": 0.87,
    "label": "ตึกศรีจันทร์"
  },
  {
    "value": "ตึกศรีสมาน (Srisaman Building)",
    "confidence": 0.72,
    "label": "ตึกศรีสมาน"
  }
]
```

**Algorithm**: SequenceMatcher (difflib) with configurable threshold

---

### 4. `update_form_data`
**Purpose**: Update form fields with validation

**Function**:
```python
async def update_form_data(
    current_form_data: Dict,
    field_path: str,
    new_value: Any,
    form_schema: Dict,
    validate: bool = True
) -> Dict
```

**Example**:
```python
updated = await update_form_data(
    current_form_data={"fullName": "John Doe"},
    field_path="equipments[0].quantity",
    new_value=2,
    form_schema=equipment_schema
)
# Returns:
{
  "fullName": "John Doe",
  "equipments": [
    {"quantity": 2}
  ]
}
```

**Supports**:
- Simple paths: `fullName`
- Nested paths: `equipments[0].type`
- Array notation: `equipments[1].quantity`

---

### 5. `validate_field`
**Purpose**: Validate field against JSON Schema

**Function**:
```python
async def validate_field(
    field_name: str,
    value: Any,
    form_schema: Dict
) -> Tuple[bool, str]
```

**Example**:
```python
is_valid, error = await validate_field(
    field_name="phoneNumber",
    value="0812345678",
    form_schema=equipment_schema
)
# Returns: (True, "")

is_valid, error = await validate_field(
    field_name="phoneNumber",
    value="123",
    form_schema=equipment_schema
)
# Returns: (False, "Field 'phoneNumber' does not match required pattern: ^0[0-9]{9}$")
```

**Validates**:
- Required fields
- Type constraints (string, integer, array)
- Pattern matching (regex)
- Enum values
- Number ranges (min/max)
- Date/time formats
- Array constraints (minItems/maxItems)

---

### 6. `ask_clarifying_question`
**Purpose**: Generate contextual questions for ambiguous fields

**Function**:
```python
async def ask_clarifying_question(
    ambiguous_fields: List[str],
    form_schema: Dict,
    context: Dict,
    language: str = "th"
) -> str
```

**Example**:
```python
question = await ask_clarifying_question(
    ambiguous_fields=["deliveryLocation", "phoneNumber"],
    form_schema=equipment_schema,
    context={
        "extracted_data": {"equipments": [...]},
        "confidence": 0.65
    },
    language="th"
)
# Returns:
"เข้าใจแล้วครับ คุณต้องการให้ส่งอุปกรณ์ไปที่ไหนครับ? (เช่น ตึกศรีจันทร์, อาคาร A)"
```

**Templates** (Thai):
- `equipments`: "คุณต้องการอุปกรณ์ประเภทใดบ้างครับ?"
- `requestDate`: "คุณต้องการใช้อุปกรณ์วันที่เท่าไหร่ครับ?"
- `phoneNumber`: "ขอเบอร์โทรศัพท์ติดต่อของคุณหน่อยครับ"
- Generic: "กรุณาระบุ {field_label} ครับ"

## Data Flow Example

### User Input
```
"I need 2 laptops for tomorrow morning at Building A"
```

### Step 1: Analyze
```json
{
  "extracted_data": {
    "equipments": [{"type": "Notebook", "quantity": 2}],
    "requestDate": "2024-01-15",
    "requestTime": "09:00",
    "deliveryLocation": "Building A"
  },
  "confidence": 0.9,
  "ambiguities": []
}
```

### Step 2: Lookup History
```json
[
  {
    "session_id": "sess_12345",
    "data": {
      "employeeId": "EMP001",
      "fullName": "John Doe",
      "department": "Engineering"
    }
  }
]
```

### Step 3: Update Form
```json
{
  "employeeId": "EMP001",        // from history
  "fullName": "John Doe",         // from history
  "department": "Engineering",    // from history
  "equipments": [
    {
      "type": "Notebook",
      "quantity": 2,
      "detail": ""
    }
  ],
  "requestDate": "2024-01-15",
  "requestTime": "09:00",
  "deliveryLocation": "Building A"
}
```

### Step 4: Validate
```
✓ equipments: valid (array with minItems=1)
✓ requestDate: valid (format: YYYY-MM-DD)
✓ requestTime: valid (format: HH:MM)
✗ phoneNumber: missing (required field)
```

### Step 5: Ask Question
```
"ขอเบอร์โทรศัพท์ติดต่อของคุณหน่อยครับ (10 หลัก)"
```

### Final Response
```json
{
  "response": "ขอเบอร์โทรศัพท์ติดต่อของคุณหน่อยครับ (10 หลัก)",
  "form_data": { ... },
  "highlighted_fields": ["equipments", "requestDate", "requestTime", "deliveryLocation"],
  "confidence": 0.9
}
```

## Implementation Status

| Component | Status | Test Coverage |
|-----------|--------|---------------|
| FastAPI App | ✅ Complete | 8 contract tests |
| SiriAgent | ✅ Complete | Integration pending |
| lookup_user_history | ✅ Complete | 4 unit tests |
| analyze_user_request | ✅ Complete | 5 unit tests |
| lookup_information | ✅ Complete | 5 unit tests |
| update_form_data | ✅ Complete | 5 unit tests |
| validate_field | ✅ Complete | 6 unit tests |
| ask_clarifying_question | ✅ Complete | 5 unit tests |
| LangSmith Integration | ⏳ Pending | - |
| Frontend | ⏳ Pending | - |
| Supabase Connection | ⏳ Pending | - |

**Total**: 38 test cases, 10/23 tasks complete (43.5%)
