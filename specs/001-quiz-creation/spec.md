# Feature Specification: Quiz Creation

**Feature Branch**: `001-quiz-creation`
**Created**: 2025-11-29
**Status**: Draft
**Input**: User description: "Allow users to create and manage quizzes"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create a Basic Quiz (Priority: P1)

As a quiz creator, I want to create a new quiz with a title and questions so that I can
share knowledge assessments with others.

The creator enters a quiz title, adds one or more questions with answer choices, marks correct
answers, and saves the quiz. Upon saving, the quiz is stored and can be retrieved later.

**Why this priority**: This is the core functionality—without quiz creation, the entire feature
has no value. It delivers the minimum viable product: a saved quiz that can be accessed.

**Independent Test**: Can be fully tested by creating a quiz with 3 questions, saving it, and
verifying it appears in the quiz list with all questions intact.

**Acceptance Scenarios**:

1. **Given** a logged-in user on the quiz creation page, **When** they enter a title "Python Basics", add 2 multiple-choice questions with 4 options each, mark correct answers, and click Save, **Then** the quiz is saved and appears in their quiz list.

2. **Given** a user creating a quiz, **When** they attempt to save without a title, **Then** the system displays a validation error and prevents saving.

3. **Given** a user creating a quiz, **When** they attempt to save with zero questions, **Then** the system displays a validation error requiring at least one question.

---

### User Story 2 - Edit an Existing Quiz (Priority: P2)

As a quiz creator, I want to edit my existing quizzes so that I can fix mistakes or update
content over time.

The creator selects an existing quiz from their list, modifies any field (title, questions,
answers), and saves the changes. The updated quiz replaces the previous version.

**Why this priority**: Editing is essential for maintaining quiz quality, but users can work
around its absence by recreating quizzes. It builds on P1's foundation.

**Independent Test**: Can be tested by creating a quiz, editing its title and one question,
saving, and verifying changes persist.

**Acceptance Scenarios**:

1. **Given** a quiz creator viewing their quiz list, **When** they select a quiz and click Edit, **Then** the quiz opens in edit mode with all existing content pre-filled.

2. **Given** a user editing a quiz, **When** they change the title from "Python Basics" to "Python Fundamentals" and save, **Then** the quiz list shows the updated title.

3. **Given** a user editing a quiz, **When** they add a new question and remove an existing one, **Then** the changes are reflected when the quiz is viewed again.

---

### User Story 3 - Delete a Quiz (Priority: P3)

As a quiz creator, I want to delete quizzes I no longer need so that my quiz list stays
organized and relevant.

The creator selects a quiz and confirms deletion. The quiz is permanently removed and no
longer appears in any listings.

**Why this priority**: Deletion is a housekeeping feature. Users can manage without it
initially, and it has the lowest urgency compared to creation and editing.

**Independent Test**: Can be tested by creating a quiz, deleting it, and verifying it no
longer appears in the quiz list.

**Acceptance Scenarios**:

1. **Given** a quiz creator viewing their quiz list, **When** they click Delete on a quiz and confirm the action, **Then** the quiz is removed from the list.

2. **Given** a user attempting to delete a quiz, **When** the confirmation dialog appears and they cancel, **Then** the quiz remains in the list unchanged.

---

### Edge Cases

- What happens when a user tries to create a quiz with a title that already exists?
  - System allows duplicate titles (quizzes are identified by unique internal ID, not title)
- What happens when a user adds a question with no correct answer marked?
  - System requires exactly one correct answer per question before saving
- What happens when a user's session expires while editing a quiz?
  - System warns user and prompts re-authentication; unsaved changes may be lost
- What happens when a quiz has the maximum allowed questions?
  - System prevents adding more and displays a message indicating the limit (default: 100 questions)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow authenticated users to create new quizzes with a title
- **FR-002**: System MUST allow users to add multiple-choice questions to a quiz
- **FR-003**: System MUST require each question to have 2-6 answer options
- **FR-004**: System MUST require exactly one answer to be marked as correct per question
- **FR-005**: System MUST validate that quiz titles are between 1 and 200 characters
- **FR-006**: System MUST validate that question text is between 1 and 1000 characters
- **FR-007**: System MUST validate that answer text is between 1 and 500 characters
- **FR-008**: System MUST persist quizzes so they survive system restarts
- **FR-009**: System MUST allow quiz creators to edit their own quizzes
- **FR-010**: System MUST allow quiz creators to delete their own quizzes
- **FR-011**: System MUST require confirmation before deleting a quiz
- **FR-012**: System MUST display a list of quizzes owned by the current user
- **FR-013**: System MUST enforce that only the quiz owner can edit or delete their quiz
- **FR-014**: System MUST support a maximum of 100 questions per quiz

### Key Entities

- **Quiz**: A collection of questions with a title, created by a specific user. Has a unique
  identifier, creation timestamp, and last-modified timestamp.
- **Question**: A prompt with multiple answer choices belonging to a quiz. Contains question
  text, display order within the quiz, and references to its answer options.
- **Answer Option**: A possible response to a question. Contains answer text and a flag
  indicating whether it is the correct answer.
- **User**: The creator/owner of quizzes. Identified by unique ID (authentication details
  handled by separate user management feature).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a complete quiz (title + 5 questions) in under 5 minutes
- **SC-002**: 95% of quiz save operations complete successfully on first attempt
- **SC-003**: Users can locate and open any of their quizzes within 10 seconds
- **SC-004**: Quiz data persists correctly with zero data loss across system restarts
- **SC-005**: 90% of users successfully create their first quiz without requiring help documentation

## Assumptions

- User authentication exists or will be implemented separately (this feature assumes a logged-in user context)
- Only multiple-choice questions are supported in this initial version (no open-ended, matching, or other question types)
- Quizzes are private to their creator by default (sharing/publishing is a separate feature)
- No rich text formatting in questions or answers (plain text only)
- No image or media attachments in questions (text-only)
- No time limits or quiz settings beyond questions (scheduling, time limits, etc. are separate features)
