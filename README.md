# SyncHub

SyncHub is a lightweight FastAPI backend that simulates connecting to enterprise data sources like SAP and Workday.  
It pulls mock employee data from connected sources and merges them for downstream use.

## Endpoints

- `POST /connect-source` – Connect a mock source (e.g. FakeSAP)
- `GET /get-data` – Returns merged data from all connected sources
- `GET /list-connected-sources` – Returns all connected sources with timestamps

## How to Run

```bash
uvicorn main:app --reload
```
Then open Swagger at: `http://127.0.0.1:8000/docs`

## Yet to Add
- Real schema normalization
- LangChain-powered field mapping
- Basic frontend or CLI