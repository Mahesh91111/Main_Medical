
# AI Medical Assistant & Clinical Intelligence Platform

A FastAPI-based platform for clinical record management, medical document
ingestion, retrieval-augmented generation (RAG), and LangGraph workflows.

## Technology stack

- Python 3.12
- FastAPI and Uvicorn
- PostgreSQL and SQLAlchemy
- Alembic database migrations
- Groq LLM API
- Hugging Face sentence-transformer embeddings
- Pinecone vector database
- LangChain and LangGraph
- Docker and Docker Compose
- Pytest

## Prerequisites

- Docker Desktop with Docker Compose
- A Groq API key
- A Pinecone API key and an index configured for 384-dimensional vectors
- Appropriate frontend origin configuration

## Configuration

Copy `.env.example` to `.env` and set your credentials.

The Docker database hostname is `postgres`:

    DATABASE_URL=postgresql+psycopg://medical_user:YOUR_PASSWORD@postgres:5432/medical_db

Never commit `.env` or real credentials.

## Start the application

From the project root:

    docker compose config
    docker compose up --build -d

View service status:

    docker compose ps

View backend logs:

    docker compose logs -f backend

View database logs:

    docker compose logs -f postgres

## API endpoints

- API root: http://localhost:8000/
- Swagger documentation: http://localhost:8000/docs
- Liveness: http://localhost:8000/health/live
- Readiness: http://localhost:8000/health/ready

## Database migrations

The development Compose command applies migrations before starting the API.

Check the current migration:

    docker compose exec backend alembic current

Inspect migration history:

    docker compose exec backend alembic history

Create a migration after changing SQLAlchemy models:

    docker compose exec backend alembic revision --autogenerate -m "describe schema change"

Review the generated file before applying it.

Apply migrations:

    docker compose exec backend alembic upgrade head

## Run tests

For local tests, activate the backend virtual environment and run:

    python -m pytest -v

Use a dedicated test database for database integration tests. Do not run destructive tests against production data.

## Stop services

    docker compose down

This preserves named volumes.

To delete the development database volume as well, use:

    docker compose down -v

WARNING: The `-v` option deletes the PostgreSQL data volume and stored uploads.
Use it only when you intentionally want to destroy development data.

## Production considerations

- Use a managed PostgreSQL database and a controlled migration step.
- Do not automatically run schema migrations in every production API replica.
- Terminate HTTPS at a secure reverse proxy or cloud load balancer.
- Store secrets in a secret manager, not in source control or image layers.
- Store clinical documents in encrypted object storage with access controls.
- Configure backups, monitoring, log redaction, and retention policies.
- Restrict database and API network access.
- Use synthetic data for development and testing.
- Do not treat AI-generated content as a confirmed medical diagnosis.
