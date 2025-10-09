-- Authentication Tables for SiriForm Agent Chatbot
-- This file extends the existing database schema with user authentication

-- =====================================================
-- Users Table
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ,
    
    -- Constraints
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'),
    CONSTRAINT username_format CHECK (username ~* '^[a-zA-Z0-9_-]{3,50}$')
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at DESC);

-- =====================================================
-- Update existing tables to link with users
-- =====================================================

-- Add user_id foreign key to form_submissions if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'form_submissions' 
        AND column_name = 'user_id'
    ) THEN
        ALTER TABLE form_submissions 
        ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE CASCADE;
        
        CREATE INDEX idx_form_submissions_user_id ON form_submissions(user_id);
    END IF;
END $$;

-- Add user_id foreign key to chat_history if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'chat_history' 
        AND column_name = 'user_id'
    ) THEN
        ALTER TABLE chat_history 
        ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE CASCADE;
        
        CREATE INDEX idx_chat_history_user_id ON chat_history(user_id);
    END IF;
END $$;

-- Add user_id foreign key to user_sessions if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'user_sessions' 
        AND column_name = 'user_id'
    ) THEN
        ALTER TABLE user_sessions 
        ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE CASCADE;
        
        CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
    END IF;
END $$;

-- =====================================================
-- Trigger to update updated_at timestamp
-- =====================================================
CREATE OR REPLACE FUNCTION update_users_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_users_updated_at();

-- =====================================================
-- Row Level Security (RLS) Policies for users table
-- =====================================================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Users can read their own data
CREATE POLICY "Users can view own profile"
    ON users FOR SELECT
    USING (auth.uid() = id);

-- Users can update their own data
CREATE POLICY "Users can update own profile"
    ON users FOR UPDATE
    USING (auth.uid() = id);

-- =====================================================
-- Helper Functions
-- =====================================================

-- Function to get user by email
CREATE OR REPLACE FUNCTION get_user_by_email(user_email TEXT)
RETURNS TABLE (
    id UUID,
    email TEXT,
    username TEXT,
    password_hash TEXT,
    full_name TEXT,
    is_active BOOLEAN,
    is_verified BOOLEAN,
    created_at TIMESTAMPTZ,
    last_login_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.id,
        u.email,
        u.username,
        u.password_hash,
        u.full_name,
        u.is_active,
        u.is_verified,
        u.created_at,
        u.last_login_at
    FROM users u
    WHERE u.email = user_email
    AND u.is_active = TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get user by username
CREATE OR REPLACE FUNCTION get_user_by_username(user_username TEXT)
RETURNS TABLE (
    id UUID,
    email TEXT,
    username TEXT,
    password_hash TEXT,
    full_name TEXT,
    is_active BOOLEAN,
    is_verified BOOLEAN,
    created_at TIMESTAMPTZ,
    last_login_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.id,
        u.email,
        u.username,
        u.password_hash,
        u.full_name,
        u.is_active,
        u.is_verified,
        u.created_at,
        u.last_login_at
    FROM users u
    WHERE u.username = user_username
    AND u.is_active = TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update last login timestamp
CREATE OR REPLACE FUNCTION update_user_last_login(user_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE users
    SET last_login_at = NOW()
    WHERE id = user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- Comments
-- =====================================================
COMMENT ON TABLE users IS 'Stores user authentication and profile data';
COMMENT ON COLUMN users.id IS 'Unique user identifier (UUID)';
COMMENT ON COLUMN users.email IS 'User email address (unique, validated)';
COMMENT ON COLUMN users.username IS 'User username (unique, 3-50 chars)';
COMMENT ON COLUMN users.password_hash IS 'Bcrypt hashed password';
COMMENT ON COLUMN users.full_name IS 'User full name (optional)';
COMMENT ON COLUMN users.is_active IS 'Whether user account is active';
COMMENT ON COLUMN users.is_verified IS 'Whether email is verified';
COMMENT ON COLUMN users.last_login_at IS 'Last successful login timestamp';
