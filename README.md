# Weather Sensor REST API

A REST API that ingests weather metrics from sensors (temperature, humidity, wind
speed, …) and lets you query aggregated statistics over a date range.

Built with **FastAPI** (async) and **SQLite** (swappable to PostgreSQL).

## Requirements

- Python 3.11 or newer (developed on 3.14)

## Setup

Clone the repo, then from the project root:

```bash
# 1. Create an isolated virtual environment
python3 -m venv .venv

# 2. Activate it
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows (PowerShell)

# 3. Install dependencies (pinned in requirements.txt for reproducibility)
pip install -r requirements.txt
```

To reproduce this environment on another machine, repeat the three steps above — the
pinned `requirements.txt` guarantees the same package versions.

## Running the API

```bash
uvicorn app.main:app --reload
```

- API base URL: http://127.0.0.1:8000
- Interactive docs (Swagger UI): http://127.0.0.1:8000/docs
- Alternative docs (ReDoc): http://127.0.0.1:8000/redoc

The `--reload` flag restarts the server automatically when you edit code (dev only).

## Project structure

```
app/
  main.py            # app entry point; mounts routers
  routers/           # HTTP layer — one module per feature
requirements.txt     # pinned direct dependencies
```

## Endpoints

| Method | Path      | Description                                  |
|--------|-----------|----------------------------------------------|
| GET    | `/health` | Liveness check — returns `{"status": "ok"}`  |

## Development status

Proof of concept, built incrementally.
