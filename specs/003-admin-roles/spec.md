# Feature Specification: Admin Roles

**Feature Branch**: `003-admin-roles`
**Created**: 2025-11-29
**Status**: Draft
**Input**: User description: "Admins. The first person to register becomes admin. Admin can appoint other admins. Admin can edit questions and correct answers as well as assign points per question. The number of points per question can vary."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - First User Becomes Admin (Priority: P1)

As the first person to register on QuizMaster, I automatically become an admin so that
there is always someone who can manage the system from the start.

When the very first user completes registration, they are automatically granted admin
privileges. This happens silently—they simply have admin capabilities available immediately.

**Why this priority**: Without an initial admin, no one can perform administrative tasks.
This bootstrapping mechanism is essential for the system to function.

**Independent Test**: Can be tested by registering on a fresh system with no existing users
and verifying admin capabilities are immediately available.

**Acceptance Scenarios**:

1. **Given** an empty system with no registered users, **When** the first user completes registration, **Then** they are automatically granted admin role.

2. **Given** a system where the first user has already registered, **When** subsequent users register, **Then** they receive standard (non-admin) roles.

3. **Given** the first registered user, **When** they access the system, **Then** they see admin-specific options and controls.

---

### User Story 2 - Appoint Another Admin (Priority: P1)

As an admin, I want to appoint other registered users as admins so that administrative
responsibilities can be shared and the system is not dependent on a single person.

The admin navigates to user management, selects a registered user, and grants them admin
privileges. The new admin immediately gains all admin capabilities.

**Why this priority**: Admin delegation is critical for operational continuity. If only one
admin exists and they become unavailable, the system cannot be managed.

**Independent Test**: Can be tested by having an admin promote a regular user and verifying
the promoted user can perform admin actions.

**Acceptance Scenarios**:

1. **Given** an admin viewing the user list, **When** they select a non-admin user and click "Make Admin", **Then** that user becomes an admin.

2. **Given** a newly appointed admin, **When** they log in, **Then** they see all admin options and controls.

3. **Given** an admin attempting to promote a user, **When** that user is already an admin, **Then** the system indicates they are already an admin (no error, just information).

---

### User Story 3 - Edit Quiz Questions (Priority: P2)

As an admin, I want to edit any quiz question so that I can correct mistakes, improve
clarity, or update content regardless of who created the quiz.

The admin can access any quiz in the system, select a question, modify its text, and save
the changes. The original quiz creator does not need to be involved.

**Why this priority**: Content quality control requires admins to fix issues across all
quizzes. This builds on admin role foundation from P1 stories.

**Independent Test**: Can be tested by having an admin edit a question in a quiz created
by another user and verifying the change persists.

**Acceptance Scenarios**:

1. **Given** an admin viewing any quiz, **When** they click edit on a question, **Then** they can modify the question text.

2. **Given** an admin editing a question, **When** they save changes, **Then** the updated question text is displayed to all users.

3. **Given** a non-admin user, **When** they view a quiz they did not create, **Then** they cannot edit its questions.

---

### User Story 4 - Edit Answer Options and Correct Answer (Priority: P2)

As an admin, I want to edit answer options and change which answer is marked correct so
that I can fix errors in quiz answers.

The admin can modify answer option text and reassign which option is the correct answer
for any question in any quiz.

**Why this priority**: Answer accuracy is as important as question accuracy. Both editing
capabilities are needed for complete content control.

**Independent Test**: Can be tested by having an admin change answer text and correct
answer marking, then verifying changes persist.

**Acceptance Scenarios**:

1. **Given** an admin editing a question, **When** they modify an answer option's text, **Then** the change is saved and visible.

2. **Given** an admin editing a question with 4 options where option A is correct, **When** they mark option C as correct instead, **Then** option C becomes the new correct answer.

3. **Given** a question with a corrected answer, **When** users take the quiz, **Then** scoring uses the updated correct answer.

---

### User Story 5 - Assign Points Per Question (Priority: P2)

As an admin, I want to assign a specific point value to each question so that harder or
more important questions can be worth more points.

The admin sets a point value for each question. Different questions in the same quiz can
have different point values. The total quiz score is calculated by summing points for
correct answers.

**Why this priority**: Variable scoring adds educational value by weighting questions
appropriately. Depends on having edit access to questions (P2 stories).

**Independent Test**: Can be tested by setting different point values for questions in
a quiz and verifying the score calculation reflects those values.

**Acceptance Scenarios**:

1. **Given** an admin editing a question, **When** they set the point value to 5, **Then** that question is worth 5 points.

2. **Given** a quiz with questions worth 1, 2, and 5 points, **When** a user answers all correctly, **Then** their score is 8 points.

3. **Given** a quiz with questions worth 1, 2, and 5 points, **When** a user answers only the 5-point question correctly, **Then** their score is 5 points.

4. **Given** an admin creating a new question, **When** they do not specify points, **Then** the question defaults to 1 point.

---

### User Story 6 - Revoke Admin Privileges (Priority: P3)

As an admin, I want to revoke admin privileges from another admin so that access can be
managed when someone should no longer have administrative capabilities.

The admin selects another admin user and removes their admin status. The demoted user
retains their regular account but loses admin capabilities.

**Why this priority**: Admin management is important for security but less urgent than
establishing the admin system. Can function initially without revocation.

**Independent Test**: Can be tested by having an admin demote another admin and verifying
the demoted user can no longer access admin functions.

**Acceptance Scenarios**:

1. **Given** an admin viewing another admin's profile, **When** they click "Remove Admin", **Then** that user loses admin privileges.

2. **Given** a demoted admin, **When** they log in, **Then** they no longer see admin options.

3. **Given** the only remaining admin, **When** they attempt to revoke their own admin status, **Then** the system prevents this action with a warning.

---

### Edge Cases

- What happens if the first registered user is deleted?
  - The system must always have at least one admin. If the sole admin is deleted, the next oldest user is automatically promoted.
- What happens when an admin tries to edit a quiz while the creator is also editing?
  - Last-save-wins approach; both users can save, but the most recent save takes precedence.
- What happens if an admin assigns zero or negative points to a question?
  - System requires point values to be at least 1 (positive integers only).
- What happens to quizzes when their creator loses admin status?
  - Quiz ownership is unchanged; the creator remains the owner. Only their admin privileges change.
- What happens when all admins try to remove each other simultaneously?
  - System prevents removal if it would result in zero admins. At least one admin must always exist.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST automatically grant admin role to the first registered user
- **FR-002**: System MUST allow admins to grant admin privileges to any registered user
- **FR-003**: System MUST allow admins to revoke admin privileges from other admins
- **FR-004**: System MUST prevent the last remaining admin from losing admin status
- **FR-005**: System MUST allow admins to edit any question text in any quiz
- **FR-006**: System MUST allow admins to edit any answer option text in any quiz
- **FR-007**: System MUST allow admins to change which answer is marked correct
- **FR-008**: System MUST allow admins to set point values per question (1-100 points)
- **FR-009**: System MUST default new questions to 1 point if no value is specified
- **FR-010**: System MUST calculate quiz scores by summing points for correct answers
- **FR-011**: System MUST restrict admin functions to users with admin role only
- **FR-012**: System MUST display admin controls only to admin users
- **FR-013**: System MUST maintain an audit trail of admin actions (who changed what, when)

### Key Entities

- **User Role**: Extends the User entity with a role attribute. Values: "admin" or "user".
  First registered user gets "admin"; all subsequent registrations get "user" by default.
- **Question Points**: Extends the Question entity with a points attribute. Integer value
  from 1-100, defaulting to 1. Used in score calculation.
- **Admin Action Log**: Records administrative actions. Contains admin user reference,
  action type (grant-admin, revoke-admin, edit-question, edit-answer, set-points),
  target reference, timestamp, and before/after values where applicable.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: First user registration results in admin role 100% of the time on fresh systems
- **SC-002**: Admins can promote a user to admin in under 30 seconds
- **SC-003**: Admins can edit any question and save changes in under 1 minute
- **SC-004**: Quiz scores accurately reflect point values 100% of the time
- **SC-005**: Zero unauthorized access to admin functions by non-admin users
- **SC-006**: System maintains at least one admin at all times (never zero admins)

## Assumptions

- User Management feature (002) is implemented—users can register and log in
- Quiz Creation feature (001) is implemented—quizzes with questions exist
- Admin role is binary (admin or not)—no intermediate privilege levels
- All admins have equal privileges—no hierarchy among admins
- Admin actions are logged but not reversible through the UI (manual database intervention required for rollback)
- Point values are whole numbers only (no fractional points)
- Quiz taking and scoring depend on this feature for point calculation
