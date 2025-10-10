# 🚀 SiriForm Agent Setup Guide

## Overview

This guide will help you set up all the necessary API keys and configurations to run the SiriForm Agent Chatbot.

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- Git

---

## Step 1: Get OpenRouter API Key (Required)

OpenRouter provides access to multiple AI models including Claude, GPT-4, etc.

### 1.1 Create OpenRouter Account
1. Go to https://openrouter.ai/
2. Click "Sign Up" or "Sign In"
3. Log in with your preferred method (Google, GitHub, etc.)

### 1.2 Get API Key
1. Go to https://openrouter.ai/keys
2. Click "Create Key"
3. Give it a name (e.g., "SiriForm Agent")
4. Copy the key (starts with `sk-or-v1-...`)

### 1.3 Add Credits (if needed)
- OpenRouter requires credits to use
- Go to https://openrouter.ai/credits
- Add credits via credit card
- Recommended: Start with $5-10 for testing

**Important:** Keep this key safe! You'll need it in Step 3.

---

## Step 2: Get LangSmith API Key (Optional - for observability)

LangSmith helps you trace and debug your AI agent execution.

### 2.1 Create LangSmith Account
1. Go to https://smith.langchain.com/
2. Click "Sign Up" 
3. Sign up with email or GitHub

### 2.2 Get API Key
1. After login, go to https://smith.langchain.com/settings
2. Click "API Keys" tab
3. Click "Create API Key"
4. Give it a name (e.g., "SiriForm")
5. Copy the key (starts with `ls__...` or `lsv2_pt_...`)

### 2.3 Create Project
1. Go to https://smith.langchain.com/
2. Click "New Project"
3. Name it `siriform-agent` (or any name you prefer)

**Note:** LangSmith has a free tier that's sufficient for development.

---

## Step 3: Setup Supabase (Optional - for chat history)

Supabase provides PostgreSQL database for storing form submissions and chat history.

### 3.1 Create Supabase Project
1. Go to https://supabase.com/
2. Click "Start your project"
3. Sign in with GitHub
4. Click "New Project"
5. Fill in:
   - Name: `siriform-agent`
   - Database Password: (create a strong password)
   - Region: Choose closest to you
6. Click "Create new project" (takes ~2 minutes)

### 3.2 Get Database Credentials
1. After project is created, go to **Settings** (left sidebar)
2. Click **API** section
3. Copy these values:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **Project API keys** → `anon` `public` key

### 3.3 Run Database Schema
1. Go to **SQL Editor** (left sidebar)
2. Click "New Query"
3. Copy content from `backend/database/schema.sql`
4. Paste and click "Run"
5. Wait for "Success" message

**Note:** You can skip Supabase for initial testing. The app works without it (no persistence).

---

## Step 4: Configure Environment Variables

### 4.1 Backend Configuration

1. Navigate to project root:
   ```powershell
   cd D:\Users\User\Documents\GitHub\siriform-agent-chatbot
   ```

2. Check if `.env` file exists:
   ```powershell
   Test-Path .env
   ```

3. If it returns `False`, copy from example:
   ```powershell
   Copy-Item .env.example .env
   ```

4. Open `.env` file in your editor and update these values:

```bash
# ✅ REQUIRED: OpenRouter API Key
OPENROUTER_API_KEY=sk-or-v1-YOUR_ACTUAL_KEY_HERE

# ⚙️ OPTIONAL: LangSmith (for tracing and debugging)
LANGSMITH_API_KEY=ls__YOUR_ACTUAL_KEY_HERE
LANGSMITH_PROJECT=siriform-agent

# ⚙️ OPTIONAL: Supabase (for chat history persistence)
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_KEY=YOUR_ANON_KEY_HERE
```

### 4.2 Frontend Configuration

The frontend uses Vite and reads from `frontend/.env`:

```powershell
cd frontend
```

Check if `.env` exists:
```powershell
Test-Path .env
```

If not, copy from example:
```powershell
Copy-Item .env.example .env
```

Content should be:
```bash
VITE_API_BASE_URL=http://localhost:8000
```

---

## Step 5: Install Dependencies

### 5.1 Backend Dependencies

```powershell
cd D:\Users\User\Documents\GitHub\siriform-agent-chatbot\backend

# Install with uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .
```

### 5.2 Frontend Dependencies

```powershell
cd D:\Users\User\Documents\GitHub\siriform-agent-chatbot\frontend

# Install with npm
npm install
```

---

## Step 6: Start the Application

### 6.1 Start Backend Server

Open a terminal and run:

```powershell
cd D:\Users\User\Documents\GitHub\siriform-agent-chatbot\backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
✓ LangSmith tracing enabled for project: siriform-agent
INFO:     Started server process
INFO:     Application startup complete.
```

**Troubleshooting:**
- ❌ If you see "OpenRouter API key not found" → Check `OPENROUTER_API_KEY` in `.env`
- ⚠️ If you see "LangSmith API key not found - tracing disabled" → That's OK, app still works
- ⚠️ If you see "Supabase not configured" → That's OK, app works without database

### 6.2 Start Frontend Server

Open **another terminal** and run:

```powershell
cd D:\Users\User\Documents\GitHub\siriform-agent-chatbot\frontend
npm run dev
```

You should see:
```
VITE v7.1.9  ready in 451 ms
➜  Local:   http://localhost:5173/
```

---

## Step 7: Test the Application

### 7.1 Open in Browser

Open your browser and go to:
```
http://localhost:5173
```

### 7.2 Test Chat (Anonymous)

1. You should see the SiriForm Agent interface
2. Type a message in Thai: `ขอ laptop 2 เครื่อง สำหรับพรุ่งนี้`
3. Press Enter
4. The agent should respond and update the form on the right

### 7.3 View LangSmith Traces (if configured)

1. Go to https://smith.langchain.com/
2. Click your project name (`siriform-agent`)
3. You should see traces of your chat interactions
4. Click on a trace to see the full execution flow (like your screenshot!)

---

## Step 8: Verify Backend API

Test backend endpoints manually:

### 8.1 Health Check
```powershell
# PowerShell
Invoke-WebRequest -Uri http://localhost:8000/health | Select-Object -ExpandProperty Content
```

Expected output:
```json
{"status":"healthy","version":"0.1.0"}
```

### 8.2 Get Form Schema
```powershell
Invoke-WebRequest -Uri http://localhost:8000/api/v1/form-schema/equipment_form
```

### 8.3 Test Chat API
```powershell
$body = @{
    message = "ขอ laptop 2 เครื่อง"
    session_id = "test_123"
    form_data = @{}
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/api/v1/chat -Method POST -Body $body -ContentType "application/json"
```

---

## Configuration Checklist

Use this checklist to verify your setup:

### ✅ Required Configuration
- [ ] OpenRouter API Key configured in `.env`
- [ ] Backend `.env` file exists with correct values
- [ ] Frontend `.env` file exists
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed

### ⚙️ Optional Configuration
- [ ] LangSmith API Key configured (for tracing/debugging)
- [ ] LangSmith Project created
- [ ] Supabase Project created
- [ ] Supabase credentials configured
- [ ] Database schema executed (schema.sql)

### 🧪 Testing
- [ ] Backend server starts without errors
- [ ] Frontend server starts without errors
- [ ] Can access http://localhost:5173
- [ ] Can send chat messages and see responses
- [ ] Form updates when agent extracts data

---

## Common Issues & Solutions

### Issue 1: "OpenRouter API key not found"

**Cause:** Missing or invalid OpenRouter API key

**Solution:**
1. Check `.env` file has `OPENROUTER_API_KEY=sk-or-v1-...`
2. Verify the key is correct (copy-paste again from OpenRouter)
3. Restart backend server

### Issue 2: "LangSmith tracing disabled"

**Cause:** Missing LangSmith API key

**Solution:**
- This is just a warning - app works fine without it
- If you want tracing, add `LANGSMITH_API_KEY` to `.env`
- If not needed, you can ignore this warning

### Issue 3: Backend crashes with "Supabase error"

**Cause:** Invalid Supabase credentials

**Solution:**
- Remove Supabase credentials from `.env` to run without database
- Or fix the credentials by copying from Supabase dashboard

### Issue 4: "Cannot connect to backend" in frontend

**Cause:** Backend not running or wrong URL

**Solution:**
1. Check backend is running on port 8000
2. Check `frontend/.env` has `VITE_API_BASE_URL=http://localhost:8000`
3. Check browser console (F12) for error messages

### Issue 5: Agent gives generic error responses

**Cause:** OpenRouter API issue (insufficient credits, rate limit, etc.)

**Solution:**
1. Check OpenRouter dashboard: https://openrouter.ai/activity
2. Verify you have sufficient credits
3. Check if there are any API errors
4. Try a different model in `.env`: `OPENROUTER_MODEL=openai/gpt-3.5-turbo`

---

## Next Steps

After successful setup:

1. **Explore the UI**
   - Try different Thai phrases
   - Watch how the form fills automatically
   - Test the progress bar

2. **Check LangSmith Traces** (if configured)
   - See how the agent thinks
   - Debug any issues
   - Optimize prompts

3. **Test Authentication**
   - Register multiple users
   - Check user-specific data in Supabase

4. **Try Different Forms**
   - Meeting room booking: `/api/v1/form-schema/meeting_room_form`
   - Leave request: `/api/v1/form-schema/leave_request_form`

5. **Customize**
   - Create your own form schemas
   - Modify agent prompts
   - Add new features

---

## Support & Documentation

- **Main Documentation:** `backend/README.md`
- **Supabase Setup:** `backend/database/README.md`
- **Authentication:** `backend/JWT_AUTHENTICATION.md`
- **Multi-Schema:** `backend/MULTI_SCHEMA_TESTING.md`

---

## Summary

### Minimum Setup (to test basic functionality):
1. ✅ Get OpenRouter API Key
2. ✅ Create `.env` file with OpenRouter key
3. ✅ Install dependencies
4. ✅ Start both servers

### Full Setup (with observability and persistence):
1. ✅ OpenRouter API Key
2. ✅ LangSmith API Key (for observability)
3. ✅ Supabase Project (for chat history)
4. ✅ Run database migration (schema.sql)
5. ✅ Configure all environment variables
6. ✅ Test all features

---

**Ready to start? Begin with Step 1! 🚀**