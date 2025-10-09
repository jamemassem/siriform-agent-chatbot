# JWT Authentication System

## Overview

The SiriForm Agent Chatbot now includes a complete JWT (JSON Web Token) based authentication system. This system allows users to:

- Register new accounts with email and username
- Login with username/email and password
- Securely access the chat interface with authentication
- Track user-specific form submissions and chat history in Supabase
- Use the system anonymously (authentication is optional)

## Architecture

### Backend Components

1. **Auth Module** (`backend/app/auth/`)
   - `security.py`: Password hashing (bcrypt) and JWT token generation/validation
   - `dependencies.py`: FastAPI dependencies for extracting user from JWT tokens
   - Supports both required (`get_current_user`) and optional (`get_optional_user`) authentication

2. **Auth Service** (`backend/app/services/auth_service.py`)
   - User registration with duplicate email/username checking
   - User login with password verification
   - User profile retrieval
   - Automatic last login timestamp updates

3. **Auth Router** (`backend/app/routers/auth.py`)
   - `POST /api/v1/auth/register`: Create new user account
   - `POST /api/v1/auth/login`: Authenticate and get JWT token
   - `GET /api/v1/auth/me`: Get current user profile (protected)
   - `POST /api/v1/auth/verify-token`: Verify JWT token validity

4. **Database Schema** (`backend/database/auth_schema.sql`)
   - `users` table with email, username, password_hash, full_name
   - Indexes on email and username for fast lookups
   - RLS (Row Level Security) policies
   - Helper functions: `get_user_by_email()`, `get_user_by_username()`, `update_user_last_login()`

### Frontend Components

1. **AuthContext** (`frontend/src/contexts/AuthContext.tsx`)
   - React context for managing authentication state
   - Stores JWT token and user info in localStorage
   - Provides `login()`, `register()`, `logout()` functions
   - `useAuth()` hook for accessing auth state

2. **Auth Components** (`frontend/src/components/Auth/`)
   - `LoginForm`: Email/username + password login
   - `RegisterForm`: Full registration form with validation
   - `AuthModal`: Modal dialog that switches between login/register
   - `UserMenu`: Dropdown menu showing user info and logout button

3. **Integration**
   - `App.tsx` wrapped in `<AuthProvider>`
   - Optional authentication: works with or without login
   - JWT token automatically sent with API requests when available
   - Header shows login button (anonymous) or user menu (authenticated)

## Database Setup

### 1. Run Authentication Schema

After setting up the base Supabase schema (`schema.sql`), run the authentication schema:

```sql
-- In Supabase SQL Editor, execute:
\i backend/database/auth_schema.sql
```

This creates:
- `users` table
- Foreign key relationships to `form_submissions`, `chat_history`, `user_sessions`
- Helper functions for user management

### 2. Update Existing Data (Optional)

If you have existing data, you may need to backfill `user_id` fields or allow NULL values temporarily.

## Configuration

### Environment Variables

Add to `.env`:

```bash
# JWT Authentication
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24
```

**Security Note:** Generate a secure secret key for production:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Backend Configuration

The `Settings` class in `backend/app/config.py` includes:

```python
JWT_SECRET_KEY: str = "your-secret-key-here-change-in-production"
JWT_ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS: int = 24
```

## API Usage

### Register New User

**Endpoint:** `POST /api/v1/auth/register`

**Request:**
```json
{
  "email": "user@example.com",
  "username": "john_doe",
  "password": "securePassword123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "username": "john_doe",
  "full_name": "John Doe",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### Login

**Endpoint:** `POST /api/v1/auth/login`

**Request:**
```json
{
  "username": "john_doe",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "username": "john_doe",
  "full_name": "John Doe",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### Get Current User Profile

**Endpoint:** `GET /api/v1/auth/me`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "username": "john_doe",
  "full_name": "John Doe",
  "created_at": "2024-01-01T00:00:00Z",
  "last_login_at": "2024-01-15T10:30:00Z"
}
```

### Use Chat Endpoint with Authentication

**Endpoint:** `POST /api/v1/chat`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
  "message": "ขอ laptop 2 เครื่อง",
  "session_id": "sess_123",
  "form_data": {}
}
```

When authenticated, the backend automatically:
1. Extracts user_id from JWT token
2. Saves chat messages with user_id
3. Associates form submissions with user_id
4. Tracks user activity

## Frontend Integration

### Using Auth Context

```tsx
import { useAuth } from './contexts/AuthContext';

function MyComponent() {
  const { user, token, login, logout, isAuthenticated } = useAuth();

  const handleLogin = async () => {
    try {
      await login('john_doe', 'password123');
      console.log('Login successful!');
    } catch (error) {
      console.error('Login failed:', error.message);
    }
  };

  return (
    <div>
      {isAuthenticated ? (
        <div>
          <p>Welcome, {user?.username}!</p>
          <button onClick={logout}>Logout</button>
        </div>
      ) : (
        <button onClick={handleLogin}>Login</button>
      )}
    </div>
  );
}
```

### Showing Auth Modal

```tsx
import { AuthModal } from './components/Auth';

function App() {
  const [showAuth, setShowAuth] = useState(false);

  return (
    <>
      <button onClick={() => setShowAuth(true)}>Login</button>
      <AuthModal
        isOpen={showAuth}
        onClose={() => setShowAuth(false)}
        initialMode="login"
      />
    </>
  );
}
```

### Making Authenticated API Calls

The `api.ts` service automatically includes the JWT token when available:

```typescript
import { useAuth } from './contexts/AuthContext';
import { sendChatMessage } from './services/api';

const { token } = useAuth();

const response = await sendChatMessage(
  { message: 'Hello', session_id: 'sess_123' },
  token  // Automatically adds Authorization header
);
```

## Security Features

### Password Security

- **Hashing:** bcrypt with automatic salt generation
- **Minimum Length:** 8 characters required
- **No Plain Text:** Passwords never stored in plain text

### Token Security

- **Algorithm:** HS256 (HMAC-SHA256)
- **Expiration:** 24 hours (configurable)
- **Payload:** Contains user_id, email, username
- **Validation:** Signature verified on every request

### API Security

- **Optional Authentication:** Chat endpoint works with or without auth
- **Protected Endpoints:** `/auth/me` requires valid token
- **Error Handling:** Returns 401 Unauthorized for invalid tokens
- **CORS:** Configured for allowed origins only

### Database Security

- **Row Level Security (RLS):** Enabled on users table
- **Policies:** Users can only view/update their own data
- **Foreign Keys:** Cascade delete on user removal
- **Constraints:** Email/username format validation

## Testing

### Manual Testing

1. **Start backend server:**
   ```bash
   cd backend
   .\.venv\Scripts\activate
   uvicorn app.main:app --reload
   ```

2. **Start frontend server:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test registration:**
   - Open http://localhost:5173
   - Click "เข้าสู่ระบบ"
   - Switch to "สมัครสมาชิก"
   - Fill form and register

4. **Test login:**
   - Use registered credentials
   - Verify user menu appears
   - Check token in localStorage

5. **Test chat with auth:**
   - Send a message
   - Check backend logs for "✓ Authenticated user"
   - Verify data saved with user_id in Supabase

### API Testing with cURL

**Register:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123",
    "full_name": "Test User"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

**Get Profile:**
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <your_token_here>"
```

**Chat with Auth:**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token_here>" \
  -d '{
    "message": "ขอ laptop 2 เครื่อง",
    "session_id": "sess_test_123",
    "form_data": {}
  }'
```

## User Flows

### Registration Flow

```
User clicks "เข้าสู่ระบบ"
  → Modal opens with Login form
  → User clicks "สมัครสมาชิก"
  → Register form appears
  → User fills: email, username, password, name
  → Submit → POST /api/v1/auth/register
  → Backend creates user in Supabase
  → Backend returns JWT token
  → Frontend stores token + user in localStorage
  → Modal closes
  → User menu appears in header
  → User can now chat with authentication
```

### Login Flow

```
User clicks "เข้าสู่ระบบ"
  → Modal opens with Login form
  → User enters username + password
  → Submit → POST /api/v1/auth/login
  → Backend verifies credentials
  → Backend returns JWT token
  → Frontend stores token + user in localStorage
  → Modal closes
  → User menu appears in header
```

### Logout Flow

```
User clicks avatar in header
  → Dropdown menu opens
  → User clicks "ออกจากระบบ"
  → Frontend removes token + user from localStorage
  → User menu disappears
  → "เข้าสู่ระบบ" button appears
  → User becomes anonymous (can still chat)
```

### Anonymous Usage Flow

```
User opens app (no login)
  → "เข้าสู่ระบบ" button visible
  → User can chat normally
  → Messages saved without user_id
  → All features work except:
    × Cannot retrieve personal history across sessions
    × Cannot view user profile
    × Data not associated with account
```

## Best Practices

### For Developers

1. **Always validate JWT_SECRET_KEY in production**
   - Never use default secret key
   - Rotate keys periodically
   - Store in secure environment variables

2. **Handle token expiration gracefully**
   - Frontend should detect 401 errors
   - Prompt re-login when token expires
   - Consider implementing refresh tokens for longer sessions

3. **Protect sensitive data**
   - Never log passwords or tokens
   - Use HTTPS in production
   - Implement rate limiting for auth endpoints

4. **Test authentication flows**
   - Unit tests for password hashing
   - Integration tests for login/register
   - E2E tests for full user flows

### For Users

1. **Use strong passwords**
   - Minimum 8 characters
   - Mix letters, numbers, symbols
   - Don't reuse passwords

2. **Logout on shared devices**
   - Always logout when done
   - Don't save passwords in browsers on public computers

3. **Keep credentials secure**
   - Don't share username/password
   - Report suspicious activity

## Troubleshooting

### "Could not validate credentials" Error

**Cause:** Invalid or expired JWT token

**Solution:**
- Logout and login again
- Check JWT_SECRET_KEY matches between token creation and validation
- Verify token hasn't expired (check `exp` claim)

### "Email already registered" Error

**Cause:** Attempting to register with existing email

**Solution:**
- Use login instead
- Use different email address
- Reset password if forgotten

### "Invalid username or password" Error

**Cause:** Incorrect credentials

**Solution:**
- Verify username/password
- Check caps lock
- Username can be either username or email

### User_id Not Saved in Database

**Cause:** JWT token not sent with request

**Solution:**
- Verify `Authorization: Bearer <token>` header present
- Check token stored in localStorage
- Verify `sendChatMessage()` receives token parameter

### Frontend Not Showing User Menu

**Cause:** Auth state not loading

**Solution:**
- Check browser console for errors
- Verify localStorage has `siriform_auth_token` and `siriform_user`
- Refresh page to reload auth state

## Future Enhancements

Potential improvements for the authentication system:

1. **Email Verification**
   - Send confirmation email on registration
   - Verify email before allowing full access

2. **Password Reset**
   - Forgot password flow
   - Email-based password reset links

3. **Refresh Tokens**
   - Longer-lived sessions
   - Automatic token renewal

4. **OAuth Integration**
   - Login with Google/GitHub/Microsoft
   - Social authentication options

5. **Two-Factor Authentication (2FA)**
   - TOTP-based 2FA
   - SMS verification

6. **Account Management**
   - Change password
   - Update profile
   - Delete account

7. **Admin Panel**
   - User management
   - Role-based access control (RBAC)
   - Usage analytics

## References

- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT.io](https://jwt.io/)
- [Supabase Auth](https://supabase.com/docs/guides/auth)
- [React Context](https://react.dev/reference/react/useContext)
- [bcrypt](https://github.com/pyca/bcrypt/)

---

**Last Updated:** October 2025
**Version:** 1.0.0
**Author:** SiriForm Team
