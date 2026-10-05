# Weather Sensor REST API

A REST API that ingests weather metrics from sensors (temperature, humidity, wind
speed, ...) and lets you query the latest readings or aggregate a lookback period.

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

### ✅ Implemented endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness check. Returns `{"status": "ok"}`. |
| POST | `/readings` | Store one reading. Metrics: `temperature`, `humidity`, or `wind_speed`. |
| GET | `/readings` | Return latest readings or aggregate the previous `days=1..30` days. Supports sensor, metric, and statistic filters. |

When `days` is omitted, the API returns the latest reading for each selected
sensor/metric pair and reports `"statistic": "latest"`. When `days` is supplied,
the API aggregates all matching readings from that lookback period. The supported
statistics are `min`, `max`, `avg`, and `sum`; the default is `avg`.

### Sample requests and responses

Health check:

```bash
curl 'http://127.0.0.1:8000/health'
```

```json
{"status":"ok"}
```

Store a reading:

```bash
curl -X POST 'http://127.0.0.1:8000/readings' \
  -H 'Content-Type: application/json' \
  -d '{"sensor_id":"sensor-1","metric":"temperature","value":21.4}'
```

Example response:

```json
{
  "id": 12,
  "sensor_id": "sensor-1",
  "metric": "temperature",
  "value": 21.4,
  "timestamp": "2026-10-05T12:00:00"
}
```

Get the latest reading. Omit `days` to return the newest value for each
sensor/metric combination:

```bash
curl 'http://127.0.0.1:8000/readings?sensor_ids=sensor-1&metrics=temperature'
```

Example response:

```json
[
  {
    "sensor_id": "sensor-1",
    "metric": "temperature",
    "statistic": "latest",
    "value": 21.4
  }
]
```

Get an average over the previous eight days:

```bash
curl 'http://127.0.0.1:8000/readings?sensor_ids=sensor-1&metrics=temperature&days=8'
```

Example response:

```json
[
  {
    "sensor_id": "sensor-1",
    "metric": "temperature",
    "statistic": "avg",
    "value": 20.8
  }
]
```

Get the maximum humidity over the previous 30 days:

```bash
curl 'http://127.0.0.1:8000/readings?sensor_ids=sensor-1&metrics=humidity&statistic=max&days=30'
```

Example response:

```json
[
  {
    "sensor_id": "sensor-1",
    "metric": "humidity",
    "statistic": "max",
    "value": 55.2
  }
]
```

Query all sensors and metrics:

```bash
curl 'http://127.0.0.1:8000/readings?statistic=avg&days=30'
```

Query multiple selected sensors. Repeat `sensor_ids` for each sensor:

```bash
curl 'http://127.0.0.1:8000/readings?sensor_ids=sensor-1&sensor_ids=sensor-2&metrics=temperature&statistic=avg&days=30'
```

Example response:

```json
[
  {
    "sensor_id": "sensor-1",
    "metric": "temperature",
    "statistic": "avg",
    "value": 20.8
  },
  {
    "sensor_id": "sensor-2",
    "metric": "temperature",
    "statistic": "avg",
    "value": 10.0
  }
]
```

## Development status

Proof of concept, built incrementally over 5 days.

- **Day 1**: Planning, framework selection, GET /health ✅
- **Day 2**: Data layer, POST /readings ingest ✅
- **Day 3**: Debugging session, GET /readings query endpoint, latest mode, lookback aggregation, and verification complete
- **Day 4**: Resilience, caching, rate limiting
- **Day 5**: Documentation polish, Postgres migration, monitoring
