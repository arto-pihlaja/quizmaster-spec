# Research: Scoreboard Feature

**Feature**: 004-scoreboard
**Date**: 2025-11-29

## Research Tasks

### 1. SQLite Performance for Scoreboard Queries

**Question**: Can SQLite handle 10,000+ users with efficient ranking queries?

**Decision**: Yes, SQLite is suitable with proper indexing.

**Rationale**:
- SQLite handles millions of rows efficiently for read-heavy workloads
- Window functions (`RANK() OVER`) are supported in SQLite 3.25+ (Python 3.11 ships with 3.39+)
- Single-file database simplifies container deployment
- For 10,000 users, query time will be <100ms with indexes

**Alternatives Considered**:
- PostgreSQL: More features but adds deployment complexity; overkill for local-first app
- In-memory caching: Premature optimization; add later if needed

**Implementation Notes**:
- Create index on `(total_score DESC, display_name ASC)` for efficient sorting
- Use `RANK()` window function for competition ranking
- Pagination via `LIMIT/OFFSET` is acceptable at this scale

### 2. Score Aggregation Strategy

**Question**: How to calculate total scores efficiently?

**Decision**: Materialized view pattern using a `user_scores` summary table.

**Rationale**:
- Real-time aggregation across quiz attempts would require joins on every request
- Pre-computed totals with incremental updates balance accuracy and performance
- Update user's total score when they complete a quiz (event-driven)

**Alternatives Considered**:
- Real-time aggregation: Too slow for 10,000+ users with many quiz attempts
- Caching layer (Redis): Adds dependency; violates simplicity principle
- Periodic batch updates: Delays score visibility; poor UX

**Implementation Notes**:
- `user_scores` table: `user_id`, `total_score`, `quizzes_completed`, `last_updated`
- Trigger or service call updates this table on quiz completion
- Scoreboard queries this pre-aggregated table

### 3. Frontend Architecture (Plain HTML/JS)

**Question**: How to implement refresh without page reload using vanilla JS?

**Decision**: Fetch API with JSON endpoint + DOM manipulation.

**Rationale**:
- Native `fetch()` is well-supported in all modern browsers
- No build step required (aligns with simplicity)
- Jinja2 renders initial page; JS handles subsequent updates

**Alternatives Considered**:
- HTMX: Elegant but adds dependency; keep for future consideration
- React/Vue: Heavy frameworks; violates user requirement for plain HTML/JS
- Full page reload: Poor UX; doesn't meet FR-011

**Implementation Notes**:
- `/api/scoreboard` returns JSON for refresh
- `/scoreboard` returns HTML (server-rendered) for initial load
- JS replaces table body content on refresh click

### 4. Competition Ranking Implementation

**Question**: How to implement standard competition ranking (1, 2, 2, 4)?

**Decision**: SQL `RANK()` window function.

**Rationale**:
- `RANK()` natively implements competition ranking semantics
- Single query handles both ranking and pagination
- Database-level ranking is more reliable than application-level

**Alternatives Considered**:
- `ROW_NUMBER()`: Would give 1, 2, 3, 4 (not competition ranking)
- `DENSE_RANK()`: Would give 1, 2, 2, 3 (not standard competition)
- Application-level ranking: More code, potential bugs

**SQL Pattern**:
```sql
SELECT
  RANK() OVER (ORDER BY total_score DESC, display_name ASC) as rank,
  user_id,
  display_name,
  total_score
FROM user_scores
ORDER BY rank
LIMIT 50 OFFSET ?
```

### 5. User Highlighting and "Jump to My Rank"

**Question**: How to highlight current user and enable jumping to their position?

**Decision**: Separate endpoint for user's rank + client-side highlighting.

**Rationale**:
- Server returns current user's rank via `/api/scoreboard/my-rank`
- Client calculates which page contains that rank
- CSS class applied to matching row in rendered table

**Alternatives Considered**:
- Server-side highlighting: Requires session info in every scoreboard query; couples concerns
- Always showing user at top: Violates ranking order requirement

**Implementation Notes**:
- `GET /api/scoreboard/my-rank` returns `{ rank: 42, page: 1 }` (if logged in)
- JS adds `.highlight` class to row matching current user ID
- "Jump to my rank" button navigates to calculated page

### 6. Authentication Context for Public Page

**Question**: How to identify logged-in user on a public page?

**Decision**: Optional session cookie; graceful degradation.

**Rationale**:
- Scoreboard is viewable by anyone (FR-007)
- If session cookie present, extract user ID for highlighting
- If no session, show scoreboard without highlighting (FR-003)

**Alternatives Considered**:
- Require login: Violates FR-007 (public access)
- Separate logged-in/logged-out pages: Duplication; unnecessary

**Implementation Notes**:
- FastAPI dependency injection: `current_user: Optional[User] = Depends(get_current_user_optional)`
- Pass `current_user_id` to template if available
- JS uses embedded user ID for highlight logic

## Dependencies Identified

| Dependency | Version | Purpose | Justification |
|------------|---------|---------|---------------|
| FastAPI | 0.100+ | Web framework | Constitution-mandated |
| Uvicorn | 0.20+ | ASGI server | Standard FastAPI runner |
| SQLAlchemy | 2.0+ | ORM/Query builder | Type-safe DB access |
| Jinja2 | 3.0+ | HTML templating | Built into FastAPI |
| pytest | 7.0+ | Testing | Constitution-mandated |
| pytest-asyncio | 0.21+ | Async test support | FastAPI is async |
| httpx | 0.24+ | Test client | FastAPI test standard |

## Open Questions Resolved

All NEEDS CLARIFICATION items from Technical Context have been resolved:

1. **Database**: SQLite (user-specified)
2. **Performance at scale**: Achievable with indexes and pre-aggregation
3. **Frontend refresh**: Fetch API + JSON endpoint
4. **Ranking algorithm**: SQL RANK() window function
5. **User identification**: Optional session-based, graceful degradation
