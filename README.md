# Highly Concurrent Task Queue (PostgreSQL SKIP LOCKED)

A distributed, concurrency-safe background job queue built with **Python, FastAPI, SQLAlchemy, and PostgreSQL**. 

This project demonstrates how to build a scalable worker pool that can process thousands of background jobs simultaneously without encountering race conditions, database deadlocks, or double-execution.

## 🚀 The Elevator Pitch (Why I Built This)
If you ask me about this project, here is what I will tell you:
> *"I built a distributed, concurrency-safe task queue. I used FastAPI to ingest jobs, but the real challenge was preventing race conditions when multiple worker threads tried to grab the same job. I solved this by implementing PostgreSQL's `FOR UPDATE SKIP LOCKED`, which allowed my multi-threaded worker pool to concurrently consume tasks without blocking each other or causing double-execution."*

## 💡 Real-World Applications
This exact architecture is used under the hood at major tech companies:
* **YouTube/Netflix (Video Processing):** The web server doesn't freeze while compressing a video. It saves a `PENDING` job, and a background worker picks it up.
* **Stripe (Payment Processing):** Using row-level locks ensures only ONE worker processes a transaction, preventing a customer from being charged twice (Race Condition).
* **Uber/Swiggy (Notifications):** Queuing SMS and push notifications to be processed asynchronously by millions of workers.

---

## 🧠 The Intellectual Core: Concurrency & `SKIP LOCKED`
If 10 background workers run `SELECT * FROM jobs WHERE status = 'PENDING'` at the exact same millisecond, they will all grab Job #1. 

To solve this, this system uses **Row-Level Locking**:
1. **`FOR UPDATE`**: When a worker grabs a row, it puts a database lock on it.
2. **`SKIP LOCKED`**: When the next worker queries the database, it sees the lock on Job #1, completely ignores it, and instantly grabs Job #2. 

**Zero freezing. Zero blocking. Maximum throughput.**

### Proof of Concurrency
Here is actual terminal output from a stress test where multiple jobs were submitted simultaneously. Notice how Worker 1, Worker 2, and Worker 3 grab jobs 4, 5, and 6 at the exact same time without waiting for each other:
```text
[Worker 2] Picked up Job 4 - Payload: spanning the system
[Worker 3] Picked up Job 5 - Payload: spanning the system
[Worker 1] Picked up Job 6 - Payload: spanning the system
[Worker 2] Successfully finished Job 4
[Worker 1] Successfully finished Job 6
[Worker 3] Successfully finished Job 5
```

---

## 🏗️ Architecture & Engineering Decisions

### 1. File Structure
* `database.py`: Handles PostgreSQL connections using **Connection Pooling** (`pool_size=10`) and **Thread-Local Sessions** (`scoped_session`) to ensure threads don't corrupt each other's data.
* `models.py`: SQLAlchemy models representing the database tables.
* `schemas.py`: Pydantic models for JSON validation. (Separating DB structure from API structure).
* `main.py`: The FastAPI web server acting as the ingress point for new jobs.
* `worker.py`: The multi-threaded background worker pool using `ThreadPoolExecutor`.

### 2. Database Optimization
The `status` column in the database has a **B-Tree Index** (`index=True`). Because workers are constantly querying `WHERE status = 'PENDING'`, this prevents sequential table scans and keeps queries at sub-millisecond speeds even with millions of rows.

### 3. Separation of Concerns (Pydantic vs SQLAlchemy)
* **SQLAlchemy (`models.py`)**: Represents the raw data stored in the database freezer.
* **Pydantic (`schemas.py`)**: Represents the plated meal presented to the user. Users cannot pass sensitive fields like `status` or `id` via the API; they can only send the `payload`.

---

## 🔄 The Lifecycle of a Task
1. **The Submission:** A client sends a POST request with a JSON payload to the FastAPI app. FastAPI instantly saves it as `PENDING` and returns a 200 OK. The user is not kept waiting.
2. **The Polling:** In the background, worker threads constantly query the DB for `PENDING` jobs.
3. **The Lock & Process:** A worker finds a job, locks it using `SKIP LOCKED`, marks it as `PROCESSING`, and executes the heavy workload.
4. **The Completion:** The worker marks the job as `COMPLETED`. The client can poll the API to see the finished status.

---

## 🛠️ How to Run Locally

**1. Start the PostgreSQL Database (via Docker)**
```bash
docker run --name taskqueue-pg -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=taskqueue -p 5432:5432 -d postgres
```

**2. Setup Python Environment**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic
```

**3. Run the API Server**
```bash
uvicorn main:app --reload
```
*API available at `http://localhost:8000/docs`*

**4. Run the Worker Pool** (In a separate terminal)
```bash
source .venv/bin/activate
python worker.py
```