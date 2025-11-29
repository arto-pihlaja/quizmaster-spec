# Feature Specification: User Management

**Feature Branch**: `002-user-management`
**Created**: 2025-11-29
**Status**: Draft
**Input**: User description: "User registration, authentication, and profile management"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Register a New Account (Priority: P1)

As a new visitor, I want to create an account so that I can access QuizMaster features and
have my quizzes associated with my identity.

The visitor provides their email address, chooses a password, and submits the registration
form. Upon successful registration, they receive a confirmation and can immediately log in.

**Why this priority**: Registration is the gateway to all authenticated features. Without it,
users cannot create or manage quizzes. This is the foundational user journey.

**Independent Test**: Can be fully tested by registering with a valid email and password,
then verifying the account exists and can be used to log in.

**Acceptance Scenarios**:

1. **Given** a visitor on the registration page, **When** they enter a valid email "user@example.com" and a password meeting requirements, **Then** an account is created and they see a success message.

2. **Given** a visitor attempting to register, **When** they enter an email already associated with an account, **Then** the system displays an error indicating the email is taken.

3. **Given** a visitor attempting to register, **When** they enter a password that does not meet requirements, **Then** the system displays specific feedback about what is missing.

4. **Given** a visitor attempting to register, **When** they enter an invalid email format, **Then** the system displays a validation error before submission.

---

### User Story 2 - Log In to Existing Account (Priority: P1)

As a registered user, I want to log in to my account so that I can access my quizzes and
personal data.

The user enters their email and password on the login page. If credentials are valid, they
are authenticated and redirected to their dashboard.

**Why this priority**: Login is equally critical as registration—users must authenticate to
use core features. Both P1 stories are required for a functional MVP.

**Independent Test**: Can be tested by logging in with valid credentials and verifying
access to authenticated pages.

**Acceptance Scenarios**:

1. **Given** a registered user on the login page, **When** they enter correct email and password, **Then** they are logged in and redirected to their dashboard.

2. **Given** a user attempting to log in, **When** they enter an incorrect password, **Then** the system displays a generic "invalid credentials" error (not revealing which field is wrong).

3. **Given** a user attempting to log in, **When** they enter an email not associated with any account, **Then** the system displays the same generic "invalid credentials" error.

4. **Given** a logged-in user, **When** they navigate to the login page, **Then** they are redirected to their dashboard.

---

### User Story 3 - Log Out (Priority: P2)

As a logged-in user, I want to log out so that I can secure my account when using shared
devices or ending my session.

The user clicks a logout option, their session is terminated, and they are returned to
a public page.

**Why this priority**: Logout is essential for security but is a single-action flow.
Users technically have workarounds (closing browser, clearing cookies).

**Independent Test**: Can be tested by logging in, clicking logout, and verifying that
authenticated pages are no longer accessible.

**Acceptance Scenarios**:

1. **Given** a logged-in user, **When** they click the logout button, **Then** their session ends and they are redirected to the home page.

2. **Given** a user who just logged out, **When** they attempt to access an authenticated page, **Then** they are redirected to the login page.

---

### User Story 4 - Reset Forgotten Password (Priority: P2)

As a user who forgot their password, I want to reset it so that I can regain access to
my account.

The user requests a password reset by providing their email. They receive a reset link,
click it, and set a new password.

**Why this priority**: Password reset is critical for account recovery but is not needed
for initial use. Users who remember passwords can function without it.

**Independent Test**: Can be tested by requesting a reset, using the link, setting a new
password, and logging in with the new password.

**Acceptance Scenarios**:

1. **Given** a user on the forgot password page, **When** they enter their registered email, **Then** they see a confirmation message (regardless of whether email exists, for security).

2. **Given** a user who received a reset link, **When** they click it within the validity period, **Then** they can set a new password.

3. **Given** a user with a reset link, **When** they click it after it has expired, **Then** they see a message indicating the link is no longer valid.

4. **Given** a user who has reset their password, **When** they try to use the old password, **Then** authentication fails.

---

### User Story 5 - View and Edit Profile (Priority: P3)

As a registered user, I want to view and update my profile information so that I can
keep my account details current.

The user accesses their profile page, views their current information, makes changes,
and saves updates.

**Why this priority**: Profile management is a convenience feature. Users can function
with their initial registration details; updates are not urgent for core functionality.

**Independent Test**: Can be tested by viewing profile, changing display name, saving,
and verifying the change persists.

**Acceptance Scenarios**:

1. **Given** a logged-in user on their profile page, **When** they view the page, **Then** they see their email and display name.

2. **Given** a user editing their profile, **When** they change their display name and save, **Then** the new name is shown throughout the application.

3. **Given** a user editing their profile, **When** they attempt to save an empty display name, **Then** the system shows a validation error.

---

### Edge Cases

- What happens when a user tries to register with an email containing uppercase letters?
  - System normalizes email to lowercase; "User@Example.COM" and "user@example.com" are the same account
- What happens when a user's session expires while they are active?
  - System prompts re-authentication on next action; unsaved work may be lost
- What happens when a user requests multiple password reset links?
  - Each new request invalidates previous links; only the most recent link works
- What happens when a user tries to log in with excessive failed attempts?
  - After 5 failed attempts, account is temporarily locked for 15 minutes (brute force protection)
- What happens when a user tries to change their email address?
  - Email changes require verification of the new email before taking effect

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow visitors to register with email and password
- **FR-002**: System MUST validate email format before accepting registration
- **FR-003**: System MUST require passwords to be at least 8 characters with one uppercase, one lowercase, and one number
- **FR-004**: System MUST prevent duplicate registrations with the same email (case-insensitive)
- **FR-005**: System MUST allow registered users to log in with email and password
- **FR-006**: System MUST create a session upon successful authentication
- **FR-007**: System MUST allow users to log out, terminating their session
- **FR-008**: System MUST provide password reset functionality via email
- **FR-009**: System MUST expire password reset links after 24 hours
- **FR-010**: System MUST invalidate previous reset links when a new one is requested
- **FR-011**: System MUST allow users to view their profile information
- **FR-012**: System MUST allow users to update their display name
- **FR-013**: System MUST require display names to be 1-50 characters
- **FR-014**: System MUST implement account lockout after 5 failed login attempts (15-minute lockout)
- **FR-015**: System MUST use generic error messages for login failures (not revealing account existence)
- **FR-016**: System MUST protect authenticated routes from unauthenticated access

### Key Entities

- **User**: A registered account holder. Has email (unique, normalized to lowercase), hashed password,
  display name, creation timestamp, and last login timestamp.
- **Session**: An authenticated state for a user. Has unique identifier, user reference, creation time,
  expiration time, and active/revoked status.
- **Password Reset Token**: A time-limited credential for password recovery. Has unique token value,
  user reference, creation time, expiration time, and used/unused status.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete registration in under 2 minutes
- **SC-002**: Users can log in within 10 seconds of entering credentials
- **SC-003**: 95% of password reset emails are delivered within 5 minutes
- **SC-004**: Zero unauthorized access to authenticated resources
- **SC-005**: 90% of users successfully complete registration on first attempt
- **SC-006**: Account lockout reduces brute force attack success rate by 99%

## Assumptions

- Email delivery infrastructure exists or will be provided (SMTP/email service)
- Only email/password authentication is supported initially (no social login, SSO, or MFA)
- Sessions expire after a reasonable period of inactivity (default: 7 days)
- Display name is the only editable profile field initially (no avatar, bio, etc.)
- Email address changes are not supported in this initial version (can be added later)
- Users must be logged in to create quizzes (ties into Quiz Creation feature)
