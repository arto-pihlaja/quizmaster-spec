# Quickstart: User Management Feature

**Feature**: 002-user-management
**Date**: 2025-11-29

## Prerequisites

- Python 3.11+ installed
- QuizMaster backend running
- SQLite database initialized

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Required packages:
- fastapi
- uvicorn
- sqlalchemy
- jinja2
- passlib[bcrypt]
- python-jose
- pytest
- pytest-asyncio
- httpx

### 2. Database Migration

Run the migration to add authentication tables:

```bash
# If using Alembic
alembic upgrade head

# Or run the migration script directly
python -m src.db.migrations.add_auth_tables
```

This creates:
- `users` table
- `sessions` table
- `login_attempts` table
- `password_resets` table

### 3. Verify Tables

```bash
sqlite3 quizmaster.db ".schema users"
sqlite3 quizmaster.db ".schema sessions"
sqlite3 quizmaster.db ".schema login_attempts"
sqlite3 quizmaster.db ".schema password_resets"
```

### 4. Configure Email (Optional)

For password reset functionality in development, console logging is used by default.

For production SMTP:
```bash
export EMAIL_BACKEND=smtp
export SMTP_HOST=smtp.example.com
export SMTP_PORT=587
export SMTP_USER=your-user
export SMTP_PASSWORD=your-password
```

## Running the Feature

### Start the Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Access Auth Features

- **Login**: http://localhost:8000/login
- **Register**: http://localhost:8000/register
- **Forgot Password**: http://localhost:8000/forgot-password
- **Profile**: http://localhost:8000/profile

## Verification Steps

### User Story 1: Register a New Account (P1)

1. Navigate to http://localhost:8000/register
2. Enter email: "test@example.com"
3. Enter password: "securepass123"
4. Enter display name: "TestUser"
5. Click "Register"
6. Verify: Redirected to home page or profile
7. Verify: Session cookie is set

```bash
# API test - Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "email": "test@example.com",
    "password": "securepass123",
    "display_name": "TestUser"
  }'
```

Expected: 201 response with user data and session cookie.

### User Story 2: Log In (P1)

1. Navigate to http://localhost:8000/login
2. Enter email: "test@example.com"
3. Enter password: "securepass123"
4. Click "Log In"
5. Verify: Redirected to home page
6. Verify: Session cookie is set

```bash
# API test - Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "email": "test@example.com",
    "password": "securepass123"
  }'
```

Expected: 200 response with user data.

### User Story 3: Log Out (P2)

1. While logged in, click "Log Out"
2. Verify: Session cookie is cleared
3. Verify: Redirected to login page
4. Verify: Protected pages redirect to login

```bash
# API test - Logout
curl -X POST http://localhost:8000/auth/logout \
  -b cookies.txt \
  -c cookies.txt
```

Expected: 200 response, session cookie cleared.

### User Story 4: Reset Forgotten Password (P2)

1. Navigate to http://localhost:8000/forgot-password
2. Enter email: "test@example.com"
3. Click "Send Reset Link"
4. Verify: Success message shown (regardless of email existence)
5. Check console/email for reset link
6. Click reset link
7. Enter new password: "newpassword456"
8. Click "Reset Password"
9. Verify: Success message, can log in with new password

```bash
# API test - Request reset
curl -X POST http://localhost:8000/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# Check console for token, then:
curl -X POST http://localhost:8000/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "token": "TOKEN_FROM_CONSOLE",
    "new_password": "newpassword456"
  }'
```

### User Story 5: Update Profile (P3)

1. Log in and navigate to http://localhost:8000/profile
2. Verify: Current display name shown
3. Change display name to "UpdatedName"
4. Click "Save"
5. Verify: Success message
6. Verify: Scoreboard shows new name

```bash
# API test - Update profile
curl -X PUT http://localhost:8000/profile \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"display_name": "UpdatedName"}'
```

Expected: 200 response with updated user data.

### Account Lockout Test

```bash
# Attempt login with wrong password 6+ times
for i in {1..6}; do
  curl -X POST http://localhost:8000/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com", "password": "wrongpass"}'
done

# 6th attempt should return 429 with lockout info
```

### Validation Tests

```bash
# Test: Password too short
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "short", "display_name": "Test"}'
# Expected: 400 error - password min 8 characters

# Test: Invalid email format
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "notanemail", "password": "securepass123", "display_name": "Test"}'
# Expected: 400 error - invalid email

# Test: Display name too long
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "securepass123", "display_name": "ThisNameIsWayTooLongAndShouldFailValidationBecauseItExceedsFiftyCharacters"}'
# Expected: 400 error - display_name max 50 characters

# Test: Duplicate email
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "securepass123", "display_name": "Test"}'
# Expected: 409 error - email already registered
```

## API Quick Reference

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/auth/register` | POST | No | Register new user |
| `/auth/login` | POST | No | Log in |
| `/auth/logout` | POST | Yes | Log out |
| `/auth/forgot-password` | POST | No | Request reset email |
| `/auth/reset-password` | POST | No | Set new password |
| `/auth/me` | GET | Yes | Get current user |
| `/profile` | GET | Yes | HTML profile page |
| `/profile` | PUT | Yes | Update profile |
| `/login` | GET | No | HTML login page |
| `/register` | GET | No | HTML register page |
| `/forgot-password` | GET | No | HTML forgot password page |
| `/reset-password` | GET | No | HTML reset password page |

## Common Issues

### "Invalid credentials"

- Check email/password are correct
- Email is case-insensitive
- Account may be locked (check for 429 response)

### "Account locked"

- Wait for lockout period to expire (shown in response)
- Lockout increases exponentially with failed attempts

### "Email already registered"

- Use a different email
- Use forgot-password to recover existing account

### "Token expired or invalid"

- Reset tokens expire after 24 hours
- Tokens are single-use
- Request a new reset link

### Session expired

- Sessions expire after 7 days of inactivity
- Log in again to create new session

## Test Commands

```bash
# Run all auth tests
pytest backend/tests -k auth -v

# Run contract tests only
pytest backend/tests/contract/test_auth_api.py -v

# Run unit tests only
pytest backend/tests/unit/test_auth_service.py -v
pytest backend/tests/unit/test_password.py -v

# Run with coverage
pytest backend/tests -k auth --cov=src.services.auth --cov=src.security
```

## Security Notes

- Passwords are hashed with bcrypt (never stored plain)
- Session tokens are HttpOnly cookies (not accessible via JS)
- Reset tokens are hashed in database
- Same error message for wrong email vs wrong password (prevents enumeration)
- Account lockout prevents brute force attacks

## Next Steps

After verifying user management works:

1. Run `/speckit.tasks` to generate implementation tasks
2. Implement tests first (TDD per constitution)
3. Build P1 stories (register/login), verify, then P2 (logout/reset), then P3 (profile)
4. Proceed to dependent features (Admin Roles uses is_admin flag)
