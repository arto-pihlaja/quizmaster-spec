# Feature Specification: Quiz Taking

**Feature Branch**: `005-quiz-taking`
**Created**: 2025-11-29
**Status**: Draft
**Input**: User description: "User answers. User selects and starts a quiz. Questions and answer options are available. While the user is taking the quiz, he can change answers. The page does not show whether answers are correct. Only once the user submits the quiz, the answers are frozen, the answers are saved to a table per quiz and user, the score is calculated and becomes available on the scoreboard."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Start and Complete a Quiz (Priority: P1)

As a logged-in user, I want to select a quiz, answer all questions, and submit my answers
so that I can test my knowledge and receive a score.

The user browses available quizzes, selects one to take, sees all questions with answer
options, selects answers for each question, and submits the quiz. After submission, the
system calculates their score and saves their attempt.

**Why this priority**: This is the core functionality—without completing a quiz and receiving
a score, the entire quiz-taking feature has no value.

**Independent Test**: Can be tested by selecting a quiz, answering all questions, submitting,
and verifying the score is calculated and saved.

**Acceptance Scenarios**:

1. **Given** a logged-in user viewing the quiz list, **When** they click "Start Quiz" on a quiz, **Then** they see the quiz with all questions and answer options.

2. **Given** a user taking a quiz, **When** they select an answer for each question and click Submit, **Then** their answers are saved, score is calculated, and they see their result.

3. **Given** a user who just submitted a quiz, **When** they view the scoreboard, **Then** their new score is reflected in their total.

4. **Given** a user taking a quiz, **When** they view any question, **Then** the correct answer is NOT visually indicated.

---

### User Story 2 - Change Answers Before Submission (Priority: P1)

As a user taking a quiz, I want to change my answers before submitting so that I can
reconsider my choices without penalty.

While the quiz is in progress (not yet submitted), the user can freely change their
selected answer for any question. Changes are tracked locally until submission.

**Why this priority**: Answer flexibility is essential for a fair quiz experience and
is tightly coupled with the core quiz-taking flow.

**Independent Test**: Can be tested by selecting an answer, changing it multiple times,
then submitting and verifying only the final selection is recorded.

**Acceptance Scenarios**:

1. **Given** a user taking a quiz who selected option A for question 1, **When** they click option B instead, **Then** option B becomes the selected answer for that question.

2. **Given** a user who has answered all questions, **When** they go back to a previous question and change their answer, **Then** the new answer replaces the old one.

3. **Given** a user taking a quiz, **When** they have not yet clicked Submit, **Then** they can change any answer as many times as they want.

---

### User Story 3 - View Quiz Results After Submission (Priority: P2)

As a user who completed a quiz, I want to see my results immediately after submission
so that I know how well I performed.

After submitting, the user sees a results page showing their score, which questions they
got right/wrong, and the correct answers.

**Why this priority**: Result feedback enhances the learning experience but the core
scoring works without detailed review. Can be added after basic submission works.

**Independent Test**: Can be tested by submitting a quiz and verifying the results page
shows score and per-question feedback.

**Acceptance Scenarios**:

1. **Given** a user who just submitted a quiz, **When** the results page loads, **Then** they see their total score (points earned / points possible).

2. **Given** a user viewing their results, **When** they look at each question, **Then** they see which answer they selected, whether it was correct, and what the correct answer was.

3. **Given** a user viewing their results, **When** they answered incorrectly, **Then** their wrong answer is visually distinguished from the correct answer.

---

### User Story 4 - Browse Available Quizzes (Priority: P2)

As a logged-in user, I want to browse all available quizzes so that I can choose which
one to take.

The user sees a list of all quizzes in the system (not just their own), with basic
information to help them decide which to attempt.

**Why this priority**: Quiz discovery is needed before taking a quiz, but could use a
simple list initially. Richer browsing can be enhanced later.

**Independent Test**: Can be tested by viewing the quiz list and verifying quizzes from
multiple creators are visible.

**Acceptance Scenarios**:

1. **Given** a logged-in user, **When** they navigate to the quiz browser, **Then** they see a list of all available quizzes.

2. **Given** the quiz browser, **When** viewing a quiz entry, **Then** they see the quiz title and number of questions.

3. **Given** quizzes created by different users, **When** viewing the browser, **Then** all quizzes are visible regardless of creator.

---

### User Story 5 - Retake a Quiz (Priority: P3)

As a user who previously completed a quiz, I want to retake it so that I can try to
improve my score.

The user can attempt any quiz multiple times. Each attempt is recorded separately.
Only the best score counts toward the scoreboard total.

**Why this priority**: Retaking enables improvement but adds complexity. Initial version
can restrict to single attempts if needed.

**Independent Test**: Can be tested by completing a quiz twice and verifying both attempts
are recorded but only the best contributes to scoreboard.

**Acceptance Scenarios**:

1. **Given** a user who has already completed a quiz, **When** they start the same quiz again, **Then** they can take it from the beginning.

2. **Given** a user with multiple attempts on a quiz, **When** viewing the scoreboard, **Then** only their best score for that quiz counts toward their total.

3. **Given** a user viewing their quiz history, **When** they have multiple attempts, **Then** they can see all attempts with their scores.

---

### Edge Cases

- What happens when a user tries to submit with unanswered questions?
  - System requires all questions to be answered before submission (validation error)
- What happens when a user's session expires during a quiz?
  - Unsaved progress is lost; user must restart the quiz after re-authentication
- What happens when a quiz is modified while someone is taking it?
  - The user sees the version they started with; changes apply to new attempts only
- What happens when a quiz is deleted while someone is taking it?
  - User receives an error upon submission; their attempt is not recorded
- What happens when the same user opens the quiz in two browser tabs?
  - Last submission wins; the other tab will show an error if submitted after

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow authenticated users to browse all available quizzes
- **FR-002**: System MUST display quiz title and question count in the browse list
- **FR-003**: System MUST allow users to start any quiz by selecting it
- **FR-004**: System MUST display all questions and answer options when a quiz is started
- **FR-005**: System MUST NOT reveal correct answers while a quiz is in progress
- **FR-006**: System MUST allow users to select one answer per question
- **FR-007**: System MUST allow users to change answers before submission
- **FR-008**: System MUST require all questions to be answered before submission
- **FR-009**: System MUST freeze answers upon submission (no further changes)
- **FR-010**: System MUST calculate score based on correct answers and point values
- **FR-011**: System MUST save quiz attempt with user, quiz, answers, and score
- **FR-012**: System MUST update user's total score on the scoreboard after submission
- **FR-013**: System MUST display results showing score and per-question feedback after submission
- **FR-014**: System MUST allow users to retake quizzes they have previously completed
- **FR-015**: System MUST use only the best attempt per quiz for scoreboard totals
- **FR-016**: System MUST record all attempts (not just best) for history purposes

### Key Entities

- **Quiz Attempt**: A single attempt by a user to complete a quiz. Contains user reference,
  quiz reference (snapshot of quiz at attempt time), submission timestamp, total score,
  and completion status (in-progress vs submitted).
- **Attempt Answer**: A user's selected answer for one question in an attempt. Contains
  attempt reference, question reference, selected answer reference, whether correct,
  and points earned.
- **Quiz (view only)**: The quiz being taken. User sees title, questions, and answer
  options but cannot modify. Point values may or may not be visible during taking.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can browse available quizzes and start one within 30 seconds
- **SC-002**: Users can complete a 10-question quiz in under 5 minutes (excluding thinking time)
- **SC-003**: 100% of submitted quiz scores are accurately calculated
- **SC-004**: Scoreboard totals update within 5 seconds of quiz submission
- **SC-005**: 95% of users successfully submit their first quiz without errors
- **SC-006**: Users can view their results immediately (within 2 seconds) after submission

## Assumptions

- User Management feature (002) is implemented—users can log in
- Quiz Creation feature (001) is implemented—quizzes with questions exist
- Admin Roles feature (003) is implemented—questions have point values
- Scoreboard feature (004) is implemented—total scores can be displayed
- Point values are visible during quiz results review (after submission)
- Point values are NOT visible during quiz taking (before submission)
- Quiz version snapshotting: user sees quiz as it was when they started
- No time limit on quiz completion (user can take as long as needed)
- No partial credit—answer is either correct (full points) or incorrect (zero points)
- Users cannot see other users' answers or attempts (private to each user)
