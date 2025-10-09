-- SiriForm Agent Database Schema
-- Supabase PostgreSQL Schema for storing form submissions and user sessions

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Form Submissions Table
-- Stores all equipment request form submissions
CREATE TABLE IF NOT EXISTS form_submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255), -- Optional: For authenticated users
    
    -- Form Data (JSONB for flexible schema)
    form_type VARCHAR(100) NOT NULL DEFAULT 'equipment_form',
    form_data JSONB NOT NULL DEFAULT '{}',
    
    -- Metadata
    status VARCHAR(50) NOT NULL DEFAULT 'draft', -- draft, submitted, approved, rejected
    confidence_score DECIMAL(3,2), -- 0.00 to 1.00
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    submitted_at TIMESTAMP WITH TIME ZONE,
    
    -- Indexes for fast lookup
    CONSTRAINT valid_status CHECK (status IN ('draft', 'submitted', 'approved', 'rejected'))
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_form_submissions_session_id ON form_submissions(session_id);
CREATE INDEX IF NOT EXISTS idx_form_submissions_user_id ON form_submissions(user_id);
CREATE INDEX IF NOT EXISTS idx_form_submissions_status ON form_submissions(status);
CREATE INDEX IF NOT EXISTS idx_form_submissions_created_at ON form_submissions(created_at DESC);

-- Chat History Table
-- Stores conversation history for each session
CREATE TABLE IF NOT EXISTS chat_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) NOT NULL,
    submission_id UUID REFERENCES form_submissions(id) ON DELETE CASCADE,
    
    -- Message Data
    role VARCHAR(20) NOT NULL, -- user, assistant, system
    content TEXT NOT NULL,
    
    -- Metadata
    confidence DECIMAL(3,2),
    highlighted_fields TEXT[], -- Array of field names
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_role CHECK (role IN ('user', 'assistant', 'system'))
);

-- Create indexes for chat history
CREATE INDEX IF NOT EXISTS idx_chat_history_session_id ON chat_history(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_submission_id ON chat_history(submission_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_created_at ON chat_history(created_at ASC);

-- User Sessions Table (Optional - for tracking)
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255),
    
    -- Session Data
    ip_address INET,
    user_agent TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for user sessions
CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_last_activity ON user_sessions(last_activity DESC);

-- Function: Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Auto-update updated_at on form_submissions
CREATE TRIGGER update_form_submissions_updated_at
    BEFORE UPDATE ON form_submissions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function: Get user's recent submissions
CREATE OR REPLACE FUNCTION get_user_recent_submissions(
    p_session_id VARCHAR(255),
    p_limit INT DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    form_type VARCHAR(100),
    form_data JSONB,
    status VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        fs.id,
        fs.form_type,
        fs.form_data,
        fs.status,
        fs.created_at
    FROM form_submissions fs
    WHERE fs.session_id = p_session_id
    ORDER BY fs.created_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function: Get chat history for a session
CREATE OR REPLACE FUNCTION get_session_chat_history(
    p_session_id VARCHAR(255),
    p_limit INT DEFAULT 50
)
RETURNS TABLE (
    id UUID,
    role VARCHAR(20),
    content TEXT,
    confidence DECIMAL(3,2),
    highlighted_fields TEXT[],
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ch.id,
        ch.role,
        ch.content,
        ch.confidence,
        ch.highlighted_fields,
        ch.created_at
    FROM chat_history ch
    WHERE ch.session_id = p_session_id
    ORDER BY ch.created_at ASC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Row Level Security (RLS) Policies
-- Enable RLS on all tables
ALTER TABLE form_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their own session data
-- Note: In production, you should use proper authentication
CREATE POLICY "Users can view their own submissions" ON form_submissions
    FOR SELECT
    USING (true); -- For now, allow all reads (adjust in production with auth.uid())

CREATE POLICY "Users can insert their own submissions" ON form_submissions
    FOR INSERT
    WITH CHECK (true); -- For now, allow all inserts

CREATE POLICY "Users can update their own submissions" ON form_submissions
    FOR UPDATE
    USING (true); -- For now, allow all updates

-- Similar policies for chat_history
CREATE POLICY "Users can view their own chat history" ON chat_history
    FOR SELECT
    USING (true);

CREATE POLICY "Users can insert their own chat messages" ON chat_history
    FOR INSERT
    WITH CHECK (true);

-- Sample Data (for testing)
-- Uncomment to insert sample data
/*
INSERT INTO form_submissions (session_id, form_type, form_data, status, confidence_score)
VALUES 
    ('test-session-001', 'equipment_form', 
     '{"requester_name": "สมชาย ใจดี", "department": "IT", "purpose": "ทดสอบระบบ"}',
     'draft', 0.85),
    ('test-session-002', 'equipment_form',
     '{"requester_name": "สมหญิง รักงาน", "department": "HR", "purpose": "ขอเครื่องใหม่"}',
     'submitted', 0.92);

INSERT INTO chat_history (session_id, role, content, confidence)
VALUES
    ('test-session-001', 'user', 'ขอ laptop 2 เครื่องครับ', NULL),
    ('test-session-001', 'assistant', 'รับทราบครับ คุณต้องการใช้เมื่อไหร่ครับ?', 0.85);
*/

-- Grant necessary permissions to service role
-- Note: Execute this after creating the tables
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
-- GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO service_role;

-- Comments for documentation
COMMENT ON TABLE form_submissions IS 'Stores equipment request form submissions with flexible JSON schema';
COMMENT ON TABLE chat_history IS 'Stores conversation history between users and the AI agent';
COMMENT ON TABLE user_sessions IS 'Tracks user sessions for analytics and security';
COMMENT ON COLUMN form_submissions.form_data IS 'Flexible JSONB column storing form field data';
COMMENT ON COLUMN form_submissions.confidence_score IS 'AI confidence score (0.00-1.00) for form completeness';
COMMENT ON FUNCTION get_user_recent_submissions IS 'Retrieves recent form submissions for a given session';
COMMENT ON FUNCTION get_session_chat_history IS 'Retrieves chat conversation history for a session';
