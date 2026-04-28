# Backend — Kapruka Gift Concierge API

The backend is a **FastAPI** application that powers the Kapruka Gift Concierge AI agent system. It combines LLM-driven multi-agent orchestration, hybrid vector search, a reflection-based safety loop, and JWT authentication into a single coherent API.

---

## Architecture Overview

```
backend/
├── config/
│   ├── models.yaml          # LLM & embedding model registry (tiers: general, strong, reason)
│   └── param.yaml           # Runtime parameters (provider, temperature, max_tokens)
│
├── data/
│   ├── catalog/             # Scraped product catalog (catalog.json)
│   ├── qdrant_data/         # Qdrant persistent vector storage
│   └── semantic_memory/     # User profiles (profiles.json)
│
├── notebooks/               # Jupyter notebooks for prototyping & testing
│
└── src/
    ├── agents/              # Core Agent Layer
    │   ├── orchestrator.py  # AgentOrchestrator — main entry point for chat
    │   ├── router.py        # LLM-powered intent classifier
    │   ├── reflection_agent.py  # Safety loop (draft → critique → revise)
    │   ├── schemas.py       # Pydantic schemas
    │   ├── prompts/
    │   │   └── agent_prompts.py  # All prompt templates
    │   └── tools/
    │       ├── catalog_search_tool.py    # Hybrid Qdrant search (dense + sparse RRF)
    │       ├── direct_chat_tool.py       # Small talk handler with chat history
    │       ├── logistics_tool.py         # LLM-based delivery feasibility check
    │       └── preference_update_tool.py # Extract & merge recipient preferences
    │
    ├── api/                 # FastAPI Layer
    │   ├── main.py          
    │   ├── dependencies.py  
    │   ├── routers/
    │   │   ├── auth.py      
    │   │   └── chat.py      
    │   ├── schemas/
    │   │   ├── auth.py      
    │   │   └── chat.py      
    │   ├── services/
    │   │   └── auth.py      
    │   └── db/
    │       ├── core.py      
    │       └── models.py    
    │
    ├── db/                  # Vector Database
    │   └── qdrant_db_client.py 
    │
    ├── infrastructure/      # Infrastructure
    │   ├── config.py        
    │   ├── observability.py  # Langfuse tracing wrappers
    │   └── llm/
    │       ├── llm_provider.py  
    │       └── embeddings.py    
    │
    ├── memory/              # Memory Managers
    │   ├── semantic_memory_manager.py  # Persistent profile storage (JSON file)
    │   └── short_term_memory_manager.py  # In-session conversation buffer
    │
    └── services/            # Data Services
        ├── web_crawler.py   # Playwright scraper for Kapruka.com
        └── ingest_service/
            └── pipeline.py  # Catalog → embed → Qdrant ingestion pipeline
```

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/signup` | No | Register a new user |
| `POST` | `/auth/signin` | No | Login and receive JWT token |
| `GET` | `/chat/session` | JWT | Create a new chat session |
| `GET` | `/chat/profile` | JWT | Retrieve user's semantic profile |
| `POST` | `/chat` | JWT | Send a message (returns SSE stream) |

---

## Configuration

### `config/param.yaml`
```yaml
llm:
  provider: openrouter       # or "openai"
  tier: general              # general, strong, or reason
  temperature: 0.0
  max_tokens: 3000
  streaming: false

embedding:
  provider: openrouter
  tier: default              # default or large

qdrant:
  collection_name: kapruka_catalog
```

### `config/models.yaml`
```yaml
openrouter:
  chat:
    general: openai/gpt-4o-mini
    strong: openai/gpt-4o
    reason: openai/o3-mini
  embedding:
    default: openai/text-embedding-3-small
    large: openai/text-embedding-3-large
```

---

## Getting Started

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — fast Python package manager

### Setup

```bash
# Install dependencies
uv sync

# Configure environment
cp .env.sample .env
# Add your API keys to .env

# Run data ingestion (first time only)
uv run python -m src.services.ingest_service.pipeline

# Start the server
uv run uvicorn src.api.main:app --reload
```
---

### Langfuse Observability

To enable LLM tracing and observability, add the following to your `.env`:

```env
LANGFUSE_SECRET_KEY=
LANGFUSE_PUBLIC_KEY=
LANGFUSE_BASE_URL=
```

When these variables are set, Langfuse automatically captures full traces of every agent call — including LLM model, token usage, cost, prompts, and completions. When unset, all tracing is disabled with zero overhead.

---

## Key Dependencies

| Package | Purpose                                         |
|---|-------------------------------------------------|
| `fastapi` | Web framework                                   |
| `langchain`, `langchain-openai` | LLM chains, structured output, prompt templates |
| `qdrant-client` | Vector database client                          |
| `fastembed` | BM25 sparse embedding model                     |
| `sqlalchemy` | ORM for PostgreSQL                              |
| `psycopg2-binary` | PostgreSQL database driver                      |
| `langfuse` | Trace agents, LLM calls                         |
| `python-jose` | JWT token handling                              |
| `bcrypt` | Password hashing                                |
| `playwright` | Web scraping for Kapruka.com                    |
| `loguru` | Structured logging                              |
