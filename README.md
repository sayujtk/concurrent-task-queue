# Concurrent Task Queue (PostgreSQL SKIP LOCKED)

A concurrency-safe background job queue built with **FastAPI + SQLAlchemy + PostgreSQL**. It uses **`FOR UPDATE SKIP LOCKED`** to prevent double execution when multiple workers consume jobs in parallel.

## Highlights
- **Row-level locking** with `SKIP LOCKED` for safe concurrent workers
- **Retry + exponential backoff** (`2^attempts`) with `max_retries`
- **Priority + scheduled execution**
- **Dockerized** API + worker + Postgres
- **Pytest** coverage + **CI** via GitHub Actions

## Architecture (Quick)
- **API** inserts jobs (status `PENDING`)
- **Workers** poll `PENDING` jobs with `SKIP LOCKED`
- **Jobs** move through `RUNNING → SUCCESS/FAILED`

## Data Model (key fields)
`status`, `priority`, `attempts`, `max_retries`, `scheduled_at`, `started_at`, `finished_at`, `error_message`

## Run with Docker Compose
```bash
docker compose up --build
```
API: `http://localhost:8000/docs`

## Local Dev (no Docker)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Worker (separate terminal):
```bash
python run_worker.py
```

## Tests
```bash
pytest
```

## CI
GitHub Actions runs `pytest` on every push/PR.
