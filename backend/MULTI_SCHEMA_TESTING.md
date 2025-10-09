# Multi-Schema Integration Testing

## Overview

This document explains how SiriForm Agent supports multiple form types through dynamic schema rendering.

## Supported Form Types

### 1. Equipment Request Form (`equipment_form`)
**Purpose**: Request computer equipment borrowing

**Key Features**:
- 26 total fields (18 required, 8 optional)
- Equipment array support
- Date/time fields for usage period
- File attachment support
- Boolean fields for software requirements

**Use Cases**:
- Laptop/desktop borrowing
- Peripheral equipment requests
- Software installation requests

**Example**:
```json
{
  "fullName": "สมชาย ใจดี",
  "department": "IT",
  "equipments": ["laptop", "mouse"],
  "usageStartDate": "2025-10-15",
  "pickupTime": "09:00"
}
```

---

### 2. Meeting Room Booking Form (`meeting_room_form`)
**Purpose**: Book meeting rooms and conference facilities

**Key Features**:
- 15 total fields (7 required, 8 optional)
- Room type enum (small, medium, large, boardroom, training)
- Equipment selection (projector, whiteboard, video conference)
- Recurring booking support
- Attendee count tracking

**Use Cases**:
- Team meetings
- Client presentations
- Training sessions
- Board meetings

**Example**:
```json
{
  "requester_name": "สมหญิง รักงาน",
  "room_type": "medium",
  "booking_date": "2025-10-16",
  "start_time": "14:00",
  "end_time": "16:00",
  "equipment_needed": ["projector", "whiteboard"]
}
```

---

### 3. Leave Request Form (`leave_request_form`)
**Purpose**: Submit employee leave requests

**Key Features**:
- 17 total fields (7 required, 10 optional)
- Leave type enum (annual, sick, personal, maternity, etc.)
- Half-day leave support
- Medical certificate tracking
- Substitute person assignment

**Use Cases**:
- Annual leave
- Sick leave with medical certificate
- Personal emergency leave
- Maternity/paternity leave

**Example**:
```json
{
  "employee_name": "สมศักดิ์ มีชัย",
  "employee_id": "IT001234",
  "leave_type": "annual",
  "start_date": "2025-10-20",
  "end_date": "2025-10-22",
  "total_days": 3
}
```

---

## How It Works

### 1. Schema-Driven Rendering

The frontend **DynamicFormRenderer** component reads JSON Schema and automatically generates appropriate UI:

```typescript
<DynamicFormRenderer
  schema={schema}         // Any JSON Schema
  formData={formData}     // Current form values
  highlightedFields={[]}  // Fields to highlight
  readOnly={true}         // Display mode
/>
```

**Supported Field Types**:
- ✅ `string` - Text input, textarea for long text
- ✅ `number` / `integer` - Number input with min/max
- ✅ `boolean` - Checkbox
- ✅ `array` - Multi-value display (equipment lists, etc.)
- ✅ `enum` - Dropdown select with Thai labels

**Supported Formats**:
- ✅ `date` - Date picker
- ✅ `time` - Time picker
- ✅ `email` - Email input with validation
- ✅ `pattern` - Regex validation

### 2. Backend API

All schemas are served through a single endpoint:

```http
GET /api/v1/form-schema/{form_name}
```

**Examples**:
```bash
# Equipment form
curl http://localhost:8000/api/v1/form-schema/equipment_form

# Meeting room form
curl http://localhost:8000/api/v1/form-schema/meeting_room_form

# Leave request form
curl http://localhost:8000/api/v1/form-schema/leave_request_form
```

**Response**:
```json
{
  "name": "meeting_room_form",
  "version": "1.0.0",
  "schema": {
    "title": "Meeting Room Booking Form",
    "properties": { ... }
  }
}
```

### 3. AI Agent Compatibility

The **SiriAgent** can work with any form schema:

```python
agent = SiriAgent(
    llm=llm_client,
    supabase_client=supabase,
    form_schema=load_form_schema("meeting_room_form")  # Any schema!
)

result = await agent.process_message(
    user_message="ขอจองห้องประชุมพรุ่งนี้ 10 คน",
    session_id="user-123",
    current_form_data={}
)
```

The agent automatically:
- Extracts relevant information from user message
- Maps to correct schema fields
- Validates against requirements
- Returns highlighted fields that were updated

---

## Testing

### Run Integration Tests

Test all schemas at once:

```bash
cd backend
uv run python -m app.test_schemas
```

**Test Coverage**:
1. ✅ Schema loading from JSON files
2. ✅ Field type compatibility with DynamicFormRenderer
3. ✅ Sample data generation
4. ✅ API endpoint readiness
5. ✅ Dependencies validation

**Expected Output**:
```
✅ Passed: 6/6 tests
🎉 All tests passed! System is ready for multiple form types.
```

### Manual API Testing

1. **Start Backend**:
   ```bash
   cd backend
   uv run uvicorn app.main:app --reload
   ```

2. **Test Endpoints**:
   ```bash
   # Equipment form (original)
   curl http://localhost:8000/api/v1/form-schema/equipment_form | jq '.schema.title'
   # Output: "Computer Equipment Request Form"
   
   # Meeting room form (new)
   curl http://localhost:8000/api/v1/form-schema/meeting_room_form | jq '.schema.title'
   # Output: "Meeting Room Booking Form"
   
   # Leave request form (new)
   curl http://localhost:8000/api/v1/form-schema/leave_request_form | jq '.schema.title'
   # Output: "Leave Request Form"
   ```

### Frontend Testing

The frontend automatically adapts to any schema:

1. **Modify App.tsx** to load different schema:
   ```typescript
   const response = await getFormSchema('meeting_room_form'); // Change here
   ```

2. **Result**: Form preview automatically renders with:
   - Correct field labels (Thai)
   - Appropriate input types
   - Enum dropdowns
   - Date/time pickers
   - Array displays

---

## Adding New Form Types

### Step 1: Create Schema File

Create `backend/app/schemas/your_form.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Your Form Title",
  "description": "Form description",
  "version": "1.0.0",
  "type": "object",
  "required": ["field1", "field2"],
  "properties": {
    "field1": {
      "type": "string",
      "title": "ฟิลด์ที่ 1",
      "description": "Field description"
    }
  }
}
```

### Step 2: Test the Schema

```bash
cd backend
uv run python -m app.test_schemas
```

### Step 3: Use in Frontend

```typescript
// Load your new form
const response = await getFormSchema('your_form');
setFormSchema(response.schema);
```

**That's it!** The system automatically:
- ✅ Serves schema via API
- ✅ Renders form in frontend
- ✅ AI agent can process it

---

## Field Type Reference

### String Fields

```json
{
  "field_name": {
    "type": "string",
    "title": "ชื่อฟิลด์",
    "minLength": 2,
    "maxLength": 100,
    "pattern": "^[A-Z]{2}[0-9]+$",
    "examples": ["Example value"]
  }
}
```

**Renders as**: Text input (or textarea if `maxLength > 200`)

### Enum Fields (Dropdown)

```json
{
  "department": {
    "type": "string",
    "title": "แผนก",
    "enum": ["IT", "HR", "Finance"],
    "enumLabels": {
      "IT": "เทคโนโลยีสารสนเทศ",
      "HR": "ทรัพยากรบุคคล",
      "Finance": "การเงิน"
    }
  }
}
```

**Renders as**: Dropdown with Thai labels

### Date/Time Fields

```json
{
  "booking_date": {
    "type": "string",
    "format": "date",
    "title": "วันที่จอง"
  },
  "start_time": {
    "type": "string",
    "format": "time",
    "title": "เวลาเริ่ม"
  }
}
```

**Renders as**: Date picker / Time picker

### Number Fields

```json
{
  "quantity": {
    "type": "integer",
    "title": "จำนวน",
    "minimum": 1,
    "maximum": 10,
    "default": 1
  }
}
```

**Renders as**: Number input with validation

### Boolean Fields

```json
{
  "urgent": {
    "type": "boolean",
    "title": "เร่งด่วน",
    "default": false
  }
}
```

**Renders as**: Checkbox

### Array Fields

```json
{
  "equipment_needed": {
    "type": "array",
    "title": "อุปกรณ์ที่ต้องการ",
    "items": {
      "type": "string",
      "enum": ["laptop", "mouse", "keyboard"]
    },
    "enumLabels": {
      "laptop": "แล็ปท็อป",
      "mouse": "เมาส์",
      "keyboard": "คีย์บอร์ด"
    }
  }
}
```

**Renders as**: List of selected items with labels

---

## Best Practices

### 1. Always Include Thai Labels

```json
{
  "field_name": {
    "title": "ชื่อฟิลด์ (ภาษาไทย)",  // Thai label
    "description": "คำอธิบายภาษาไทย"   // Thai description
  }
}
```

### 2. Provide enumLabels for Enums

```json
{
  "enum": ["value1", "value2"],
  "enumLabels": {
    "value1": "ค่าที่ 1",
    "value2": "ค่าที่ 2"
  }
}
```

### 3. Set Reasonable Constraints

```json
{
  "minLength": 2,        // Minimum reasonable length
  "maxLength": 500,      // Prevent excessive input
  "minimum": 1,          // Positive numbers only
  "pattern": "^[0-9]+$"  // Validation regex
}
```

### 4. Mark Critical Fields as Required

```json
{
  "required": [
    "requester_name",
    "date",
    "purpose"
  ]
}
```

### 5. Include Version

```json
{
  "version": "1.0.0"  // For schema evolution tracking
}
```

---

## Troubleshooting

### Schema Not Loading

**Error**: `Form schema 'xxx' not found`

**Solution**: Ensure file exists at `backend/app/schemas/xxx.json`

### Field Not Rendering

**Check**:
1. Field type is supported (string, number, boolean, array)
2. Enum has `enumLabels` if used
3. Format is valid (date, time, email)

### Validation Not Working

**Check**:
1. `required` array includes field name
2. `minLength`/`maxLength` set correctly
3. `pattern` regex is valid

---

## Statistics

| Schema | Total Fields | Required | Field Types | Special Features |
|--------|-------------|----------|-------------|------------------|
| **equipment_form** | 26 | 18 | string (22), array (2), boolean (2) | Equipment list, date/time pairs, file attachments |
| **meeting_room_form** | 15 | 7 | string (12), integer (1), array (1), boolean (1) | Room types, recurring bookings, equipment selection |
| **leave_request_form** | 17 | 7 | string (13), number (1), boolean (3) | Leave types, half-day support, medical cert tracking |

---

## Future Enhancements

### Planned Form Types
- 🔜 Travel Request Form
- 🔜 Expense Claim Form
- 🔜 IT Support Ticket Form
- 🔜 Visitor Registration Form

### Advanced Features
- 🔜 Conditional fields (show/hide based on values)
- 🔜 Field calculations (auto-compute totals)
- 🔜 File upload integration
- 🔜 Multi-step forms (wizards)
- 🔜 Form versioning and migration

---

## Conclusion

The multi-schema support demonstrates that **SiriForm Agent** is a truly flexible, schema-driven form system. By simply creating a JSON Schema file, you can instantly:

1. ✅ Generate API endpoint
2. ✅ Render dynamic form UI
3. ✅ Enable AI-powered chat filling
4. ✅ Store submissions in database

**No code changes required** - just drop in a new schema! 🚀
