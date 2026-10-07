# Load-Test Evidence

**Date:** 2026-10-05  
**Environment:** macOS 26.7.1, Python 3.14.5, local Uvicorn server, SQLite  
**Tool:** ApacheBench (`ab`)  
**Workload:** 100 requests at concurrency 10, 10-second client timeout

These are short localhost baseline measurements for the proof of concept.

## Commands

Start the API in one terminal:

```bash
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Then run these commands:

```bash
ab -n 100 -c 10 -s 10 \
  'http://127.0.0.1:8000/readings?sensor_ids=day3-sensor-1&metrics=temperature'

ab -n 100 -c 10 -s 10 \
  'http://127.0.0.1:8000/readings?metrics=temperature&statistic=avg&days=30'

ab -n 100 -c 10 -s 10 -p assets/load-test-reading.json \
  -T 'application/json' 'http://127.0.0.1:8000/readings'
```

The POST command creates rows in the local database.

## Recorded Results

| Test | Requests | Concurrency | Failures | Requests/sec | Mean ms | p95 ms | p99 ms |
|------|----------|-------------|----------|--------------|---------|--------|--------|
| Latest read | 100 | 10 | 0 | 1025.41 | 9.75 | 14 | 18 |
| Aggregate read | 100 | 10 | 0 | 1409.74 | 7.093 | 11 | 14 |
| POST write | 100 | 10 | 0 | 564.51 | 17.715 | 96 | 141 |

Finding: writes were slower because each request performs database persistence and
commit work, while reads are primarily query operations. SQLite write-lock
contention is a likely contributor to the higher tail latency. The PoC addressed
the risk with rate limiting.
