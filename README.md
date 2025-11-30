# QuizMaster

A quiz creation and management application built with FastAPI.

## Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Getting Started

### 1. Navigate to the backend directory

```bash
cd backend
```

### 2. Install dependencies

Using uv (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -e .
```

### 3. Run the application

Using uv:
```bash
uv run uvicorn src.main:app --reload
```

Or with the virtual environment activated:
```bash
uvicorn src.main:app --reload
```

The application will start at `http://localhost:8000`.

## API Documentation

Once the server is running, access:
- Interactive API docs (Swagger UI): http://localhost:8000/docs
- Alternative API docs (ReDoc): http://localhost:8000/redoc

## Running Tests

```bash
cd backend
uv run pytest
```

## Project Structure

```
backend/
├── src/
│   ├── api/          # API route handlers
│   ├── db/           # Database configuration
│   ├── middleware/   # Request middleware
│   ├── models/       # SQLAlchemy models
│   ├── schemas/      # Pydantic schemas
│   ├── security/     # Authentication & security
│   ├── services/     # Business logic
│   └── main.py       # Application entry point
├── tests/            # Test files
└── pyproject.toml    # Project dependencies
```
