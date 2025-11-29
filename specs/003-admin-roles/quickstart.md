# Quickstart: Admin Roles

**Feature**: 003-admin-roles
**Prerequisites**: User Management (002), Quiz Creation (001)

## Setup

```bash
# Ensure dependencies are installed
cd backend
pip install -r requirements.txt

# Run database migrations (includes is_admin, points columns)
python -m src.db.migrate

# Start the development server
uvicorn src.main:app --reload
```

## Test Scenarios

### Scenario 1: First User Becomes Admin

**Objective**: Verify the first registered user automatically gets admin status.

```bash
# 1. Start with fresh database (no users)
rm -f backend/data/quizmaster.db
python -m src.db.migrate

# 2. Register first user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "first@example.com", "password": "Password123", "display_name": "FirstUser"}'

# Expected: User created with is_admin=true
# Response includes: "is_admin": true

# 3. Register second user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "second@example.com", "password": "Password123", "display_name": "SecondUser"}'

# Expected: User created with is_admin=false
# Response includes: "is_admin": false
```

### Scenario 2: Promote User to Admin

**Objective**: Verify an admin can grant admin privileges to another user.

```bash
# 1. Login as first user (admin)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "first@example.com", "password": "Password123"}' \
  -c cookies.txt

# 2. Get list of users
curl http://localhost:8000/admin/users \
  -b cookies.txt

# Note the user_id of second user

# 3. Promote second user to admin
curl -X POST http://localhost:8000/admin/users/{user_id}/promote \
  -b cookies.txt

# Expected: 200 OK, user now has is_admin=true

# 4. Verify second user can access admin endpoints
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "second@example.com", "password": "Password123"}' \
  -c cookies2.txt

curl http://localhost:8000/admin/users \
  -b cookies2.txt

# Expected: 200 OK (admin access granted)
```

### Scenario 3: Edit Question as Admin

**Objective**: Verify an admin can edit any quiz question.

```bash
# 1. Create a quiz as second user
curl -X POST http://localhost:8000/quizzes \
  -H "Content-Type: application/json" \
  -b cookies2.txt \
  -d '{
    "title": "Test Quiz",
    "questions": [{
      "text": "Original question text?",
      "answers": [
        {"text": "Answer A", "is_correct": true},
        {"text": "Answer B", "is_correct": false}
      ]
    }]
  }'

# Note the question_id from response

# 2. Login as first user (different admin)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "first@example.com", "password": "Password123"}' \
  -c cookies.txt

# 3. Edit the question as admin
curl -X PUT http://localhost:8000/admin/questions/{question_id} \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"text": "Updated question text by admin?"}'

# Expected: 200 OK, question text updated
```

### Scenario 4: Set Question Points

**Objective**: Verify an admin can set variable point values for questions.

```bash
# 1. Set points for a question
curl -X PUT http://localhost:8000/admin/questions/{question_id}/points \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"points": 5}'

# Expected: 200 OK, question now worth 5 points

# 2. Try invalid points (should fail)
curl -X PUT http://localhost:8000/admin/questions/{question_id}/points \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"points": 0}'

# Expected: 400 Bad Request (points must be 1-100)

curl -X PUT http://localhost:8000/admin/questions/{question_id}/points \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"points": 101}'

# Expected: 400 Bad Request (points must be 1-100)
```

### Scenario 5: Edit Answer and Correct Flag

**Objective**: Verify an admin can edit answers and change which is correct.

```bash
# 1. Get question details to find answer IDs
curl http://localhost:8000/quizzes/{quiz_id} \
  -b cookies.txt

# Note the answer_id values

# 2. Edit answer text
curl -X PUT http://localhost:8000/admin/answers/{answer_id} \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"text": "Updated answer text", "is_correct": false}'

# Expected: 200 OK

# 3. Change which answer is correct
curl -X PUT http://localhost:8000/admin/answers/{other_answer_id} \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"text": "This is now correct", "is_correct": true}'

# Expected: 200 OK, this answer is now marked correct
```

### Scenario 6: Revoke Admin (with Last Admin Protection)

**Objective**: Verify admin revocation works but prevents zero-admin state.

```bash
# 1. Revoke admin from second user (while first user is still admin)
curl -X POST http://localhost:8000/admin/users/{second_user_id}/revoke \
  -b cookies.txt

# Expected: 200 OK, second user is no longer admin

# 2. Try to revoke admin from first user (last admin)
curl -X POST http://localhost:8000/admin/users/{first_user_id}/revoke \
  -b cookies.txt

# Expected: 400 Bad Request
# Error: "Cannot revoke last admin - system requires at least one admin"
```

### Scenario 7: Verify Audit Log

**Objective**: Verify all admin actions are logged.

```bash
# 1. Get audit log
curl http://localhost:8000/admin/logs \
  -b cookies.txt

# Expected: List of all admin actions performed:
# - grant_admin (when second user was promoted)
# - edit_question (when question was edited)
# - set_points (when points were set)
# - edit_answer (when answer was edited)
# - revoke_admin (when second user was demoted)

# 2. Filter by action type
curl "http://localhost:8000/admin/logs?action=edit_question" \
  -b cookies.txt

# Expected: Only edit_question actions
```

### Scenario 8: Non-Admin Access Denied

**Objective**: Verify non-admin users cannot access admin endpoints.

```bash
# 1. Login as demoted second user (no longer admin)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "second@example.com", "password": "Password123"}' \
  -c cookies2.txt

# 2. Try to access admin endpoint
curl http://localhost:8000/admin/users \
  -b cookies2.txt

# Expected: 403 Forbidden
# Error: "Admin access required"

# 3. Try to edit question
curl -X PUT http://localhost:8000/admin/questions/{question_id} \
  -H "Content-Type: application/json" \
  -b cookies2.txt \
  -d '{"text": "Trying to edit"}'

# Expected: 403 Forbidden
```

## Verification Checklist

- [ ] First user automatically becomes admin
- [ ] Subsequent users are not admins by default
- [ ] Admin can promote users to admin
- [ ] Newly promoted admin has full admin access
- [ ] Admin can edit any question text
- [ ] Admin can set points (1-100) for any question
- [ ] Questions default to 1 point
- [ ] Admin can edit any answer text
- [ ] Admin can change which answer is correct
- [ ] Admin can revoke other admins
- [ ] System prevents revoking last admin
- [ ] All admin actions are logged
- [ ] Non-admins get 403 on admin endpoints
- [ ] Audit log shows before/after values

## Common Issues

1. **First user not admin**: Ensure database was migrated after adding is_admin column
2. **403 on admin endpoints**: Verify session cookie is being sent and user.is_admin is True
3. **Points validation fails**: Ensure value is integer between 1-100 inclusive
4. **Audit log empty**: Check that AdminService.log_action() is called in all admin operations
