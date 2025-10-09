# Database Setup Guide

This guide walks you through setting up the Supabase database for SiriForm Agent.

## Prerequisites

- Supabase account (sign up at https://supabase.com)
- Supabase project created

## Quick Setup

### 1. Create Supabase Project

1. Go to https://app.supabase.com
2. Click "New Project"
3. Fill in project details:
   - **Name**: `siriform-agent` (or your preferred name)
   - **Database Password**: Choose a strong password
   - **Region**: Select closest to your users
4. Wait for project to be provisioned (~2 minutes)

### 2. Run Database Schema

1. In Supabase Dashboard, go to **SQL Editor**
2. Click "New Query"
3. Copy the contents of `schema.sql` from this directory
4. Paste into the SQL editor
5. Click **Run** or press `Ctrl+Enter`

You should see messages indicating successful table creation.

### 3. Get API Credentials

1. In Supabase Dashboard, go to **Settings** → **API**
2. Copy the following values:
   - **Project URL**: `https://your-project.supabase.co`
   - **anon/public key**: `eyJhbGc...` (long JWT token)
   - **service_role key**: `eyJhbGc...` (for backend only, keep secret!)

3. Add to your `backend/.env` file:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGc...your-anon-key...
SUPABASE_JWT_SECRET=your-jwt-secret
```

### 4. Verify Setup

Run this SQL query in the SQL Editor to check tables:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

You should see:
- `form_submissions`
- `chat_history`
- `user_sessions`

## Database Schema

### Tables

#### `form_submissions`
Stores equipment request forms.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `session_id` | VARCHAR(255) | User session identifier |
| `user_id` | VARCHAR(255) | User ID (optional, for auth) |
| `form_type` | VARCHAR(100) | Type of form (default: 'equipment_form') |
| `form_data` | JSONB | Form field data (flexible schema) |
| `status` | VARCHAR(50) | Form status: draft, submitted, approved, rejected |
| `confidence_score` | DECIMAL(3,2) | AI confidence (0.00-1.00) |
| `created_at` | TIMESTAMPTZ | When form was created |
| `updated_at` | TIMESTAMPTZ | Last update time (auto-updated) |
| `submitted_at` | TIMESTAMPTZ | When form was submitted |

**Indexes:**
- `session_id` (for fast session lookups)
- `user_id` (for user queries)
- `status` (for filtering)
- `created_at` (for sorting)

#### `chat_history`
Stores conversation messages.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `session_id` | VARCHAR(255) | Session identifier |
| `submission_id` | UUID | Related form submission |
| `role` | VARCHAR(20) | Message role: user, assistant, system |
| `content` | TEXT | Message content |
| `confidence` | DECIMAL(3,2) | AI confidence for this message |
| `highlighted_fields` | TEXT[] | Fields updated in this message |
| `created_at` | TIMESTAMPTZ | Message timestamp |

#### `user_sessions`
Tracks user sessions (optional, for analytics).

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `session_id` | VARCHAR(255) | Unique session ID |
| `user_id` | VARCHAR(255) | User ID (if authenticated) |
| `ip_address` | INET | User's IP address |
| `user_agent` | TEXT | Browser user agent |
| `created_at` | TIMESTAMPTZ | Session start time |
| `last_activity` | TIMESTAMPTZ | Last activity timestamp |
| `expires_at` | TIMESTAMPTZ | Session expiry |

### Functions

#### `get_user_recent_submissions(session_id, limit)`
Retrieves recent form submissions for a session.

**Parameters:**
- `session_id` (VARCHAR): Session identifier
- `limit` (INT): Max number of results (default: 10)

**Returns:** Table of recent submissions

**Example:**
```sql
SELECT * FROM get_user_recent_submissions('test-session-001', 5);
```

#### `get_session_chat_history(session_id, limit)`
Retrieves chat messages for a session.

**Parameters:**
- `session_id` (VARCHAR): Session identifier
- `limit` (INT): Max number of messages (default: 50)

**Returns:** Table of chat messages

**Example:**
```sql
SELECT * FROM get_session_chat_history('test-session-001', 20);
```

## Testing with Sample Data

Uncomment the sample data section at the end of `schema.sql` to insert test records:

```sql
INSERT INTO form_submissions (session_id, form_type, form_data, status, confidence_score)
VALUES 
    ('test-session-001', 'equipment_form', 
     '{"requester_name": "สมชาย ใจดี", "department": "IT"}',
     'draft', 0.85);
```

Then query to verify:

```sql
SELECT * FROM form_submissions WHERE session_id = 'test-session-001';
```

## Security Notes

### Row Level Security (RLS)

RLS is **enabled** by default on all tables. Current policies allow all operations for development.

⚠️ **For production**: Update RLS policies to use `auth.uid()` for proper user isolation:

```sql
CREATE POLICY "Users can view own submissions" ON form_submissions
    FOR SELECT
    USING (auth.uid() = user_id);
```

### API Keys

- **anon key**: Safe to use in frontend (has RLS restrictions)
- **service_role key**: ⚠️ **NEVER expose in frontend!** Only use in backend
  - Bypasses RLS
  - Full database access
  - Keep in `.env` file (gitignored)

## Backup and Migration

### Export Schema

```bash
# Using Supabase CLI
supabase db dump -f schema.sql
```

### Backup Data

In Supabase Dashboard:
1. Go to **Database** → **Backups**
2. Create manual backup
3. Download if needed

### Migration

For schema changes:
1. Create migration file: `migrations/001_add_new_field.sql`
2. Test in development first
3. Apply to production via SQL Editor or Supabase CLI

## Troubleshooting

### Connection Issues

**Error**: `Failed to connect to Supabase`

**Solutions**:
1. Check `.env` has correct `SUPABASE_URL` and `SUPABASE_KEY`
2. Verify project is active in Supabase Dashboard
3. Check API rate limits (free tier: 100 requests/second)

### Permission Errors

**Error**: `permission denied for table`

**Solutions**:
1. Check RLS policies are set correctly
2. Verify using correct API key (anon vs service_role)
3. Grant permissions if needed:
   ```sql
   GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
   ```

### Query Performance

For large datasets:
1. Ensure indexes are created (check `schema.sql`)
2. Add indexes for frequently queried columns:
   ```sql
   CREATE INDEX idx_custom ON table_name(column_name);
   ```
3. Use `EXPLAIN ANALYZE` to debug slow queries

## Monitoring

### Query Dashboard

Supabase Dashboard → **Database** → **Query Performance**
- View slow queries
- Analyze query plans
- Monitor table sizes

### Usage Metrics

Dashboard → **Settings** → **Usage**
- Database size
- API requests
- Storage usage

## Further Reading

- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [Supabase CLI](https://supabase.com/docs/guides/cli)
