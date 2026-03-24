# Network Route Optimization API

REST API for managing network **nodes** and **edges** (with latency weights) and computing **minimum-latency paths** between named endpoints. Results of successful shortest-path queries are stored as **route history**.

## Tech stack

| Layer | Technology |
|--------|------------|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| Server | [Uvicorn](https://www.uvicorn.org/) |
| ORM / DB | [SQLAlchemy](https://www.sqlalchemy.org/) 2.x, **SQLite** (`network_routes.db`) |
| Validation | [Pydantic](https://docs.pydantic.dev/) v2 |

## Setup

1. **Python 3.10+** recommended (uses `list[str]` union syntax).

2. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

   On macOS/Linux: `source .venv/bin/activate`

3. The database file is created automatically on first startup (tables are created via the app lifespan).

## Run the server

From the project root:

```bash
uvicorn main:app --reload
```

Default URL: **http://127.0.0.1:8000**  
Interactive API docs: **http://127.0.0.1:8000/api/docs** (ReDoc: `/api/redoc`, OpenAPI JSON: `/api/openapi.json`). **`/docs`** and **`/openapi.json`** redirect to those URLs.

## API overview

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness and database check (`SELECT 1` via app session). **200** → `{"status":"ok","database":"ok"}`; **503** if the DB is unreachable |
| `GET` | `/nodes/` | List nodes (`skip`, `limit`) |
| `POST` | `/nodes/` | Create node (JSON `name`) |
| `DELETE` | `/nodes/{node_id}` | Delete node |
| `GET` | `/edges/` | List edges (`skip`, `limit`) |
| `GET` | `/edges/{edge_id}` | Get one edge (response includes `source_name`, `destination_name`) |
| `POST` | `/edges/` | Create edge (`source_name`, `destination_name`, `latency` > 0); node names must exist (unique per node) |
| `DELETE` | `/edges/{edge_id}` | Delete edge |
| `GET` | `/routes/history` | List route history (filters below) |
| `POST` | `/routes/shortest` | Shortest path by latency (Dijkstra); persists history |
| `POST` | `/routes/optimize` | Placeholder (returns empty path / zero latency) |

**`/routes/history` query parameters:** `source`, `destination`, `limit` (default 100), `date_from`, `date_to` (ISO datetimes).

## Sample requests

Create nodes first, then reference them by **name** when creating edges.

**Health**

```bash
curl -s http://127.0.0.1:8000/health
```

**Create nodes**

```bash
curl -s -X POST http://127.0.0.1:8000/nodes/ -H "Content-Type: application/json" -d "{\"name\": \"A\"}"
curl -s -X POST http://127.0.0.1:8000/nodes/ -H "Content-Type: application/json" -d "{\"name\": \"B\"}"
curl -s -X POST http://127.0.0.1:8000/nodes/ -H "Content-Type: application/json" -d "{\"name\": \"C\"}"
```

**Create edges** (endpoints are node **names**)

```bash
curl -s -X POST http://127.0.0.1:8000/edges/ -H "Content-Type: application/json" -d "{\"source_name\": \"A\", \"destination_name\": \"B\", \"latency\": 5.0}"
curl -s -X POST http://127.0.0.1:8000/edges/ -H "Content-Type: application/json" -d "{\"source_name\": \"B\", \"destination_name\": \"C\", \"latency\": 3.0}"
```

**Shortest path** (by node **names**)

```bash
curl -s -X POST http://127.0.0.1:8000/routes/shortest -H "Content-Type: application/json" -d "{\"source\": \"A\", \"destination\": \"C\"}"
```

Example response shape: `{"total_latency": 8.0, "path": ["A", "B", "C"]}`.

**Route history**

```bash
curl -s "http://127.0.0.1:8000/routes/history?source=A&destination=C&limit=10"
```

## How Dijkstra is used

In the API, nodes are identified by **name** (unique): edge create/read payloads use `source_name` / `destination_name`, and routing requests use `source` / `destination` strings. In memory, the graph is built from stored edges as directed arcs between **node IDs** with weight **latency**. For `POST /routes/shortest`, the API resolves the endpoint names to IDs, runs **Dijkstra’s algorithm** (non-negative weights, priority queue) to minimize **total latency**, then returns the path as an ordered list of **node names** and the sum of edge weights. If either endpoint is missing or no path exists, the API responds with `400` or `404` respectively. A successful computation is appended to route history for later querying.
