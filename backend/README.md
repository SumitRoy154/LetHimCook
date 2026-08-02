# Let Him Cook! - Backend

FastAPI backend service and AI agent orchestrator using LangGraph, SQLAlchemy, and MySQL.

## Project Structure

```
backend/
│
├── app/
│   ├── api/          # FastAPI routes & endpoints
│   ├── agents/       # AI agents logic
│   ├── core/         # Core application setup & settings (config.py)
│   ├── database/     # SQLAlchemy database connection & session setup
│   ├── models/       # Database ORM models
│   ├── schemas/      # Pydantic schemas for request/response validation
│   ├── services/     # Business logic & application services
│   ├── graph/        # LangGraph agent graph definitions
│   ├── prompts/      # Agent system prompts & templates
│   ├── utils/        # Utility modules & helpers
│   └── main.py       # FastAPI main entrypoint
│
├── alembic/          # Database migrations folder
├── alembic.ini       # Alembic migration configuration
├── requirements.txt  # Python package dependencies
├── .env.example      # Environment variables template
└── README.md         # Backend documentation
```

## Setup & Running Locally

### 1. Environment Setup

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Configure your local MySQL parameters in `.env`:
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=let_him_cook
MYSQL_PASSWORD=let_him_cook
MYSQL_DATABASE=let_him_cook
```

### 2. Verify Database Connection

```bash
python scripts/verify_db.py
```

### 3. Run Migrations

```bash
alembic upgrade head
```

### 4. Start Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API Base URL: `http://localhost:8000`
- Swagger Docs: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/api/health`
