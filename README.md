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
| `GET` | `/list-connected-sources` | Lists all currently connected sources |
| `GET` | `/get-data` | Returns normalized data from connected sources and persists them |
| `GET` | `/normalised-data` | Normalizes all sources without storing |
| `GET` | `/field-mapping/{source_name}` | Shows dynamic field mapping for a given source |
| `POST` | `/upload-csv` | Upload CSV and normalize + store its data |
| `GET` | `/employees` | Returns all employees from the database |

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

---

## Upcoming Milestones

### Day 3: Natural Language Query Layer
- Build a LangGraph-based agent to handle user questions
- Use LLM to translate natural language to SQL queries
- Support questions like:
  - "How many employees joined after Jan 2024?"
  - "Show employees in the Marketing department"
- Add `/ask` endpoint for querying employee data with natural language
- Integrate SQLite with LangChain's SQL agent
- Return results in conversational format

---

## Noted Issues

- Discconect source route to be added
- LLM invoked for every record as of now