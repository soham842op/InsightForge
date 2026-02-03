# InsightForge Backend

AI-powered analytics platform backend built with FastAPI.

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Environment configuration
│   ├── database.py          # Database connection
│   │
│   ├── api/                 # API routes (endpoints)
│   │   ├── deps.py          # Shared dependencies
│   │   └── v1/              # API version 1
│   │
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── base.py          # Base model with common fields
│   │   ├── user.py          # User model
│   │   ├── organization.py  # Organization (tenant) model
│   │   └── membership.py    # User-Organization relationship
│   │
│   ├── schemas/             # Pydantic request/response schemas
│   ├── services/            # Business logic layer
│   └── core/                # Core utilities (security, exceptions)
│
├── alembic/                 # Database migrations
├── tests/                   # Test suite
├── requirements.txt         # Python dependencies
└── .env.example            # Environment template
```

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy environment file and configure:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. Run database migrations:
   ```bash
   alembic upgrade head
   ```

5. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Architecture

### Multi-Tenant Design

InsightForge uses a **shared schema** multi-tenant architecture:
- All tenants share the same database tables
- Tenant isolation is enforced via `organization_id` foreign keys
- Every tenant-specific query is scoped to the current user's organization

### Key Concepts

- **Organization**: A tenant (company/team) that owns datasets and analyses
- **Membership**: Links users to organizations with specific roles
- **Roles**: OWNER, ADMIN, ANALYST, VIEWER (RBAC)

## API Documentation

When running in development mode, API docs are available at:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Interview Topics Covered

This codebase demonstrates:
- Multi-tenant SaaS architecture
- Role-Based Access Control (RBAC)
- JWT authentication
- SQLAlchemy 2.0 patterns
- Dependency injection in FastAPI
- Application factory pattern
- Custom exception handling
- Environment-based configuration (12-Factor App)
