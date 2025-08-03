# SyncHub

SyncHub is a backend service that connects to multiple enterprise data sources (like Workday, SAP, or custom CSVs), uses an LLM to automatically map and normalize employee data fields into a unified schema, and provides normalized data through a clean API.

Think of it as your data pipeline brain that cleans up incoming chaos into structured harmony.

---

## Features

- Connect to multiple data sources (SAP, Workday, CSV)
- Use LLM (Ollama or OpenAI) to **auto-map fields** dynamically
- Normalize data into a **common schema**: `employee_id`, `name`, `salary`, `email`, `department`, `location`
- Retrieve unified employee data through a clean API
- Upload CSVs as custom sources
- In-memory simulation for fast prototyping

---

## Tech Stack

- **FastAPI** – for building the REST API
- **LangChain** – for prompt templates and LLM calls
- **Ollama** (or **OpenAI**) – for smart field mapping
- **Pydantic** – schema validation
- **Python** – main backend language

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/connect-source` | Connects a source like `FakeSAP`, `FakeWorkday`, or CSV |
| `GET` | `/get-data` | Returns normalized data from connected sources |
| `GET` | `/list-connected-sources` | Lists all currently connected sources |
| `GET` | `/normalised-data` | Normalizes all sources, not just the connected ones |

---

## Completed Milestones

### Day 1: Foundation
- Basic FastAPI setup
- Connected mock data sources
- Created unified schema
- Implemented hardcoded field mapping

### Day 2: LLM Mapping + CSV
- Replaced hardcoded mapping with LLM-based dynamic mapping
- Integrated Ollama LLM (LangChain interface)
- Parsed CSV headers and allowed dynamic source connections
- Built endpoints for data access and transformation

## Upcoming Milestone

### Day 3:
- Store normalized data in SQLite or Postgres
- Filter and query employees (by name, salary range, etc.)
- Analytics / aggregation layer
- Add source-specific configurations
- Simple frontend dashboard (optional)