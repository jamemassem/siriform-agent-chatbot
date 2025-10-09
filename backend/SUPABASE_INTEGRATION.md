# Supabase Integration Guide

## Overview

SiriForm Agent uses **Supabase** (PostgreSQL database) to:
- 📝 Store form submissions (drafts and completed forms)
- 💬 Save chat conversation history
- 👤 Track user sessions for analytics
- 🔍 Enable AI agent to lookup user's historical data

## Architecture

```
Frontend (React)
    ↓ HTTP POST /api/v1/chat
Backend (FastAPI)
    ↓ Process with SiriAgent
    ↓ Save to Supabase
Database (PostgreSQL)
    - form_submissions
    - chat_history
    - user_sessions
```

## Setup

### 1. Create Supabase Project

See [`database/README.md`](./database/README.md) for detailed instructions.

Quick steps:
1. Go to https://supabase.com and create account
2. Create new project
3. Run `database/schema.sql` in SQL Editor
4. Copy API credentials to `.env`

### 2. Configure Environment

Add to `backend/.env`:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGc...your-anon-key...
SUPABASE_JWT_SECRET=your-jwt-secret
```

### 3. Test Connection

Run the test script:

```bash
cd backend
uv run python -m app.test_supabase
```

Expected output:
```
✓ Supabase client initialized successfully
✓ Created submission with ID: 12345...
✓ Saved user message
✓ Saved assistant message
✓ Retrieved 1 submission(s)
```

## Database Schema

### Tables

#### `form_submissions`
Primary storage for equipment request forms.

```sql
CREATE TABLE form_submissions (
    id UUID PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    form_type VARCHAR(100) DEFAULT 'equipment_form',
    form_data JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    submitted_at TIMESTAMPTZ
);
```

**Status values:**
- `draft` - Form being filled out
- `submitted` - User completed and submitted
- `approved` - Admin approved the request
- `rejected` - Admin rejected the request

#### `chat_history`
Stores all conversation messages.

```sql
CREATE TABLE chat_history (
    id UUID PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    submission_id UUID REFERENCES form_submissions(id),
    role VARCHAR(20) NOT NULL,  -- user, assistant, system
    content TEXT NOT NULL,
    confidence DECIMAL(3,2),
    highlighted_fields TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### `user_sessions`
Tracks active sessions (optional, for analytics).

```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity TIMESTAMPTZ DEFAULT NOW()
);
```

## Usage in Code

### Creating Submissions

```python
from app.services import SupabaseService
from app.llm import get_supabase_client

# Initialize
client = get_supabase_client()
service = SupabaseService(client)

# Create new submission
submission = service.create_submission(
    session_id="user-session-123",
    form_type="equipment_form",
    form_data={
        "requester_name": "John Doe",
        "department": "IT"
    },
    status="draft",
    confidence_score=0.75
)

print(f"Created: {submission['id']}")
```

### Saving Chat Messages

```python
# Save user message
service.save_message(
    session_id="user-session-123",
    role="user",
    content="ขอ laptop 2 เครื่องครับ"
)

# Save assistant response
service.save_message(
    session_id="user-session-123",
    role="assistant",
    content="รับทราบครับ",
    confidence=0.85,
    highlighted_fields=["equipment_type", "quantity"]
)
```

### Retrieving History

```python
from app.agent.tools.history import lookup_user_history

# Get user's past submissions
history = lookup_user_history(
    supabase_client=client,
    session_id="user-session-123",
    limit=5
)

for item in history:
    print(f"Previous request: {item['form_data']}")
```

### Updating Submissions

```python
# Update form data
service.update_submission(
    submission_id="12345-uuid",
    form_data={"requester_name": "Jane Doe"},
    confidence_score=0.90
)

# Mark as submitted
from datetime import datetime
service.update_submission(
    submission_id="12345-uuid",
    status="submitted",
    submitted_at=datetime.utcnow()
)
```

## Integration Points

### 1. Chat Endpoint (`/api/v1/chat`)

When user sends a message:

```python
# 1. Save user message
supabase_service.save_message(
    session_id=request.session_id,
    role="user",
    content=request.message
)

# 2. Process with SiriAgent
result = await agent.process_message(...)

# 3. Save assistant response
supabase_service.save_message(
    session_id=request.session_id,
    role="assistant",
    content=result["response"],
    confidence=result["confidence"],
    highlighted_fields=result["highlighted_fields"]
)

# 4. Update or create submission
submission = supabase_service.get_or_create_submission(
    session_id=request.session_id
)

supabase_service.update_submission(
    submission_id=submission["id"],
    form_data=result["form_data"]
)
```

### 2. SiriAgent - History Lookup

The AI agent can access past submissions:

```python
# In SiriAgent.process_message()
if self.supabase_client:
    history = lookup_user_history(
        supabase_client=self.supabase_client,
        session_id=session_id,
        limit=3
    )
    
    if history:
        # Use history to inform responses
        last_request = history[0]
        print(f"User previously requested: {last_request['form_data']}")
```

### 3. Graceful Fallback

If Supabase is not configured, the system continues working without persistence:

```python
try:
    supabase = get_supabase_client()
    supabase_service = SupabaseService(supabase)
except ValueError:
    print("⚠ Supabase not configured - persistence disabled")
    supabase = None
    supabase_service = None

# Later, check before using
if supabase_service:
    supabase_service.save_message(...)
```

## Security

### Row Level Security (RLS)

RLS is enabled on all tables. Current policies (development mode):

```sql
CREATE POLICY "Users can view own submissions" ON form_submissions
    FOR SELECT USING (true);

CREATE POLICY "Users can insert submissions" ON form_submissions
    FOR INSERT WITH CHECK (true);
```

⚠️ **Production**: Update policies to use `auth.uid()` for proper user isolation.

### API Keys

- **anon key**: Used in backend, safe (RLS applied)
- **service_role key**: Full access, NEVER expose in frontend
- Both keys should be in `.env` (gitignored)

## Monitoring

### Supabase Dashboard

1. **Table Editor**: View and edit data
   - Go to project → Table Editor
   - Browse `form_submissions`, `chat_history`

2. **SQL Editor**: Run custom queries
   ```sql
   -- Get today's submissions
   SELECT * FROM form_submissions
   WHERE created_at >= CURRENT_DATE
   ORDER BY created_at DESC;
   
   -- Count messages per session
   SELECT session_id, COUNT(*) as message_count
   FROM chat_history
   GROUP BY session_id
   ORDER BY message_count DESC;
   ```

3. **Database → Performance**: Monitor slow queries

4. **Auth → Logs**: View authentication events (if using auth)

### Useful Queries

**Get submission with chat history:**
```sql
SELECT 
    fs.id,
    fs.form_data,
    fs.status,
    json_agg(ch ORDER BY ch.created_at) as messages
FROM form_submissions fs
LEFT JOIN chat_history ch ON ch.session_id = fs.session_id
WHERE fs.session_id = 'your-session-id'
GROUP BY fs.id;
```

**Find incomplete forms:**
```sql
SELECT * FROM form_submissions
WHERE status = 'draft'
AND updated_at < NOW() - INTERVAL '1 day'
ORDER BY updated_at DESC;
```

**Top requested equipment:**
```sql
SELECT 
    form_data->>'equipment_type' as equipment,
    COUNT(*) as count
FROM form_submissions
WHERE form_data->>'equipment_type' IS NOT NULL
GROUP BY equipment
ORDER BY count DESC;
```

## Troubleshooting

### Connection Issues

**Error**: `Failed to connect to Supabase`

**Check:**
1. `.env` file exists in `backend/` directory
2. `SUPABASE_URL` format: `https://xxx.supabase.co`
3. `SUPABASE_KEY` is the **anon** key (not service_role)
4. Project is active in Supabase dashboard
5. Network allows connections to Supabase

**Test:**
```bash
curl https://your-project.supabase.co/rest/v1/
```

### Permission Errors

**Error**: `permission denied for table form_submissions`

**Solutions:**
1. Check RLS policies are created (run `schema.sql`)
2. Verify using correct API key
3. Grant permissions in SQL Editor:
   ```sql
   GRANT ALL ON ALL TABLES IN SCHEMA public TO anon;
   GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
   ```

### Data Not Saving

**Check:**
1. `supabase_client` is not None before calling save functions
2. Check backend logs for errors
3. Verify table exists: `SELECT * FROM form_submissions LIMIT 1;`
4. Test with `test_supabase.py` script

## Migration from Development to Production

### Backup Data

```bash
# Using Supabase Dashboard
1. Go to Database → Backups
2. Create manual backup
3. Download if needed

# Or using pg_dump (if you have direct access)
pg_dump -h your-db-host -U postgres -d postgres > backup.sql
```

### Update RLS Policies

Replace development policies with production ones:

```sql
-- Drop dev policies
DROP POLICY IF EXISTS "Users can view own submissions" ON form_submissions;

-- Add production policies with auth
CREATE POLICY "Users can view own submissions" ON form_submissions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own submissions" ON form_submissions
    FOR INSERT WITH CHECK (auth.uid() = user_id);
```

### Set Up Indexes

For large datasets, add indexes:

```sql
CREATE INDEX idx_form_submissions_user_id ON form_submissions(user_id);
CREATE INDEX idx_chat_history_session_created ON chat_history(session_id, created_at);
```

## Further Reading

- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL JSONB](https://www.postgresql.org/docs/current/datatype-json.html)
- [Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)
- [Supabase Python Client](https://github.com/supabase-community/supabase-py)
