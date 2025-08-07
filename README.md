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
| `GET` | `/employees` | Lists all employees from the database |
| `POST` | `/ask` | Ask natural language questions on employee data |
| `GET` | `/logs` | Retrieve Q&A history |

---

## Completed Milestones

### Day 1: Foundation
- Basic FastAPI setup
- Connected mock data sources
- Created unified schema
- Implemented hardcoded field mapping

### Day 2: LLM Mapping + CSV + DB
- Replaced hardcoded mapping with LLM-based dynamic mapping
- Integrated Ollama LLM (LangChain interface)
- Parsed CSV headers and allowed dynamic source connections
- Built endpoints for data access and transformation
- Added SQLite persistence with SQLAlchemy
- Prevented duplicates with upsert logic
- Implemented `/employees` route for final normalized output
- Thorough testing of all routes (LLM-based, CSV upload, DB sync)
- Verified deduplication and idempotency
- Polished and documented current implementation

### Day 3: Natural Language Query Layer
- Set up SQLite for persistent storage
- Stored normalized employee data
- Built `/employees` endpoint for DB access
- Added `/ask` endpoint to answer questions via SQL
- Logged all Q&A to database with `/logs`

### Day 4: Product Polish & Plugin System

- `/stats` showing data ingestion stats
- Source schema visualizer
- Swagger UI documentation
- Plugin-based loader system (FakeSAP, FakeWorkday, CSV)

---

## Noted Issues

- LLM invoked for every record as of now
