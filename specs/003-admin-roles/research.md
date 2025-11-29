# Research: Admin Roles

**Feature**: 003-admin-roles
**Date**: 2025-11-29
**Status**: Complete

## Research Questions

### RQ-001: First User Admin Assignment

**Question**: How should the first user be automatically granted admin status?

**Options Considered**:
1. **Check at registration time** - Count users before insert, grant admin if count=0
2. **Database trigger** - SQLite trigger to set is_admin on first insert
3. **Seeded admin account** - Pre-create admin user in migration

**Decision**: Check at registration time in AuthService

**Rationale**:
- Simple implementation with clear logic
- No SQLite-specific features (portable)
- Testable in application layer
- No hardcoded credentials needed

**Implementation Notes**:
```python
async def register_user(self, user_data: UserRegister) -> User:
    is_first_user = await self.db.query(User).count() == 0
    user = User(
        ...user_data,
        is_admin=is_first_user
    )
    await self.db.add(user)
    return user
```

---

### RQ-002: Admin Authorization Pattern

**Question**: How should admin-only endpoints be protected?

**Options Considered**:
1. **Dependency injection** - FastAPI Depends() with admin check
2. **Middleware** - Check all /admin/* routes
3. **Decorator** - @requires_admin on each endpoint

**Decision**: FastAPI Depends() with reusable dependency

**Rationale**:
- Consistent with existing auth pattern (get_current_user)
- Explicit per-endpoint (no implicit route matching)
- Easy to test (mock the dependency)
- Composable (can combine with other dependencies)

**Implementation Notes**:
```python
async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# Usage
@router.post("/admin/users/{user_id}/promote")
async def promote_user(
    user_id: UUID,
    admin: User = Depends(require_admin)
):
    ...
```

---

### RQ-003: Last Admin Protection

**Question**: How to prevent the system from having zero admins?

**Options Considered**:
1. **Count check before revoke** - Query admin count, block if would become 0
2. **Database constraint** - CHECK constraint (complex in SQLite)
3. **Soft delete for admins** - Never actually remove admin status

**Decision**: Count check before revoke in AdminService

**Rationale**:
- Clear business logic in application layer
- Easy to test and understand
- Provides meaningful error message
- Works with any database

**Implementation Notes**:
```python
async def revoke_admin(self, target_user_id: UUID, acting_admin: User) -> None:
    admin_count = await self.db.query(User).filter(User.is_admin == True).count()
    if admin_count <= 1:
        raise ValueError("Cannot revoke last admin - system requires at least one admin")

    target = await self.db.get(User, target_user_id)
    target.is_admin = False
    await self.log_action(acting_admin, "revoke_admin", target_user_id)
```

---

### RQ-004: Point Value Constraints

**Question**: What constraints should apply to question point values?

**Options Considered**:
1. **1-100 range** - As specified in requirements
2. **Positive integer only** - Any positive number
3. **Configurable maximum** - Admin-settable cap

**Decision**: 1-100 range with database constraint

**Rationale**:
- Clear boundaries per spec (FR-008)
- Prevents accidental extreme values
- Simple validation logic
- Default of 1 point for new questions (FR-009)

**Implementation Notes**:
```python
class Question(Base):
    points: int = Column(Integer, default=1, nullable=False)

    @validates('points')
    def validate_points(self, key, value):
        if not 1 <= value <= 100:
            raise ValueError("Points must be between 1 and 100")
        return value
```

---

### RQ-005: Audit Log Design

**Question**: What information should be stored in the admin audit log?

**Options Considered**:
1. **Minimal** - action, admin_id, timestamp only
2. **Detailed** - Include target, before/after values
3. **JSON blob** - Flexible schema in JSON column

**Decision**: Structured columns with before/after JSON

**Rationale**:
- Queryable for common fields (admin, action, target)
- Flexible for action-specific data (JSON)
- Supports audit requirements (FR-013)
- Balance between structure and flexibility

**Implementation Notes**:
```python
class AdminActionLog(Base):
    id: UUID = Column(UUID, primary_key=True)
    admin_id: UUID = Column(UUID, ForeignKey("users.id"), nullable=False)
    action: str = Column(String(50), nullable=False)  # grant_admin, revoke_admin, edit_question, etc.
    target_type: str = Column(String(50), nullable=False)  # user, question, answer
    target_id: UUID = Column(UUID, nullable=False)
    before_value: str = Column(Text, nullable=True)  # JSON
    after_value: str = Column(Text, nullable=True)   # JSON
    created_at: datetime = Column(DateTime, nullable=False)
```

---

### RQ-006: Admin Edit vs Owner Edit

**Question**: How should admin edits coexist with owner edits?

**Options Considered**:
1. **Override check** - Admin can edit any quiz, owner edit unchanged
2. **Unified edit** - Single edit endpoint checks admin OR owner
3. **Separate endpoints** - /admin/quizzes/{id}/edit vs /quizzes/{id}/edit

**Decision**: Unified edit with permission check (admin OR owner)

**Rationale**:
- Single endpoint reduces duplication
- Consistent UI experience
- Permission logic centralized in service
- Follows least-privilege principle

**Implementation Notes**:
```python
async def can_edit_quiz(self, user: User, quiz_id: UUID) -> bool:
    """Returns True if user is admin OR quiz owner."""
    if user.is_admin:
        return True
    quiz = await self.db.get(Quiz, quiz_id)
    return quiz.owner_id == user.id
```

---

## Dependencies Identified

| Dependency | Version | Purpose | Notes |
|------------|---------|---------|-------|
| FastAPI | 0.100+ | Web framework | Constitution-mandated |
| SQLAlchemy | 2.0+ | ORM | Existing dependency |
| pytest | 7.0+ | Testing | Constitution-mandated |

No new dependencies required for this feature.

## Security Considerations

1. **Authorization checks**: Every admin endpoint must verify is_admin flag
2. **Audit logging**: All admin actions logged with actor and target
3. **Last admin protection**: System prevents zero-admin state
4. **Timing attacks**: Use constant-time comparison for admin checks

## Open Questions Resolved

- First user admin: Application-level check at registration
- Authorization: FastAPI dependency injection
- Last admin: Service-level count check
- Point values: 1-100 with database validation
- Audit log: Structured columns + JSON for flexibility
- Admin edits: Unified endpoint with permission check

## Next Steps

Proceed to Phase 1: Generate data model and API contracts.
