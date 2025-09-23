# Hermes API

This document describes the HTTP API exposed by the Hermes project (REST Framework).

Base path: `/api/`

## Authentication

No authentication is configured by default. If you enable Django auth or token auth in your deployment, secure endpoints appropriately.

## Endpoints

### DataSources

GET /api/datasources/
- Returns list of configured data sources (DataSource model).

POST /api/datasources/
- Create a new data source. JSON body should match the DataSource model fields:
  - name (string)
  - type (string) - e.g. `csv`, `lean`, `web` etc.
  - config (object) - JSON config passed to adapters, e.g. `{ "path": "rt/mydata.csv" }`
  - enabled (boolean)

GET /api/datasources/{id}/
- Retrieve a single DataSource.

PUT /api/datasources/{id}/, PATCH /api/datasources/{id}/
- Update a data source.

DELETE /api/datasources/{id}/
- Delete a data source.

Example DataSource JSON:

{
  "id": 1,
  "name": "Local CSV",
  "type": "csv",
  "config": {"path": "rt/sample.csv"},
  "enabled": true
}

---

### Stocks

GET /api/stocks/
- Returns stocks (Stock model). Each item includes `datasource` (read-only nested object).

GET /api/stocks/{id}/
- Retrieve a single stock.

GET /api/stocks/by_symbol/?symbol=FOO
- Custom action: returns stocks matching a symbol (case-insensitive).

Example Stock JSON:

{
  "id": 1,
  "datasource": {"id": 1, "name": "Local CSV", "type": "csv", "config": {"path": "rt/sample.csv"}, "enabled": true},
  "symbol": "FOO",
  "name": "Foo Corp"
}

---

### OHLC Range (query endpoint)

GET /api/ohlc/?symbol=SYMBOL[&datasource=NAME_OR_ID][&start=ISO_DATETIME][&end=ISO_DATETIME]

Parameters:
- symbol (required): stock symbol to query
- datasource (optional): datasource name or numeric id to prefer
- start, end (optional): ISO-8601 datetimes (e.g. `2025-09-22T10:00:00`) to bound results

Behavior:
- If the database already contains OHLC rows for the requested symbol and time range, those stored rows are returned first.
- Otherwise the configured adapters for the matching datasource(s) are queried in order and their rows are returned.
- If no rows are found, returns 404 with `{ "detail": "no data found" }`.

Successful response: a JSON array of OHLC rows with fields: `timestamp`, `open`, `high`, `low`, `close`, `volume`.

Example request:

GET /api/ohlc/?symbol=FOO&start=2025-09-22T00:00:00&end=2025-09-23T00:00:00

Example response:

[
  {"timestamp": "2025-09-22T10:00:00Z", "open": 1.0, "high": 2.0, "low": 0.5, "close": 1.5, "volume": 100},
  {"timestamp": "2025-09-22T11:00:00Z", "open": 1.5, "high": 2.1, "low": 1.0, "close": 1.9, "volume": 200}
]

Notes:
- Timestamps returned by adapters are serialized by DRF; ensure timezone awareness is handled by your deployment.
- Adapters must return dictionaries with the expected fields; the API passes adapter-returned dicts through unchanged.

---

## Adapter types and config

- csv: `config` should contain `path` (path to CSV file) and optional `timezone`.
- lean: `config` should contain `path` to a JSONL/NDJSON file, optional `field_map` to remap short fields, and optional `timezone`.

Example lean datasource config:

{
  "type": "lean",
  "config": {"path": "rt/sample_lean.jsonl", "field_map": {"timestamp":"t","open":"o"}}
}

## Errors

- 400 is returned for missing required parameters.
- 404 is returned for datasource not found or when no data is available for the requested symbol/range.

## Contact

For contributions or questions, open an issue in the repository.
