# Research: User Management

**Feature**: 002-user-management
**Date**: 2025-11-29
**Status**: Complete

## Research Questions

### RQ-001: Password Hashing Strategy

**Question**: Which password hashing algorithm and library should we use?

**Options Considered**:
1. **passlib with bcrypt** - Industry standard, adaptive cost factor
2. **argon2-cffi** - Memory-hard, newer algorithm, winner of PHC
3. **hashlib (PBKDF2)** - Built-in, NIST approved

**Decision**: passlib with bcrypt

**Rationale**:
- bcrypt is battle-tested and widely adopted
- passlib provides a clean abstraction with automatic salt generation
- Adaptive cost factor allows increasing work over time
- Built-in verification prevents timing attacks
- Easy migration path if algorithm needs to change later
- Lower memory requirements than Argon2 (better for containers)

**Implementation Notes**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

---

### RQ-002: Session Management Approach

**Question**: How should user sessions be managed?

**Options Considered**:
1. **Server-side sessions in SQLite** - Simple, stateful, easy revocation
2. **JWT tokens** - Stateless, scalable, harder to revoke
3. **Redis-backed sessions** - Fast, scalable, adds dependency

**Decision**: Server-side sessions in SQLite

**Rationale**:
- Matches existing SQLite storage strategy
- Simple revocation (delete session row)
- No additional dependencies
- Session data can include user agent, IP for security
- Easy to implement logout-all-devices feature
- Performance adequate for target scale (10,000 users)
- Can migrate to Redis later if needed

**Implementation Notes**:
- Session ID: UUID v4 (cryptographically secure)
- Cookie: HttpOnly, Secure (in production), SameSite=Lax
- Expiry: 7 days default, sliding expiration on activity
- Store: session_id, user_id, created_at, expires_at, user_agent, ip_address

---

### RQ-003: Account Lockout Implementation

**Question**: How should account lockout after failed attempts work?

**Options Considered**:
1. **Progressive lockout with exponential backoff** - 5 attempts, then exponential wait
2. **Fixed lockout period** - Lock for 30 minutes after 5 attempts
3. **CAPTCHA after threshold** - Show CAPTCHA instead of locking

**Decision**: Progressive lockout with exponential backoff

**Rationale**:
- More user-friendly than fixed lockout
- Balances security with usability
- Discourages brute force without frustrating legitimate users
- No CAPTCHA dependency (keeps frontend simple)

**Implementation Notes**:
- Track failed attempts per email in database
- Lockout schedule:
  - 1-5 attempts: No delay
  - 6th attempt: 1 minute wait
  - 7th attempt: 5 minute wait
  - 8th attempt: 15 minute wait
  - 9th+ attempt: 30 minute wait
- Reset counter on successful login
- Store: email, attempt_count, last_attempt_at, locked_until
- Check lockout status before password verification

---

### RQ-004: Email Delivery for Password Reset

**Question**: How should password reset emails be sent?

**Options Considered**:
1. **SMTP with smtp.py** - Direct SMTP, no dependencies
2. **SendGrid/Mailgun API** - Managed service, reliable delivery
3. **Console logging (dev only)** - No actual email, just log the link

**Decision**: Pluggable email service with console fallback

**Rationale**:
- Development: Console logging for testing
- Production: SMTP or managed service configurable via environment
- Keeps core code simple with interface abstraction
- No hard dependency on external services
- Environment variable controls email backend

**Implementation Notes**:
```python
# Interface
class EmailService(Protocol):
    async def send_reset_email(self, to: str, reset_link: str) -> bool: ...

# Development implementation
class ConsoleEmailService:
    async def send_reset_email(self, to: str, reset_link: str) -> bool:
        print(f"Password reset for {to}: {reset_link}")
        return True

# Production implementation (optional)
class SMTPEmailService:
    async def send_reset_email(self, to: str, reset_link: str) -> bool:
        # Use aiosmtplib for async SMTP
        ...
```

Environment variables:
- `EMAIL_BACKEND`: "console" | "smtp"
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` (for SMTP)

---

### RQ-005: Reset Token Generation and Storage

**Question**: How should password reset tokens be generated and validated?

**Options Considered**:
1. **Random UUID stored in database** - Simple, explicit expiry
2. **JWT with embedded expiry** - Stateless, self-contained
3. **Signed timestamp token** - No storage, but harder to revoke

**Decision**: Random UUID stored in database

**Rationale**:
- Explicit revocation (delete token after use)
- Can invalidate all tokens for user if needed
- Simple implementation, consistent with session approach
- No JWT library needed just for reset tokens
- Clear audit trail in database

**Implementation Notes**:
- Token: UUID v4 (secrets.token_urlsafe(32))
- Store: token_hash (SHA256 of token), user_id, created_at, expires_at, used
- Hash token before storage (tokens are like passwords)
- Expiry: 24 hours
- Mark as used rather than delete (audit trail)
- Limit active tokens per user (invalidate old ones on new request)

---

### RQ-006: Display Name Validation

**Question**: What validation rules should apply to display names?

**Options Considered**:
1. **Minimal validation** - 1-100 chars, any printable
2. **Strict validation** - Alphanumeric, underscores only
3. **Moderate validation** - Block profanity, limit special chars

**Decision**: Minimal validation with length limits

**Rationale**:
- Simple implementation (YAGNI principle)
- Allow international characters
- No profanity filter (complex, locale-dependent)
- Admin can address issues manually if needed
- Display names don't need uniqueness

**Implementation Notes**:
- Length: 1-50 characters
- Strip leading/trailing whitespace
- Collapse multiple spaces to single
- Allow Unicode letters, numbers, spaces, common punctuation
- Reject control characters and zero-width chars

---

## Dependencies Identified

| Dependency | Version | Purpose |
|------------|---------|---------|
| passlib | 1.7.4+ | Password hashing |
| bcrypt | 4.0.0+ | bcrypt backend for passlib |
| python-jose | 3.3.0+ | Optional, for future JWT if needed |
| aiosmtplib | 2.0+ | Optional, for SMTP email |

## Security Considerations

1. **Password Storage**: Never store plaintext, use bcrypt with cost 12
2. **Session Cookies**: HttpOnly, Secure, SameSite=Lax
3. **Reset Tokens**: Hash before storage, single-use, short expiry
4. **Rate Limiting**: Account lockout prevents brute force
5. **Timing Attacks**: passlib handles constant-time comparison
6. **HTTPS**: Required in production for all auth endpoints

## Open Questions Resolved

- ✅ Password hashing: bcrypt via passlib
- ✅ Session storage: SQLite (same as other data)
- ✅ Lockout strategy: Exponential backoff
- ✅ Email delivery: Pluggable with console fallback
- ✅ Token storage: Database with hashing

## Next Steps

Proceed to Phase 1: Generate data model and API contracts.
